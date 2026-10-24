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
    args = parser.parse_args()
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
                for ix, xx in enumerate(x):
                    real, imag = np.zeros(shape[1:]), np.zeros(shape[1:])
                    for component in (mp.Ex,mp.Ey,mp.Ez):
                        field = sim.get_array(center=mp.Vector3(xx,0,0),size=mp.Vector3(0,5,4),component=component,cmplx=True)
                        real += field.real**2
                        imag += field.imag**2
                    finite &= bool(np.isfinite(real).all() and np.isfinite(imag).all())
                    r2[ix], i2[ix] = real, imag
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

    def wrapped_run(sim, *steps, **kwargs):
        return original_run(sim, mp.at_every(1,checkpoint),mp.at_end(export),**kwargs)

    mp.Simulation.run = wrapped_run
    os.chdir(out)
    if args.beam == "lg":
        physical = dict(e_z=1,e_y=0,m_charge=2,n1=1.0,n2=1.54,ref_medium=0,kw_0=8,kr_w=0,chi_deg=45)
        result["numerical"] = dict(cell=[5,5,4],resolution=77,pml=.25,frequency=5,runtime=10,courant=1/3,optical_periods=50)
    else:
        physical = dict(s_pol=True,n1=1.0,n2=1.0,ref_medium=0,kw_0=7,kr_w=0,M=0,W=4,chi_deg=45)
        result["numerical"] = dict(cell=[10,10],resolution=180,pml=.25,frequency=12,runtime=90,courant=.5,optical_periods=1080)
    result["physical"] = physical
    (out / "started.json").write_text(json.dumps(result,indent=2))
    try:
        module.main(SimpleNamespace(**physical))
    finally:
        mp.Simulation.run = original_run


if __name__ == "__main__":
    main()
