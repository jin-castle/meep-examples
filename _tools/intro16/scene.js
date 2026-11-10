// Saved cylindrical Er(z,r), m=-1. All displayed axial coordinates are magnified 8x.
import * as THREE from 'three';
const metadata = await (await fetch('field.json')).json();
const bytes = new Uint8Array(await (await fetch('field.bin')).arrayBuffer());
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, innerWidth / innerHeight, .1, 1000);
const renderer = new THREE.WebGLRenderer({canvas:document.querySelector('canvas'),antialias:true,alpha:true});
renderer.setPixelRatio(1);renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0,0);renderer.outputColorSpace=THREE.SRGBColorSpace;
scene.add(new THREE.HemisphereLight(0xffffff,0x7799aa,2));
const light=new THREE.DirectionalLight(0xffffff,2.0);light.position.set(-80,130,60);scene.add(light);
const fill=new THREE.DirectionalLight(0xc3ecff,.9);fill.position.set(80,60,-40);scene.add(fill);
const radius=metadata.extent[1], axial=metadata.display.axial_magnification;

// A reference grid; it is not an extra material in the simulation.
const ground=new THREE.Mesh(new THREE.CircleGeometry(58,192),new THREE.MeshBasicMaterial({color:0xafd9e9,transparent:true,opacity:.15,depthWrite:false,side:THREE.DoubleSide}));
ground.rotation.x=-Math.PI/2;ground.position.y=-18.6;scene.add(ground);
const grid=[];
for(let q=-56;q<=56;q+=8){const edge=Math.sqrt(58*58-q*q);grid.push(new THREE.Vector3(q,-18.5,-edge),new THREE.Vector3(q,-18.5,edge),new THREE.Vector3(-edge,-18.5,q),new THREE.Vector3(edge,-18.5,q));}
scene.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(grid),new THREE.LineBasicMaterial({color:0x6ca8bf,transparent:true,opacity:.22})));

const substrate=new THREE.Mesh(new THREE.CylinderGeometry(radius,radius,16,192),new THREE.MeshPhysicalMaterial({color:0x6fc4df,transparent:true,opacity:.18,depthWrite:false,roughness:.32,metalness:0,clearcoat:.4}));
substrate.position.y=-10;substrate.renderOrder=1;scene.add(substrate);
function circle(r,y,color,opacity){const pts=[];for(let i=0;i<=192;i++){const p=i/192*Math.PI*2;pts.push(new THREE.Vector3(r*Math.cos(p),y,r*Math.sin(p)));}return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color,transparent:true,opacity}));}
scene.add(circle(radius,-18,0xb99645,.4),circle(radius,-2,0x2188a7,.45));
// Concentric binary-phase relief: glass on even zero-based zones, air on odd ones.
function annulus(inner,outer,bottom,top){
  const positions=[];
  const quad=(a,b,c,d)=>positions.push(...a,...b,...c,...a,...c,...d);
  for(let i=0;i<192;i++){
    const a=i/192*2*Math.PI,b=(i+1)/192*2*Math.PI;
    const pt=(r,y,p)=>[r*Math.cos(p),y,r*Math.sin(p)];
    quad(pt(inner,top,a),pt(inner,top,b),pt(outer,top,b),pt(outer,top,a));
    quad(pt(inner,bottom,b),pt(inner,bottom,a),pt(outer,bottom,a),pt(outer,bottom,b));
    quad(pt(outer,bottom,a),pt(outer,top,a),pt(outer,top,b),pt(outer,bottom,b));
    if(inner>0)quad(pt(inner,bottom,b),pt(inner,top,b),pt(inner,top,a),pt(inner,bottom,a));
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.computeVertexNormals();return g;
}
for(let i=0;i<25;i+=2){
  const outer=metadata.zone_radii_um[i],inner=i?metadata.zone_radii_um[i-1]:0;
  const ring=new THREE.Mesh(annulus(inner,outer,-2,2),new THREE.MeshPhysicalMaterial({color:0x65b9d7,transparent:true,opacity:.38,depthWrite:false,roughness:.32,metalness:0,clearcoat:.4,side:THREE.DoubleSide}));
  ring.renderOrder=1;scene.add(ring,circle(outer,2,0x267b97,.48));if(inner)scene.add(circle(inner,2,0x267b97,.38));
}

const texture=new THREE.DataTexture(bytes,metadata.nx,metadata.ny,THREE.RGBAFormat,THREE.UnsignedByteType);
texture.minFilter=texture.magFilter=THREE.LinearFilter;texture.unpackAlignment=1;texture.needsUpdate=true;
const colors=['#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061'];
const material=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.BackSide,
 uniforms:{field:{value:texture},phase:{value:0},radius:{value:radius},axial:{value:axial},lo:{value:new THREE.Vector3(-radius,-18,-radius)},hi:{value:new THREE.Vector3(radius,18,radius)},map:{value:colors.map(c=>new THREE.Color(c))}},
 vertexShader:`varying vec3 pointWorld;void main(){vec4 p=modelMatrix*vec4(position,1.);pointWorld=p.xyz;gl_Position=projectionMatrix*viewMatrix*p;}`,
 fragmentShader:`precision highp float;uniform sampler2D field;uniform float phase,radius,axial;uniform vec3 lo,hi,map[11];varying vec3 pointWorld;
 void main(){vec3 origin=cameraPosition,dir=normalize(pointWorld-origin);vec3 t0=(lo-origin)/dir,t1=(hi-origin)/dir;vec3 n=min(t0,t1),f=max(t0,t1);float a=max(max(max(n.x,n.y),n.z),0.),b=min(min(f.x,f.y),f.z);if(b<=a)discard;
 float ds=(b-a)/168.;vec3 rgb=vec3(0.);float alpha=0.;
 for(int k=0;k<168;k++){
  vec3 p=origin+dir*(a+(float(k)+.5)*ds);float r=length(p.xz);if(r>radius)continue;
  vec2 uv=vec2(r/radius,(p.y/axial+2.25)/4.5);vec2 v=texture2D(field,uv).rg*2.-1.;if(length(v)<.012)continue;
  float angle=-atan(p.z,p.x)-phase;float e=v.x*cos(angle)-v.y*sin(angle);
  float c=(clamp(e*3.,-1.,1.)+1.)*5.;int idx=int(min(floor(c),9.));vec3 color=mix(map[idx],map[idx+1],c-float(idx));
  float opacity=1.-exp(-.35*pow(abs(e),1.3)*ds);rgb+=(1.-alpha)*opacity*color;alpha+=(1.-alpha)*opacity;if(alpha>.985)break;
 }
 if(alpha<.003)discard;gl_FragColor=vec4(rgb/max(alpha,.0001),alpha);
 #include <colorspace_fragment>
 }`,});
const volume=new THREE.Mesh(new THREE.BoxGeometry(radius*2,36,radius*2),material);volume.renderOrder=2;scene.add(volume);

let frozen=new URLSearchParams(location.search).has('t');let current=Number(new URLSearchParams(location.search).get('t')||0);
const fixedCamera=new URLSearchParams(location.search).get('camera')==='fixed';
function setTime(t){current=t;const tau=((t%8)+8)%8,p=2*Math.PI*tau/8;material.uniforms.phase.value=2*p;
 const cp=fixedCamera?0:p;
 const az=.65+.045*Math.sin(cp),el=.57+.025*Math.cos(cp),distance=195-3*(1-Math.cos(cp));
 camera.position.set(distance*Math.cos(el)*Math.sin(az),distance*Math.sin(el),distance*Math.cos(el)*Math.cos(az));camera.lookAt(0,-3,0);renderer.render(scene,camera);}
window.__hero={setTime,play(){frozen=false;},camera,metadata};
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);setTime(current);});
const start=performance.now();function animate(now){if(!frozen)setTime((now-start)/1000);requestAnimationFrame(animate);}setTime(current);requestAnimationFrame(animate);
