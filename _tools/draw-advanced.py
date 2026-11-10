"""Analytic apparatus illustrations for 19/21/25/26/27; no EM solver data."""
import math
import numpy as np

TITLES = {
    "19": {"ko": "유한한 폭을 가진 Gaussian 빔", "en": "A Gaussian beam with a finite waist"},
    "21": {"ko": "회전하는 광축과 편광 회절", "en": "Rotating optical axes and diffraction"},
    "25": {"ko": "물체 안의 흡수와 경계의 전력", "en": "Absorption inside and power at the boundary"},
    "26": {"ko": "공기 구멍 사이에 가두는 빛", "en": "Light confined between air holes"},
    "27": {"ko": "넓어지는 도파로의 모드 분해", "en": "Modal analysis of a widening waveguide"},
}
MODELS = {
    "19": "Paraxial free-space Gaussian envelope w=w0*sqrt(1+(x/zR)^2), w0=0.8, zR=3; curved phase fronts and direction marker. Dimensionless concept, not archived interface fields.",
    "21": "Liquid-crystal film with optic axis rotating in the yz plane along y. Circular incident wave and possible +/-1 diffraction directions; angles exaggerated, no efficiency encoded.",
    "25": "2D cylinder cross-section and square inward-flux contour; finite display extrusion only. Traveling incident phase and pulsing interior illustrate absorption, not a computed temperature or field.",
    "26": "N=3 holes per side, centers +/-0.7,+/-1.7,+/-2.7 a, radius0.36a, guide width1.2a. Extruded 2D geometry; periodic central lobe is a concept, not measured Q or a decay fit.",
    "27": "2D guide widens from w1=1 to w2=2 through a taper. Input-side modal monitor and separate forward/backward direction markers; no power fractions or solved modes encoded.",
}


def draw(ch, art, line, locale="en", theme="light", video=False):
    fig, ax, th = art.frame(locale, theme)
    if video:
        fig.set_size_inches(12.8, 7.2)
        fig.set_dpi(100)
        fig.patch.set_facecolor("#edf7fb")
    ax.set_xlim(-8.5, 8.5)
    ax.set_ylim(-5.8, 5.8)
    moving = []

    def dot(p, color, size=10, z=20):
        q = art.project(p)
        return ax.plot([q[0]], [q[1]], "o", color=color, ms=size, zorder=z)[0]

    if ch == "19":
        # Both envelope and phase fronts belong to the same propagation plane.
        x = np.linspace(-6, 6, 300)
        w = .8*np.sqrt(1+(x/3)**2)
        art.poly(ax, list(zip(x, w, np.zeros_like(x))) +
                 list(zip(x[::-1], -w[::-1], np.zeros_like(x))), th["teal"], alpha=.12)
        for sign in [-1, 1]:
            line(ax, list(zip(x, sign*w, np.zeros_like(x))), th["teal"], 3)
        line(ax, [(-6, 0, 0), (6, 0, 0)], th["grid"], 1.5, dashed=True)
        line(ax, [(0, -.8, 0), (0, .8, 0)], th["amber"], 5)
        q = art.project((0, 1.5, 0))
        ax.text(q[0]-.5, q[1], r"$2w_0$", color=th["text"], fontsize=25)
        art.arrow(ax, (3.5, 0, .1), (6, 0, .1), th["amber"], lw=4)
        fronts = [line(ax, [(0, 0, 0), (0, 0, 0)], th["teal"], 2.4) for _ in range(10)]

        def update(t):
            for i, curve in enumerate(fronts):
                c = -6+((i*1.2+t/4*1.2) % 12)
                width = .8*math.sqrt(1+(c/3)**2)
                y = np.linspace(-width, width, 60)
                inv_r = c/(c*c+9)
                xx = c-.5*y*y*inv_r
                pts = np.array([art.project(p) for p in zip(xx, y, np.zeros_like(y))])
                curve.set_data(pts[:, 0], pts[:, 1])
        moving.append(update)
    elif ch == "21":
        # Film is normal to x; optic axis lies in yz and rotates along y.
        art.box(ax, -.5, .5, -3.6, 3.6, -.8, 2.5, th["glass"], th, alpha=.65)
        for y in np.linspace(-3.1, 3.1, 11):
            phi = math.pi*(y+3.1)/3.1
            v = np.array([0, .42*math.cos(phi), .42*math.sin(phi)])
            p = np.array([.55, y, .85])
            line(ax, [p-v, p+v], th["teal"], 4, z=8)
        x = np.linspace(-6, -.7, 220)
        helix = line(ax, list(zip(x, np.zeros_like(x), np.ones_like(x))), th["amber"], 3.5)
        for sign in [-1, 1]:
            art.arrow(ax, (.7, 0, 1), (6, sign*2.4, 1), th["teal"], lw=3.5)
            q = art.project((6, sign*2.4, 1))
            ax.text(q[0]+.2, q[1], f"{sign:+d}", color=th["text"], fontsize=24)

        def update(t):
            phase = 2*math.pi*x/2-2*math.pi*t/4
            pts = np.array([art.project(p) for p in zip(x, .45*np.cos(phase), 1+.45*np.sin(phase))])
            helix.set_data(pts[:, 0], pts[:, 1])
        moving.append(update)
    elif ch == "25":
        # No substrate: the original cylinder is infinite in z.
        r = 1.8
        art.poly(ax, art.ring_pts(r, -.7), art.shade(th["blue"], (0, 1, 0), th), z=3)
        a = np.linspace(0, math.pi, 70)
        art.poly(ax, [(r*math.cos(v), r*math.sin(v), -.7) for v in a] +
                 [(r*math.cos(v), r*math.sin(v), .35) for v in a[::-1]], th["blue"], z=4)
        art.poly(ax, art.ring_pts(r, .35), th["glass"], z=5)
        contour = [(-2.3, -2.3, .4), (2.3, -2.3, .4), (2.3, 2.3, .4), (-2.3, 2.3, .4), (-2.3, -2.3, .4)]
        line(ax, contour, th["teal"], 2.5, z=7, dashed=True)
        for y in [-1, 0, 1]:
            art.arrow(ax, (-6, y, .5), (-2.5, y, .5), th["amber"], lw=3)
        for y in [-1.2, 1.2]:
            art.arrow(ax, (3.2, y, .5), (5.5, y, .5), th["teal"], lw=2)
        for p, end in [((-3, 0, .5), (-2.3, 0, .5)), ((3, 0, .5), (2.3, 0, .5)), ((0, -3, .5), (0, -2.3, .5)), ((0, 3, .5), (0, 2.3, .5))]:
            art.arrow(ax, p, end, th["teal"], lw=2.2, head=.3, z=9)
        glow = dot((.5, 0, .5), th["amber"], 34)
        marker = dot((-6, -.6, .5), th["amber"], 8)

        def update(t):
            phase = 2*math.pi*(t % 4)/4
            glow.set_alpha(.35+.35*(1+math.cos(phase))/2)
            q = art.project((-6+3.4*((t/4) % 1), -.6, .5))
            marker.set_data([q[0]], [q[1]])
        moving.append(update)
    elif ch == "26":
        # Uniform scale preserves the actual six-hole geometry and defect gap.
        scale = 1.65
        art.box(ax, -4.2*scale, 4.2*scale, -.6*scale, .6*scale, -.65, 0, th["blue"], th, z=2)
        for center in [-2.7, -1.7, -.7, .7, 1.7, 2.7]:
            points = [(scale*(center+.36*math.cos(v)), scale*.36*math.sin(v), .025) for v in np.linspace(0, 2*math.pi, 90)]
            art.poly(ax, points, th["ink"], z=5, edge=th["pale"], lw=1.5)
        art.arrow(ax, (-7.6, 0, .15), (-5.5, 0, .15), th["amber"], lw=4)
        x = np.linspace(-.52*scale, .52*scale, 120)
        field = line(ax, list(zip(x, np.zeros_like(x), np.full_like(x, .2))), th["amber"], 6, z=10)
        q = art.project((0, 0, 1.9))
        ax.text(q[0], q[1], r"$d=1.4a$", color=th["text"], ha="center", fontsize=26)

        def update(t):
            z = .25+.75*np.exp(-(x/.55)**2)*math.cos(2*math.pi*(t % 4)/4)
            pts = np.array([art.project(p) for p in zip(x, np.zeros_like(x), z)])
            field.set_data(pts[:, 0], pts[:, 1])
        moving.append(update)
    else:
        # Widening guide, with the reflection/modal monitor on the narrow side.
        top = [(-6, -0.65, 0), (-2, -.65, 0), (2, -1.3, 0), (6, -1.3, 0), (6, 1.3, 0), (2, 1.3, 0), (-2, .65, 0), (-6, .65, 0)]
        bottom = [(x, y, -.65) for x, y, _ in top]
        for i in [3, 4, 5, 6, 7]:
            j = (i+1) % 8
            art.poly(ax, [bottom[i], bottom[j], top[j], top[i]], th["blue"], z=2)
        art.poly(ax, top, art.shade(th["glass"], (0, 0, 1), th), z=3)
        art.poly(ax, [(-3.5, -1.3, -.1), (-3.5, 1.3, -.1), (-3.5, 1.3, 1.7), (-3.5, -1.3, 1.7)], th["teal"], alpha=.2, z=5, edge=th["teal"])
        art.arrow(ax, (-5.8, -.2, .3), (-1.8, -.2, .3), th["amber"], lw=4, z=9)
        art.arrow(ax, (-2.2, .4, 1), (-5.7, .4, 1), th["teal"], lw=2.8, z=9)
        marker = dot((-6, 0, .3), th["amber"], 10)
        for pos, label in [((-5.7, 1.3, 0), r"$w_1$"), ((5.5, 2.1, 0), r"$2w_1$")]:
            q = art.project(pos)
            ax.text(q[0], q[1]-.4, label, color=th["text"], fontsize=25)

        def update(t):
            q = art.project((-6+12*((t/4) % 1), 0, .3))
            marker.set_data([q[0]], [q[1]])
        moving.append(update)

    if not video:
        art.labels(fig, ch, locale, th)

    def set_time(t):
        for update in moving:
            update(t)
    set_time(0)
    return fig, set_time
