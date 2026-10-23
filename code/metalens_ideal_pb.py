"""Why the wrapped-staircase phase plot is an 'ideal PB metalens' (explainer PNG).

1D (cylindrical-lens cut) scalar model, ideal half-wave fins (100 % conversion).
Focusing checked by angular-spectrum propagation, not FDTD.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.gridspec import GridSpec
from matplotlib import font_manager

for font in (Path("/mnt/c/Windows/Fonts/malgun.ttf"), Path("/mnt/c/Windows/Fonts/malgunbd.ttf")):
    if font.is_file():
        font_manager.fontManager.addfont(str(font))

plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
out = sys.argv[1]

lam, U, f = 0.532, 0.25, 10.0      # um
k = 2 * np.pi / lam
ncell = 20
a = (ncell + 0.5) * U              # half aperture
NA = a / np.sqrt(a**2 + f**2)


def phase(x):
    return -k * (np.sqrt(x**2 + f**2) - f)


xc = np.arange(-ncell, ncell + 1) * U
phc = np.mod(phase(xc), 2 * np.pi)
thc = np.rad2deg(phc / 2)
step_edge = np.rad2deg(k * U * NA)          # phase step per cell at the edge
edge_waves = (np.sqrt(a**2 + f**2) - f) / lam

# ---- angular-spectrum propagation (1D scalar) ----
dx, N = 0.005, 2**14
x = (np.arange(N) - N // 2) * dx
inside = np.abs(x) <= a
cell = np.clip(np.round(x / U), -ncell, ncell)
E_samp = np.where(inside, np.exp(1j * phase(cell * U)), 0)   # staircase (PB fins)
E_cont = np.where(inside, np.exp(1j * phase(x)), 0)          # continuous ideal phase
E_opp = np.conj(E_samp)                                       # opposite spin: -phi
kx = 2 * np.pi * np.fft.fftfreq(N, dx)
kz = np.sqrt((k**2 - kx**2).astype(complex))
zs = np.linspace(0, 20, 401)
crop = np.abs(x) <= 8
xk = x[crop]


def propagate(E0):
    F = np.fft.fft(E0)
    return np.array([np.abs(np.fft.ifft(F * np.exp(1j * kz * z))[crop])**2 for z in zs])


I_samp, I_cont, I_opp = propagate(E_samp), propagate(E_cont), propagate(E_opp)
i0 = np.argmin(np.abs(xk))
iz = np.argmax(I_cont[:, i0])
z_peak = zs[iz]
peak_ratio = I_samp[:, i0].max() / I_cont[:, i0].max()


def fwhm(xx, I):
    i = np.argmax(I)
    half = I[i] / 2
    l, r = i, i
    while I[l] > half:
        l -= 1
    while I[r] > half:
        r += 1
    xl = np.interp(half, [I[l], I[l + 1]], [xx[l], xx[l + 1]])
    xr = np.interp(half, [I[r], I[r - 1]], [xx[r], xx[r - 1]])
    return xr - xl


w_cont = fwhm(xk, I_cont[iz])
w_samp = fwhm(xk, I_samp[iz])
print(f"NA={NA:.3f} edge step={step_edge:.1f} deg z_peak={z_peak:.2f} "
      f"FWHM cont={w_cont:.3f} samp={w_samp:.3f} peak ratio={peak_ratio:.3f}")

# ---- figure ----
fig = plt.figure(figsize=(18, 21))
gs = GridSpec(4, 6, figure=fig, height_ratios=[1, 1, 1, 0.62], hspace=0.38, wspace=0.6, top=0.955)
fig.suptitle("이 계단 위상이 이상적인 PB metalens의 위상인 이유", fontsize=22, fontweight="bold", y=0.995)
xf = np.linspace(-a, a, 4001)

# (A) geometry
ax = fig.add_subplot(gs[0, 0:3])
for xr in [-4.5, -3, -1.5, 0, 1.5, 3, 4.5]:
    ax.annotate("", xy=(xr, 0), xytext=(xr, -2), arrowprops=dict(arrowstyle="->", color="0.55"))
    hi = xr == 4.5
    ax.plot([xr, 0], [0, f], color="C3" if hi else "C1", lw=2.2 if hi else 1)
ax.plot([-a, a], [0, 0], color="steelblue", lw=7, solid_capstyle="butt")
ax.plot(0, f, "k*", ms=16)
ax.text(0.15, 10.4, "초점", fontsize=12)
ax.text(2.55, 5.2, "경로 = √(x²+f²)", color="C3", fontsize=12)
ax.text(0.15, 3.0, "f", fontsize=14)
ax.text(-5.9, -1.4, "평면파 입사", color="0.4", fontsize=11)
ax.text(-5.9, 0.35, "렌즈 (z = 0)", color="steelblue", fontsize=11)
ax.text(-5.9, 14.3, "렌즈 위 모든 점 → 초점까지 총 위상이 같아야 함\n"
        "φ(x) + k·√(x²+f²) = k·f\n⇒  φ(x) = −k(√(x²+f²) − f)",
        fontsize=12, va="top", bbox=dict(boxstyle="round", fc="lightyellow", ec="0.6"))
ax.set_xlim(-6, 6)
ax.set_ylim(-2.3, 14.6)
ax.set_xlabel("x (μm)")
ax.set_ylabel("z (μm)")
ax.set_title("(A) 이상적 렌즈 조건: 등광로 (Fermat)", fontsize=14, loc="left")

# (B) unwrapped phase
ax = fig.add_subplot(gs[0, 3:6])
ax.plot(xf, (np.sqrt(xf**2 + f**2) - f) / lam, color="C1", label="추가 경로 ΔL/λ")
ax.plot(xf, phase(xf) / (2 * np.pi), color="C0", lw=2, label="필요한 위상 φ/2π = −ΔL/λ")
ax.plot(xf, -xf**2 / (2 * f) / lam, ":", color="0.4", label="근축 근사 −x²/(2fλ)")
ax.axhline(0, color="0.8", lw=0.8)
ax.set_xlabel("x (μm)")
ax.set_ylabel("파장 수")
ax.legend(fontsize=11, loc="upper center")
ax.set_title(f"(B) 접기 전: 매끄러운 쌍곡선 (가장자리 {edge_waves:.2f} 파장)\n"
             "→ 가장자리 빛이 더 먼 길을 가는 만큼 위상을 미리 빼 줌", fontsize=14, loc="left")

# (C) wrapped + sampled (the plot in question)
ax = fig.add_subplot(gs[1, 0:3])
ax.plot(xf, np.mod(phase(xf), 2 * np.pi), color="0.65", lw=1, label="목표 위상 (mod 2π)")
ax.step(xc, phc, where="mid", color="C3", lw=1.8, label=f"격자 샘플링 (U = {U*1e3:.0f} nm)")
ax.annotate("중앙 홈: 0 ≡ 2π\n(접기 표시)", xy=(0, 0.05), xytext=(0.3, 0.55),
            fontsize=11, arrowprops=dict(arrowstyle="->", color="k"))
ax.text(a, 2 * np.pi + 1.95,
        f"톱니 폭이 바깥으로 갈수록 좁아짐\n(|dφ/dx| = k·sinθ, 가장자리로 갈수록 ↑)\n"
        f"칸당 위상 변화: 최대 {step_edge:.0f}° < 180° (Nyquist 만족)",
        fontsize=11, ha="right", va="top")
ax.set_ylim(-0.3, 2 * np.pi + 2.1)
ax.set_yticks([0, np.pi, 2 * np.pi], ["0", "π", "2π"])
ax.set_xlabel("x (μm)")
ax.set_ylabel("위상")
ax.legend(fontsize=11, loc="upper left")
ax.set_title("(C) 위상을 0~2π로 접고 격자점마다 샘플링", fontsize=14, loc="left")

# (D) PB mapping theta = phi/2, with fins
sub = gs[1, 3:6].subgridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
ax = fig.add_subplot(sub[0])
ax.step(xc, thc, where="mid", color="C2", lw=1.8)
ax.set_ylim(-8, 230)
ax.set_yticks([0, 45, 90, 135, 180])
ax.set_ylabel("fin 각도 θ (°)")
ax.set_xlim(-a - 0.1, a + 0.1)
ax.tick_params(labelbottom=False)
ax.text(0, 225, "θ = φ/2  →  한쪽 원편광 +2θ, 반대쪽 −2θ\nfin은 180° 대칭: 중앙 0° ≈ 옆칸 179° (거의 평행)",
        fontsize=11, ha="center", va="top")
ax.set_title("(D) PB 매핑: 위상을 fin 회전각으로 그대로 옮김", fontsize=14, loc="left")
ax2 = fig.add_subplot(sub[1], sharex=ax)
L, W = 0.21, 0.07
polys = []
for xx, t in zip(xc, np.deg2rad(thc)):
    pts = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2]])
    rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    polys.append(pts @ rot.T + [xx, 0])
pc = PolyCollection(polys, array=thc, cmap="twilight", edgecolors="k", linewidths=0.5)
pc.set_clim(0, 180)
ax2.add_collection(pc)
ax2.set_ylim(-0.16, 0.16)
ax2.set_yticks([])
ax2.set_xlabel("x (μm)  — 위에서 본 fin (중앙 행)")

# (E) focusing, converted spin
ext = [xk[0], xk[-1], zs[0], zs[-1]]
ax = fig.add_subplot(gs[2, 0:2])
ax.imshow(I_samp / I_samp.max(), extent=ext, origin="lower", aspect="auto", cmap="hot", vmin=0, vmax=1)
ax.axhline(f, color="w", ls="--", lw=0.8)
ax.plot([-a, a], [0.15, 0.15], color="cyan", lw=4)
ax.set_xlabel("x (μm)")
ax.set_ylabel("z (μm)")
ax.set_title("(E) 변환된 원편광: +φ → z ≈ f 에 초점", fontsize=13, loc="left")

# (F) opposite spin
ax = fig.add_subplot(gs[2, 2:4])
ax.imshow(I_opp / I_opp.max(), extent=ext, origin="lower", aspect="auto", cmap="hot", vmin=0, vmax=1)
ax.axhline(f, color="w", ls="--", lw=0.8)
ax.plot([-a, a], [0.15, 0.15], color="cyan", lw=4)
ax.set_xlabel("x (μm)")
ax.set_title("(F) 반대 원편광: −φ → 발산 (오목렌즈)", fontsize=13, loc="left")

# (G) focal-plane cut
ax = fig.add_subplot(gs[2, 4:6])
norm = I_cont[iz].max()
ax.plot(xk, I_cont[iz] / norm, color="0.5", lw=3, label=f"연속 이상 위상 (FWHM {w_cont*1e3:.0f} nm)")
ax.plot(xk, I_samp[iz] / norm, "C3--", lw=1.6, label=f"계단 샘플링 (FWHM {w_samp*1e3:.0f} nm)")
ax.plot(xk, I_opp[iz] / norm, color="C0", lw=1.2, label="반대 원편광")
ax.set_xlim(-3, 3)
ax.set_ylim(0, 1.5)
ax.set_xlabel("x (μm)")
ax.set_ylabel("세기 (연속 위상 초점 = 1)")
ax.legend(fontsize=10, loc="upper right")
ax.set_title(f"(G) 초점면 z = {z_peak:.1f} μm 단면\n계단/연속 피크 비 = {peak_ratio:.2f}", fontsize=13, loc="left")

# summary box
ax = fig.add_subplot(gs[3, :])
ax.axis("off")
summary = (
    "정리 — 이 계단 위상이 이상적인 PB metalens의 위상인 이유\n"
    "①  목표 위상이 등광로 조건에서 나온 쌍곡 위상 φ(x) = −k(√(x²+f²) − f) 이다 → 수직 입사·단일 파장에서 축상 수차 0  (A, B)\n"
    "②  PB 위상은 θ = φ/2 로 위상을 fin 각도로 옮긴다 → 빨간 계단이 격자점마다 회색 목표선 위에 올라감, "
    "직경형 같은 라이브러리 오차 없음  (C, D)\n"
    f"③  칸당 위상 변화가 최대 {step_edge:.0f}° < 180° (Nyquist) → 계단으로 샘플링해도 초점 폭은 같고 피크는 연속 위상의 {peak_ratio*100:.0f} %  (E, G)\n"
    "④  중앙 홈·톱니는 0 ≡ 2π 로 접어 그린 표시일 뿐이고, fin 은 0° ≡ 180° 라 구조상 끊김이 없다  (C, D)\n\n"
    "이상적이라는 가정: 모든 fin 이 완벽한 반파장판(변환 효율 100 %, 진폭 균일). 실제 fin 은 변환 안 된 동편광 누설, 이웃 셀 결합(LPA 오차),\n"
    f"파장 의존(색수차)이 있다. 반대 원편광에는 −φ 가 걸려 발산한다 (F).\n초점이 {z_peak:.1f} μm 로 약간 당겨진 것은 작은 구경(Fresnel 수 ≈ {a**2/(lam*f):.0f})의 회절 효과로, 연속 이상 위상에서도 같다.\n"
    f"계산 조건: λ = {lam*1e3:.0f} nm, f = {f:.0f} μm, 구경 ±{a:.2f} μm (NA {NA:.2f}), 격자 {U*1e3:.0f} nm — "
    "1D 단면 스칼라 각스펙트럼 전파 (FDTD/Meep 아님)"
)
ax.text(0.0, 1.0, summary, fontsize=13, va="top", ha="left", linespacing=1.6,
        bbox=dict(boxstyle="round,pad=0.8", fc="#f3f6fb", ec="0.6"))

fig.savefig(out, dpi=100, bbox_inches="tight")



