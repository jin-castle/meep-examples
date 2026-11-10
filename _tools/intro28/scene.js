// Actual saved Ey(x,y) DFT field, analytically extended along Meep's Bloch z axis.
// World coordinates equal simulation coordinates; the grid and rods share x/z axes.
import * as THREE from 'three';

const metadata = await (await fetch('field.json')).json();
const bytes = new Uint8Array(await (await fetch('field.bin')).arrayBuffer());
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, innerWidth / innerHeight, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ canvas: document.querySelector('canvas'), antialias: true, alpha: true });
renderer.setPixelRatio(1);
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
scene.add(new THREE.HemisphereLight(0xffffff, 0x7799aa, 2.1));
const key = new THREE.DirectionalLight(0xffffff, 2.0);
key.position.set(-4, 9, 3); scene.add(key);
const fill = new THREE.DirectionalLight(0xd9f5ff, 1.0);
fill.position.set(5, 3, -6); scene.add(fill);

// A single horizontal reference plane. It is not a physical substrate.
const ground = new THREE.Mesh(new THREE.PlaneGeometry(5.3, 10.7), new THREE.MeshBasicMaterial({ color: 0xafd9e9, transparent: true, opacity: 0.18, depthWrite: false, side: THREE.DoubleSide }));
ground.rotation.x = -Math.PI / 2; ground.position.y = -0.525; scene.add(ground);
const gridPoints = [];
for (let x = -2.5; x <= 2.5; x += .5) gridPoints.push(new THREE.Vector3(x, -.518, -5.25), new THREE.Vector3(x, -.518, 5.25));
for (let z = -5.25; z <= 5.25; z += .75) gridPoints.push(new THREE.Vector3(-2.5, -.518, z), new THREE.Vector3(2.5, -.518, z));
const grid = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(gridPoints), new THREE.LineBasicMaterial({ color: 0x6ca8bf, transparent: true, opacity: .26 }));
scene.add(grid);

for (const x of [-.75, .75]) {
  const box = new THREE.BoxGeometry(1, 1, 9);
  const rod = new THREE.Mesh(box, new THREE.MeshPhysicalMaterial({ color: 0xf0b23e, roughness: .38, metalness: .02, clearcoat: .35, transparent: true, opacity: .46, depthWrite: false, side: THREE.DoubleSide }));
  rod.position.x = x; rod.renderOrder = 1; scene.add(rod);
  const edge = new THREE.LineSegments(new THREE.EdgesGeometry(box), new THREE.LineBasicMaterial({ color: 0x9e732c, transparent: true, opacity: .47 }));
  edge.position.copy(rod.position); edge.renderOrder = 3; scene.add(edge);
}

const texture = new THREE.DataTexture(bytes, metadata.nx, metadata.ny, THREE.RGBAFormat, THREE.UnsignedByteType);
texture.minFilter = texture.magFilter = THREE.LinearFilter;
texture.unpackAlignment = 1; texture.needsUpdate = true;
const colors = ['#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061'];
const material = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, side: THREE.BackSide,
  uniforms: { field: { value: texture }, phase: { value: 0 }, kz: { value: metadata.kz },
    lo: { value: new THREE.Vector3(-1.85, -.49, -4.495) }, hi: { value: new THREE.Vector3(1.85, .9, 4.495) },
    extent: { value: new THREE.Vector4(...metadata.extent) },
    map: { value: colors.map(c => new THREE.Color(c)) } },
  vertexShader: `varying vec3 pointWorld;
    void main(){vec4 p=modelMatrix*vec4(position,1.);pointWorld=p.xyz;gl_Position=projectionMatrix*viewMatrix*p;}`,
  fragmentShader: `precision highp float;
    uniform sampler2D field;uniform float phase,kz;uniform vec3 lo,hi,map[11];uniform vec4 extent;varying vec3 pointWorld;
    void main(){
      vec3 origin=cameraPosition,dir=normalize(pointWorld-origin);
      vec3 t0=(lo-origin)/dir,t1=(hi-origin)/dir;
      vec3 nearT=min(t0,t1),farT=max(t0,t1);
      float enter=max(max(max(nearT.x,nearT.y),nearT.z),0.);
      float leave=min(min(farT.x,farT.y),farT.z);if(leave<=enter)discard;
      float stepSize=(leave-enter)/112.;vec3 rgb=vec3(0.);float alpha=0.;
      for(int k=0;k<112;k++){
        vec3 p=origin+dir*(enter+(float(k)+.5)*stepSize);
        vec2 uv=vec2((p.x-extent.x)/(extent.y-extent.x),(p.y-extent.z)/(extent.w-extent.z));
        vec2 value=texture2D(field,uv).rg*2.-1.;
        float angle=6.28318530718*kz*p.z-phase;
        float f=value.x*cos(angle)-value.y*sin(angle);
        float magnitude=length(value);if(magnitude<.012)continue;
        float signedColor=clamp(f*1.25,-1.,1.);
        float c=(signedColor+1.)*5.;int idx=int(min(floor(c),9.));
        vec3 color=mix(map[idx],map[idx+1],c-float(idx));
        float opacity=1.-exp(-3.8*pow(abs(f),1.3)*stepSize);
        rgb+=(1.-alpha)*opacity*color;alpha+=(1.-alpha)*opacity;if(alpha>.985)break;
      }
      if(alpha<.003)discard;gl_FragColor=vec4(rgb/max(alpha,.0001),alpha);
      #include <colorspace_fragment>
    }`,
});
const volume = new THREE.Mesh(new THREE.BoxGeometry(3.7, 1.39, 8.99), material);
volume.position.y = .205; volume.renderOrder = 2; scene.add(volume);

let frozen = new URLSearchParams(location.search).has('t');
let current = Number(new URLSearchParams(location.search).get('t') || 0);
function setTime(t) {
  current = t;
  const tau = ((t % 8) + 8) % 8;
  const phase = 2 * Math.PI * tau / 8;
  material.uniforms.phase.value = phase * 2;
  const azimuth = .90 + .035 * Math.sin(phase), elevation = .59 + .025 * Math.cos(phase);
  const distance = 15.8 - .20 * (1 - Math.cos(phase));
  camera.position.set(distance*Math.cos(elevation)*Math.sin(azimuth),distance*Math.sin(elevation),distance*Math.cos(elevation)*Math.cos(azimuth));
  camera.lookAt(0, -.3, 0); renderer.render(scene, camera);
}
window.__hero = { setTime, play(){ frozen=false; }, camera, metadata };
window.addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);setTime(current);});
const start = performance.now();
function animate(now){if(!frozen)setTime((now-start)/1000);requestAnimationFrame(animate);}
setTime(current);requestAnimationFrame(animate);
