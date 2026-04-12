import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const canvas = document.getElementById('nerve-canvas');
if (!canvas) throw new Error('No #nerve-canvas found');
const infoEl = document.getElementById('viewer-info');

const data = await fetch('data/nerve-geometry.json').then(r => r.json());

// --- Constants ---
const S = 1 / 1000; // μm → mm (scene units)
const RHO = data.tissue_resistivity;
const NERVE_DEPTH = 2.5;
const smaj = data.nerve.semi_major * S;
const smin = data.nerve.semi_minor * S;

// --- Presets ---
const PRESETS = {
  bipolar:  { label: 'Bipolar E1↔E5',       electrodes: { 1: 1, 5: -1 } },
  tripolar: { label: 'Tripolar E8·E1·E2',   electrodes: { 1: 1, 8: -1, 2: -1 } },
  steering: { label: 'Steer E1+E2↔E5+E6',   electrodes: { 1: 1, 2: 1, 5: -1, 6: -1 } },
  custom:   { label: 'Custom',               electrodes: null },
};

// --- Scene ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f1a0f);

const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
camera.position.set(0, 6, 12);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(canvas.clientWidth, canvas.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = false;
controls.minDistance = 4;
controls.maxDistance = 25;

scene.add(new THREE.AmbientLight(0x405040, 2.5));
const dir1 = new THREE.DirectionalLight(0xffffff, 1.5);
dir1.position.set(5, 8, 5);
scene.add(dir1);
const dir2 = new THREE.DirectionalLight(0x3a7d44, 0.6);
dir2.position.set(-4, -3, -5);
scene.add(dir2);

const nerveGroup = new THREE.Group();
scene.add(nerveGroup);

// --- State ---
let activeElectrodes = new Map();
let currentAmplitude = 0.15; // start in Aα dynamic range
let electrodeMode = 'cathode';
let currentPreset = null; // not set until user interacts
let fiberTypeIdx = 0;
const fiberTypes = ['Aalpha', 'B', 'C'];
const fiberLabels = ['Aα motor', 'B autonomic', 'C unmyelin.'];

// Compute dynamic range for current electrode config + fiber type
// Returns { min, max } in mA — the amplitude at which first/full recruitment occurs
function computeDynamicRange() {
  const activeList = [...activeElectrodes.entries()];
  if (activeList.length === 0) return { min: 0, max: 1 };

  const threshold = data.fiber_thresholds_mA[fiberTypes[fiberTypeIdx]];
  const nominalDist = 2.5e-3;
  const E_threshold = (RHO * threshold * 1e-3) / (4 * Math.PI * nominalDist * nominalDist);

  let firstAmp = null, fullAmp = null;
  const SWEEP_STEPS = 200;
  const MAX_AMP = 5; // mA

  for (let i = 1; i <= SWEEP_STEPS; i++) {
    const amp = (i / SWEEP_STEPS) * MAX_AMP;
    let recruited = 0;
    for (const f of data.fascicles) {
      let Ey = 0, Ez = 0;
      for (const [eId, weight] of activeList) {
        const el = data.electrodes.find(e => e.id === eId);
        const dy = (f.y - el.y) * 1e-6;
        const dz = (f.z - el.z) * 1e-6;
        const r2 = dy * dy + dz * dz;
        const r = Math.sqrt(r2);
        const r3 = Math.max(r * r2, 1e-18);
        const coeff = (RHO * amp * 1e-3 * weight) / (4 * Math.PI * r3);
        Ey += coeff * dy;
        Ez += coeff * dz;
      }
      if (Math.sqrt(Ey * Ey + Ez * Ez) >= E_threshold) recruited++;
    }
    if (recruited > 0 && firstAmp === null) firstAmp = amp;
    if (recruited === data.fascicles.length && fullAmp === null) { fullAmp = amp; break; }
  }

  return {
    min: firstAmp || 0,
    max: fullAmp ? fullAmp * 1.15 : MAX_AMP, // 15% headroom past full recruitment
  };
}

let currentDR = { min: 0, max: 1 }; // updated by onUpdate
let hasInteracted = false;
let isDistantReturn = false;
let hoveredFascicle = null;

// --- Nerve boundary ---
const boundaryShape = new THREE.Shape();
for (let i = 0; i <= 128; i++) {
  const a = (i / 128) * Math.PI * 2;
  const x = smaj * Math.cos(a), y = smin * Math.sin(a);
  i === 0 ? boundaryShape.moveTo(x, y) : boundaryShape.lineTo(x, y);
}
const boundaryGeom = new THREE.ExtrudeGeometry(boundaryShape, { depth: NERVE_DEPTH, bevelEnabled: false });
boundaryGeom.center();
const boundaryMesh = new THREE.Mesh(boundaryGeom, new THREE.MeshPhysicalMaterial({
  color: 0x88aa88, transparent: true, opacity: 0.06,
  roughness: 0.3, side: THREE.DoubleSide, depthWrite: false,
}));
boundaryMesh.rotation.x = Math.PI / 2;
nerveGroup.add(boundaryMesh);

const ringMat = new THREE.LineBasicMaterial({ color: 0x5a8a5a, transparent: true, opacity: 0.35 });
for (const yOff of [-NERVE_DEPTH / 2, NERVE_DEPTH / 2]) {
  const pts = [];
  for (let i = 0; i <= 128; i++) {
    const a = (i / 128) * Math.PI * 2;
    pts.push(new THREE.Vector3(smaj * Math.cos(a), yOff, smin * Math.sin(a)));
  }
  nerveGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), ringMat));
}

// --- Electric field texture ---
const FIELD_RES = 128;
const fieldCanvas = document.createElement('canvas');
fieldCanvas.width = FIELD_RES;
fieldCanvas.height = FIELD_RES;
const fieldCtx = fieldCanvas.getContext('2d');
const fieldTexture = new THREE.CanvasTexture(fieldCanvas);
fieldTexture.minFilter = THREE.LinearFilter;

const fieldPlane = new THREE.Mesh(
  new THREE.PlaneGeometry(smaj * 2.4, smin * 2.4),
  new THREE.MeshBasicMaterial({
    map: fieldTexture, transparent: true, opacity: 0.6,
    side: THREE.DoubleSide, depthWrite: false,
  })
);
fieldPlane.rotation.x = -Math.PI / 2;
fieldPlane.position.y = -NERVE_DEPTH / 2 - 0.01;
nerveGroup.add(fieldPlane);

function computeField() {
  const imgData = fieldCtx.createImageData(FIELD_RES, FIELD_RES);
  const activeList = [...activeElectrodes.entries()];

  if (activeList.length === 0) {
    fieldCtx.clearRect(0, 0, FIELD_RES, FIELD_RES);
    fieldTexture.needsUpdate = true;
    return;
  }

  // Heatmap shows |E| (electric field magnitude), not V.
  // |E| is the correct proxy for activation in biphasic stimulation:
  // strongest between electrodes where gradients add constructively.
  let maxE = 0;
  const vals = new Float32Array(FIELD_RES * FIELD_RES);

  for (let py = 0; py < FIELD_RES; py++) {
    for (let px = 0; px < FIELD_RES; px++) {
      const y_um = ((px / FIELD_RES) - 0.5) * smaj * 2.4 * 1000;
      const z_um = ((py / FIELD_RES) - 0.5) * smin * 2.4 * 1000;
      const normY = y_um / data.nerve.semi_major;
      const normZ = z_um / data.nerve.semi_minor;
      if (normY * normY + normZ * normZ > 1.3) continue;

      const [Ey, Ez] = eField(y_um, z_um, activeList);
      const eMag = Math.sqrt(Ey * Ey + Ez * Ez);
      vals[py * FIELD_RES + px] = eMag;
      if (eMag > maxE) maxE = eMag;
    }
  }

  for (let i = 0; i < vals.length; i++) {
    const t = maxE > 0 ? Math.min(vals[i] / maxE, 1) : 0;
    const idx = i * 4;
    // Single colormap: dark green → bright green-white (field strength)
    imgData.data[idx] = Math.floor(30 + t * 225);
    imgData.data[idx + 1] = Math.floor(80 + t * 175);
    imgData.data[idx + 2] = Math.floor(40 + t * 130);
    imgData.data[idx + 3] = Math.floor(t * t * 200);
  }

  fieldCtx.putImageData(imgData, 0, 0);
  fieldTexture.needsUpdate = true;
}

// --- Streamlines ---
const streamlineGroup = new THREE.Group();
nerveGroup.add(streamlineGroup);

// Analytical E-field: E = -∇V
// E_y = Σ  ρ·I·w·(y - ye) / (4π·r³)   (points away from cathode for w=+1)
// E_z = Σ  ρ·I·w·(z - ze) / (4π·r³)
function eField(y_um, z_um, activeList) {
  let Ey = 0, Ez = 0;
  for (const [eId, weight] of activeList) {
    const el = data.electrodes.find(e => e.id === eId);
    const dy = (y_um - el.y) * 1e-6;
    const dz = (z_um - el.z) * 1e-6;
    const r2 = dy * dy + dz * dz;
    const r = Math.sqrt(r2);
    const r3 = Math.max(r * r2, 1e-18);
    const coeff = (RHO * currentAmplitude * 1e-3 * weight) / (4 * Math.PI * r3);
    Ey += coeff * dy;
    Ez += coeff * dz;
  }
  return [Ey, Ez];
}

function computeStreamlines() {
  // Clear old
  while (streamlineGroup.children.length > 0) {
    const c = streamlineGroup.children[0];
    c.geometry?.dispose();
    c.material?.dispose();
    streamlineGroup.remove(c);
  }

  const activeList = [...activeElectrodes.entries()];
  if (activeList.length === 0) return;

  const cathodes = activeList.filter(([, w]) => w > 0);
  const anodes = activeList.filter(([, w]) => w < 0);

  // Line count scales with amplitude relative to current dynamic range
  const ampFrac = currentDR.max > 0 ? Math.min(currentAmplitude / currentDR.max, 1) : 0;
  const SEED_COUNT = Math.max(4, Math.floor(4 + ampFrac * 12));
  const STEP = 40; // μm per integration step
  const MAX_STEPS = 250;
  const ANODE_STOP_DIST = 250; // μm — stop near anode
  const BOUNDARY_MARGIN = 1.15;

  // Anode positions in μm for stop detection
  const anodePositions = anodes.map(([eId]) => {
    const el = data.electrodes.find(e => e.id === eId);
    return [el.y, el.z];
  });

  // Seed streamlines across the nerve cross-section, perpendicular to the
  // cathode-anode axis. This shows current spreading through the tissue.
  // For each cathode, place seeds along a line through the nerve center,
  // perpendicular to the cathode→anode direction.
  for (const [catId] of cathodes) {
    const catEl = data.electrodes.find(e => e.id === catId);

    // Direction from cathode toward center (or toward anode centroid)
    let targetY = 0, targetZ = 0;
    if (anodes.length > 0) {
      for (const [aId] of anodes) {
        const ae = data.electrodes.find(e => e.id === aId);
        targetY += ae.y; targetZ += ae.z;
      }
      targetY /= anodes.length; targetZ /= anodes.length;
    }

    // Perpendicular to cathode→target axis
    const axisY = targetY - catEl.y;
    const axisZ = targetZ - catEl.z;
    const axisLen = Math.sqrt(axisY * axisY + axisZ * axisZ);
    // Perpendicular direction (rotated 90°)
    const perpY = -axisZ / axisLen;
    const perpZ = axisY / axisLen;

    // Seed from multiple rows at different depths from cathode toward center.
    // Each row is a perpendicular line; deeper rows get fewer seeds.
    const seedRows = [
      { depth: 0.55, count: Math.ceil(SEED_COUNT * 0.5) },   // near cathode
      { depth: 0.30, count: Math.ceil(SEED_COUNT * 0.35) },  // mid
      { depth: 0.08, count: Math.ceil(SEED_COUNT * 0.25) },  // near center
    ];

    for (const row of seedRows) {
      const seedLineY = catEl.y * row.depth;
      const seedLineZ = catEl.z * row.depth;
      // Spread wider for deeper rows (they're further from boundary)
      const spread = data.nerve.semi_minor * (0.5 + row.depth * 0.5);

      for (let s = 0; s < row.count; s++) {
        const t = row.count > 1 ? (s / (row.count - 1)) * 2 - 1 : 0;
        let py = seedLineY + perpY * t * spread;
        let pz = seedLineZ + perpZ * t * spread;

        // Skip if outside boundary
        const ny = py / data.nerve.semi_major;
        const nz = pz / data.nerve.semi_minor;
        if (ny * ny + nz * nz > 0.95) continue;

      const points = [];
      const colors = [];

      for (let step = 0; step < MAX_STEPS; step++) {
        // Inside boundary check (with margin)
        const ny = py / data.nerve.semi_major;
        const nz = pz / data.nerve.semi_minor;
        if (ny * ny + nz * nz > BOUNDARY_MARGIN * BOUNDARY_MARGIN) break;

        points.push(new THREE.Vector3(py * S, 0, pz * S));

        // Color: red near cathode → blue near anode, based on step fraction
        const t = step / MAX_STEPS;
        if (anodes.length > 0) {
          colors.push(1 - t * 0.7, 0.25 + t * 0.15, 0.25 + t * 0.75);
        } else {
          // Monopolar: red fading to dim
          colors.push(1 - t * 0.6, 0.3 - t * 0.15, 0.2);
        }

        // Near anode? stop
        let nearAnode = false;
        for (const [ay, az] of anodePositions) {
          const d = Math.sqrt((py - ay) ** 2 + (pz - az) ** 2);
          if (d < ANODE_STOP_DIST) { nearAnode = true; break; }
        }
        if (nearAnode) {
          // Add final point at anode
          const closest = anodePositions.reduce((best, [ay, az]) => {
            const d = Math.sqrt((py - ay) ** 2 + (pz - az) ** 2);
            return d < best.d ? { d, y: ay, z: az } : best;
          }, { d: Infinity, y: 0, z: 0 });
          points.push(new THREE.Vector3(closest.y * S, 0, closest.z * S));
          colors.push(0.3, 0.4, 1.0);
          break;
        }

        // eField() returns E = -∇V. With cathode weight=+1, E points
        // away from cathode toward anode. Follow +E for cathode→anode streamlines.
        const [Ey, Ez] = eField(py, pz, activeList);
        const mag = Math.sqrt(Ey * Ey + Ez * Ez);
        if (mag < 1e-20) break;
        py += (Ey / mag) * STEP; // STEP is in μm, py/pz are in μm
        pz += (Ez / mag) * STEP;
      }

      if (points.length < 3) continue;

      const geom = new THREE.BufferGeometry().setFromPoints(points);
      geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

      const line = new THREE.Line(geom, new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: Math.min(0.2 + ampFrac * 0.6, 0.8),
      }));
      streamlineGroup.add(line);
    }
    } // end seedRows
  }
}

// --- Fascicle materials ---
// Separate materials: base (dim) and recruited (bright), never mutated
const fascicleObjects = [];
const matDefs = {
  vagal:       { base: { color: 0x2a5a8a, emissive: 0x000000, emissiveIntensity: 0, opacity: 0.6 },
                 recruited: { color: 0x80ddff, emissive: 0x40aaff, emissiveIntensity: 0.7, opacity: 1.0 } },
  sympathetic: { base: { color: 0x8a4a20, emissive: 0x000000, emissiveIntensity: 0, opacity: 0.6 },
                 recruited: { color: 0xffcc44, emissive: 0xff8800, emissiveIntensity: 0.7, opacity: 1.0 } },
};

function makeFascMat(def) {
  return new THREE.MeshPhysicalMaterial({
    color: def.color, roughness: 0.4, metalness: 0.1, clearcoat: 0.3,
    emissive: new THREE.Color(def.emissive), emissiveIntensity: def.emissiveIntensity,
    transparent: true, opacity: def.opacity,
  });
}

for (const f of data.fascicles) {
  const r = Math.max(f.r * S, 0.03);
  const geom = new THREE.CylinderGeometry(r, r, NERVE_DEPTH, 16);
  const defs = matDefs[f.type];
  const baseMat = makeFascMat(defs.base);
  const recruitedMat = makeFascMat(defs.recruited);
  const mesh = new THREE.Mesh(geom, baseMat);
  mesh.position.set(f.y * S, 0, f.z * S);
  mesh.userData = {
    type: 'fascicle', fascicleType: f.type, id: f.id,
    radius: f.r, y: f.y, z: f.z, baseMat, recruitedMat, recruited: false,
  };
  nerveGroup.add(mesh);
  fascicleObjects.push(mesh);
}

// --- Electrodes ---
const electrodeObjects = [];
// Cached materials — one per state, reused across all electrodes (fix: no leak)
const elCachedMats = {
  inactive: new THREE.MeshPhysicalMaterial({
    color: 0xc4742e, roughness: 0.3, metalness: 0.6,
    emissive: new THREE.Color(0xc4742e), emissiveIntensity: 0.15,
  }),
  cathode: new THREE.MeshPhysicalMaterial({
    color: 0xff4444, roughness: 0.2, metalness: 0.8,
    emissive: new THREE.Color(0xff2222), emissiveIntensity: 0.8,
  }),
  anode: new THREE.MeshPhysicalMaterial({
    color: 0x4488ff, roughness: 0.2, metalness: 0.8,
    emissive: new THREE.Color(0x2266ff), emissiveIntensity: 0.8,
  }),
};

for (const e of data.electrodes) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.14, 16, 16), elCachedMats.inactive);
  mesh.position.set(e.y * S, 0, e.z * S);
  mesh.userData = { type: 'electrode', id: e.id, y: e.y, z: e.z };

  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    color: 0xc4742e, transparent: true, opacity: 0.15, blending: THREE.AdditiveBlending,
  }));
  sprite.scale.set(0.5, 0.5, 1);
  sprite.userData = { isGlow: true };
  mesh.add(sprite);

  nerveGroup.add(mesh);
  electrodeObjects.push(mesh);
}

// Electrode ring wire
const ringElPts = data.electrodes.map(e => new THREE.Vector3(e.y * S, 0, e.z * S));
ringElPts.push(ringElPts[0].clone());
nerveGroup.add(new THREE.Line(
  new THREE.BufferGeometry().setFromPoints(ringElPts),
  new THREE.LineBasicMaterial({ color: 0xc4742e, transparent: true, opacity: 0.2 })
));

// --- Recruitment (|E|-based approximation — will be replaced with real NRV data) ---
// Biphasic stimulation: both phases activate, so recruitment is symmetric.
// Use |E| (field magnitude) as proxy for activating function.
// Threshold |E| = field strength at nominal distance for threshold current.
function computeRecruitment() {
  const activeList = [...activeElectrodes.entries()];
  const threshold = data.fiber_thresholds_mA[fiberTypes[fiberTypeIdx]];
  // |E| from a point source at distance r: |E| = ρ·I / (4π·r²)
  const nominalDist = 2.5e-3; // m
  const E_threshold = (RHO * threshold * 1e-3) / (4 * Math.PI * nominalDist * nominalDist);

  for (const mesh of fascicleObjects) {
    const d = mesh.userData;
    let recruited = false;

    if (activeList.length > 0) {
      // Compute |E| at fascicle center from all electrodes
      const [Ey, Ez] = eField(d.y, d.z, activeList);
      const eMag = Math.sqrt(Ey * Ey + Ez * Ez);
      recruited = eMag >= E_threshold;
    }

    d.recruited = recruited;
    mesh.material = recruited ? d.recruitedMat : d.baseMat;
  }
}

// --- Electrode visuals ---
function updateElectrodeVisuals() {
  for (const mesh of electrodeObjects) {
    const w = activeElectrodes.get(mesh.userData.id);
    const state = w === 1 ? 'cathode' : w === -1 ? 'anode' : 'inactive';
    mesh.material = elCachedMats[state];
    const glowColor = { cathode: 0xff4444, anode: 0x4488ff, inactive: 0xc4742e }[state];
    const glowOpacity = state === 'inactive' ? 0.15 : 0.4;
    mesh.children.forEach(c => {
      if (!c.userData.isGlow) return;
      c.material.color.setHex(glowColor);
      c.material.opacity = glowOpacity;
    });
  }
}

// --- Distant return check ---
function checkDistantReturn() {
  if (activeElectrodes.size === 0) {
    isDistantReturn = false;
    return;
  }
  const weights = [...activeElectrodes.values()];
  const hasCathode = weights.some(w => w > 0);
  const hasAnode = weights.some(w => w < 0);
  isDistantReturn = !(hasCathode && hasAnode);
}

function onUpdate() {
  checkDistantReturn();
  updateElectrodeVisuals();
  currentDR = computeDynamicRange();
  // Update slider range if controls exist
  const slider = document.getElementById('vc-slider');
  if (slider) {
    slider.max = String(currentDR.max);
    slider.step = String(Math.max(0.002, currentDR.max / 200));
    if (currentAmplitude > currentDR.max) {
      currentAmplitude = currentDR.max;
      slider.value = String(currentAmplitude);
      const sliderVal = document.getElementById('vc-slider-val');
      if (sliderVal) sliderVal.textContent = `${currentAmplitude.toFixed(2)} mA`;
    }
  }
  computeField();
  computeStreamlines();
  computeRecruitment();
  updateStats();
  updateDistantReturnBadge();
}

// --- Apply a preset ---
function applyPreset(name) {
  currentPreset = name;
  const preset = PRESETS[name];

  // Update preset button active states
  document.querySelectorAll('.vc-preset').forEach(btn => {
    btn.classList.toggle('vc-preset-active', btn.dataset.preset === name);
  });

  // Show/hide custom mode controls
  const customControls = document.getElementById('vc-custom-controls');
  if (customControls) customControls.style.display = name === 'custom' ? 'flex' : 'none';

  activeElectrodes.clear();
  if (preset.electrodes) {
    for (const [id, w] of Object.entries(preset.electrodes)) {
      activeElectrodes.set(Number(id), w);
    }
  }
  // Custom mode starts clean — user places electrodes manually

  onUpdate();
}

// --- Stats display ---
const statsEl = document.createElement('div');
statsEl.id = 'viewer-stats';
document.querySelector('.viewer-container').appendChild(statsEl);

function updateStats() {
  if (activeElectrodes.size === 0) {
    statsEl.style.display = 'none';
    return;
  }
  statsEl.style.display = 'flex';
  const total = fascicleObjects.filter(m => m.userData.recruited).length;
  const vagal = fascicleObjects.filter(m => m.userData.recruited && m.userData.fascicleType === 'vagal').length;
  const symp = fascicleObjects.filter(m => m.userData.recruited && m.userData.fascicleType === 'sympathetic').length;
  statsEl.innerHTML = `
    <div class="vs-stat"><span class="vs-num">${total}</span><span class="vs-label">recruited</span></div>
    <div class="vs-divider"></div>
    <div class="vs-stat"><span class="vs-num vs-vagal">${vagal}</span><span class="vs-label">vagal</span></div>
    <div class="vs-stat"><span class="vs-num vs-symp">${symp}</span><span class="vs-label">sympathetic</span></div>
  `;
}

// --- Distant return badge ---
const distantBadge = document.createElement('div');
distantBadge.id = 'distant-return-badge';
distantBadge.innerHTML = 'Distant return (analytical monopolar)';
document.querySelector('.viewer-container').appendChild(distantBadge);

function updateDistantReturnBadge() {
  distantBadge.style.display = isDistantReturn && activeElectrodes.size > 0 ? 'block' : 'none';
}

// --- HTML Controls ---
function createControls() {
  const container = document.querySelector('.viewer-container');

  // Onboarding overlay
  const overlay = document.createElement('div');
  overlay.id = 'viewer-onboarding';
  overlay.innerHTML = `
    <div class="onboard-content">
      <h3>Interactive Nerve Model</h3>
      <p>103 fascicles from real pig SPARC morphometry, scaled to bovine</p>
      <div class="onboard-steps">
        <div><span class="onboard-num">1</span> Pick an electrode configuration</div>
        <div><span class="onboard-num">2</span> Drag the current slider</div>
        <div><span class="onboard-num">3</span> Watch field lines and fascicle recruitment</div>
      </div>
      <button id="onboard-start">Explore</button>
      <p class="onboard-note">Recruitment is an analytical approximation (point-source model).<br>Full NRV/NEURON cable-model results coming soon.</p>
    </div>
  `;
  container.appendChild(overlay);

  document.getElementById('onboard-start').addEventListener('click', () => {
    overlay.classList.add('onboard-hidden');
    overlay.style.pointerEvents = 'none';
    overlay.addEventListener('transitionend', () => { overlay.style.display = 'none'; }, { once: true });
    hasInteracted = true;
    applyPreset('bipolar');
  });

  // Control bar
  const bar = document.createElement('div');
  bar.id = 'viewer-controls';
  bar.innerHTML = `
    <div class="vc-row vc-row-presets">
      <label>Config</label>
      <div class="vc-presets">
        <button class="vc-preset" data-preset="bipolar">Bipolar</button>
        <button class="vc-preset" data-preset="tripolar">Tripolar</button>
        <button class="vc-preset" data-preset="steering">Steering</button>
        <button class="vc-preset" data-preset="custom">Custom</button>
      </div>
    </div>
    <div class="vc-row">
      <div class="vc-group">
        <label>Current</label>
        <input type="range" id="vc-slider" min="0" max="1" step="0.002" value="${currentAmplitude}">
        <span id="vc-slider-val">${currentAmplitude.toFixed(2)} mA</span>
      </div>
      <div class="vc-group">
        <button id="vc-fiber" class="vc-btn">${fiberLabels[fiberTypeIdx]}</button>
        <div id="vc-custom-controls" style="display:none">
          <button id="vc-mode" class="vc-btn vc-mode-cathode">Cathode</button>
        </div>
        <button id="vc-reset" class="vc-btn">Reset</button>
      </div>
    </div>
  `;
  container.appendChild(bar);

  // Preset buttons
  bar.querySelectorAll('.vc-preset').forEach(btn => {
    btn.addEventListener('click', () => applyPreset(btn.dataset.preset));
  });

  // Current slider
  const slider = document.getElementById('vc-slider');
  const sliderVal = document.getElementById('vc-slider-val');
  slider.addEventListener('input', () => {
    currentAmplitude = parseFloat(slider.value);
    sliderVal.textContent = `${currentAmplitude.toFixed(2)} mA`;
    updateSliderThumb();
    onUpdate();
  });

  // Scale thumb size with amplitude fraction relative to current DR
  function updateSliderThumb() {
    const frac = currentDR.max > 0 ? Math.min(currentAmplitude / currentDR.max, 1) : 0;
    const size = 14 + frac * 10; // 14px → 24px
    slider.style.setProperty('--thumb-size', `${size}px`);
  }

  document.getElementById('vc-fiber').addEventListener('click', (e) => {
    fiberTypeIdx = (fiberTypeIdx + 1) % fiberTypes.length;
    e.target.textContent = fiberLabels[fiberTypeIdx];
    onUpdate(); // recomputes DR, updates slider range, etc.
    updateSliderThumb();
  });

  // Custom mode: cathode/anode toggle
  const modeBtn = document.getElementById('vc-mode');
  modeBtn.addEventListener('click', () => {
    electrodeMode = electrodeMode === 'cathode' ? 'anode' : 'cathode';
    modeBtn.textContent = electrodeMode === 'cathode' ? 'Cathode' : 'Anode';
    modeBtn.className = `vc-btn vc-mode-${electrodeMode}`;
  });

  // Reset
  document.getElementById('vc-reset').addEventListener('click', () => {
    activeElectrodes.clear();
    fiberTypeIdx = 0;
    electrodeMode = 'cathode';
    currentAmplitude = 0.15;
    document.getElementById('vc-fiber').textContent = fiberLabels[0];
    const mb = document.getElementById('vc-mode');
    mb.textContent = 'Cathode';
    mb.className = 'vc-btn vc-mode-cathode';
    applyPreset('bipolar'); // this calls onUpdate → recomputes DR → updates slider
    slider.value = String(currentAmplitude);
    sliderVal.textContent = `${currentAmplitude.toFixed(2)} mA`;
    updateSliderThumb();
  });
}

createControls();

// --- Pointer interaction ---
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2(-999, -999);
let isDragging = false;
let isPointerDown = false;
let pointerDownTime = 0;

canvas.addEventListener('mousemove', (ev) => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
});

canvas.addEventListener('pointerdown', () => {
  isPointerDown = true;
  isDragging = false;
  pointerDownTime = Date.now();
});
canvas.addEventListener('pointermove', () => {
  if (isPointerDown && Date.now() - pointerDownTime > 150) isDragging = true;
});

canvas.addEventListener('pointerup', () => {
  isPointerDown = false;
  if (isDragging) { isDragging = false; return; }
  if (!currentPreset || currentPreset !== 'custom') return; // Only allow clicking in custom mode

  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(electrodeObjects);
  if (hits.length > 0) {
    const eId = hits[0].object.userData.id;
    if (activeElectrodes.has(eId)) {
      activeElectrodes.delete(eId);
    } else {
      activeElectrodes.set(eId, electrodeMode === 'cathode' ? 1 : -1);
    }
    hasInteracted = true;
    onUpdate();
  }
});

canvas.addEventListener('contextmenu', (e) => e.preventDefault());

// --- Animate ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();

  // Hover — track previous hover target to avoid mutating all materials each frame
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects([...fascicleObjects, ...electrodeObjects]);

  // Clear previous hover highlight
  if (hoveredFascicle && !hoveredFascicle.userData.recruited) {
    hoveredFascicle.userData.baseMat.emissive.setHex(0x000000);
    hoveredFascicle.userData.baseMat.emissiveIntensity = 0;
    hoveredFascicle = null;
  }

  if (hits.length > 0) {
    const obj = hits[0].object;
    const d = obj.userData;
    if (d.type === 'fascicle') {
      if (!d.recruited) {
        d.baseMat.emissive.setHex(d.fascicleType === 'vagal' ? 0x4a9eff : 0xff6b35);
        d.baseMat.emissiveIntensity = 0.5;
        hoveredFascicle = obj;
      }
      const status = d.recruited ? ' — recruited' : '';
      infoEl.innerHTML = `<strong>${d.fascicleType} #${d.id}</strong> — diameter: ${(d.radius * 2).toFixed(0)}μm${status}`;
    } else if (d.type === 'electrode') {
      const w = activeElectrodes.get(d.id);
      const state = w === 1 ? 'cathode (+)' : w === -1 ? 'anode (−)' : currentPreset === 'custom' ? 'tap to activate' : 'inactive';
      infoEl.innerHTML = `<strong>E${d.id}</strong> — ${state}`;
    }
  } else if (activeElectrodes.size > 0) {
    const presetLabel = PRESETS[currentPreset]?.label || 'Custom';
    const returnInfo = isDistantReturn ? ' — distant return' : '';
    infoEl.innerHTML = `${presetLabel} · ${fiberLabels[fiberTypeIdx]} @ ${currentAmplitude.toFixed(2)} mA${returnInfo}`;
  } else {
    infoEl.innerHTML = currentPreset === 'custom' ? 'Tap electrodes to place cathodes and anodes' : 'Click Explore or select a configuration';
  }

  renderer.render(scene, camera);
}

const ro = new ResizeObserver(() => {
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  camera.aspect = canvas.clientWidth / canvas.clientHeight;
  camera.updateProjectionMatrix();
});
ro.observe(canvas);

animate();
