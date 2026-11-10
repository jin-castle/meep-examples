"""E 트랙 — Meep 공식 예제 zone_plate.py·.ipynb 재현 (Cylindrical_Coordinates.md "Focusing Properties of a Binary-Phase Zone Plate").
원본: NanoComp/meep python/examples/zone_plate.py @ upstream/COMMIT :10–164 그대로
(cyl m=−1, res 25, PML 1, 기판 유리 2(+PML), 홈 높이 0.5, padding 2, λ 0.5 fwidth 0.2 f, 평면파 Er + (−i)Eφ is_integrated(기판 안 z = −size_z/2 + pml),
N zones r_n² = nλ(f + nλ/4), f 200; near2far 면: 윗면 z = size_z/2 − pml(폭 size_r − pml) + 옆면; stop_when_fields_decayed(50, Er, (size_r/2, 0, 0), 1e-6);
far field r 스캔(z = f, 0…size_r−pml)·z 스캔(r 0, f ± 50) 간격 1/far_res).
더한 것(장 불변): 투과 flux 면(near2far 윗면과 같은 위치)·입사 flux(기판 안 source 위 z), 반구 far-field 적분 전력(수지), DFT Er 지도, source 점 파형, (--anim) 녹화, 피크·FWHM·첫 영점 후처리, 해상도 인자.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import meep as mp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_blog", "tools"))
ap = argparse.ArgumentParser()
ap.add_argument("--num-zones", type=int, default=25)
ap.add_argument("--resolution", type=float, default=25)
ap.add_argument("--far-res", type=float, default=10, help="far-field 스캔 점/µm (upstream 10)")
ap.add_argument("--scan-z", type=float, default=100)
ap.add_argument("--rscan-max", type=float, default=None, help="r 스캔 끝(기본 size_r − pml; 작게 주면 빠름)")
ap.add_argument("--hemi", type=int, default=0, help="반구 far-field 적분 점 수(0이면 생략), 반지름 = f")
ap.add_argument("--anim", action="store_true")
ap.add_argument("--tag", default="zp")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
resolution_um = a.resolution
pml_um, substrate_um, padding_um, height_um = 1.0, 2.0, 2.0, 0.5
focal_length_um, scan_length_z_um, farfield_resolution_um = 200, a.scan_z, a.far_res
wavelength_um = 0.5
frequency = 1 / wavelength_um
fwidth = 0.2 * frequency
num_zones = a.num_zones
zone_radius_um = np.array([math.sqrt(n * wavelength_um * (focal_length_um + n * wavelength_um / 4)) for n in range(1, num_zones + 1)])
size_r_um = zone_radius_um[-1] + padding_um + pml_um
size_z_um = pml_um + substrate_um + height_um + padding_um + pml_um
cell_size = mp.Vector3(size_r_um, 0, size_z_um)
src_z = -0.5 * size_z_um + pml_um
sources = [mp.Source(mp.GaussianSource(frequency, fwidth=fwidth, is_integrated=True), component=mp.Er, center=mp.Vector3(0.5 * size_r_um, 0, src_z), size=mp.Vector3(size_r_um)),
           mp.Source(mp.GaussianSource(frequency, fwidth=fwidth, is_integrated=True), component=mp.Ep, center=mp.Vector3(0.5 * size_r_um, 0, src_z), size=mp.Vector3(size_r_um), amplitude=-1j)]
glass = mp.Medium(index=1.5)
geometry = [mp.Block(material=glass, size=mp.Vector3(size_r_um, 0, pml_um + substrate_um), center=mp.Vector3(0.5 * size_r_um, 0, -0.5 * size_z_um + 0.5 * (pml_um + substrate_um)))]
z_lens = -0.5 * size_z_um + pml_um + substrate_um + 0.5 * height_um
for n in range(num_zones - 1, -1, -1):
    geometry.append(mp.Block(material=glass if n % 2 == 0 else mp.vacuum, size=mp.Vector3(zone_radius_um[n], 0, height_um), center=mp.Vector3(0.5 * zone_radius_um[n], 0, z_lens)))
sim = mp.Simulation(cell_size=cell_size, boundary_layers=[mp.PML(thickness=pml_um)], resolution=resolution_um, sources=sources, geometry=geometry, dimensions=mp.CYLINDRICAL, m=-1)
z_top = 0.5 * size_z_um - pml_um
n2f = sim.add_near2far(frequency, 0, 1, mp.Near2FarRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, z_top), size=mp.Vector3(size_r_um - pml_um, 0, 0)),
                       mp.Near2FarRegion(center=mp.Vector3(size_r_um - pml_um, 0, z_top - 0.5 * (height_um + padding_um)), size=mp.Vector3(0, 0, height_um + padding_um)))
# 추가 monitor: 투과 flux(윗면), 입사 flux(기판 안, source 위 0.5), DFT Er 지도
fl_top = sim.add_flux(frequency, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, z_top), size=mp.Vector3(size_r_um - pml_um, 0, 0)))
fl_inc = sim.add_flux(frequency, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, src_z + 0.5), size=mp.Vector3(size_r_um - pml_um, 0, 0)))
dm = sim.add_dft_fields([mp.Er], [frequency], center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), size=mp.Vector3(size_r_um - pml_um, 0, size_z_um - 2 * pml_um))
probe = mp.Vector3(0.5 * size_r_um, 0, 0)
tv = {"t": [], "v": []}


def rec_probe(s_):
    v = s_.get_field_point(mp.Er, probe)
    if mp.am_master():
        tv["t"].append(s_.meep_time()); tv["v"].append([float(np.real(v)), float(np.imag(v))])


steps = [mp.at_every(0.1, rec_probe)]
rec = None
if a.anim:
    from field_anim import Recorder
    rec = Recorder(sim, mp.Er, mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), mp.Vector3(min(size_r_um - pml_um, 20.0), 0, size_z_um - 2 * pml_um), dt=0.25, t_max=30.0, probe=probe, period=1 / frequency)
    steps += [rec.step, rec.pstep]
t1 = time.time()
sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50.0, mp.Er, probe, 1e-6))
out = {"tag": a.tag, "num_zones": num_zones, "resolution": resolution_um, "far_res": farfield_resolution_um, "size_r": size_r_um, "size_z": size_z_um, "R_N": float(zone_radius_um[-1]), "outer_zone_width": float(zone_radius_um[-1] - zone_radius_um[-2]),
       "steps": int(round(sim.meep_time() / sim.fields.dt)), "t_end": sim.meep_time(), "wall_fdtd": time.time() - t1}
out["flux_top"] = float(mp.get_fluxes(fl_top)[0]); out["flux_inc"] = float(mp.get_fluxes(fl_inc)[0]); out["T_top_over_inc"] = out["flux_top"] / out["flux_inc"]
z_f = -0.5 * size_z_um + pml_um + substrate_um + height_um + focal_length_um
r_max = a.rscan_max if a.rscan_max else (size_r_um - pml_um)
t2 = time.time()
ff_r = sim.get_farfields(n2f, farfield_resolution_um, center=mp.Vector3(0.5 * r_max, 0, z_f), size=mp.Vector3(r_max, 0, 0))
ff_z = sim.get_farfields(n2f, farfield_resolution_um, center=mp.Vector3(0, 0, z_f), size=mp.Vector3(0, 0, scan_length_z_um))
out["wall_farfield"] = time.time() - t2
Ir = np.abs(ff_r["Ex"]) ** 2 + np.abs(ff_r["Ey"]) ** 2 + np.abs(ff_r["Ez"]) ** 2
Iz = np.abs(ff_z["Ex"]) ** 2 + np.abs(ff_z["Ey"]) ** 2 + np.abs(ff_z["Ez"]) ** 2
rr = np.linspace(0, r_max, Ir.size); zz = np.linspace(focal_length_um - 0.5 * scan_length_z_um, focal_length_um + 0.5 * scan_length_z_um, Iz.size)


def fwhm_first_zero(x, y):
    i0 = int(np.argmax(y)); half = y[i0] / 2
    j = i0
    while j + 1 < len(y) and y[j + 1] > half:
        j += 1
    xr = x[j] + (x[j + 1] - x[j]) * (y[j] - half) / (y[j] - y[j + 1]) if j + 1 < len(y) else x[-1]
    k = i0
    while k - 1 >= 0 and y[k - 1] > half:
        k -= 1
    xl = x[k] - (x[k] - x[k - 1]) * (y[k] - half) / (y[k] - y[k - 1]) if k - 1 >= 0 else x[0]
    m = i0
    while m + 1 < len(y) and y[m + 1] < y[m]:
        m += 1
    return float(xr - xl), float(x[m])


out["I_peak_r"] = float(Ir.max()); out["r_peak"] = float(rr[int(np.argmax(Ir))]); out["I_peak_z"] = float(Iz.max()); out["z_peak"] = float(zz[int(np.argmax(Iz))])
w_r, r_first_min = fwhm_first_zero(rr, Ir)
out["fwhm_r_half_profile"] = w_r; out["fwhm_r_full"] = 2 * (w_r if rr[int(np.argmax(Ir))] == 0 else w_r)   # r ≥ 0 반쪽 → 전체 폭 2×(반폭) (피크가 r=0일 때)
out["r_first_min"] = r_first_min
w_z, _ = fwhm_first_zero(zz, Iz); out["fwhm_z"] = w_z
if a.hemi:
    t3 = time.time()
    th = np.linspace(0, 0.5 * math.pi, a.hemi)
    Rh = focal_length_um
    P = 0.0; rows = []
    for t_ in th:
        pt = mp.Vector3(Rh * math.sin(t_), 0, z_f - focal_length_um + Rh * math.cos(t_))
        E = sim.get_farfield(n2f, pt)
        Ex, Ey, Ez, Hx, Hy, Hz = [E[i] for i in range(6)]
        Sx = np.real(Ey * np.conj(Hz) - Ez * np.conj(Hy)); Sz = np.real(Ex * np.conj(Hy) - Ey * np.conj(Hx))
        Sr = Sx * math.sin(t_) + Sz * math.cos(t_)
        rows.append([float(t_), float(Sr)])
    th_a = np.array([r_[0] for r_ in rows]); Sr_a = np.array([r_[1] for r_ in rows])
    P = float(np.trapezoid(Sr_a * 2 * math.pi * Rh**2 * np.sin(th_a), th_a))   # m = ±1 성분의 φ 평균은 축대칭 → φ 적분 = 2π (Sr은 φ 평균값)
    out["P_far_hemisphere"] = P; out["hemi_rows"] = rows; out["P_far_over_flux_top"] = P / out["flux_top"] if out["flux_top"] else None; out["wall_hemi"] = time.time() - t3
er = sim.get_dft_array(dm, mp.Er, 0)
eps = sim.get_array(component=mp.Dielectric, center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), size=mp.Vector3(size_r_um - pml_um, 0, size_z_um - 2 * pml_um))
if mp.am_master():
    out["probe"] = tv
    out["wall_total"] = time.time() - T0
    np.savez_compressed(os.path.join(a.out, a.tag + "_fields.npz"), er=er, eps=np.real(eps), extent=np.array([0, size_r_um - pml_um, -(size_z_um / 2 - pml_um), size_z_um / 2 - pml_um]), rr=rr, Ir=Ir, zz=zz, Iz=Iz)
    if rec is not None:
        pass
    json.dump(out, open(os.path.join(a.out, a.tag + ".json"), "w"), indent=1)
    print(f"RESULT N={num_zones} res={resolution_um:g} z_peak={out['z_peak']:.2f} I_peak_z={out['I_peak_z']:.1f} I_peak_r={out['I_peak_r']:.1f} fwhm_r_full={out['fwhm_r_full']:.3f} r_first_min={out['r_first_min']:.3f} fwhm_z={out['fwhm_z']:.2f} T={out['T_top_over_inc']:.4f} Pfar/Ptop={out.get('P_far_over_flux_top')} steps={out['steps']} wall={out['wall_total']:.0f}s", flush=True)
if rec is not None:
    rec.save(os.path.join(a.out, a.tag + "_anim.npz"), eps=True, meta=dict(title=f"zone plate N={num_zones} Er(r,z,t)", extent=[0, min(size_r_um - pml_um, 20.0), -(size_z_um / 2 - pml_um), size_z_um / 2 - pml_um], probe_label="r 중앙 z 0"))
