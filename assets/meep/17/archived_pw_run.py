"""E 트랙 — Meep 공식 예제 oblique-planewave.py 재현 (Eigenmode_Source.md "Planewaves in Homogeneous Media").
원본: NanoComp/meep python/examples/oblique-planewave.py @ upstream/COMMIT (읽기 전용) :14–68 그대로
(res 50, 셀 (10+2·2)×10, PML 2 (x), n 1.5, CW f 1, EigenModeSource 폭 10, NO_DIRECTION, eig_kpoint = n f 회전, band 1, ODD_Z, eig_vol 한 픽셀, k_point, until 23.56).
더한 것: 각도 인자, 정상 상태 복소 Ez(10×10) 저장 → 위상 기울기로 전파각 추정, 2D FFT로 후방파 몫. (문서는 그림만.)
"""
import argparse
import json
import math
import os
import time

import numpy as np
import meep as mp

ap = argparse.ArgumentParser()
ap.add_argument("--resolution", type=float, default=50)
ap.add_argument("--angle", type=float, default=40)
ap.add_argument("--until", type=float, default=23.56)
ap.add_argument("--tag", default="pw")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
mp.verbosity(1)
resolution_um = a.resolution
pml_um, size_um = 2.0, 10.0
cell_size = mp.Vector3(size_um + 2 * pml_um, size_um, 0)
pml_layers = [mp.PML(thickness=pml_um, direction=mp.X)]
incident_angle = math.radians(a.angle)
frequency = 1.0
n_mat = 1.5
k_point = mp.Vector3(n_mat * frequency, 0, 0).rotate(mp.Vector3(0, 0, 1), incident_angle)
if incident_angle == 0:
    direction, eig_parity, symmetries, eig_vol = mp.AUTOMATIC, mp.EVEN_Y + mp.ODD_Z, [mp.Mirror(mp.Y)], None
else:
    direction, eig_parity, symmetries = mp.NO_DIRECTION, mp.ODD_Z, []
    eig_vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 1 / resolution_um, 0))
sources = [mp.EigenModeSource(src=mp.ContinuousSource(frequency), center=mp.Vector3(), size=mp.Vector3(0, size_um, 0), direction=direction, eig_kpoint=k_point, eig_band=1, eig_parity=eig_parity, eig_vol=eig_vol)]
sim = mp.Simulation(cell_size=cell_size, resolution=resolution_um, boundary_layers=pml_layers, sources=sources, k_point=k_point, default_material=mp.Medium(index=n_mat), symmetries=symmetries)
sim.run(until=a.until)
Ez = sim.get_array(component=mp.Ez, center=mp.Vector3(), size=mp.Vector3(size_um, size_um))
Ez = np.asarray(Ez)
# 위상 기울기 → k 벡터 (복소 장일 때만 의미; 0°는 실수 장이라 FFT로)
dx = 1 / resolution_um
xs = slice(int(2 * resolution_um), int(8 * resolution_um))   # 중앙 6 µm
sub = Ez[xs, xs]
out = dict(res=a.resolution, angle=a.angle, until=a.until, steps=sim.timestep(), complex=bool(np.iscomplexobj(Ez)), wall=time.time() - T0)
if np.iscomplexobj(Ez):
    kx = np.angle(np.sum(sub[1:, :] * np.conj(sub[:-1, :]))) / dx / (2 * math.pi)
    ky = np.angle(np.sum(sub[:, 1:] * np.conj(sub[:, :-1]))) / dx / (2 * math.pi)
    out.update(kx=float(kx), ky=float(ky), k_mag=float(math.hypot(kx, ky)), angle_fit=float(math.degrees(math.atan2(ky, kx))), k_expected=n_mat * frequency)
F = np.fft.fftshift(np.fft.fft2(sub * np.hanning(sub.shape[0])[:, None] * np.hanning(sub.shape[1])[None, :]))
P = np.abs(F) ** 2
fx = np.fft.fftshift(np.fft.fftfreq(sub.shape[0], dx))
i, j = np.unravel_index(np.argmax(P), P.shape)
kpk = (fx[i], fx[j])
# 후방파: 피크의 점대칭 위치(−k) 근방 전력 / 피크 근방 전력
def box(ii, jj, r=3):
    return P[max(ii - r, 0):ii + r + 1, max(jj - r, 0):jj + r + 1].sum()
ib, jb = len(fx) - 1 - i, len(fx) - 1 - j
out.update(fft_peak_k=[float(kpk[0]), float(kpk[1])], fft_peak_angle=float(math.degrees(math.atan2(kpk[1], kpk[0]))), backward_fraction_fft=float(box(ib, jb) / box(i, j)))
if mp.am_master():
    np.savez_compressed(os.path.join(a.out, f"{a.tag}.npz"), Ez=Ez, extent=np.array([-5, 5, -5, 5]))
    json.dump(out, open(os.path.join(a.out, f"{a.tag}.json"), "w"), indent=1, default=float)
    print("RESULT " + json.dumps(out, default=float), flush=True)
