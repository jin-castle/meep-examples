"""blogfig.py — figure helpers for the Meep example blog series.

Two things every post needs:

1. ``annotated_layout``: ``sim.plot2D()`` plus labels that tie each drawn object
   (core, source, monitors, PML) to the code step number in section 4 of the post.
2. ``field_figure``: the standard two-panel steady-state field plot
   (Re(E) wavefront on top, |E| envelope below) with the core outline drawn.

Usage::

    from blogfig import annotated_layout, field_figure, Label

    annotated_layout(sim, "01_layout.png", title="...", dpml=dpml,
                     labels=[Label("source", (-5, 1.5), (-5, 2.6), step=3, color="red"), ...])

    field_figure(ey, extent, "02_field.png", core_halfwidth=w_core / 2, wl=1.55)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np


@dataclass
class Label:
    """One annotation: an arrow from ``text_xy`` to ``point_xy`` with a step badge."""
    text: str
    point_xy: tuple[float, float]       # where the arrow points (in cell coordinates)
    text_xy: tuple[float, float]        # where the text sits
    step: int | None = None             # section-4 step number -> drawn as a circled badge
    color: str = "black"


def scale_axes(ax, scale: float, unit: str, step: float) -> None:
    """Relabel both axes of a plot drawn in Meep units as physical units.

    ``scale`` = physical length per Meep unit (e.g. 0.2325 um per a), ``step`` = tick spacing
    in physical units. Tick positions stay in Meep units; only the labels change.
    """
    for axis, lim in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
        lo, hi = lim[0] * scale, lim[1] * scale
        ticks_phys = np.arange(np.ceil(lo / step) * step, hi + 1e-9, step)
        axis.set_ticks(ticks_phys / scale)
        axis.set_ticklabels([f"{t:g}" for t in ticks_phys])
    ax.set_xlabel(f"x [{unit}]")
    ax.set_ylabel(f"y [{unit}]")


def _badge(ax, xy, step, color):
    ax.text(xy[0], xy[1], str(step), fontsize=8, fontweight="bold", color="white",
            ha="center", va="center",
            bbox=dict(boxstyle="circle,pad=0.25", fc=color, ec=color, lw=0.8), zorder=6)


def annotated_layout(sim, out_png: str, *, title: str, dpml: float,
                     labels: Sequence[Label], figsize=(9, 4.4), dpi=150,
                     unit: str = "um", pml_xy: tuple[float, float] | None = None,
                     params_text: str | None = None, params_xy: tuple[float, float] | None = None,
                     decay_point: tuple[float, float] | None = None,
                     decay_text_xy: tuple[float, float] | None = None,
                     axis_scale: float | None = None, axis_step: float = 0.5) -> None:
    """Draw ``sim.plot2D()`` and overlay step-numbered labels.

    Badges follow the 7 code steps of the post: 1 parameters (``params_text`` box),
    2 geometry / 3 source / 5 monitors (``labels``), 4 PML (automatic, from ``dpml``),
    6 the field-decay watch point of the stop condition (``decay_point``).
    Step 7 (post-processing) draws nothing.
    """
    fig, ax = plt.subplots(figsize=figsize)
    sim.plot2D(ax=ax)
    ax.set_title(title, fontsize=10)
    sx, sy = sim.cell_size.x, sim.cell_size.y

    # step 1: parameter box (top-left inside the PML band by default)
    if params_text:
        pxy = params_xy or (-sx / 2 + dpml + 0.3, sy / 2 - dpml - 0.3)
        _badge(ax, pxy, 1, "dimgray")
        ax.text(pxy[0] + 0.35, pxy[1], params_text, fontsize=8, color="dimgray",
                ha="left", va="top", family="monospace", zorder=5,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="dimgray", lw=0.6, alpha=0.9))

    # step 6: field-decay watch point of stop_when_fields_decayed
    if decay_point is not None:
        ax.plot(decay_point[0], decay_point[1], marker="x", ms=8, mew=1.6, color="purple", zorder=6)
        txy = decay_text_xy or (decay_point[0], decay_point[1] - 0.8)
        _badge(ax, txy, 6, "purple")
        ax.text(txy[0], txy[1], "decay watch point", color="purple", fontsize=9,
                ha="left", va="center", zorder=5,
                transform=transforms.offset_copy(ax.transData, fig=fig, x=9, y=0, units="points"))

    # text starts a few points to the right of the badge, badge sits at text_xy
    shift = transforms.offset_copy(ax.transData, fig=fig, x=9, y=0, units="points")

    for lb in labels:
        anchor = lb.text_xy
        if lb.step is not None:
            _badge(ax, anchor, lb.step, lb.color)
            ax.text(anchor[0], anchor[1], lb.text, color=lb.color, fontsize=9,
                    ha="left", va="center", transform=shift, zorder=5,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
        else:
            ax.text(anchor[0], anchor[1], lb.text, color=lb.color, fontsize=9,
                    ha="center", va="center", zorder=5)
        ax.annotate("", xy=lb.point_xy, xytext=anchor, zorder=4,
                    arrowprops=dict(arrowstyle="->", color=lb.color, lw=1.0,
                                    shrinkA=8, shrinkB=2))

    # PML label: middle of the bottom PML band (step 4)
    if pml_xy is None:
        pml_xy = (0.0, -sy / 2 + dpml / 2)
    _badge(ax, pml_xy, 4, "green")
    ax.text(pml_xy[0], pml_xy[1], "PML (boundary_layers)", color="green", fontsize=9,
            ha="left", va="center", fontweight="bold", transform=shift, zorder=5,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))

    if axis_scale is not None:
        # drawn in Meep units, labelled in physical units (e.g. a -> um)
        scale_axes(ax, axis_scale, unit, axis_step)
    else:
        ax.set_xlabel(f"x [{unit}]")
        ax.set_ylabel(f"y [{unit}]")
    fig.tight_layout()
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def field_figure(field: np.ndarray, extent, out_png: str, *, core_halfwidth: float | None,
                 wl: float, component: str = "Ey", layout: str = "column",
                 aspect: str = "auto", unit: str = "um", wl_unit: str | None = None,
                 figsize=None, dpi=150, eps: np.ndarray | None = None) -> None:
    """Two panels: Re(field) wavefront and |field| envelope, with the structure outlined.

    ``field`` is the complex DFT array as returned by ``sim.get_dft_array`` (x along axis 0).
    ``eps`` is the permittivity over the same region (``sim.get_array(..., component=mp.Dielectric)``);
    its mid-level contour is drawn as a thin line so the reader sees where the structure is.
    ``core_halfwidth`` additionally draws a straight horizontal core outline (dashed); ``None`` to skip.
    ``layout="column"`` stacks the panels (long thin cells); ``"row"`` puts them side by side.
    """
    if layout == "row":
        fig, axs = plt.subplots(1, 2, figsize=figsize or (12, 5.2), sharey=True)
    else:
        fig, axs = plt.subplots(2, 1, figsize=figsize or (9, 6), sharex=True)
    panels = ((axs[0], np.real(field).T, f"Re({component}) @ {wl} {wl_unit or unit}  (wavefront)", "RdBu", "k"),
              (axs[1], np.abs(field).T, f"|{component}|  (envelope)", "inferno", "w"))
    for ax, data, ttl, cmap, line_color in panels:
        im = ax.imshow(data, extent=extent, origin="lower", aspect=aspect, cmap=cmap)
        if eps is not None and eps.max() > eps.min():
            xs = np.linspace(extent[0], extent[1], eps.shape[0])
            ys = np.linspace(extent[2], extent[3], eps.shape[1])
            ax.contour(xs, ys, eps.T, levels=[0.5 * (eps.min() + eps.max())],
                       colors=line_color, linewidths=0.7, alpha=0.9)
        if core_halfwidth is not None:
            for yb in (-core_halfwidth, core_halfwidth):
                ax.axhline(yb, color=line_color, lw=0.6, ls="--")
        ax.set_title(ttl)
        fig.colorbar(im, ax=ax, shrink=0.85 if layout == "row" else 1.0)
    if layout == "row":
        axs[0].set_ylabel(f"y [{unit}]")
        for ax in axs:
            ax.set_xlabel(f"x [{unit}]")
    else:
        for ax in axs:
            ax.set_ylabel(f"y [{unit}]")
        axs[1].set_xlabel(f"x [{unit}]")
    fig.tight_layout()
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def spectrum_figure(wavelengths, curves: dict, out_png: str, *, unit: str = "nm",
                    mark: float | None = None, mark_label: str | None = None,
                    ylabel: str = "fraction of input power", figsize=(7, 4), dpi=150) -> None:
    """Plot several spectra (name -> array) against wavelength on one axis.

    Pass wavelengths already converted to physical units (nm by default) so the axis reads
    like a datasheet (e.g. 1550 nm). ``mark`` draws a dashed line at the center wavelength.
    """
    fig, ax = plt.subplots(figsize=figsize)
    for name, y in curves.items():
        ax.plot(wavelengths, y, marker="o", ms=3, label=name)
    if mark is not None:
        ax.axvline(mark, color="gray", ls="--", lw=0.8)
        ax.text(mark, 1.06, mark_label or f"{mark:g} {unit}", ha="center", va="center",
                fontsize=8, color="gray",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.set_xlabel(f"wavelength [{unit}]")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1.12)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def line_figure(x, curves: dict, out_png: str, *, xlabel: str,
                ylabel: str = "fraction of input power", mark: float | None = None,
                mark_label: str | None = None, ylim=(0, 1.12), logy: bool = False,
                hline: float | None = None, hline_label: str | None = None, figsize=(7, 4), dpi=150) -> None:
    """Several curves (name -> y) against one x axis, optional vertical marker."""
    fig, ax = plt.subplots(figsize=figsize)
    for name, y in curves.items():
        ax.plot(x, y, marker="o", ms=3.5, label=name)
    if mark is not None:
        ax.axvline(mark, color="gray", ls="--", lw=0.8)
        if mark_label:
            ax.text(mark, ylim[1] - 0.05, mark_label, ha="center", va="center", fontsize=8, color="gray",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    if hline is not None:
        ax.axhline(hline, color="tab:red", ls="--", lw=0.9, label=hline_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if logy:
        ax.set_yscale("log")
        ax.grid(alpha=0.3, which="both")
    else:
        ax.set_ylim(*ylim)
        ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def source_figure(fcen: float, fwidth: float, out_png: str, *, mon_fcen: float | None = None,
                  mon_df: float | None = None, cutoff: float = 5.0, wl_scale: float = 1.0,
                  wl_unit: str = "nm", time_unit: str = "a/c", figsize=(11, 3.8), dpi=150) -> dict:
    """Time waveform and power spectrum of ``mp.GaussianSource(fcen, fwidth=fwidth)``.

    Meep's Gaussian source has ``width = 1/fwidth`` and its peak at ``t0 = cutoff * width``
    (cutoff defaults to 5). The spectrum is computed numerically from the sampled waveform.
    ``mon_fcen``/``mon_df`` mark the monitor band (edges at mon_fcen +- mon_df/2) and the
    relative power there is annotated and returned, so the post can say how much (little)
    source power the band edges receive. ``wl_scale`` converts 1/f to the wavelength unit.
    """
    width = 1.0 / fwidth
    t0 = cutoff * width
    dt = 1.0 / (fcen * 60)
    t = np.arange(0.0, 2 * t0, dt)
    env = np.exp(-((t - t0) ** 2) / (2 * width ** 2))
    s = env * np.cos(2 * np.pi * fcen * t)

    npad = 16 * len(t)
    spec = np.abs(np.fft.rfft(s, n=npad)) ** 2
    f = np.fft.rfftfreq(npad, dt)
    spec /= spec.max()
    # plot window: around the monitor band if given, else around the source band; never down to f = 0
    if mon_fcen is not None and mon_df is not None:
        f_lo, f_hi = mon_fcen - 0.8 * mon_df, mon_fcen + 0.8 * mon_df
    else:
        f_lo, f_hi = fcen - 1.2 * fwidth, fcen + 1.2 * fwidth
    f_lo = max(f_lo, 0.4 * fcen)
    sel = (f >= f_lo) & (f <= f_hi)

    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=figsize)
    ax_t.plot(t, s, lw=0.8, color="tab:blue")
    ax_t.plot(t, env, lw=1.0, color="tab:red", ls="--", label="envelope")
    ax_t.plot(t, -env, lw=1.0, color="tab:red", ls="--")
    ax_t.axvline(t0, color="gray", ls=":", lw=1.0)
    ax_t.text(t0, 1.08, f"t0 = {cutoff:g}/fwidth = {t0:.1f}", ha="center", fontsize=8, color="gray")
    ax_t.set_xlabel(f"time [{time_unit}]")
    ax_t.set_ylabel("source amplitude")
    ax_t.set_ylim(-1.2, 1.25)
    ax_t.set_title(f"GaussianSource(fcen={fcen:g}, fwidth={fwidth:g}): width = 1/fwidth = {width:.2f}", fontsize=9)
    ax_t.legend(loc="lower right", fontsize=8)

    wl = wl_scale / f[sel]
    ax_f.semilogy(wl, spec[sel], color="tab:blue", lw=1.2)
    ax_f.set_xlabel(f"wavelength [{wl_unit}]")
    ax_f.set_ylabel("relative source power")
    ax_f.set_ylim(1e-6, 2)
    ax_f.grid(alpha=0.3, which="both")
    info = {"t0": t0, "width": width}
    if mon_fcen is not None and mon_df is not None:
        edges = (mon_fcen - mon_df / 2, mon_fcen + mon_df / 2)
        pes = []
        for fe in edges:
            pe = float(np.interp(fe, f, spec))
            pes.append(pe)
            ax_f.axvline(wl_scale / fe, color="tab:red", ls="--", lw=0.9)
            ax_f.plot([wl_scale / fe], [pe], "o", color="tab:red", ms=4)
            info[f"rel_power_at_f={fe:.4g}"] = pe
        ax_f.axvline(wl_scale / mon_fcen, color="gray", ls=":", lw=1.0)
        ax_f.set_title(f"power spectrum; red = monitor band edges "
                       f"({wl_scale/edges[1]:.0f}-{wl_scale/edges[0]:.0f} {wl_unit})\n"
                       f"relative source power at the edges: {pes[1]:.1e} / {pes[0]:.1e}", fontsize=8.5)
        info["band_edges_rel_power"] = pes
    fig.tight_layout()
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)
    return info


def panel_grid(fields, titles, extent, out_png: str, *, ncols: int = 3, unit: str = "um",
               component: str = "Ez", marks=None, circles=None, suptitle: str | None = None,
               lines=None, rects=None, figsize=None, dpi=150) -> None:
    """Grid of Re(field) snapshots sharing ONE color scale (so amplitude decay stays visible).

    ``marks``: list of (x, y) points drawn as black dots on every panel (e.g. the source).
    ``circles``: dict {panel_index: (x, y, r, label)} dashed circles, e.g. the predicted wavefront.
    ``lines``: dict {panel_index: ((x0, y0), (x1, y1))} thick black line, e.g. a line source.
    """
    n = len(fields)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize or (4.3 * ncols, 3.4 * nrows), squeeze=False)
    lim = max(float(np.max(np.abs(np.real(f)))) for f in fields)
    for i, ax in enumerate(axes.ravel()):
        if i >= n:
            ax.axis("off")
            continue
        im = ax.imshow(np.real(fields[i]).T, origin="lower", extent=extent, cmap="RdBu",
                       vmin=-lim, vmax=lim, aspect="equal")
        for (x, y) in (marks or []):
            ax.plot(x, y, "o", color="k", ms=4, zorder=5)
        for (rx, ry, rw, rh) in (rects or []):          # e.g. the edge band used for a metric
            ax.add_patch(plt.Rectangle((rx, ry), rw, rh, fill=False, ls="--", lw=1.0, color="k"))
        if lines and i in lines:
            (x0, y0), (x1, y1) = lines[i]
            ax.plot([x0, x1], [y0, y1], color="k", lw=2.5, zorder=5)
        if circles and i in circles:
            x, y, r, label = circles[i]
            ax.add_patch(plt.Circle((x, y), r, fill=False, ls="--", lw=1.1, color="k"))
            ax.text(x, y + r, label, ha="center", va="bottom", fontsize=8)
        ax.set_title(titles[i], fontsize=9)
        ax.set_xlabel(f"x [{unit}]")
        ax.set_ylabel(f"y [{unit}]")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.8, label=f"Re({component})")
    if suptitle:
        fig.suptitle(suptitle, fontsize=11)
    fig.savefig(out_png, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def bar_figure(categories, series: dict, out_png: str, *, ylabel: str, reference: float | None = None,
               reference_label: str | None = None, logy: bool = False, fmt: str = "{:.3f}",
               figsize=(6.5, 3.8), dpi=150) -> None:
    """Grouped bars: one group per category, one bar per series entry."""
    fig, ax = plt.subplots(figsize=figsize)
    k = len(series)
    width = 0.8 / k
    xs = np.arange(len(categories))
    for j, (name, vals) in enumerate(series.items()):
        bars = ax.bar(xs + (j - (k - 1) / 2) * width, vals, width, label=name)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v * 1.15 if logy else v + 0.01, fmt.format(v),
                    ha="center", va="bottom", fontsize=7.5)
    if reference is not None:
        ax.axhline(reference, color="gray", ls="--", lw=0.9, label=reference_label)
    ax.set_xticks(xs)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(min(min(v) for v in series.values()) / 3, max(max(v) for v in series.values()) * 4)
        ax.grid(True, axis="y", alpha=0.3, which="both")
    else:
        ax.set_ylim(0, max(max(v) for v in series.values()) * 1.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def record_frames(sim, vol, component, t_start: float, t_end: float, n_frames: int):
    """Step a fresh Simulation and collect ``n_frames`` field snapshots between t_start and t_end.

    Meep's ``sim.run(until=...)`` counts from the current time, so the pulse timing has to be
    derived from the source: start at about ``t0 - 2*width`` (before the pulse) and end when the
    pulse has reached the farthest monitor (``t0 + distance * n``).
    """
    sim.run(until=t_start)
    dt = (t_end - t_start) / n_frames
    frames, times = [], []
    for i in range(n_frames):
        sim.run(until=dt)
        frames.append(np.real(sim.get_array(vol=vol, component=component)))
        times.append(t_start + (i + 1) * dt)
    return frames, times


def animate_fields(frames, times, extent, out_gif: str, *, eps: np.ndarray | None = None,
                   lines=None, points=None, unit: str = "um", component: str = "Ez",
                   time_unit: str = "um/c", fps: int = 10, figsize=(7.5, 4.0), dpi=80,
                   aspect: str = "equal", title: str | None = None, legend_loc: str = "upper right") -> None:
    """Write a GIF of Re(field) snapshots with the structure outline and source/monitor markers.

    ``lines``: [((x0, y0), (x1, y1), color, label), ...] e.g. source and monitor planes.
    ``points``: [(x, y, color, label), ...]. One color scale for all frames (PillowWriter, no ffmpeg).
    """
    from matplotlib import animation
    lim = max(float(np.max(np.abs(f))) for f in frames)
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(frames[0].T, origin="lower", extent=extent, cmap="RdBu", vmin=-lim, vmax=lim, aspect=aspect)
    if eps is not None and eps.max() > eps.min():
        xs = np.linspace(extent[0], extent[1], eps.shape[0])
        ys = np.linspace(extent[2], extent[3], eps.shape[1])
        ax.contour(xs, ys, eps.T, levels=[0.5 * (eps.min() + eps.max())], colors="k", linewidths=0.7)
    for (p0, p1, color, label) in (lines or []):
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=2.0, label=label)
    for (x, y, color, label) in (points or []):
        ax.plot(x, y, "o", color=color, ms=5, label=label)
    if lines or points:
        ax.legend(loc=legend_loc, fontsize=7, framealpha=0.8)
    ax.set_xlabel(f"x [{unit}]")
    ax.set_ylabel(f"y [{unit}]")
    ttl = ax.set_title("", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.85, label=f"Re({component})")
    fig.tight_layout()

    def update(i):
        im.set_data(frames[i].T)
        ttl.set_text((title + "   " if title else "") + f"t = {times[i]:.1f} {time_unit}")
        return im, ttl

    anim = animation.FuncAnimation(fig, update, frames=len(frames), blit=False)
    anim.save(out_gif, writer=animation.PillowWriter(fps=fps), dpi=dpi)
    plt.close(fig)


def animate_compare(frame_sets, titles, times, extent, out_gif: str, *, points=None, unit: str = "um",
                    component: str = "Ez", time_unit: str = "um/c", fps: int = 10, figsize=(10, 4.2),
                    dpi=80, suptitle: str | None = None) -> None:
    """Side-by-side GIF of several runs that share the same time axis and ONE color scale.

    ``frame_sets``: list of frame lists (one per panel), ``titles``: panel titles,
    ``points``: [(x, y, color, label)] drawn on every panel (e.g. the source).
    """
    from matplotlib import animation
    n = len(frame_sets)
    lim = max(float(np.max(np.abs(f))) for fs in frame_sets for f in fs)
    fig, axes = plt.subplots(1, n, figsize=figsize, squeeze=False)
    ims = []
    for ax, fs, ttl in zip(axes[0], frame_sets, titles):
        ims.append(ax.imshow(fs[0].T, origin="lower", extent=extent, cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"))
        for (x, y, color, label) in (points or []):
            ax.plot(x, y, "o", color=color, ms=5)
        ax.set_title(ttl, fontsize=9)
        ax.set_xlabel(f"x [{unit}]")
    axes[0][0].set_ylabel(f"y [{unit}]")
    fig.colorbar(ims[-1], ax=list(axes[0]), shrink=0.85, label=f"Re({component})")
    sup = fig.suptitle("", fontsize=10)

    def update(i):
        for im, fs in zip(ims, frame_sets):
            im.set_data(fs[i].T)
        sup.set_text((suptitle + "   " if suptitle else "") + f"t = {times[i]:.1f} {time_unit}")
        return ims

    anim = animation.FuncAnimation(fig, update, frames=len(times), blit=False)
    anim.save(out_gif, writer=animation.PillowWriter(fps=fps), dpi=dpi)
    plt.close(fig)
