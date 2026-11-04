"""courant_gif.py — animations of a Courant-unstable run next to a stable one (concept page: Courant condition).

    OMP_NUM_THREADS=1 python courant_gif.py

A. 2D vacuum, S = 0.70 (below 1/sqrt(2) = 0.7071) vs S = 0.71 (above): Ez maps on one colour scale,
   a 1 x 1 um zoom of the unstable run normalised per frame (the checkerboard), and max|Ez| vs time.
B. 1D vacuum, S = 1.00 vs 1.003 (0.3 % over the limit): Ex(z) on the grid points, a 1 um zoom (sign flips every pixel), max|Ex| vs time.
C. 1D Lorentzian medium (f_n = 5.7, res 10, closed cell): S = 0.5 (just past the measured onset 5.6..5.7)
   vs S = 0.25 (rough limit res/(pi S) = 12.7, stable).
A run is stopped once max|E| > 1e6 (the pulse peak is about 1); its last frame is held afterwards.
Outputs: ../assets/terms-courant/{02_anim_2d.gif, 02_anim_2d.png, 03_anim_1d.gif, 03_anim_1d.png,
         04_anim_lorentz.gif, 04_anim_lorentz.png, anim.json}
The published GIFs were recompressed with one shared palette (PillowWriter output is 3-6 MB):
    ffmpeg -i in.gif -filter_complex "[0:v]split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle" out.gif
"""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp
import numpy as np
from matplotlib import animation

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "terms-courant")
os.makedirs(OUT, exist_ok=True)
mp.verbosity(0)

FCEN, FWIDTH = 1.0, 0.5          # same source as courant_stability.py: peak t0 = 10, off at t = 20
STOP = 1e6
C_STABLE, C_UNSTABLE = "#2166ac", "#b2182b"


class Diverged(Exception):
    pass


def record(sim, comp, dt, t_end, vol=None):
    """Run and keep (time, field array, max|field|) every dt until t_end or max|field| > STOP."""
    times, frames, peaks = [], [], []

    def grab(s):
        a = np.real(s.get_array(component=comp, vol=vol)) if vol is not None else np.real(s.get_array(component=comp))
        m = float(np.nan_to_num(np.abs(a).max(), nan=np.inf, posinf=np.inf))
        times.append(s.meep_time()); frames.append(a.copy()); peaks.append(m)
        if m > STOP:
            raise Diverged

    status = "stable"
    try:
        sim.run(mp.at_every(dt, grab), until=t_end)
    except Diverged:
        status = "diverged"
    except RuntimeError:
        status = "diverged (Meep abort)"
    return dict(times=np.array(times), frames=frames, peaks=np.array(peaks), status=status)


def held(run, i):
    """Frame index for animation step i: the last recorded frame once the run has stopped."""
    return min(i, len(run["frames"]) - 1)


def trace_panel(ax, runs, labels, colors, t_end):
    lines, dots = [], []
    for run, lab, col in zip(runs, labels, colors):
        ax.semilogy(run["times"], np.maximum(run["peaks"], 1e-12), color=col, lw=1.0, alpha=0.25)
        ln, = ax.semilogy([], [], color=col, lw=1.8, label=lab)
        dt, = ax.semilogy([], [], "o", color=col, ms=5)
        lines.append(ln); dots.append(dt)
    ax.axhline(STOP, color="gray", ls="--", lw=0.8)
    ax.text(0.3, STOP * 2.5, "stop: max|E| > 1e6", fontsize=7, color="gray")
    ax.axvline(20, color="gray", ls=":", lw=0.8)
    ax.text(20.3, 1e-10, "source off", fontsize=7, color="gray")
    ax.set_xlim(0, t_end); ax.set_ylim(1e-12, 1e9)
    ax.set_xlabel("time [a/c]  (a = 1 um)", fontsize=8); ax.set_ylabel("max |E| in the cell", fontsize=8)
    ax.tick_params(labelsize=7); ax.grid(alpha=0.3, which="major")
    ax.legend(fontsize=7, loc="upper right")
    return lines, dots


def update_trace(lines, dots, runs, i):
    for ln, dt, run in zip(lines, dots, runs):
        j = held(run, i)
        ln.set_data(run["times"][:j + 1], np.maximum(run["peaks"][:j + 1], 1e-12))
        dt.set_data([run["times"][j]], [max(run["peaks"][j], 1e-12)])


def save(anim, fig, name, png_step, update):
    anim.save(os.path.join(OUT, name + ".gif"), writer=animation.PillowWriter(fps=12), dpi=80)
    update(png_step)
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=110)
    plt.close(fig)


# ---------------------------------------------------------------- A. 2D vacuum
def run_2d(S):
    sim = mp.Simulation(cell_size=mp.Vector3(8, 8), resolution=10, Courant=S, boundary_layers=[mp.PML(1.0)],
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ez, center=mp.Vector3())])
    return record(sim, mp.Ez, 0.25, 30.0, vol=mp.Volume(center=mp.Vector3(), size=mp.Vector3(6, 6)))


def gif_2d():
    st, un = run_2d(0.70), run_2d(0.71)
    n = len(st["frames"])
    lim = float(np.percentile(np.abs(np.stack(st["frames"])), 97))
    ext = [-3, 3, -3, 3]
    z0, z1 = 20, 30                                      # zoom window: 10 x 10 pixels = 1 x 1 um at (-1..0, -1..0)
    fig = plt.figure(figsize=(10.5, 6.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1], width_ratios=[1, 1, 0.8])
    axs = [fig.add_subplot(gs[0, k]) for k in range(3)]
    axt = fig.add_subplot(gs[1, :])
    ims = []
    for ax, run, ttl, col in ((axs[0], st, "S = 0.70  (below 1/sqrt(2) = 0.7071)", C_STABLE),
                              (axs[1], un, "S = 0.71  (above the limit)", C_UNSTABLE)):
        ims.append(ax.imshow(run["frames"][0].T, origin="lower", extent=ext, cmap="RdBu", vmin=-lim, vmax=lim))
        ax.set_title(ttl, fontsize=9, color=col); ax.set_xlabel("x [um]", fontsize=8); ax.set_ylabel("y [um]", fontsize=8)
        ax.tick_params(labelsize=7)
    axs[1].add_patch(plt.Rectangle((-1, -1), 1, 1, fill=False, ec="k", lw=1.0, ls="--"))
    zim = axs[2].imshow(np.zeros((10, 10)), origin="lower", extent=[-1, 0, -1, 0], cmap="RdBu", vmin=-1, vmax=1, interpolation="nearest")
    axs[2].set_title("S = 0.71, dashed 1 x 1 um box\neach frame scaled to its own max", fontsize=8, color=C_UNSTABLE)
    axs[2].set_xlabel("x [um]  (10 pixels)", fontsize=8); axs[2].tick_params(labelsize=7)
    stop_txt = axs[1].text(0, 0, "", ha="center", va="center", fontsize=10, color="k",
                           bbox=dict(fc="white", ec=C_UNSTABLE, alpha=0.9))
    lines, dots = trace_panel(axt, [st, un], ["S = 0.70", "S = 0.71"], [C_STABLE, C_UNSTABLE], 30)
    sup = fig.suptitle("", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    def update(i):
        ims[0].set_data(st["frames"][i].T)
        j = held(un, i)
        ims[1].set_data(un["frames"][j].T)
        z = un["frames"][j][z0:z1, z0:z1]
        zim.set_data(z.T / max(np.abs(z).max(), 1e-300))
        stop_txt.set_text(f"stopped at t = {un['times'][-1]:.1f}\nmax|Ez| > 1e6" if i >= len(un["frames"]) - 1 else "")
        update_trace(lines, dots, [st, un], i)
        sup.set_text(f"2D vacuum, resolution 10, same source and colour scale (±{lim:.2g}); t = {st['times'][i]:.1f}")

    anim = animation.FuncAnimation(fig, update, frames=n, blit=False)
    save(anim, fig, "02_anim_2d", min(len(un["frames"]) + 4, n - 1), update)
    return {"S": [0.70, 0.71], "status": [st["status"], un["status"]], "t_stop_unstable": float(un["times"][-1]),
            "colour_limit": lim}


# ---------------------------------------------------------------- B / C. 1D line animations
def run_1d(S, res, L, medium=None, pml=True, t_end=30.0, dt=0.25):
    kw = dict(default_material=medium) if medium is not None else {}
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, L), resolution=res, dimensions=1, Courant=S,
                        boundary_layers=[mp.PML(1.0)] if pml else [],
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex,
                                           center=mp.Vector3(0, 0, 0.3 if medium is not None else 0))], **kw)
    inner = L - 2.0 if pml else L
    run = record(sim, mp.Ex, dt, t_end, vol=mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 0, inner)))
    run["z"] = np.linspace(-inner / 2, inner / 2, len(run["frames"][0]))
    return run


def gif_1d(st, un, labels, title, name, zoom_um, t_end):
    n = len(st["frames"])
    ylim = 1.4 * float(np.max(np.abs(np.stack(st["frames"]))))
    fig = plt.figure(figsize=(10.5, 6.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1], width_ratios=[1.25, 1])
    ax = fig.add_subplot(gs[0, :]); axz = fig.add_subplot(gs[1, 0]); axt = fig.add_subplot(gs[1, 1])
    l_st, = ax.plot([], [], "-", color=C_STABLE, lw=1.4, label=labels[0])
    l_un, = ax.plot([], [], "-", color=C_UNSTABLE, lw=1.0, label=labels[1])
    ax.set_xlim(st["z"][0], st["z"][-1]); ax.set_ylim(-ylim, ylim)
    ax.set_xlabel("z [um]", fontsize=8); ax.set_ylabel("Ex", fontsize=8)
    ax.tick_params(labelsize=7); ax.legend(fontsize=7, loc="upper right"); ax.grid(alpha=0.3)
    stop_txt = ax.text(0.5, 0.12, "", transform=ax.transAxes, ha="center", fontsize=9,
                       bbox=dict(fc="white", ec=C_UNSTABLE, alpha=0.9))
    z = un["z"]; sel = (z >= zoom_um[0]) & (z <= zoom_um[1])
    l_z, = axz.plot([], [], "o-", color=C_UNSTABLE, lw=1.0, ms=4)
    axz.set_xlim(*zoom_um); axz.set_ylim(-1.15, 1.15); axz.axhline(0, color="gray", lw=0.6)
    axz.set_title(f"{labels[1]}: z = {zoom_um[0]:g}..{zoom_um[1]:g} um, scaled to its own max", fontsize=8, color=C_UNSTABLE)
    axz.set_xlabel("z [um]  (dots = grid points)", fontsize=8); axz.tick_params(labelsize=7)
    lines, dots = trace_panel(axt, [st, un], labels, [C_STABLE, C_UNSTABLE], t_end)
    sup = fig.suptitle("", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    def update(i):
        l_st.set_data(st["z"], st["frames"][i])
        j = held(un, i)
        l_un.set_data(z, np.clip(un["frames"][j], -1e3 * ylim, 1e3 * ylim))
        w = un["frames"][j][sel]
        l_z.set_data(z[sel], w / max(np.abs(w).max(), 1e-300))
        stop_txt.set_text(f"{labels[1]} stopped at t = {un['times'][-1]:.1f}: max|Ex| > 1e6" if i >= len(un["frames"]) - 1 else "")
        update_trace(lines, dots, [st, un], i)
        sup.set_text(f"{title}; t = {st['times'][i]:.1f}")

    anim = animation.FuncAnimation(fig, update, frames=n, blit=False)
    save(anim, fig, name, min(len(un["frames"]) + 4, n - 1), update)
    return {"labels": labels, "status": [st["status"], un["status"]], "t_stop_unstable": float(un["times"][-1])}


if __name__ == "__main__":
    info = {"meep_version": mp.__version__, "stop_threshold": STOP}
    info["2d"] = gif_2d()
    info["1d"] = gif_1d(run_1d(1.00, 20, 16.0, dt=0.4), run_1d(1.003, 20, 16.0, dt=0.4), ["S = 1.00", "S = 1.003"],
                        "1D vacuum, resolution 20 (limit S = 1)", "03_anim_1d", (-3.0, -2.0), 30.0)
    lor = mp.Medium(epsilon=2.25, E_susceptibilities=[mp.LorentzianSusceptibility(frequency=5.7, gamma=0.05, sigma=0.5)])
    info["lorentz"] = gif_1d(run_1d(0.25, 10, 10.0, lor, pml=False, t_end=40.0, dt=0.4), run_1d(0.5, 10, 10.0, lor, pml=False, t_end=40.0, dt=0.4),
                             ["S = 0.25", "S = 0.5"],
                             "1D Lorentz medium f_n = 5.7, resolution 10, closed cell (rough limit res/(pi S): 12.7 and 6.4)",
                             "04_anim_lorentz", (-2.0, -1.0), 40.0)
    for k in ("2d", "1d", "lorentz"):
        print(k, info[k])
    with open(os.path.join(OUT, "anim.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=1)
