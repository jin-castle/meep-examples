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
                    ha="left", va="center", transform=shift, zorder=5)
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
