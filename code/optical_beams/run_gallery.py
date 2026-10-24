import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import math
from functools import lru_cache
from types import SimpleNamespace

import h5py
import meep as mp
import numpy as np
from scipy.integrate import quad
from scipy.special import jv


def accelerated_lg(optbeam, out):
    original = optbeam.LaguerreGauss3d.profile

    @lru_cache(maxsize=100000)
    def radial(rho, shift, k, waist, m):
        def integrand(theta):
            sine, cosine = math.sin(theta), math.cos(theta)
            return sine*cosine*math.exp(-(k*waist*sine/2)**2)*theta**abs(m)*jv(m,k*rho*sine)*np.exp(1j*k*shift*cosine)
        real = quad(lambda t: integrand(t).real,0,math.pi/2,epsabs=1e-11,epsrel=1e-10)[0]
        imag = quad(lambda t: integrand(t).imag,0,math.pi/2,epsabs=1e-11,epsrel=1e-10)[0]
        return 2*math.pi*(-1)**m*k*k*(real+1j*imag)

    def reduced(self,r):
        rho = round(math.hypot(r.y,r.z),14)
        return radial(rho,self.x,self._k,self._W_y,self._m)*np.exp(1j*self._m*math.atan2(r.z,r.y))

    beam = optbeam.LaguerreGauss3d(-2.15,{"W_y":8/(10*math.pi),"k":10*math.pi,"m":2})
    points = [(0,0),(.25,0),(-.25,0),(0,.25),(0,-.25),(.25,.25),(-.25,.25),(.25,-.25),(-.25,-.25),(.8,0),(-.8,0),(0,.8),(0,-.8),(.7,.4),(-.7,.4),(.7,-.4),(-.7,-.4),(1.5,1.5),(-1.5,1.5),(1.5,-1.5),(-1.5,-1.5),(1.5,0),(.03,.07)]
    checks=[]
    for y,z in points:
        r=mp.Vector3(0,y,z)
        expected,actual=original(beam,r),reduced(beam,r)
        absolute=abs(actual-expected)
        relative=absolute/abs(expected) if abs(expected)>1e-6 else None
        checks.append(dict(y=y,z=z,original=[expected.real,expected.imag],reduced=[actual.real,actual.imag],absolute_error=absolute,relative_error=relative))
        assert absolute<1e-5 and (relative is None or relative<1e-4)
    info=dict(passed=True,points=checks,max_absolute_error=max(c["absolute_error"] for c in checks),
              max_relative_error_above_1e_minus6=max(c["relative_error"] for c in checks if c["relative_error"] is not None),
              formula="2*pi*(-1)^m*k^2*exp(i*m*atan2(z,y))*integral_0^(pi/2)[sin(theta)cos(theta)exp(-(k*w*sin(theta)/2)^2)*theta^abs(m)*J_m(k*rho*sin(theta))*exp(i*k*x*cos(theta))] dtheta",
              method="Exact analytic azimuth integral of upstream spherical spectrum; no paraxial approximation. Cached radius rounded to14 decimals. SciPy quad epsabs1e-11 epsrel1e-10.",
              orientation="exp(+i*m*atan2(z,y)); verified all y,z quadrants against original double quadrature")
    (out/"source-validation.json").write_text(json.dumps(info,indent=2))
    optbeam.LaguerreGauss3d.profile=reduced
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--beam", choices=("lg", "airy"), required=True)
    parser.add_argument("--capture-motion", action="store_true",
                        help="LG only: retain the phase cross term and verify later FDTD samples")
    args = parser.parse_args()
    if args.capture_motion and args.beam != "lg":
        parser.error("--capture-motion requires --beam lg")
    root, out = args.upstream.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root))
    import optbeam
    source = root / ("scripts/Laguerre_Gauss_3d/LaguerreGauss3d.py" if args.beam == "lg" else "scripts/Airy_2d/Airy2d.py")
    spec = importlib.util.spec_from_file_location("gallery_original", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    started = time.monotonic()
    original_run = mp.Simulation.run
    result = dict(beam=args.beam, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  upstream_commit="ca145119e5bd0f0804d846ea42e35e4c3daa91de", meep=mp.__version__,
                  source_script_unchanged=True, mpi_processes=mp.count_processors(),
                  threads={k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
                  output_change="Original Python per-cell output callbacks replaced by native get_array plane exports; simulation grid/source/steps unchanged")
    if args.beam == "lg":
        result["source_acceleration"] = accelerated_lg(optbeam,out)

    def checkpoint(sim):
        state = dict(beam=args.beam, time=float(sim.meep_time()), elapsed_seconds=time.monotonic()-started)
        (out / "progress.json").write_text(json.dumps(state))
        print("PROGRESS", json.dumps(state), flush=True)

    def export(sim):
        checkpoint(sim)
        if args.beam == "airy":
            ez = sim.get_array(component=mp.Ez)
            eps = sim.get_array(component=mp.Dielectric)
            x, y, z, weights = sim.get_array_metadata()
            np.savez_compressed(out / "fields.npz", ez=ez, real2=ez**2, epsilon=eps, x=x, y=y)
            result.update(shape=list(ez.shape), finite=bool(np.isfinite(ez).all()),
                          quantity="Instantaneous real Ez(t)^2 at t=90, not time-averaged intensity", epsilon_range=[float(eps.min()),float(eps.max())])
        else:
            x, y, z, weights = sim.get_array_metadata()
            del weights
            shape = (len(x), len(y), len(z))
            finite = True
            with h5py.File(out / "fields.h5", "w") as hf:
                for name, coords in (("x",x),("y",y),("z",z)):
                    hf.create_dataset(name, data=coords)
                r2 = hf.create_dataset("real2", shape=shape, dtype="f8", chunks=(1,shape[1],shape[2]), compression="lzf")
                i2 = hf.create_dataset("imag2", shape=shape, dtype="f8", chunks=(1,shape[1],shape[2]), compression="lzf")
                cross = hf.create_dataset("cross", shape=shape, dtype="f8", chunks=(1,shape[1],shape[2]), compression="lzf") if args.capture_motion else None
                for ix, xx in enumerate(x):
                    real, imag = np.zeros(shape[1:]), np.zeros(shape[1:])
                    mixed = np.zeros(shape[1:])
                    for component in (mp.Ex,mp.Ey,mp.Ez):
                        field = sim.get_array(center=mp.Vector3(xx,0,0),size=mp.Vector3(0,5,4),component=component,cmplx=True)
                        real += field.real**2
                        imag += field.imag**2
                        if cross is not None:
                            mixed += field.real * field.imag
                    finite &= bool(np.isfinite(real).all() and np.isfinite(imag).all())
                    r2[ix], i2[ix] = real, imag
                    if cross is not None:
                        finite &= bool(np.isfinite(mixed).all())
                        cross[ix] = mixed
                    if ix % 50 == 0:
                        print("EXPORT",ix,shape[0],flush=True)
                for name, center, size in (("longitudinal",mp.Vector3(),mp.Vector3(5,5,0)),("transverse",mp.Vector3(-1.5,0,0),mp.Vector3(0,5,4))):
                    group = hf.create_group(name)
                    for label, component in (("ex",mp.Ex),("ey",mp.Ey),("ez",mp.Ez),("epsilon",mp.Dielectric)):
                        group.create_dataset(label,data=sim.get_array(center=center,size=size,component=component,cmplx=label!="epsilon"))
            result.update(shape=list(shape), finite=finite, quantity="sum(Re(E_j(t))^2), sum(Im(E_j(t))^2), j=x,y,z; their sum is sum(abs(complex E_j(t))^2)")
        result.update(passed=result["finite"], elapsed_seconds=time.monotonic()-started, final_time=float(sim.meep_time()))
        (out / "result.json").write_text(json.dumps(result, indent=2))
        print("RESULT",json.dumps(result),flush=True)

    def validate_motion(sim):
        now = float(sim.meep_time())
        delta = now - result["final_time"]
        if delta < .01:
            return
        phase = 2 * math.pi * result["numerical"]["frequency"] * delta
        cosine, sine = math.cos(phase), math.sin(phase)
        sums = {name: [0., 0.] for name in ("native_half_volume", "incident_cut", "reflected_cut")}
        with h5py.File(out / "fields.h5", "r") as hf:
            half_end = 30 + math.ceil((len(hf["z"]) - 60) / 2) + 1
            for ix in range(30, len(hf["x"]) - 30):
                actual = np.zeros((len(hf["y"]), len(hf["z"])))
                for component in (mp.Ex, mp.Ey, mp.Ez):
                    field = sim.get_array(center=mp.Vector3(float(hf["x"][ix]),0,0),
                                          size=mp.Vector3(0,5,4),component=component,cmplx=True)
                    actual += field.real**2
                predicted = (hf["real2"][ix] * cosine**2 + hf["imag2"][ix] * sine**2
                             + 2 * hf["cross"][ix] * sine * cosine)
                selectors = [("native_half_volume", (slice(30,-30), slice(30,half_end))),
                             ("reflected_cut", (-31, slice(30,-30)))]
                if ix == 30:
                    selectors.append(("incident_cut", (slice(30,-30), slice(30,-30))))
                for name, selector in selectors:
                    observed, expected = actual[selector], predicted[selector]
                    sums[name][0] += float(np.sum((observed - expected)**2))
                    sums[name][1] += float(np.sum(observed**2))
        errors = {name: math.sqrt(error / norm) for name, (error, norm) in sums.items()}
        sample = dict(time=now, delta=delta, phase_radians=phase, relative_l2=errors)
        motion["samples"].append(sample)
        (out / "motion-validation.json").write_text(json.dumps(motion, indent=2))
        print("MOTION_SAMPLE", json.dumps(sample), flush=True)

    def wrapped_run(sim, *steps, **kwargs):
        value = original_run(sim, mp.at_every(1,checkpoint),mp.at_end(export),**kwargs)
        if args.capture_motion:
            original_run(sim, mp.at_every(.025,validate_motion), until=.11)
            motion["passed"] = (len(motion["samples"]) >= 4 and
                                all(error < .01 for sample in motion["samples"]
                                    for error in sample["relative_l2"].values()))
            motion["maximum_relative_l2"] = max(error for sample in motion["samples"]
                                                for error in sample["relative_l2"].values())
            (out / "motion-validation.json").write_text(json.dumps(motion, indent=2))
            assert motion["passed"], motion
            print("MOTION_VALIDATION_COMPLETE", json.dumps(motion), flush=True)
        return value

    mp.Simulation.run = wrapped_run
    os.chdir(out)
    if args.beam == "lg":
        physical = dict(e_z=1,e_y=0,m_charge=2,n1=1.0,n2=1.54,ref_medium=0,kw_0=8,kr_w=0,chi_deg=45)
        result["numerical"] = dict(cell=[5,5,4],resolution=77,pml=.25,frequency=5,runtime=10,courant=1/3,optical_periods=50)
    else:
        physical = dict(s_pol=True,n1=1.0,n2=1.0,ref_medium=0,kw_0=7,kr_w=0,M=0,W=4,chi_deg=45)
        result["numerical"] = dict(cell=[10,10],resolution=180,pml=.25,frequency=12,runtime=90,courant=.5,optical_periods=1080)
    result["physical"] = physical
    motion = dict(method="monochromatic phase reconstruction, not transient frames or a DFT accumulator",
                  formula="A*cos(omega*dt)^2+B*sin(omega*dt)^2+2*C*sin(omega*dt)*cos(omega*dt)",
                  A="sum(Re(E_j(t0))^2)", B="sum(Im(E_j(t0))^2)",
                  C="sum(Re(E_j(t0))*Im(E_j(t0)))", time_convention="exp(-i*omega*dt)",
                  spatial_stride=1, crop_cells_each_face=30, relative_l2_tolerance=.01,
                  comparison="directly evolved Meep samples on every native half-volume/cut grid point",
                  samples=[], passed=False)
    (out / "started.json").write_text(json.dumps(result,indent=2))
    try:
        module.main(SimpleNamespace(**physical))
    finally:
        mp.Simulation.run = original_run


if __name__ == "__main__":
    main()
