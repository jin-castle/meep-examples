"""Band gap, resonant modes and transmission of a perforated waveguide cavity.

Adapted from NanoComp/meep holey-wvg-cavity.py and holey-wvg-bands.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e, via holey_repro.py.
Upstream licensing remains applicable; see assets/meep/26/provenance.json.
Publication uses archived calculations. No optional animation helpers are needed.
Modes: bands (periodic cell), harminv (defect modes), trans (two-run spectrum).
"""
import argparse
import json
import os
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["bands", "trans", "harminv"], required=True)
    ap.add_argument("--resolution", type=float, default=20)
    ap.add_argument("-N", type=int, nargs="+", default=[3])
    ap.add_argument("--sy", type=float, default=6)
    ap.add_argument("--fcen", type=float, default=0.25)
    ap.add_argument("--df", type=float, default=0.2)
    ap.add_argument("--window", type=float, default=400, help="harminv: time after source ends (default 400)")
    ap.add_argument("--decay", type=float, default=1e-3, help="trans: field-decay threshold (default 1e-3)")
    ap.add_argument("--noavg", action="store_true", help="disable subpixel averaging")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default="photonic-crystal-cavity-output")
    a = ap.parse_args()
    import meep as mp
    if a.resolution <= 0 or a.sy <= 2 or a.window <= 0 or not 0 < a.decay < 1 or any(n < 0 for n in a.N):
        ap.error("require resolution/window > 0, sy > 2, 0 < decay < 1, N >= 0")
    os.makedirs(a.out, exist_ok=True)
    T0 = time.time()
    eps, w, r, d, pad, dpml = 13, 1.2, 0.36, 1.4, 2, 1
    WG = mp.Medium(epsilon=eps)


    def geom(N):
        g = [mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), material=WG)]
        for i in range(N):
            g.append(mp.Cylinder(r, center=mp.Vector3(d / 2 + i)))
            g.append(mp.Cylinder(r, center=mp.Vector3(-(d / 2 + i))))
        return g


    def dump(name, obj):
        if mp.am_master():
            json.dump(obj, open(os.path.join(a.out, name), "w"), indent=1, default=float)


    if a.mode == "bands":
        sim = mp.Simulation(cell_size=mp.Vector3(1, 12), geometry=[mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), material=WG), mp.Cylinder(radius=r)],
                            sources=[mp.Source(mp.GaussianSource(0.25, fwidth=1.5), component=mp.Hz, center=mp.Vector3(0.1234))],
                            symmetries=[mp.Mirror(direction=mp.Y, phase=-1)], boundary_layers=[mp.PML(1, direction=mp.Y)], resolution=a.resolution)
        kpts = mp.interpolate(19, [mp.Vector3(0), mp.Vector3(0.5)])
        fs = sim.run_k_points(300, kpts)
        dump(f"bands_r{a.resolution:g}.json", dict(kx=[k.x for k in kpts], freqs=[[float(np.real(f)) for f in fl] for fl in fs], wall=time.time() - T0))
        if mp.am_master():
            print("BANDS done", time.time() - T0, flush=True)
        return

    if a.mode == "harminv":
        rows = []
        for N in a.N:
            sx = 2 * (pad + dpml + N) + d - 1
            sim = mp.Simulation(cell_size=mp.Vector3(sx, a.sy), geometry=geom(N), boundary_layers=[mp.PML(dpml)], resolution=a.resolution,
                                sources=[mp.Source(mp.GaussianSource(a.fcen, fwidth=a.df), component=mp.Hz, center=mp.Vector3())],
                                symmetries=[mp.Mirror(mp.Y, phase=-1), mp.Mirror(mp.X, phase=-1)], eps_averaging=not a.noavg)
            h = mp.Harminv(mp.Hz, mp.Vector3(), a.fcen, a.df)
            t1 = time.time()
            sim.run(mp.after_sources(h), until_after_sources=a.window)
            modes = [dict(f=m.freq, Q=m.Q, amp=abs(m.amp), err=abs(m.err)) for m in h.modes]
            rows.append(dict(N=N, sy=a.sy, res=a.resolution, window=a.window, noavg=a.noavg, modes=modes, wall=time.time() - t1))
            if mp.am_master():
                print("HARM " + json.dumps(rows[-1], default=float), flush=True)
            sim.reset_meep()
        dump(f"harminv_{a.tag or 'run'}.json", dict(args=vars(a), rows=rows))
        return

    # ---------------- trans
    N = a.N[0]
    sx = 2 * (pad + dpml + N) + d - 1
    X = 0.5 * sx - dpml
    Y = a.sy - 2 * dpml
    x_t = X - 0.5
    x_src = -X
    x_r = x_src + 0.5
    FR = (a.fcen, a.df, 500)
    FRD = (0.2345, 0.013, 261)
    F3 = [0.18, 0.2345, 0.27]


    def make(Nh):
        sim = mp.Simulation(cell_size=mp.Vector3(sx, a.sy), geometry=geom(Nh), boundary_layers=[mp.PML(dpml)], resolution=a.resolution,
                            sources=[mp.Source(mp.GaussianSource(a.fcen, fwidth=a.df), component=mp.Ey, center=mp.Vector3(x_src), size=mp.Vector3(0, w))],
                            symmetries=[mp.Mirror(mp.Y, phase=-1)])
        fl = dict(
            up=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, 2 * w))),
            tran=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, Y))),
            refl=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_r), size=mp.Vector3(0, Y))),
            side_p=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(0.5 * (x_r + x_t), 0.5 * Y), size=mp.Vector3(x_t - x_r))),
            side_m=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(0.5 * (x_r + x_t), -0.5 * Y), size=mp.Vector3(x_t - x_r), weight=-1)),
            dense=sim.add_flux(*FRD, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, Y))),
        )
        mode = sim.add_mode_monitor(*FR, mp.ModeRegion(center=mp.Vector3(x_r), size=mp.Vector3(0, Y)))
        return sim, fl, mode


    pt_t = mp.Vector3(x_t)
    res = {}
    for label, Nh in (("wg", 0), ("cav", N)):
        sim, fl, mode = make(Nh)
        if label == "cav":
            sim.load_minus_flux_data(fl["refl"], refl_data)
        dft = sim.add_dft_fields([mp.Hz], F3, center=mp.Vector3(), size=mp.Vector3(2 * X, Y))
        tr = {"t": [], "v": []}
        steps = [mp.at_every(0.25, lambda s: (tr["t"].append(s.meep_time()), tr["v"].append(float(np.real(s.get_field_point(mp.Ey, mp.Vector3(x_r)))))))]
        t1 = time.time()
        sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50, mp.Ey, pt_t, a.decay))
        out = {k: np.array(mp.get_fluxes(v)) for k, v in fl.items()}
        out["freqs"] = np.array(mp.get_flux_freqs(fl["up"]))
        out["dfreqs"] = np.array(mp.get_flux_freqs(fl["dense"]))
        cf = sim.get_eigenmode_coefficients(mode, [1], eig_parity=mp.EVEN_Z)
        out["a_fwd"], out["a_bwd"] = cf.alpha[0, :, 0], cf.alpha[0, :, 1]
        out["Hz"] = np.array([sim.get_dft_array(dft, mp.Hz, i) for i in range(3)])
        out["eps"] = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(2 * X, Y))
        out["trace_t"], out["trace_v"] = np.array(tr["t"]), np.array(tr["v"])
        out["t_end"], out["wall"] = sim.meep_time(), time.time() - t1
        if label == "wg":
            refl_data = sim.get_flux_data(fl["refl"])
        res[label] = out
        if mp.am_master():
            print(f"TRANS {label} t_end={out['t_end']:.1f} wall={out['wall']:.0f}s", flush=True)
        sim.reset_meep()
    if mp.am_master():
        flat = {f"{lab}_{k}": v for lab, o in res.items() for k, v in o.items()}
        np.savez_compressed(os.path.join(a.out, f"trans_{a.tag or 'r%g' % a.resolution}.npz"), N=N, sx=sx, sy=a.sy, X=X, Y=Y, x_t=x_t, x_r=x_r, x_src=x_src, F3=F3, **flat)
        inc = res["wg"]["tran"]
        R = -res["cav"]["refl"] / inc
        T = res["cav"]["tran"] / inc
        S = (res["cav"]["side_p"] + res["cav"]["side_m"]) / inc
        tot = R + T + S
        i0 = int(np.argmin(np.abs(res["wg"]["freqs"] - 0.2345)))
        mf = np.abs(res["wg"]["a_fwd"]) ** 2 / res["wg"]["refl"]
        summ = dict(tag=a.tag, res=a.resolution, N=N, decay=a.decay, t_end_cav=res["cav"]["t_end"], sum_minmax=[float(tot.min()), float(tot.max())],
                    sum_at=float(tot[i0]), T_at=float(T[i0]), R_at=float(R[i0]), S_at=float(S[i0]),
                    mode_frac_minmax=[float(mf.min()), float(mf.max())], wall=time.time() - T0)
        dump(f"trans_{a.tag or 'r%g' % a.resolution}.json", summ)
        print("RESULT " + json.dumps(summ, default=float), flush=True)


if __name__ == "__main__":
    main()
