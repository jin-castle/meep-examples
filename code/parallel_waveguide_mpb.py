"""MPB 경로 (Meep 공식 예제 parallel-wvgs-mpb.py @ upstream/COMMIT :7–61 그대로 + 논문 조건): 2D yz 단면, x 전파, 두 도파로 y 간격 s, run_yodd_zodd(anti-sym)/run_yeven_zodd(sym).
--fixed k: k_x 0.5에서 f·vg(예제) ; --fixed f: find_k 로 f 0.2의 k·vg(논문 Eq.1 조건). 힘 = −(1/ω)(dω/ds)|_k / vg (중심 차분, 예제 compute_force).
"""
import argparse
import json
import os
import time

import numpy as np
import meep as mp
from meep import mpb

ap = argparse.ArgumentParser()
ap.add_argument("--fixed", choices=["k", "f"], default="k")
ap.add_argument("--f0", type=float, default=0.2)
ap.add_argument("--resolution", type=int, default=128)
ap.add_argument("--smin", type=float, default=0.025)
ap.add_argument("--smax", type=float, default=1.075)
ap.add_argument("--ds", type=float, default=0.05)
ap.add_argument("--tag", default="mpb")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
Si = mp.Medium(index=3.45)
syz = 10
lat = mp.Lattice(size=mp.Vector3(0, syz, syz))
aa = 1.0


def solve(s, yodd):
    geometry = [mp.Block(center=mp.Vector3(0, -0.5 * (s + aa), 0), size=mp.Vector3(mp.inf, aa, aa), material=Si), mp.Block(center=mp.Vector3(0, 0.5 * (s + aa), 0), size=mp.Vector3(mp.inf, aa, aa), material=Si)]
    ms = mpb.ModeSolver(resolution=a.resolution, k_points=[mp.Vector3(0.5)], geometry_lattice=lat, geometry=geometry, num_bands=1, tolerance=1e-9)
    par = (mp.ODD_Y + mp.ODD_Z) if yodd else (mp.EVEN_Y + mp.ODD_Z)
    if a.fixed == "k":
        if yodd:
            ms.run_yodd_zodd()
        else:
            ms.run_yeven_zodd()
        f = float(ms.get_freqs()[0]); vg = float(ms.compute_group_velocity_component(mp.Vector3(1, 0, 0))[0]); k = 0.5
    else:
        ks = ms.find_k(par, a.f0, 1, 1, mp.Vector3(1, 0, 0), 1e-6, 0.4, 0.2, 0.9)
        k = float(ks[0]); f = a.f0
        vg = float(ms.compute_group_velocity_component(mp.Vector3(1, 0, 0))[0])
    return f, vg, k


ss = np.arange(a.smin, a.smax, a.ds)
rows = []
for s in ss:
    r = {"s": float(s)}
    for name, yodd in (("odd", True), ("even", False)):
        f, vg, k = solve(float(s), yodd)
        r[name] = {"f": f, "vg": vg, "k": k}
    rows.append(r)
    print(f"mpb:, {s:.3f}, odd f {r['odd']['f']:.6f} vg {r['odd']['vg']:.5f} k {r['odd']['k']:.5f}, even f {r['even']['f']:.6f} vg {r['even']['vg']:.5f} k {r['even']['k']:.5f}", flush=True)
ds = float(ss[1] - ss[0])


def force(name):
    f = np.array([r[name]["f"] for r in rows]); vg = np.array([r[name]["vg"] for r in rows])
    f_avg = 0.5 * (f[:-1] + f[1:]); df = f[1:] - f[:-1]; vg_avg = 0.5 * (vg[:-1] + vg[1:])
    return (-1 / f_avg * df / ds * 1 / vg_avg).tolist()


out = {"tag": a.tag, "fixed": a.fixed, "resolution": a.resolution, "ds": ds, "rows": rows, "s_mid": (0.5 * (ss[:-1] + ss[1:])).tolist(), "force_odd": force("odd"), "force_even": force("even"), "wall": time.time() - T0,
       "note": "예제 compute_force는 s[:-1]에 힘을 찍지만 중심 차분의 자연 위치는 s 중점(s_mid) — 둘 다 기록"}
json.dump(out, open(os.path.join(a.out, a.tag + ".json"), "w"), indent=1)
print("RESULT mpb", a.fixed, "res", a.resolution, "n", len(rows), "wall", round(out["wall"]), flush=True)
