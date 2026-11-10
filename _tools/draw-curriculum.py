"""Reproducible concept diagrams and analytic intro loops for lessons 17/18/20.

These are explanatory models, not Meep field data. Numerical figures are kept
separately under assets/meep/NN. Uses the existing illustration palette/camera.
Run: python _tools/draw-curriculum.py [--videos]
Requires matplotlib, numpy and FFmpeg (for --videos), outside the site runtime.
"""
import importlib.util
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("apparatus", ROOT / "_tools/draw-illustrations.py")
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)
TITLES = {
    "17": {"ko": "원하는 방향으로 움직이는 파면", "en": "Wavefronts in a chosen direction"},
    "18": {"ko": "계면에서 갈라지는 빛", "en": "Light meeting an interface"},
    "20": {"ko": "파장에 따라 달라지는 재료 응답", "en": "A material responds to wavelength"},
}
art.TITLES.update(TITLES)


def line(ax, points, color, width=2, alpha=1, z=5, dashed=False):
    xy = np.array([art.project(p) for p in points])
    return ax.plot(xy[:, 0], xy[:, 1], color=color, lw=width, alpha=alpha,
                   ls="--" if dashed else "-", solid_capstyle="round", zorder=z)[0]


def plane_front(ax, offset, th, alpha=0.6):
    # k=(cos40,sin40); constant phase lines clipped to the same rectangular slab.
    c, s = math.cos(math.radians(40)), math.sin(math.radians(40))
    points = []
    for x in [-5, 5]:
        y = (offset - c*x)/s
        if -3.5 <= y <= 3.5:
            points.append((x, y, .15))
    for y in [-3.5, 3.5]:
        x = (offset - s*y)/c
        if -5 <= x <= 5:
            points.append((x, y, .15))
    if len(points) == 2:
        return line(ax, points, th["teal"], 4, alpha)


def draw(chapter, locale="en", theme="light", video=False):
    fig, ax, th = art.frame(locale, theme)
    if video:
        fig.set_size_inches(12.8, 7.2)
        fig.set_dpi(100)
        fig.patch.set_facecolor("#edf7fb")
    ax.set_xlim(-10, 10)
    ax.set_ylim(-6, 6)
    dynamic = []
    if chapter == "17":
        art.box(ax, -5, 5, -3.5, 3.5, -.7, 0, th["glass"], th, z=1)
        for offset in np.arange(-6, 7, 1.35):
            p = plane_front(ax, offset, th)
            if p is not None:
                dynamic.append(p)
        art.arrow(ax, (-3, -2, .35), (3.8, 3.7, .35), th["amber"], lw=6, head=.6, z=8)
        a = art.project((3.8, 3.7, .35))
        ax.text(a[0]+.35, a[1]+.1, "k", color=th["text"], fontsize=28, zorder=9)
    elif chapter == "18":
        ax.set_ylim(-7.4, 7.5)  # keep the incident ray below the title safe area
        art.box(ax, -5.5, 5.5, -3.6, 3.6, -3, 0, th["glass"], th, z=1, alpha=.86)
        line(ax, [(0,0,-3.2),(0,0,4.4)], th["grid"], 2, z=4, dashed=True)
        transmitted_x = 3 * math.tan(math.asin(math.sin(math.pi/4)/3.5))
        raypaths = [((-4.5,0,4.5),(0,0,0),th["amber"]),
                    ((0,0,0),(4.5,0,4.5),th["amber"]),
                    ((0,0,0),(transmitted_x,0,-3),th["teal"])]
        for p0,p1,col in raypaths:
            art.arrow(ax, p0,p1,col,lw=4.5,head=.5,z=7)
            for frac in [.25,.5,.75]:
                p = np.array(p0)+(np.array(p1)-p0)*frac
                # Wavefront perpendicular to its ray, with a short y extent.
                tangent = np.array([-(p1[2]-p0[2]),0,p1[0]-p0[0]])
                tangent = tangent/np.linalg.norm(tangent)*.48
                line(ax,[p-tangent,p+tangent],col,3,.5,z=6)
        for x,y,label in [(-3.2,3.1,"incident"),(3.1,3.1,"reflected"),(1.25,-3.9,"transmitted")]:
            # Intro uses language-neutral I/R/T and stays shared across locales.
            p=art.project((x,0,y))
            ax.text(p[0],p[1]+.3,{"incident":"I","reflected":"R","transmitted":"T"}[label],
                    fontsize=24,color=th["text"],ha="center",zorder=10)
        for p0,p1,col in raypaths:
            a=art.project(p0)
            dot=ax.plot([a[0]],[a[1]],"o",color=col,ms=11,zorder=10)[0]
            dynamic.append((dot,np.array(p0),np.array(p1)))
    else:
        art.box(ax, 0, 5, -4.2, 4.2, -1.0, .0, th["glass"], th, z=1, alpha=.95)
        for i,(y,col,wavelength,n) in enumerate([(-2.8,th["teal"],2.5,1.43),(0,th["blue"],1.9,1.47),(2.8,th["amber"],1.35,1.54)]):
            x=np.linspace(-6,5,650)
            optical_x=np.where(x<0,x,n*x)
            z=.36*np.sin(2*math.pi*optical_x/wavelength)+.6
            curve=line(ax,list(zip(x,np.full_like(x,y),z)),col,3.5,z=5+i)
            dynamic.append((curve,x,y,optical_x,wavelength))
            art.arrow(ax,(-5.8,y,-.2),(-3.7,y,-.2),col,lw=2.4,head=.35,z=5+i)
        a=art.project((2.5,0,2.5))
        ax.text(a[0],a[1],r"$n(\lambda)$",fontsize=27,color=th["text"],ha="center")
    if not video:
        art.labels(fig,chapter,locale,th)

    def set_time(t):
        phase=2*math.pi*t/4  # two full optical periods, exact eight-second loop
        if chapter=="17":
            for item in dynamic:
                item.remove()
            dynamic.clear()
            shift=(t/4 % 1)*1.35
            for off in np.arange(-8,9,1.35):
                p=plane_front(ax,off+shift,th)
                if p is not None:
                    dynamic.append(p)
        elif chapter=="18":
            for dot,p0,p1 in dynamic:
                # Markers convey direction, not group delay or power fraction.
                frac=(t/4)%1
                p=art.project(p0+(p1-p0)*frac)
                dot.set_data([p[0]],[p[1]])
        else:
            for curve,x,y,optical_x,wavelength in dynamic:
                z=.36*np.sin(2*math.pi*optical_x/wavelength-phase)+.6
                pts=np.array([art.project(p) for p in zip(x,np.full_like(x,y),z)])
                curve.set_data(pts[:,0],pts[:,1])
    return fig,set_time


def main():
    for ch in TITLES:
        for lang in ["ko","en"]:
            for theme in ["light","dark"]:
                fig,_=draw(ch,lang,theme)
                fig.savefig(ROOT/f"assets/illustrations/{ch}.{lang}.{theme}.png",dpi=100,facecolor=fig.get_facecolor())
                plt.close(fig)
        if "--videos" not in sys.argv:
            continue
        ffmpeg=shutil.which("ffmpeg")
        if not ffmpeg:
            candidates=list((Path.home()/"AppData/Local/Microsoft/WinGet/Packages").glob("Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"))
            ffmpeg=str(candidates[-1]) if candidates else None
        if not ffmpeg:
            raise RuntimeError("FFmpeg is required for --videos")
        out=ROOT/f"assets/meep/{ch}"
        out.mkdir(parents=True,exist_ok=True)
        fig,set_time=draw(ch,video=True)
        process=subprocess.Popen([ffmpeg,"-y","-v","error","-f","rawvideo","-pix_fmt","rgba","-s","1280x720","-r","30","-i","-","-an","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-movflags","+faststart",str(out/"00_intro.mp4")],stdin=subprocess.PIPE)
        for frame in range(240):
            set_time(frame/30)
            fig.canvas.draw()
            process.stdin.write(fig.canvas.buffer_rgba())
        process.stdin.close()
        if process.wait()!=0:
            raise RuntimeError("FFmpeg failed")
        set_time(2)
        fig.savefig(out/"00_intro.jpg",dpi=100,facecolor=fig.get_facecolor())
        plt.close(fig)
        (out/"intro-model.json").write_text(json.dumps({"type":"analytic concept animation, not Meep field data","chapter":ch,"authoring":"_tools/draw-curriculum.py","dimensions":[1280,720],"fps":30,"duration_seconds":8,"loop_period_seconds":4,"model":{"17":"constant-phase lines k dot r=constant, direction40deg; ray k normal to fronts","18":"Snell/reflection ray schematic: incidence45deg, n1=1, n2=3.5; markers show direction, not power/speed","20":"three illustrative wavelengths with n=1.43,1.47,1.54, phase continuous across x=0; not a fitted quartz model"}[ch]},indent=2)+"\n",encoding="utf-8")
        print(f"Rendered {ch}: four concept variants and 8s analytic intro",flush=True)


if __name__=="__main__":
    main()
