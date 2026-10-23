import argparse
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image, ImageDraw

from render_scene import field_rgba, save_phase_sprite


def outlined_field(values, limit):
    image = Image.fromarray(field_rgba(values, limit))
    draw = ImageDraw.Draw(image)
    for points in (((0,165),(150,165)), ((0,135),(150,135)), ((165,0),(165,120)), ((195,0),(195,120))):
        draw.line(points, fill="black", width=1)
    return np.asarray(image)


def save_design(values, path, signed=False):
    grid = values.reshape(61,61).T[::-1]
    if signed:
        limit = float(np.max(np.abs(grid)))
        rgba = matplotlib.colormaps["RdBu"]((grid/limit+1)/2, bytes=True)
    else:
        rgba = matplotlib.colormaps["gray_r"](grid, bytes=True)
    image = Image.fromarray(rgba).resize((720,720), Image.Resampling.NEAREST)
    ImageDraw.Draw(image).rectangle((0,0,719,719), outline="black", width=3)
    image.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    result = json.loads((args.raw/"result.json").read_text())
    datasets = [dict(np.load(args.raw/r["raw"])) for r in result["records"]]
    forward_limit = max(float(np.max(np.abs(d[f"{p}_full_Ez"]))) for d in datasets for p in ("forward","updated_forward"))
    adjoint_limit = max(float(np.max(np.abs(d["adjoint_full_Ez"]))) for d in datasets)
    manifest = {**result, "records": [], "grid_shape": [61,61], "gradient_shape": [61,61], "phase_frame_count":32, "phase_columns":8, "phase_rows":4, "scene_pixels":[360,300], "forward_limit":forward_limit, "adjoint_limit":adjoint_limit, "phase_convention":"Re(Ez * exp(-i * 2*pi*k/32)); saved steady-state complex DFT, not transient propagation", "density_indexing":"x*Ny+y; 61 by 61; no threshold or binarization", "colormap":"RdBu", "normalization":"Common symmetric forward scale across all before/after states; separate common symmetric adjoint scale", "full_extent_um":[-3,3,-2.5,2.5], "design_extent_um":[-.5,.5,-.5,.5]}
    checks=[]
    previous=None
    previous_field=None
    for record, raw in zip(result["records"],datasets):
        i=record["iteration"]
        dest=args.out/f"{i:03d}"
        dest.mkdir(exist_ok=True)
        before,after=raw["density_initial"],raw["density_updated"]
        assert record["objective_after"] > record["objective_before"]
        assert before.shape == after.shape == (3721,)
        assert np.isfinite(before).all() and np.isfinite(after).all()
        assert np.all((after>=0)&(after<=1))
        gradient=raw["gradient"]
        assert gradient.shape == (3721,) and np.isfinite(gradient).all()
        expected_update=np.clip(before+record["trials"][-1]["max_density_change"]*gradient/np.max(np.abs(gradient)),0,1)
        assert np.array_equal(after,expected_update)
        if previous is not None:
            assert np.array_equal(previous, before)
        field_repeat_error=0.0
        if previous_field is not None:
            field_repeat_error=float(np.max(np.abs(previous_field-raw["forward_full_Ez"]))/np.max(np.abs(previous_field)))
            assert field_repeat_error < 1e-8
        previous_field=raw["updated_forward_full_Ez"]
        previous=after
        row={**record,"x_before":before.tolist(),"x_after":after.tolist(),"gradient":raw["gradient"].tolist(),"gradient_shape":[61,61],"grid_shape":[61,61],"raw_sha256":hashlib.sha256((args.raw/record["raw"]).read_bytes()).hexdigest()}
        check={"iteration":i,"monotonic":True,"density_chain_exact":True,"projected_gradient_update_exact":True,"repeated_geometry_forward_field_matches":True,"field_repeat_relative_linf_error":field_repeat_error,"scenes":{}}
        for prefix,stem in (("forward","forward"),("adjoint","adjoint"),("updated_forward","updated-forward")):
            field=raw[f"{prefix}_full_Ez"]
            x,y=raw[f"{prefix}_full_x"],raw[f"{prefix}_full_y"]
            assert field.shape == (360,300) and np.iscomplexobj(field) and np.isfinite(field).all()
            assert np.allclose(np.diff(x),1/60) and np.allclose(np.diff(y),1/60)
            assert np.isclose(x[0],-3+1/120) and np.isclose(y[0],-2.5+1/120)
            limit=adjoint_limit if prefix=="adjoint" else forward_limit
            rgba=outlined_field(field.real,limit)
            scene=f"{stem}-scene.png"
            Image.fromarray(rgba).save(dest/scene)
            row[f"{prefix}_scene"]=f"{i:03d}/{scene}"
            scene_check={"complex_finite":True,"coordinates_verified":True,"symmetric_limit":limit}
            if prefix != "updated_forward":
                sprite=f"{stem}-phases.png"
                scene_check.update(save_phase_sprite(field,limit,dest/sprite,render=outlined_field))
                row[f"{prefix}_phases"]=f"{i:03d}/{sprite}"
                assert np.array_equal(np.asarray(Image.open(dest/sprite).crop((0,0,360,300))),rgba)
                ix=np.flatnonzero((x>=-.5)&(x<=.5)); iy=np.flatnonzero((y>=-.5)&(y<=.5))
                assert len(ix)==len(iy)==60
                left,top=int(ix[0]),int(len(y)-1-iy[-1])
                crop=rgba[top:top+60,left:left+60]
                capture=Image.fromarray(crop).resize((720,720),Image.Resampling.NEAREST)
                capture_name=f"{stem}-capture.png"
                capture.save(dest/capture_name)
                assert np.array_equal(np.asarray(Image.open(dest/capture_name)),np.repeat(np.repeat(crop,12,axis=0),12,axis=1))
                row[f"{prefix}_capture"]=f"{i:03d}/{capture_name}"
                scene_check["phase0_capture_exact_scene_crop"]=True
                if prefix == "forward":
                    mask=(x>=-1.35)&(x<=-.65)
                    slope=float(np.polyfit(x[mask],np.unwrap(np.angle(field[mask,int(np.argmin(abs(y)))])),1)[0])
                    assert slope>0
                    scene_check["input_phase_slope_rad_per_um"]=slope
            check["scenes"][prefix]=scene_check
        for key,values,signed in (("gradient_design",raw["gradient"],True),("density_initial",before,False),("density_updated",after,False)):
            name=key.replace("_","-")+".png"
            save_design(values,dest/name,signed)
            row[key]=f"{i:03d}/{name}"
        manifest["records"].append(row)
        checks.append(check)
    manifest["render_source_sha256"]={}
    for name in ("render_iterations.py","render_scene.py"):
        path=Path(__file__).with_name(name)
        shutil.copy2(path,args.raw/"executed-source"/name)
        manifest["render_source_sha256"][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    (args.out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    validation={"passed":True,"iterations":len(checks),"checks":checks,"finite_difference_gate":result["records"][1]["finite_difference_gate"],"all_physical_runs_before_time_cap":all(all(t<1000 for t in r["simulation_times"].values()) for r in result["records"])}
    (args.raw/"validation.json").write_text(json.dumps(validation,indent=2))
    (args.out/"validation.json").write_text(json.dumps(validation,indent=2))
    print(json.dumps({"passed":True,"iterations":len(checks),"manifest":str(args.out/"manifest.json"),"forward_limit":forward_limit,"adjoint_limit":adjoint_limit}))


if __name__ == "__main__":
    main()
