import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const canvas = document.getElementById('nerve-canvas');
if (!canvas) throw new Error('No #nerve-canvas found');

const infoEl = document.getElementById('viewer-info');

const geomData = await fetch('data/nerve-geometry.json').then(r => r.json());

// Scale: μm → scene units (1 unit = 1 mm)
const S = 1 / 1000;

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f1a0f);

const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
camera.position.set(0, 4, 10);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(canvas.clientWidth, canvas.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = false;
controls.minDistance = 5;
controls.maxDistance = 20;
controls.target.set(0, 0, 0);

// Lighting
scene.add(new THREE.AmbientLight(0x404060, 2));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);
const backLight = new THREE.DirectionalLight(0x3a7d44, 0.5);
backLight.position.set(-3, -3, -5);
scene.add(backLight);

// All nerve geometry goes in one group so auto-rotation stays in sync
const nerveGroup = new THREE.Group();
scene.add(nerveGroup);

const nerveDepth = 3;
const { semi_major, semi_minor } = geomData.nerve;
const smaj = semi_major * S;
const smin = semi_minor * S;

// --- Nerve boundary (transparent extruded ellipse) ---
const boundaryShape = new THREE.Shape();
for (let i = 0; i <= 64; i++) {
  const angle = (i / 64) * Math.PI * 2;
  const x = smaj * Math.cos(angle);
  const y = smin * Math.sin(angle);
  if (i === 0) boundaryShape.moveTo(x, y);
  else boundaryShape.lineTo(x, y);
}

const boundaryGeom = new THREE.ExtrudeGeometry(boundaryShape, { depth: nerveDepth, bevelEnabled: false });
boundaryGeom.center();
const boundaryMesh = new THREE.Mesh(boundaryGeom, new THREE.MeshPhysicalMaterial({
  color: 0x8888cc,
  transparent: true,
  opacity: 0.08,
  roughness: 0.3,
  side: THREE.DoubleSide,
  depthWrite: false,
}));
boundaryMesh.rotation.x = Math.PI / 2;
nerveGroup.add(boundaryMesh);

// Boundary wireframe rings at each end
const ringMat = new THREE.LineBasicMaterial({ color: 0x6666aa, transparent: true, opacity: 0.4 });
for (const yOff of [-nerveDepth / 2, nerveDepth / 2]) {
  const pts = [];
  for (let i = 0; i <= 64; i++) {
    const a = (i / 64) * Math.PI * 2;
    pts.push(new THREE.Vector3(smaj * Math.cos(a), yOff, smin * Math.sin(a)));
  }
  nerveGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), ringMat));
}

// --- Fascicles (cylinders) ---
const fascicleObjects = [];
const fascMat = new THREE.MeshPhysicalMaterial({
  color: 0x4a9eff,
  roughness: 0.4,
  metalness: 0.1,
  clearcoat: 0.3,
});

for (const f of geomData.fascicles) {
  const r = f.radius * S;
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(r, r, nerveDepth, 32),
    fascMat.clone()
  );
  mesh.position.set(f.cx * S, 0, f.cy * S);
  mesh.userData = { type: 'fascicle', id: f.id, radius: f.radius, cx: f.cx, cy: f.cy };
  nerveGroup.add(mesh);
  fascicleObjects.push(mesh);
}

// --- Electrodes (spheres with glow) ---
const electrodeObjects = [];

for (const e of geomData.electrodes) {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.15, 16, 16),
    new THREE.MeshPhysicalMaterial({
      color: 0xff6b35,
      roughness: 0.2,
      metalness: 0.8,
      emissive: new THREE.Color(0xff6b35),
      emissiveIntensity: 0.3,
    })
  );
  mesh.position.set(e.x * S, 0, e.y * S);
  mesh.userData = { type: 'electrode', id: e.id, x: e.x, y: e.y };

  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    color: 0xff6b35,
    transparent: true,
    opacity: 0.2,
    blending: THREE.AdditiveBlending,
  }));
  sprite.scale.set(0.6, 0.6, 1);
  mesh.add(sprite);

  nerveGroup.add(mesh);
  electrodeObjects.push(mesh);
}

// Electrode ring wire
const ringElPts = geomData.electrodes.map(e => new THREE.Vector3(e.x * S, 0, e.y * S));
ringElPts.push(ringElPts[0].clone());
nerveGroup.add(new THREE.Line(
  new THREE.BufferGeometry().setFromPoints(ringElPts),
  new THREE.LineBasicMaterial({ color: 0xff6b35, transparent: true, opacity: 0.2 })
));

// --- Labels (each gets its own canvas to avoid shared texture) ---
function makeLabel(text) {
  const c = document.createElement('canvas');
  c.width = 64;
  c.height = 64;
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#e8e8f0';
  ctx.font = 'bold 36px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 32, 32);
  const tex = new THREE.CanvasTexture(c);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
  sprite.scale.set(0.3, 0.3, 1);
  return sprite;
}

for (const f of geomData.fascicles) {
  const label = makeLabel(String(f.id));
  label.position.set(f.cx * S, nerveDepth / 2 + 0.3, f.cy * S);
  nerveGroup.add(label);
}
for (const e of geomData.electrodes) {
  const label = makeLabel('E' + e.id);
  label.position.set(e.x * S, nerveDepth / 2 + 0.3, e.y * S);
  nerveGroup.add(label);
}

// --- Interaction ---
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let isDragging = false;

canvas.addEventListener('mousemove', (ev) => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
});
canvas.addEventListener('pointerdown', () => isDragging = true);
canvas.addEventListener('pointerup', () => isDragging = false);

function resetHighlights() {
  for (const m of fascicleObjects) {
    m.material.emissive.setHex(0x000000);
    m.material.emissiveIntensity = 0;
  }
  for (const m of electrodeObjects) {
    m.material.emissiveIntensity = 0.3;
  }
}

// --- Animate ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();

  if (!isDragging) {
    nerveGroup.rotation.y += 0.002;
  }

  // Hover detection
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects([...fascicleObjects, ...electrodeObjects]);
  resetHighlights();

  if (hits.length > 0) {
    const obj = hits[0].object;
    const d = obj.userData;
    if (d.type === 'fascicle') {
      obj.material.emissive.setHex(0x4a9eff);
      obj.material.emissiveIntensity = 0.5;
      infoEl.innerHTML = `<strong>Fascicle ${d.id}</strong> — radius: ${d.radius.toFixed(0)} μm — position: (${d.cx.toFixed(0)}, ${d.cy.toFixed(0)}) μm`;
    } else if (d.type === 'electrode') {
      obj.material.emissiveIntensity = 1.0;
      infoEl.innerHTML = `<strong>Electrode E${d.id}</strong> — position: (${d.x.toFixed(0)}, ${d.y.toFixed(0)}) μm`;
    }
  } else {
    infoEl.innerHTML = 'Hover over structures for details';
  }

  renderer.render(scene, camera);
}

// Responsive
const ro = new ResizeObserver(() => {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
});
ro.observe(canvas);

animate();
