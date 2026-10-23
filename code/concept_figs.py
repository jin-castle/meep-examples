"""Concept illustrations for posts 10-13, in the format of the post 01-09 concept figures:
a headline, three numbered panels, a one-line summary bar, and a spec footnote. Qualitative, not to scale.

Run (no Meep needed):  python concept_figs.py      -> ../assets/NN/00_concept.png
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle, Polygon

plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, BLUE, PALE, GUIDE, AMBER, PURPLE, GRAY = "#0d2a4a", "#2f6fb5", "#e3efff", "#5b9bd5", "#f5a623", "#7b4fd6", "#8a97a6"


RY = (0.32 * 15.36) / (0.70 * 10.24)   # y data units per x data unit, so circles stay round in the panels


def circ(ax, xy, r, **kw):
    ax.add_patch(Ellipse(xy, 2 * r, 2 * r * RY, **kw))


def frame(title, panels, summary, footnote):
    fig = plt.figure(figsize=(15.36, 10.24), dpi=100)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.955, title, ha="center", va="center", fontsize=34, fontweight="bold", color=NAVY)
    axes = []
    for k, head in enumerate(panels):
        x0 = 0.01 + k * 0.33
        ax = fig.add_axes([x0, 0.19, 0.32, 0.70])
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.05, 0.05), 9.9, 9.9, boxstyle="round,pad=0,rounding_size=0.35", fc="white", ec="#c9dcf2", lw=1.5))
        ax.add_patch(FancyBboxPatch((0.05, 8.95), 9.9, 1.0, boxstyle="round,pad=0,rounding_size=0.35", fc=PALE, ec="none"))
        ax.add_patch(Circle((0.85, 9.45), 0.36, fc=NAVY, ec="none"))
        ax.text(0.85, 9.43, str(k + 1), ha="center", va="center", color="white", fontsize=17, fontweight="bold")
        ax.text(1.45, 9.45, head, ha="left", va="center", fontsize=19, fontweight="bold", color=NAVY)
        axes.append(ax)
    bar = fig.add_axes([0.01, 0.095, 0.98, 0.075]); bar.axis("off"); bar.set_xlim(0, 1); bar.set_ylim(0, 1)
    bar.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.25", fc=PALE, ec="none", transform=bar.transAxes, mutation_aspect=0.08))
    bar.text(0.5, 0.5, summary, ha="center", va="center", fontsize=24, fontweight="bold", color=NAVY)
    fig.text(0.5, 0.055, footnote[0], ha="center", va="center", fontsize=15, color="#333")
    fig.text(0.5, 0.02, footnote[1], ha="center", va="center", fontsize=15, color="#333")
    fig.text(0.985, 0.02, "개념도 · 비례 아님 · 시뮬레이션 결과 아님", ha="right", va="center", fontsize=11, color=GRAY)
    return fig, axes


def label(ax, xy, txy, text, color=NAVY, size=14, ha="left"):
    ax.annotate(text, xy=xy, xytext=txy, fontsize=size, color=color, ha=ha, va="center", fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=color, lw=1.2, shrinkA=2, shrinkB=2))
    ax.plot(*xy, "o", color=color, ms=4)


def arrow(ax, p0, p1, color=AMBER, lw=4, style="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=22, color=color, lw=lw))


def dipole(ax, x, y, ang=0, L=0.55, color=AMBER):
    dx, dy = L * np.cos(np.radians(ang)), L * np.sin(np.radians(ang))
    ax.add_patch(FancyArrowPatch((x - dx, y - dy), (x + dx, y + dy), arrowstyle="<|-|>", mutation_scale=16, color=color, lw=3))


def lobes(ax, x, y, fn, scale, color=BLUE, alpha=0.25, th0=0, th1=2 * np.pi):
    th = np.linspace(th0, th1, 400)
    r = scale * fn(th)
    ax.fill(x + r * np.cos(th), y + RY * r * np.sin(th), color=color, alpha=alpha, lw=0)
    ax.plot(x + r * np.cos(th), y + RY * r * np.sin(th), color=color, lw=1.6)


def save(fig, nn):
    out = os.path.join(HERE, "..", "assets", nn, "00_concept.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=100); plt.close(fig); print("wrote", out)


# ------------------------------------------------------------------ post 10
fig, (a, b, c) = frame("거울 하나가 점광원이 빛나는 방향을 바꾼다",
                       ["진공의 쌍극자", "1D run 하나 = 방향 하나", "거울 = 반대 부호 image"],
                       "3D 패턴은 1D run 묶음으로, 무한한 거울은 image와 대칭으로 계산한다.",
                       ("x 쌍극자 패턴 1 − sin²θ cos²φ  ·  1D run의 z flux × cosθ = 그 방향의 power",
                        "PEC 위 높이 h = 1.25 µm, n = 1.2, λ = 650 nm  ·  array factor sin²(kh cosθ)"))
lobes(a, 5, 4.6, lambda t: np.sin(t) ** 2, 3.6)                           # x-dipole in the x-z plane: zero along its axis
dipole(a, 5, 4.6, 0)
a.text(6.4, 4.0, "Ex 쌍극자", ha="center", fontsize=14, color=AMBER, fontweight="bold")
a.plot([1.3, 8.7], [4.6, 4.6], color=GRAY, ls=":", lw=1.2)
label(a, (8.6, 4.6), (7.0, 2.0), "축 방향: 빛 없음")
label(a, (5, 4.6 + 3.6 * RY), (5.6, 8.2), "축에 수직: 가장 밝다")
a.text(5, 0.7, "3D 패턴 = 방향마다 다른 세기", ha="center", fontsize=14, color=NAVY)
b.add_patch(Rectangle((4.4, 1.0), 1.2, 7.4, fc="#f4f7fb", ec=GRAY, lw=1.5))
b.add_patch(Rectangle((4.4, 1.0), 1.2, 0.8, fc="#cfe8cf", ec="none")); b.add_patch(Rectangle((4.4, 7.6), 1.2, 0.8, fc="#cfe8cf", ec="none"))
dipole(b, 5.0, 2.4, 0, 0.35)
b.add_patch(Rectangle((4.7, 6.75), 0.6, 0.35, fc=BLUE, ec="none"))
arrow(b, (5.0, 2.6), (7.6, 6.6), color=PURPLE, lw=3)
b.text(6.0, 7.7, "k = f (sinθ cosφ,\n   sinθ sinφ, cosθ)", fontsize=12, color=PURPLE, fontweight="bold")
label(b, (4.4, 4.6), (0.6, 5.6), "z축만 계산", color=NAVY)
label(b, (4.7, 6.9), (1.4, 7.6), "z flux", color=BLUE)
b.text(5.0, 0.4, "k_point만 바꿔 240번", ha="center", fontsize=14, color=NAVY)
c.add_patch(Rectangle((0.8, 3.6), 8.4, 0.35, fc=GRAY, ec="none"))
c.text(8.9, 3.25, "PEC 거울", ha="right", fontsize=13, color=NAVY, fontweight="bold")
th = np.linspace(0, np.pi, 600)
r = 2.6 * np.sin(14.5 * np.cos(th - np.pi / 2)) ** 2
r = 3.6 * np.sin(14.5 * np.cos(th - np.pi / 2)) ** 2
c.fill(5 + r * np.cos(th), 3.95 + RY * r * np.sin(th), color=BLUE, alpha=0.22, lw=0); c.plot(5 + r * np.cos(th), 3.95 + RY * r * np.sin(th), color=BLUE, lw=1.4)
c.plot(5, 5.2, "o", color=AMBER, ms=12); c.plot(5, 2.4, "o", mfc="white", mec=AMBER, mew=2.5, ms=12)
c.plot([5, 5], [2.4, 5.2], color=AMBER, ls="--", lw=1.2)
label(c, (5.15, 5.2), (6.6, 6.6), "쌍극자 (+1)", color=AMBER)
label(c, (5.15, 2.4), (6.6, 1.6), "image (−1)", color=AMBER)
c.text(1.0, 8.3, "lobe 5개", fontsize=14, color=BLUE, fontweight="bold")
save(fig, "10")

# ------------------------------------------------------------------ post 11
fig, (a, b, c) = frame("두 거울 사이에서는 내는 빛의 양이 바뀐다",
                       ["bulk: 비교 기준", "두 거울 사이", "Purcell 인자 = 비율"],
                       "같은 source로 두 번 돌려, 거울이 있을 때의 LDOS를 없을 때로 나눈다.",
                       ("in-plane 쌍극자, 유전체 n = 2.4, 손실 없는 금속 거울  ·  t = nL/λ",
                        "F = LDOS(cavity) / LDOS(bulk)  ·  반파장마다 모드가 하나씩 열린다"))
for rr in (1.0, 1.8, 2.6, 3.4):
    circ(a, (5, 4.9), rr, fill=False, ec=BLUE, lw=1.6, alpha=0.9 - 0.18 * rr)
dipole(a, 5, 4.9, 0)
a.text(5, 1.0, "dft_ldos = 1 (기준)", ha="center", fontsize=15, color=NAVY, fontweight="bold")
label(a, (5 + 3.4 * 0.71, 4.9 + 3.4 * 0.71 * RY), (4.0, 8.3), "사방 PML: 거울 없음")
for yy in (2.0, 7.6):
    b.add_patch(Rectangle((0.6, yy), 8.8, 0.35, fc=GRAY, ec="none"))
b.add_patch(Rectangle((0.6, 2.35), 8.8, 5.25, fc="#eef4fb", ec="none"))
xs = np.linspace(0.8, 9.2, 300)
for n_, col in ((1, BLUE), (2, PURPLE)):
    b.plot(xs, 4.97 + 2.3 * np.cos(np.pi * n_ * (np.linspace(0, 1, 300)) + (0 if n_ == 1 else 0)) * 0, color="none")
zz = np.linspace(2.35, 7.6, 200)
b.plot(5.0 + 1.6 * np.sin(np.pi * (zz - 2.35) / 5.25), zz, color=BLUE, lw=2.5)
b.plot(5.0 + 1.2 * np.sin(2 * np.pi * (zz - 2.35) / 5.25) + 2.6, zz, color=PURPLE, lw=2.0, alpha=0.8)
dipole(b, 5.0, 4.97, 0, 0.45)
b.annotate("", xy=(1.2, 7.6), xytext=(1.2, 2.35), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.5))
b.text(1.45, 4.97, "L", fontsize=17, color=NAVY, fontweight="bold")
label(b, (3.0, 7.95), (1.2, 8.55), "금속 거울 (z PML 없음)")
b.text(6.7, 6.4, "모드 1", fontsize=13, color=BLUE, fontweight="bold"); b.text(8.0, 3.0, "모드 2", fontsize=13, color=PURPLE, fontweight="bold")
b.text(5.0, 1.1, "열린 모드 수 N = fix(t + ½)", ha="center", fontsize=15, color=NAVY, fontweight="bold")
c.plot([1.0, 9.4], [2.0, 2.0], color=NAVY, lw=1.2); c.plot([1.0, 1.0], [2.0, 8.4], color=NAVY, lw=1.2)
tt = np.linspace(0.5, 2.5, 800)
N = np.fix(tt + 0.5); F = 3 * N / (4 * tt) + (4 * N ** 3 - N) / (16 * tt ** 3)
c.plot(1.0 + (tt - 0.5) / 2.0 * 8.4, 2.0 + (F - 0.4) / 2.8 * 6.4, color=BLUE, lw=2.6)
c.plot([1.0, 9.4], [2.0 + 0.6 / 2.8 * 6.4] * 2, color=GRAY, ls="--", lw=1.2); c.text(9.4, 3.6, "bulk = 1", ha="right", fontsize=12, color=GRAY)
for tc in (0.5, 1.5, 2.5):
    c.plot([1.0 + (tc - 0.5) / 2 * 8.4] * 2, [2.0, 8.4], color=AMBER, ls=":", lw=1.4)
c.text(5.2, 1.3, "두께 t = nL/λ", ha="center", fontsize=14, color=NAVY)
c.text(1.2, 8.0, "F", fontsize=17, color=NAVY, fontweight="bold")
label(c, (1.0 + 4.2, 2.0 + (1.556 - 0.4) / 2.8 * 6.4), (2.4, 7.4), "새 모드가 열리면 뛴다", color=AMBER)
save(fig, "11")

# ------------------------------------------------------------------ post 12
fig, (a, b, c) = frame("고리는 특정 주파수의 빛만 오래 붙잡는다",
                       ["펄스로 두드린다", "울림을 Harminv로 분해", "둘레에 파장 m개"],
                       "울림의 주파수가 공진, 감쇠가 Q, 공진 사이 간격이 FSR이다.",
                       ("n = 3.4 고리, 안쪽 반지름 1, 폭 1 (a = 1 µm)  ·  광대역 펄스 0.10~0.20",
                        "Q = f / Δf  ·  FSR ≈ 1 / (n_g L)  ·  solve_cw로 같은 모드를 주파수 영역에서 확인"))
for ax_, mm in ((a, 0), (c, 4)):
    circ(ax_, (5, 4.9), 2.6, fc="none", ec=GUIDE, lw=34, alpha=0.55)
a.plot(5 + 2.2, 4.9, "o", color=AMBER, ms=13)
arrow(a, (8.6, 8.2), (7.25, 5.2), color=AMBER, lw=3)
a.text(8.7, 8.4, "광대역 펄스", fontsize=14, color=AMBER, fontweight="bold", ha="right")
a.text(5, 1.0, "모든 공진이 함께 울린다", ha="center", fontsize=15, color=NAVY, fontweight="bold")
t = np.linspace(0, 10, 900)
sig = np.exp(-0.18 * t) * np.cos(2 * np.pi * 1.3 * t) * 0.9 + 0.5 * np.exp(-0.05 * t) * np.cos(2 * np.pi * 1.7 * t)
b.plot(0.8 + 8.4 * t / 10, 6.7 + 1.2 * sig, color=BLUE, lw=1.4)
b.plot(0.8 + 8.4 * t / 10, 6.7 + 1.2 * (np.exp(-0.18 * t) * 0.9 + 0.5 * np.exp(-0.05 * t)), color=GRAY, ls="--", lw=1)
b.text(0.8, 8.4, "probe 한 점의 시간 신호", fontsize=13, color=NAVY)
arrow(b, (5, 5.2), (5, 4.2), color=PURPLE, lw=3)
b.plot([1.0, 9.0], [1.9, 1.9], color=NAVY, lw=1.2)
for fx, h, q in ((2.4, 1.0, "Q 79"), (5.0, 1.6, "Q 340"), (7.6, 2.0, "Q 2100")):
    w = 0.9 / (1 + 2.2 * (h - 1))
    xx = np.linspace(fx - 1.2, fx + 1.2, 200)
    b.plot(xx, 1.9 + h / (1 + ((xx - fx) / (w * 0.25)) ** 2), color=BLUE, lw=2)
    b.text(fx, 1.9 + h + 0.25, q, ha="center", fontsize=12, color=BLUE, fontweight="bold")
b.annotate("", xy=(5.0, 1.4), xytext=(2.4, 1.4), arrowprops=dict(arrowstyle="<->", color=AMBER, lw=1.5))
b.text(3.7, 0.95, "FSR", ha="center", fontsize=14, color=AMBER, fontweight="bold")
b.text(9.0, 1.4, "f", fontsize=14, color=NAVY)
ph = np.linspace(0, 2 * np.pi, 400)
for s_ in (1, -1):
    pts = [(5 + 2.6 * np.cos(p), 4.9 + 2.6 * np.sin(p)) for p in ph if s_ * np.cos(4 * p) > 0.35]
c.scatter(5 + 2.6 * np.cos(ph), 4.9 + RY * 2.6 * np.sin(ph), c=np.cos(4 * ph), cmap="RdBu", s=60, zorder=3)
c.text(5, 4.9, "m = 4", ha="center", va="center", fontsize=20, color=NAVY, fontweight="bold")
c.text(5, 1.0, "부호 lobe 2m개, 모드마다 m이 하나씩 늘어난다", ha="center", fontsize=13, color=NAVY, fontweight="bold")
save(fig, "12")

# ------------------------------------------------------------------ post 13
fig, (a, b, c) = frame("축 대칭 구조는 m마다 2D 계산 하나로 푼다",
                       ["3D 축 대칭 구조", "(r, z) 단면 하나만", "점 하나 = m의 합"],
                       "field를 exp(imφ)로 나누면 φ 방향은 계산하지 않아도 된다.",
                       ("dimensions = mp.CYLINDRICAL, m = 정수  ·  축 위 z 쌍극자는 m = 0, x 쌍극자는 m = ±1",
                        "축에서 떨어진 점광원은 m = 0, 1, 2, … 의 급수, 각 m이 독립된 2D run"))
a.add_patch(Ellipse((5, 3.6), 6.4, 1.6 * RY * 1.4, fc=GUIDE, ec=BLUE, lw=1.5, alpha=0.5))
a.add_patch(Rectangle((1.8, 3.6), 6.4, 1.2, fc=GUIDE, ec="none", alpha=0.5))
a.add_patch(Ellipse((5, 4.8), 6.4, 1.6 * RY * 1.4, fc="#9cc3ea", ec=BLUE, lw=1.5))
a.plot([5, 5], [1.2, 8.3], color=NAVY, ls="-.", lw=1.4); a.text(5.15, 8.2, "z 축", fontsize=13, color=NAVY, fontweight="bold")
a.add_patch(FancyArrowPatch((7.4, 6.4), (3.0, 6.5), connectionstyle="arc3,rad=0.35", arrowstyle="-|>", mutation_scale=20, color=PURPLE, lw=2.5))
a.text(5.0, 7.45, "φ: 돌려도 같다", ha="center", fontsize=14, color=PURPLE, fontweight="bold")
a.text(5, 0.6, "디스크·고리·렌즈·LED 메사", ha="center", fontsize=14, color=NAVY)
b.add_patch(Rectangle((1.6, 1.8), 6.8, 6.4, fc="#f4f7fb", ec=GRAY, lw=1.5))
b.plot([1.6, 1.6], [1.4, 8.6], color=NAVY, ls="-.", lw=1.6)
b.add_patch(Rectangle((1.6, 2.3), 3.2, 1.1, fc="#9cc3ea", ec=BLUE, lw=1.5))
b.add_patch(Rectangle((7.6, 1.8), 0.8, 6.4, fc="#cfe8cf", ec="none")); b.add_patch(Rectangle((1.6, 7.4), 6.8, 0.8, fc="#cfe8cf", ec="none"))
b.text(1.75, 8.85, "r = 0 (축)", fontsize=12, color=NAVY)
b.text(8.6, 1.5, "r", fontsize=15, color=NAVY, fontweight="bold"); b.text(1.2, 8.3, "z", fontsize=15, color=NAVY, fontweight="bold")
b.plot(3.2, 2.85, "o", color=AMBER, ms=11)
label(b, (3.2, 2.85), (4.4, 5.4), "Er ring source", color=AMBER)
label(b, (8.0, 5.0), (5.4, 6.4), "PML", color="#2e7d32")
b.text(5.0, 0.7, "field ∝ E(r, z) · exp(imφ)", ha="center", fontsize=15, color=NAVY, fontweight="bold")
ms = np.arange(0, 9)
pw = np.exp(-0.75 * ms); pw[0] = 0.55
for k_, (m_, p_) in enumerate(zip(ms, pw)):
    x_ = 1.3 + k_ * 0.95
    c.add_patch(Rectangle((x_ - 0.32, 2.0), 0.64, 5.4 * p_, fc=BLUE if p_ > 1e-2 else GRAY, ec="none", alpha=0.8))
    c.text(x_, 1.55, str(m_), ha="center", fontsize=13, color=NAVY)
c.plot([0.8, 9.4], [2.0, 2.0], color=NAVY, lw=1.2)
c.text(5.1, 0.95, "azimuthal order m", ha="center", fontsize=13, color=NAVY)
c.text(5.1, 8.2, "각 m의 방사 power", ha="center", fontsize=14, color=NAVY, fontweight="bold")
label(c, (8.9, 2.1), (4.6, 6.0), "1e-4 아래에서 멈춘다", color=AMBER)
save(fig, "13")
