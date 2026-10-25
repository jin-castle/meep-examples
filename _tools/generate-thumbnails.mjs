// Original, dependency-free orthographic apparatus drawings. Not field simulations.
// Run: node _tools/generate-thumbnails.mjs (from any directory).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'assets/thumbnails');
const C = { blue: '#76b6da', substrate: '#e9e5ce', plane: '#edf3f6', boundary: '#c9dce8', metal: '#899baa', gold: '#e3a331', teal: '#0087ad', ink: '#526579', white: '#ffffff' };
const camera = [.433, .75, .5];
const light = [-.35, -.45, .82];
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const sub = (a, b) => a.map((x, i) => x - b[i]);
const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const norm = a => { const n = Math.hypot(...a); return a.map(x => x / (n || 1)); };
const rgb = hex => hex.match(/\w\w/g).map(x => parseInt(x, 16));
const mix = (a, b, t) => '#' + rgb(a.slice(1)).map((x, i) => Math.round(x*(1-t)+rgb(b.slice(1))[i]*t).toString(16).padStart(2, '0')).join('');
const shade = (hex, n) => { const k = dot(n, light); return k > 0 ? mix(hex, C.white, Math.min(.48, k*.42)) : mix(hex, C.ink, -k*.34); };
const esc = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const fmt = n => Number(n.toFixed(2));
const circle = (r, z, cx=0, cy=0, n=72) => Array.from({length:n+1}, (_, i) => [cx+r*Math.cos(i/n*Math.PI*2), cy+r*Math.sin(i/n*Math.PI*2), z]);

class Scene {
  constructor(id, title, description, mode='2D · CONCEPT VIEW') {
    this.id=id; this.title=title; this.description=description; this.mode=mode;
    this.items=[]; this.overlay=[]; this.layer=0; this.scale=59; this.center=[400, 265];
  }
  project([x,y,z]) { return [this.center[0]+this.scale*(.866*x-.5*y), this.center[1]+this.scale*(.25*x+.433*y-.866*z)]; }
  points(ps) { return ps.map(p => this.project(p).map(fmt).join(',')).join(' '); }
  add(ps, markup, bias=0) { this.items.push({layer:this.layer, depth:ps.reduce((s,p)=>s+dot(p,camera),0)/ps.length+bias, markup}); }
  face(ps, color, opacity=1, lit=true) {
    const n=norm(cross(sub(ps[1],ps[0]),sub(ps[2],ps[0])));
    if(lit && dot(n,camera)<-.001) return;
    const fill=lit?shade(color,n):color;
    this.add(ps, `<polygon points="${this.points(ps)}" fill="${fill}" fill-opacity="${opacity}" stroke="${fill}" stroke-width=".7" stroke-linejoin="round"/>`);
  }
  extrude(p, bottom, top, color=C.blue, opacity=1) {
    this.face(p.map(([x,y])=>[x,y,top]),color,opacity);
    p.forEach(([x,y],i)=>{ const [nx,ny]=p[(i+1)%p.length]; this.face([[x,y,bottom],[nx,ny,bottom],[nx,ny,top],[x,y,top]],color,opacity); });
  }
  box(x0,y0,x1,y1,z0,z1,color=C.blue,opacity=1) { this.extrude([[x0,y0],[x1,y0],[x1,y1],[x0,y1]],z0,z1,color,opacity); }
  line(ps, color=C.teal, width=3, {dash='',opacity=1,arrow=false,overlay=false}={}) {
    const markup=`<polyline points="${this.points(ps)}" fill="none" stroke="${color}" stroke-width="${width}" stroke-opacity="${opacity}" stroke-linecap="round" stroke-linejoin="round"${dash?` stroke-dasharray="${dash}"`:''}${arrow?` marker-end="url(#arrow-${color===C.gold?'gold':'teal'})"`:''}/>`;
    if(overlay)this.overlay.push(markup);else this.add(ps,markup,.03);
  }
  source(p,r=10) { const [x,y]=this.project(p); this.overlay.push(`<circle cx="${fmt(x)}" cy="${fmt(y)}" r="${r+7}" fill="${C.gold}" opacity=".12"/><circle cx="${fmt(x)}" cy="${fmt(y)}" r="${r}" fill="url(#source)" stroke="#ffffff" stroke-width="2"/>`); }
  label(text,p,dx=0,dy=0) {const [x,y]=this.project(p);this.overlay.push(`<text x="${fmt(x+dx)}" y="${fmt(y+dy)}" fill="${C.ink}" font-size="24">${esc(text)}</text>`);}
  slab(color=C.substrate,z=-.35,thickness=.36) {
    this.layer=-1; // A broad base face must not occlude smaller apparatus above it.
    this.box(-4,-2.7,4,2.7,z-thickness,z,color);
    this.layer=0;
  }
  plane() {
    this.layer=-1;
    this.face([[-4,-2.7,-.05],[4,-2.7,-.05],[4,2.7,-.05],[-4,2.7,-.05]],C.plane,.72,false);
    for(let x=-4;x<=4;x+=1)this.line([[x,-2.7,-.045],[x,2.7,-.045]],C.boundary,1,{opacity:.55});
    for(let y=-2;y<=2;y+=1)this.line([[-4,y,-.045],[4,y,-.045]],C.boundary,1,{opacity:.55});
    this.layer=0;
  }
  annulus(inner,outer,z0,z1,color=C.blue,cx=0,cy=0) {
    const n=96;
    for(let i=0;i<n;i++) {
      const a=i/n*Math.PI*2,b=(i+1)/n*Math.PI*2;
      const p=(r,t,z)=>[cx+r*Math.cos(t),cy+r*Math.sin(t),z];
      this.face([p(outer,a,z1),p(outer,b,z1),p(inner,b,z1),p(inner,a,z1)],color);
      this.face([p(outer,a,z0),p(outer,b,z0),p(outer,b,z1),p(outer,a,z1)],color);
      if(inner>0)this.face([p(inner,b,z0),p(inner,a,z0),p(inner,a,z1),p(inner,b,z1)],color);
    }
  }
  render() {
    const defs=`<defs><linearGradient id="paper" x2="0" y2="1"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#f5f8fa"/></linearGradient><radialGradient id="source" cx=".32" cy=".25"><stop stop-color="#fff4d9"/><stop offset=".5" stop-color="${C.gold}"/><stop offset="1" stop-color="#b37a18"/></radialGradient><filter id="shadow" x="-.3" y="-.8" width="1.6" height="2.6"><feGaussianBlur stdDeviation="12"/></filter>${['gold','teal'].map(c=>`<marker id="arrow-${c}" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto-start-reverse"><path d="M0 0L5 2.5L0 5Z" fill="${C[c]}"/></marker>`).join('')}</defs>`;
    const meshes=this.items.sort((a,b)=>a.layer-b.layer || a.depth-b.depth).map(i=>i.markup).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480" viewBox="0 0 800 480" role="img" aria-labelledby="title desc"><title id="title">${esc(this.title)}</title><desc id="desc">${esc(this.description)}</desc>${defs}<rect width="800" height="480" fill="url(#paper)"/><ellipse cx="410" cy="365" rx="205" ry="30" fill="#0d1b2a" opacity=".08" filter="url(#shadow)"/><g font-family="system-ui, sans-serif">${meshes}${this.overlay.join('')}<text x="32" y="43" fill="${C.ink}" font-size="24" letter-spacing="2">${esc(this.title)}</text><text x="32" y="450" fill="${C.ink}" font-size="22" letter-spacing="1">${esc(this.mode)}</text></g></svg>\n`;
  }
}

const scenes=[];
const add=(...args)=>{const s=new Scene(...args);scenes.push(s);return s;};
const arrow=(s,a,b,color=C.gold,width=5)=>s.line([a,b],color,width,{arrow:true,overlay:true});
const densities = n => JSON.parse(fs.readFileSync(path.join(root,`assets/meep/${n}/result.json`),'utf8')).x_optimized;

{
 const s=add('01-point-line-source','POINT / LINE SOURCE','Vacuum calculation plane with a point source and finite line source. Rings and arrows show schematic propagation, not a calculated field.');
 s.plane();
 for(const r of [.5,.95,1.4,1.85])s.line(circle(r,.03,-1.7,0),C.teal,2.4,{opacity:1-r*.25});
 s.source([-1.7,0,.08]);
 s.line([[1.1,-1.5,.05],[1.1,1.5,.05]],C.gold,7);
 for(let x=1.7;x<3.6;x+=.6)s.line([[x,-1.4,.06],[x,1.4,.06]],C.teal,2.5,{opacity:1-(x-1.1)*.2});
 arrow(s,[1.1,0,.12],[3.6,0,.12]);
}
{
 const s=add('02-boundary-pml','ABSORBING BOUNDARY','A vacuum computational plane surrounded by a PML band. The band is a computational boundary, not a physical material.');
 s.plane();
 for(let i=0;i<4;i++){const t=i*.16;s.line([[-4+t,-2.7+t,.03],[4-t,-2.7+t,.03],[4-t,2.7-t,.03],[-4+t,2.7-t,.03],[-4+t,-2.7+t,.03]],C.boundary,9,{opacity:.8});}
 for(const r of [.65,1.2,1.75,2.3])s.line(circle(r,.07,-.9,0),C.teal,2.5,{opacity:1-r*.28});
 s.source([-.9,0,.1]);arrow(s,[-.2,0,.13],[3.1,0,.13]);s.label('PML',[2.8,2.2,.15],0,35);
}
{
 const s=add('03-reference-subtraction','SCATTERED LIGHT','An invariant-z dielectric cylinder, incident plane wave and dashed closed flux contour. Extrusion and arrows are explanatory.');
 s.plane();s.annulus(0,.85,-.02,1.6,C.blue,.2,0);
 s.line([[-1.4,-1.8,.1],[1.8,-1.8,.1],[1.8,1.8,.1],[-1.4,1.8,.1],[-1.4,-1.8,.1]],C.teal,2,{dash:'7 7'});
 for(let x=-3.7;x<-.9;x+=.65)s.line([[x,-1.5,.12],[x,1.5,.12]],C.teal,2.4,{opacity:.65});
 arrow(s,[-3.6,0,.16],[-1,0,.16]);
 for(const r of [1.1,1.55,2])s.line(Array.from({length:30},(_,i)=>{const a=-1.1+i/29*2.2;return [.2+r*Math.cos(a),r*Math.sin(a),.13];}),C.teal,2.4,{opacity:.65});
}
{
 const s=add('04-straight-waveguide','GUIDED LIGHT','Straight silicon core in uniform silica cladding, with an input and a transverse output monitor. The finite display depth is conceptual.');
 s.slab(C.substrate);s.box(-3.8,-.42,3.8,.42,-.34,.25);
 arrow(s,[-3.5,0,.29],[3.5,0,.29]);
 s.face([[2.8,-1.2,-.34],[2.8,1.2,-.34],[2.8,1.2,1.25],[2.8,-1.2,1.25]],C.teal,.13,false);
 s.line([[2.8,-1.2,-.34],[2.8,1.2,-.34],[2.8,1.2,1.25],[2.8,-1.2,1.25],[2.8,-1.2,-.34]],C.teal,2,{dash:'7 6'});
}
{
 const s=add('05-waveguide-bend','90° WAVEGUIDE BEND','A sharp 90-degree dielectric waveguide bend. Light follows the L-shaped core; the short dashed arrow indicates possible bend radiation, not measured intensity.');
 s.plane();s.extrude([[-3.6,.6],[.75,.6],[.75,-2.6],[1.55,-2.6],[1.55,1.4],[-3.6,1.4]],0,.55);
 s.line([[-3.4,1,.61],[1.15,1,.61],[1.15,-2.5,.61]],C.gold,5,{arrow:true,overlay:true});
 s.line([[1.2,1.15,.64],[2.7,1.7,.64]],C.teal,2.5,{dash:'7 6',arrow:true,overlay:true});
}
{
 const s=add('06-binary-grating','DIFFRACTION ORDERS','Equal glass ridges on a glass substrate, invariant along the ridge direction. Incident light splits into schematic diffraction-order directions.');
 s.slab();for(let x=-3.5;x<3.4;x+=1)s.box(x,-1.75,x+.5,1.75,-.34,.45,C.blue);
 arrow(s,[0,0,-.9],[0,0,.35]);
 for(const dx of [-2.2,0,2.2])arrow(s,[0,0,.6],[dx,0,2.4],C.teal,4);
}
{
 const s=add('07-meta-atom','PHASE BY WIDTH','Four repeated silicon ridges of varying width and constant height on silica. These are invariant ridges, not finite nanopillars.');
 s.slab();const widths=[.28,.38,.66,.84];for(let i=0;i<8;i++){let x=-3.5+i*.95,w=widths[i%4];s.box(x,-1.7,x+w,1.7,-.34,.9);}
 for(let i=0;i<4;i++)arrow(s,[-2.6+i*1.4,0,1.05],[-1.6+i*1.4,0,2.5],C.teal,3.5);
}
{
 const s=add('08-metagrating-inverse','DESIGN A DIRECTION','Stored 73-by-1 optimized gray MaterialGrid density, shown as constant-height longitudinal strips. Arrows show a target direction, not a measured field.');
 s.slab();const d=densities('08');d.forEach((v,i)=>{const x=-3.65+i*7.3/d.length;s.box(x,-1.7,x+7.3/d.length,1.7,-.34,.9,mix('#edf3f6',C.blue,v));});
 arrow(s,[-.8,0,1.08],[1.4,0,2.7],C.teal,6);
}
{
 const s=add('09-bend-inverse','121 DESIGN VARIABLES','The original stored 11-by-11 gray density between fixed left input and upper output arms. Color encodes material interpolation, not structure height or a fabricated binary result.');
 s.slab();s.box(-3.8,-.38,-.88,.38,-.34,.28);s.box(-.38,-2.7,.38,-.88,-.34,.28);
 const d=densities('09'),h=1.76/11;for(let x=0;x<11;x++)for(let y=0;y<11;y++)s.box(-.88+x*h,-.88+(10-y)*h,-.88+(x+1)*h,-.88+(11-y)*h,-.34,.28,mix('#edf3f6',C.blue,d[x*11+y]));
 arrow(s,[-3.4,0,.35],[-1.13,0,.35]);arrow(s,[0,-1.08,.35],[0,-2.5,.35],C.teal);
 s.line([[-.9,-.9,.32],[.9,-.9,.32],[.9,.9,.32],[-.9,.9,.32],[-.9,-.9,.32]],C.teal,1.5,{dash:'5 5'});
}
{
 const s=add('10-dipole-pattern','DIPOLE ABOVE A MIRROR','A dipole parallel to a PEC mirror. Schematic wireframe radiation lobes explain spatial direction; these are not sampled Meep radiation data.','3D · CONCEPT VIEW');
 s.slab(C.metal,-.35,.2);
 for(let j=0;j<10;j++){
   const phi=j/10*2*Math.PI,ps=[];for(let i=0;i<=48;i++){const t=i/48*Math.PI;const r=1.9*Math.sin(t);ps.push([r*Math.cos(t),r*Math.sin(t)*Math.cos(phi),1.15+r*Math.sin(t)*Math.sin(phi)]);}
   s.line(ps.filter(p=>p[2]>-.3),C.teal,2,{opacity:.55});
 }
 s.line([[-.42,0,1.15],[.42,0,1.15]],C.gold,7,{overlay:true});s.source([0,0,1.15],8);arrow(s,[0,0,1.45],[0,0,2.8],C.teal,3);
}
{
 const s=add('11-cavity-ldos','A SOURCE BETWEEN MIRRORS','A parallel-plate PEC cavity with a dipole inside the dielectric gap. The upper mirror is cut away for visibility; wave arcs are conceptual.','PLANAR CAVITY · CONCEPT VIEW');
 s.scale=49; // Keep the raised upper mirror clear of the title and the image edge.
 s.slab(C.metal,-.45,.22);s.box(-4,-2.7,4,-.7,1.65,1.87,C.metal);
 s.face([[-4,-.7,1.65],[4,-.7,1.65],[4,2.7,1.65],[-4,2.7,1.65]],C.metal,.12,false);
 for(let z=-.4;z<1.7;z+=.35)s.line([[-4,2.7,z],[4,2.7,z]],C.boundary,1,{opacity:.3});
 s.source([0,.4,.55]);s.line([[-.45,.4,.55],[.45,.4,.55]],C.gold,7,{overlay:true});
 for(const r of [.6,1.2,1.8])s.line(circle(r,.58,0,.4),C.teal,2,{opacity:.65});
 s.line([[3.65,2.2,-.4],[3.65,2.2,1.65]],C.ink,2,{overlay:true});s.label('L',[3.65,2.2,.65],12,0);
}
{
 const s=add('12-ring-resonator','LIGHT AROUND A RING','An isolated dielectric annulus with no bus waveguide. A source lies in the ring near its inner edge; alternating arcs suggest a circulating resonant pattern.');
 s.plane();s.annulus(1.05,2.1,0,.65);
 for(let i=0;i<18;i++){const a=i/18*Math.PI*2;s.line(Array.from({length:5},(_,j)=>{const t=a+j/4*.18;return [1.58*Math.cos(t),1.58*Math.sin(t),.69];}),i%2?C.teal:C.gold,5,{opacity:.8});}
 s.source([1.18,0,.71],7);
 s.line(Array.from({length:24},(_,i)=>{const a=1+i/23*.9;return [1.58*Math.cos(a),1.58*Math.sin(a),.73];}),C.teal,3,{arrow:true,overlay:true});
}
{
 const s=add('13-cylindrical-dipole','ROTATIONAL SYMMETRY','A finite dielectric disc above a PEC plane, with vertical symmetry axis and a radial-z computational half-plane. Source marks an azimuthal harmonic, not a complete off-axis point dipole.','CYLINDRICAL · CONCEPT VIEW');
 s.slab(C.metal,-.35,.2);s.annulus(0,1.9,-.34,.65);
 s.face([[0,0,-.34],[2.4,0,-.34],[2.4,0,2.25],[0,0,2.25]],C.teal,.1,false);
 s.line([[0,0,-.35],[0,0,2.6]],C.ink,2,{dash:'7 7',overlay:true});
 s.line([[0,0,2.1],[2.3,0,2.1]],C.teal,3,{arrow:true,overlay:true});
 s.line(Array.from({length:40},(_,i)=>{const t=-.2+i/39*4.8;return [2.25*Math.cos(t),2.25*Math.sin(t),.75];}),C.teal,3,{arrow:true,overlay:true});
 s.source([.95,0,.7],8);s.label('r–z',[2.3,0,2.1],0,-18);
}
{
 const s=add('14-extraction-efficiency','LIGHT OUT OF A THIN FILM','A cropped infinite dielectric thin film on PEC, containing a horizontal dipole. Upward arrows escape into air, lateral arrows stay guided. No numerical efficiency is encoded.','THIN FILM · CONCEPT VIEW');
 s.slab(C.metal,-.5,.18);s.box(-4,-2.7,4,2.7,-.49,.18,C.blue);
 s.source([0,0,.04],9);s.line([[-.42,0,.04],[.42,0,.04]],C.gold,6,{overlay:true});
 for(const dx of [-1.25,0,1.25])arrow(s,[0,0,.25],[dx,0,2.45],C.teal,4);
 arrow(s,[.35,0,.09],[3.55,0,.09],C.gold,4);arrow(s,[-.35,0,.09],[-3.55,0,.09],C.gold,4);
 s.line([[-3.6,-2.4,2.6],[3.6,-2.4,2.6],[3.6,2.4,2.6]],C.teal,2,{dash:'7 7',opacity:.6});
}

fs.mkdirSync(out,{recursive:true});
for(const scene of scenes)fs.writeFileSync(path.join(out,scene.id+'.svg'),scene.render());
console.log(`Generated ${scenes.length} original spatial thumbnails in assets/thumbnails`);
