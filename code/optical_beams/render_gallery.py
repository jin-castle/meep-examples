import argparse
import hashlib
import json
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image, ImageOps


def map_figure(array, extent, name, output, vmax, xlabel, ylabel):
    fig,ax=plt.subplots(figsize=(7,6),facecolor="#080808")
    ax.set_facecolor("black")
    image=ax.imshow(array.T,origin="lower",extent=extent,cmap="hot",vmin=0,vmax=vmax,interpolation="nearest",aspect="equal")
    ax.set(xlabel=xlabel,ylabel=ylabel,title=name)
    ax.tick_params(colors="white")
    for item in (ax.xaxis.label,ax.yaxis.label,ax.title): item.set_color("white")
    cb=fig.colorbar(image,ax=ax,fraction=.035,pad=.04)
    cb.ax.tick_params(colors="white")
    cb.set_label("instantaneous real E squared (a.u.)",color="white")
    fig.tight_layout()
    fig.savefig(output,dpi=150,facecolor=fig.get_facecolor())
    plt.close(fig)


def clean_tile(array,vmax):
    rgba=plt.cm.hot(np.clip(array.T[::-1]/vmax,0,1),bytes=True)
    return ImageOps.pad(Image.fromarray(rgba).convert("RGB"),(600,600),method=Image.Resampling.LANCZOS,color="black")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("directory",type=Path)
    args=parser.parse_args()
    root=args.directory.resolve()
    native=json.loads((root/"native3d/scene.json").read_text())
    renders={scalar:json.loads((root/"native3d"/("render_"+scalar+".json")).read_text()) for scalar in ("real2","modulus2")}
    assert native["spatial_stride"]==1 and not native["mesh_decimation"]
    assert all(render["passed"] and render["cut_planes"]==2 for render in renders.values())
    provenance={"normalization":"linear hot; 2D LG vmax=0.20*global max real2, 3D cuts and contour=0.02*each full-volume scalar maximum; Airy vmax=global max real2", "lg_quantity":"sum(Re(Ej(t=10))^2), j=x,y,z; alternative 3D modulus image explicitly uses sum(abs(Ej)^2)", "airy_quantity":"real Ez(t=90)^2; not time average", "lg_export":"native Meep get_array centers/interpolates component fields before squaring; not claimed numerically identical to nonlinear upstream output_field_function", "display_only_decimation":1, "iso_level_fraction_global_real2_max":.02,"reference_provenance":"README embeds the named m=2 PNGs but does not supply per-PNG run metadata; native VTK contours and restored original scene, not a bit-identical historical figure", "caveat":"Airy curvature is an interference pattern, not accelerating particles. Isosurfaces show selected instantaneous field magnitude, not physical material boundaries.","native_scene":native,"blender_renders":renders}
    with h5py.File(root/"lg/fields.h5","r") as hf:
        x,y,z=(hf[n][:] for n in ("x","y","z"))
        maximum=max(float(hf["real2"][i].max()) for i in range(len(x)))
        all_finite=all(np.isfinite(hf["real2"][i]).all() and np.isfinite(hf["imag2"][i]).all() for i in range(len(x)))
        vmax=.2*maximum
        provenance["isosurface_half"]="Original lower half-volume, inclusive ceil(Nz/2) endpoint at z="+str(native["half_z_max"])
        longitudinal=sum(hf["longitudinal/"+c][:].real**2 for c in ("ex","ey","ez"))
        transverse=sum(hf["transverse/"+c][:].real**2 for c in ("ex","ey","ez"))
        complex_transverse=hf["transverse/ez"][:]
        identity_errors={}
        geometry_ranges={}
        for plane in ("longitudinal","transverse"):
            fields=[hf[plane+"/"+c][:] for c in ("ex","ey","ez")]
            summed_parts=sum(v.real**2+v.imag**2 for v in fields)
            complex_modulus=sum(abs(v)**2 for v in fields)
            identity_errors[plane]=float(np.max(abs(summed_parts-complex_modulus))/max(float(complex_modulus.max()),1e-30))
            assert identity_errors[plane]<1e-12
            epsilon=hf[plane+"/epsilon"][:]
            geometry_ranges[plane]=[float(epsilon.min()),float(epsilon.max())]
        provenance["complex_squared_identity_relative_errors"]=identity_errors
        provenance["epsilon_ranges"]=geometry_ranges
        phi=np.linspace(0,2*np.pi,721)
        radius=.6
        iy=np.interp(radius*np.cos(phi),y,np.arange(len(y)))
        iz=np.interp(radius*np.sin(phi),z,np.arange(len(z)))
        sampled=map_coordinates(complex_transverse.real,[iy,iz],order=1)+1j*map_coordinates(complex_transverse.imag,[iy,iz],order=1)
        winding=float(np.diff(np.unwrap(np.angle(sampled))).sum()/(2*np.pi))
        provenance["transverse_plane"]={"x":-1.5,"coordinates":"get_array requested x=-1.5, collapsed dimension interpolated; y/z span full cell", "ez_phase_winding_radius":radius,"ez_phase_winding":winding,"minimum_ring_amplitude":float(abs(sampled).min())}
        provenance["longitudinal_plane"]={"z":0,"coordinates":"get_array requested z=0, collapsed dimension interpolated; x/y span full cell"}
        imax=np.where((x>=-2)&(x<=2.2))[0]
        jmax=np.where((y>=-2.2)&(y<=2.2))[0]
        kmax=np.where((z>=-1.7)&(z<=1.7))[0]
        map_figure(longitudinal[np.ix_(imax,jmax)],[x[imax[0]],x[imax[-1]],y[jmax[0]],y[jmax[-1]]],"LG m=2: longitudinal z=0",root/"vortex_longitudinal.png",vmax,"x (Meep units)","y (Meep units)")
        map_figure(transverse[np.ix_(jmax,kmax)],[y[jmax[0]],y[jmax[-1]],z[kmax[0]],z[kmax[-1]]],"LG m=2: transverse x=-1.5",root/"vortex_transverse.png",vmax,"y (Meep units)","z (Meep units)")
        gallery_longitudinal=clean_tile(longitudinal[np.ix_(imax,jmax)],vmax)
        gallery_transverse=clean_tile(transverse[np.ix_(jmax,kmax)],vmax)
        provenance["surface_lighting"]="Blender Cycles CPU one thread, smooth VTK field-gradient normals; no mesh smoothing or decimation"
        provenance["3d_cut_planes"]=native["cuts"]
        provenance["isosurface_triangles"]=native["surfaces"]["real2"]["triangles"]
        provenance["lg_global_max_real2"]=maximum
        provenance["lg_shape"]=list(hf["real2"].shape)
    raw=np.load(root/"airy/fields.npz")
    assert np.array_equal(raw["real2"],raw["ez"]**2)
    assert np.allclose(raw["epsilon"],1)
    map_figure(raw["real2"],[raw["x"][0],raw["x"][-1],raw["y"][0],raw["y"][-1]],"Incomplete Airy: M=0, W=4, free space",root/"airy_free_space.png",float(raw["real2"].max()),"x (Meep units)","y (Meep units)")
    names=["vortex_longitudinal.png","vortex_transverse.png","vortex_3d.png","vortex_3d_modulus.png","airy_free_space.png"]
    canvas=Image.new("RGB",(1800,1200),"#f8fafc")
    clean3d=ImageOps.fit(Image.open(root/"vortex_3d.png").convert("RGB"),(600,600))
    tiles=[gallery_longitudinal,gallery_transverse,clean3d,clean_tile(raw["real2"],float(raw["real2"].max()))]
    for i,tile in enumerate(tiles):
        canvas.paste(tile,((i%3)*600,(i//3)*600))
    canvas.save(root/"reference_gallery.png")
    provenance["runs"]={name:json.loads((root/name/"result.json").read_text()) for name in ("lg","airy")}
    airy_log=(root/"airy/run.log").read_text()
    provenance["airy_source_quadrature_warnings"]={"count":airy_log.count("IntegrationWarning:"),"note":"Unchanged upstream incomplete-Airy quadrature emitted subdivision/slow-convergence warnings during source initialization. Finite fields and a completed FDTD run do not establish quadrature convergence or physical accuracy; no convergence study is claimed."}
    source_root=Path(__file__).resolve().parent/"source/scripts"
    provenance["source_file_bytes_note"]="Executed source files use CRLF; Git text normalization may produce LF. Canonical SHA256 replaces CRLF with LF before hashing; this changes no Python tokens or physical parameters."
    provenance["source_hashes"]={}
    for name,relative in (("lg","Laguerre_Gauss_3d/LaguerreGauss3d.py"),("airy","Airy_2d/Airy2d.py")):
        contents=(source_root/relative).read_bytes()
        hashes={"executed_sha256":provenance["runs"][name]["source_sha256"],"copied_source_sha256":hashlib.sha256(contents).hexdigest(),"canonical_lf_sha256":hashlib.sha256(contents.replace(b"\r\n",b"\n")).hexdigest()}
        assert hashes["executed_sha256"]==hashes["copied_source_sha256"]
        provenance["source_hashes"][name]=hashes
    checks=dict(passed=bool(all_finite and np.isfinite(raw["ez"]).all()),lg_finite=bool(all_finite),lg_complex_squared_identity_relative_errors=identity_errors,lg_epsilon_ranges=geometry_ranges,airy_instantaneous_identity_exact=True,airy_uniform_epsilon=True,lg_phase_winding=winding,source_reduction_passed=provenance["runs"]["lg"]["source_acceleration"]["passed"],figures={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names})
    (root/"provenance.json").write_text(json.dumps(provenance,indent=2))
    (root/"checks.json").write_text(json.dumps(checks,indent=2))
    (root/"result.json").write_text(json.dumps({"passed":checks["passed"],"figures":names,"runs":provenance["runs"]},indent=2))
    print(json.dumps(checks),flush=True)


if __name__=="__main__": main()
