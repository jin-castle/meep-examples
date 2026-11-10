"""E 트랙 — Meep 공식 예제 absorbed_power_density.py·.ipynb 재현 (Python_Tutorials/Basics.md "Absorbed Power Density Map of a Lossy Cylinder").
원본: NanoComp/meep python/examples/absorbed_power_density.py @ upstream/COMMIT (읽기 전용). 물리 설정 :10–68 그대로
(res 100, SiO2 원기둥 r 1 (meep.materials), 공기 2, PML 1, Ez 평면파 is_integrated, λ 1, fwidth 0.1 f, Mirror(Y), k_point 0, until_after_sources 100).
더한 것(field 불변): 더 큰 닫힌 상자(r+1)로 흡수 확인, 같은 상자에 빈 셀 정규화 run의 load_minus로 산란 전력, 입사 세기(빈 셀 x 면), source 하류 파형,
셀 전체 DFT Ez 지도, (--anim) 녹화.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import meep as mp
from meep.materials import SiO2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_blog", "tools"))
ap = argparse.ArgumentParser()
ap.add_argument("--resolution", type=float, default=100)
ap.add_argument("--anim", action="store_true")
ap.add_argument("--tag", default="")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
dpml, r, dair = 1.0, 1.0, 2.0
s = 2 * (dpml + dair + r)
fcen = 1.0
R2 = r + 1.0


def make(geo):
    src = [mp.Source(mp.GaussianSource(fcen, fwidth=0.1 * fcen, is_integrated=True), center=mp.Vector3(-0.5 * s + dpml), size=mp.Vector3(0, s), component=mp.Ez)]
    return mp.Simulation(resolution=a.resolution, cell_size=mp.Vector3(s, s), boundary_layers=[mp.PML(dpml)], sources=src, k_point=mp.Vector3(),
                         symmetries=[mp.Mirror(mp.Y)], geometry=geo)


def box(sim, h):
    return sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x=-h), size=mp.Vector3(0, 2 * h), weight=+1),
                        mp.FluxRegion(center=mp.Vector3(x=+h), size=mp.Vector3(0, 2 * h), weight=-1),
                        mp.FluxRegion(center=mp.Vector3(y=+h), size=mp.Vector3(2 * h, 0), weight=-1),
                        mp.FluxRegion(center=mp.Vector3(y=-h), size=mp.Vector3(2 * h, 0), weight=+1))


# 1) 빈 셀: 입사 세기 + 큰 상자 입사 장 저장
sim = make([])
inc_line = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(x=-R2), size=mp.Vector3(0, 2 * r)))
bigb = box(sim, R2)
tv = {"t": [], "v": []}
sim.run(mp.at_every(0.05, lambda s_: (tv["t"].append(s_.meep_time()), tv["v"].append(float(np.real(s_.get_field_point(mp.Ez, mp.Vector3(-0.5 * s + dpml + 0.5))))))), until_after_sources=100)
I0 = mp.get_fluxes(inc_line)[0] / (2 * r)   # 입사 세기(단위 길이당)
big_data = sim.get_flux_data(bigb)
sim.reset_meep()
# 2) 원기둥 (upstream)
sim = make([mp.Cylinder(material=SiO2, center=mp.Vector3(), radius=r, height=mp.inf)])
dft = sim.add_dft_fields([mp.Dz, mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(2 * r, 2 * r), yee_grid=True)
fb = box(sim, r)
fb2 = box(sim, R2)
scat = box(sim, R2)
sim.load_minus_flux_data(scat, big_data)
dmap = sim.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(s - 2 * dpml, s - 2 * dpml))
steps = []
rec = None
if a.anim:
    from field_anim import Recorder
    rec = Recorder(sim, mp.Ez, mp.Vector3(), mp.Vector3(s - 2 * dpml, s - 2 * dpml), dt=1.0, t_max=60, probe=mp.Vector3(r + 0.5, 0.3), period=1 / fcen)
    steps += [rec.step, rec.pstep]
sim.run(*steps, until_after_sources=100)
Dz = sim.get_dft_array(dft, mp.Dz, 0)
Ez = sim.get_dft_array(dft, mp.Ez, 0)
apd = 2 * np.pi * fcen * np.imag(np.conj(Ez) * Dz)
P_dft = float(np.sum(apd) / a.resolution ** 2)
P_box = mp.get_fluxes(fb)[0]
P_box2 = mp.get_fluxes(fb2)[0]
P_scat = -mp.get_fluxes(scat)[0]
if rec is not None:
    rec.save(os.path.join(a.out, f"field_{a.tag or 'abs'}.npz"),
             meta=dict(title=f"Re Ez — SiO₂ 원기둥(r 1 µm) 위 Ez 평면파 펄스, λ 1 µm (res {a.resolution:g})", extent=[-(s - 2 * dpml) / 2, (s - 2 * dpml) / 2, -(s - 2 * dpml) / 2, (s - 2 * dpml) / 2],
                       probe_label="원기둥 뒤 (1.5, 0.3) Ez"))
eps_c = SiO2.epsilon(fcen)[0][0]
summ = dict(res=a.resolution, t_end=sim.meep_time(), timesteps=sim.timestep(), P_dft=P_dft, P_box=P_box, err=abs(P_dft - P_box) / P_box, P_box_big=P_box2,
            P_scat=P_scat, I0=I0, Q_abs=P_box / (I0 * 2 * r), Q_scat=P_scat / (I0 * 2 * r), eps_SiO2=[eps_c.real, eps_c.imag], wall=time.time() - T0)
Ezmap = sim.get_dft_array(dmap, mp.Ez, 0)          # 집단 연산 — 모든 rank에서 (2026-11-09 MPI 교착 수정)
epsmap = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(s - 2 * dpml, s - 2 * dpml))
if mp.am_master():
    np.savez_compressed(os.path.join(a.out, f"{a.tag or 'abs'}.npz"), apd=apd, Ezmap=Ezmap, eps=epsmap,
                        trace_t=np.array(tv["t"]), trace_v=np.array(tv["v"]))
    json.dump(summ, open(os.path.join(a.out, f"{a.tag or 'abs'}.json"), "w"), indent=1, default=float)
    print("RESULT " + json.dumps(summ, default=float), flush=True)
