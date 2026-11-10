"""phase 1 — Povinelli 2005 OL 'Evanescent-wave bonding' Fig.1(c) 재현 (Meep 공식 예제 parallel-wvgs-force.py 방식).
원본 예제: NanoComp/meep python/examples/parallel-wvgs-force.py @ upstream/COMMIT :6–100 그대로
(res 40, Si n 3.45, 셀 (5+2, 3+2), PML 1, 정사각 a 1 도파로 2개 간격 s, k_point z 0.5, Mirror X(±1)·Y(−1); get_eigenmode(band 1/2, ODD_Y, match_frequency False) → f;
EigenModeSource Gaussian fwidth 0.1 f; flux 면 z(셀 전체), ForceRegion x 두 선(0.49 s, 0.5 s + 1.01 a); until_after_sources 1500; 힘/전력 = −F/P).
논문 조건(재현용 가정): 논문은 고정 주파수 νa/c 0.2에서 d/a 를 바꾼다(Fig.1(c)) → --fixed f 이면 get_eigenmode(0.2, match_frequency=True)로 k를 찾아 k_point를 그 값으로 다시 세운다(예제는 고정 k 0.5).
더한 것(장 불변): flux·force 시간 수렴(여러 종료 시각), 모드 단면 |Ey| 저장, 입력 모드 k·f·vg 기록.
"""
import argparse
import json
import os
import time

import numpy as np
import meep as mp

ap = argparse.ArgumentParser()
ap.add_argument("--s", type=float, required=True, help="도파로 간격 s/a (논문 d/a)")
ap.add_argument("--mode", choices=["odd", "even"], required=True, help="odd = x-odd(anti-symmetric), even = x-even(symmetric)")
ap.add_argument("--fixed", choices=["k", "f"], default="k", help="k: 예제(k_z 0.5), f: 논문(νa/c 0.2, k 탐색)")
ap.add_argument("--f0", type=float, default=0.2)
ap.add_argument("--resolution", type=float, default=40)
ap.add_argument("--after", type=float, default=1500)
ap.add_argument("--tag", default="pf")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
Si = mp.Medium(index=3.45)
dpml = 1.0
sx, sy = 5, 3
cell = mp.Vector3(sx + 2 * dpml, sy + 2 * dpml, 0)
aa = 1.0
s = a.s
xodd = a.mode == "odd"
geometry = [mp.Block(center=mp.Vector3(-0.5 * (s + aa)), size=mp.Vector3(aa, aa, mp.inf), material=Si), mp.Block(center=mp.Vector3(0.5 * (s + aa)), size=mp.Vector3(aa, aa, mp.inf), material=Si)]
symmetries = [mp.Mirror(mp.X, phase=-1 if xodd else 1), mp.Mirror(mp.Y, phase=-1)]
band = 2 if xodd else 1
k_point = mp.Vector3(z=0.5)
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(dpml)], symmetries=symmetries, k_point=k_point)
sim.init_sim()
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx, sy))
if a.fixed == "k":
    em = sim.get_eigenmode(0.22, mp.Z, vol, band, k_point, match_frequency=False, parity=mp.ODD_Y)
    fcen = float(np.real(em.freq)); kz = 0.5
else:
    em = sim.get_eigenmode(a.f0, mp.Z, vol, band, k_point, match_frequency=True, parity=mp.ODD_Y)
    fcen = float(np.real(em.freq)); kz = float(em.k.z)
    k_point = mp.Vector3(z=kz)
out = {"tag": a.tag, "s": s, "mode": a.mode, "fixed": a.fixed, "resolution": a.resolution, "fcen": fcen, "kz": kz, "band": band, "group_velocity": float(np.real(em.group_velocity)) if hasattr(em, "group_velocity") else None}
print(f"freq:, {'xodd' if xodd else 'xeven'}, {s}, {fcen}, kz {kz}", flush=True)
sim.reset_meep()
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(dpml)], symmetries=symmetries, k_point=k_point)
sim.change_sources([mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=0.1 * fcen), size=mp.Vector3(sx, sy), center=mp.Vector3(), eig_band=band, eig_kpoint=k_point, eig_match_freq=False, eig_parity=mp.ODD_Y)])
wvg_flux = sim.add_flux(fcen, 0, 1, mp.FluxRegion(direction=mp.Z, center=mp.Vector3(), size=mp.Vector3(sx, sy)))
wvg_force = sim.add_force(fcen, 0, 1, mp.ForceRegion(mp.Vector3(0.49 * s), direction=mp.X, weight=1, size=mp.Vector3(y=sy)), mp.ForceRegion(mp.Vector3(0.5 * s + 1.01 * aa), direction=mp.X, weight=-1, size=mp.Vector3(y=sy)))
dm = sim.add_dft_fields([mp.Ey], [fcen], center=mp.Vector3(), size=mp.Vector3(sx, sy))
conv = {"t": [], "flux": [], "force": []}


def rec(s_):
    fl = mp.get_fluxes(wvg_flux)[0]; fo = mp.get_forces(wvg_force)[0]
    if mp.am_master():
        conv["t"].append(s_.meep_time()); conv["flux"].append(float(fl)); conv["force"].append(float(fo))


sim.run(mp.at_every(100, rec), until_after_sources=a.after)
flux = float(mp.get_fluxes(wvg_flux)[0]); force = float(mp.get_forces(wvg_force)[0])
ey = sim.get_dft_array(dm, mp.Ey, 0)
eps = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(sx, sy))
out.update(flux=flux, force=force, F_over_P=-force / flux, steps=int(round(sim.meep_time() / sim.fields.dt)), t_end=sim.meep_time(), wall=time.time() - T0)
if mp.am_master():
    out["convergence"] = {"t": conv["t"], "F_over_P": [-(fo / fl) if fl else None for fl, fo in zip(conv["flux"], conv["force"])]}
    np.savez_compressed(os.path.join(a.out, a.tag + "_ey.npz"), ey_re=np.real(ey), ey_im=np.imag(ey), eps=np.real(eps), extent=np.array([-sx / 2, sx / 2, -sy / 2, sy / 2]))
    json.dump(out, open(os.path.join(a.out, a.tag + ".json"), "w"), indent=1)
    print(f"data:, {'xodd' if xodd else 'xeven'}, {s}, {flux}, {force}, {-force / flux}  (fixed {a.fixed}, f {fcen:.6f}, kz {kz:.6f}, wall {out['wall']:.0f}s)", flush=True)
