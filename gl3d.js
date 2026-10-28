/* ───────────────────────────────────────────────────────────────────────────
   Retro Baseball 3D: the ballpark, the players and the cameras, all built in code with three.js.
   World units are FEET.  X = to the right of the batter, Y = up, Z = toward the backstop (so the
   outfield is at negative Z).  A ball at {d: feet out from home, lat: feet to the right} sits at
   (X = lat, Z = -d).  Nothing here is a picture: the ground is painted from the real dimensions
   and every person is a skeleton of boxes.
   ─────────────────────────────────────────────────────────────────────────── */
(function(){
'use strict';
const TAU = Math.PI * 2, D2R = Math.PI / 180;
const lerp = (a, b, t) => a + (b - a) * t, clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const hex = c => new THREE.Color(c);
let R_ = 1;                                                   // a tiny seeded random so the crowd looks the same every time
const rr = () => (R_ = (R_ * 16807) % 2147483647) / 2147483647;

const GL = { ready:false, rows:270, view:'bat', park:null };
window.GL3D = GL;

// ── the fence line: its distance from home for every angle around the park ─────────────────────
function fenceR(park, deg){
  const a = Math.abs(deg);
  const wd = d => d < 0 ? lerp(park.lf, park.cf, (clamp(d, -45, 0) + 45) / 45) : lerp(park.cf, park.rf, clamp(d, 0, 45) / 45);
  if (a <= 45) return wd(deg);
  const pole = deg < 0 ? park.lf : park.rf;
  if (a <= 90) return lerp(pole, 215, (a - 45) / 45);              // the foul-ground wall bends in toward the stands
  return lerp(215, 70, clamp((a - 90) / 50, 0, 1));
}
GL.fenceR = fenceR;
const toX = (d, lat) => lat, toZ = (d, lat) => -d;

// ── paint the whole ground, top-down, from real measurements ─────────────────────────────────────
const TEX = 2048, X0 = -330, XW = 660, D0 = -120, DW = 660;       // texture covers X -330..330 ft, depth -120..540 ft
function paintGround(park, reg){
  reg = reg || { x0:X0, xw:XW, d0:D0, dw:DW, w:TEX, h:TEX, near:false };
  const c = document.createElement('canvas'); c.width = reg.w; c.height = reg.h; const g = c.getContext('2d');
  const S = reg.w / reg.xw;
  const P = (lat, d) => [(lat - reg.x0) * S, (reg.d0 + reg.dw - d) * S];
  const poly = (pts, fill) => { g.beginPath(); pts.forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.fillStyle = fill; g.fill(); };
  const circ = (lat, d, r, fill) => { const q = P(lat, d); g.beginPath(); g.arc(q[0], q[1], r * S, 0, TAU); g.fillStyle = fill; g.fill(); };
  const GRASS_A = '#4d7e38', GRASS_B = '#467636', GRASS_C = '#548440', DIRT = '#b07946', DIRT2 = '#a56f3f', TRACK = '#a9743f', CHALK = '#f1ede2';
  // base grass, with wide mowing stripes running out from home
  g.fillStyle = GRASS_A; g.fillRect(0, 0, reg.w, reg.h);
  for (let i = -24; i < 24; i++){
    if (i % 2) continue;
    poly([[i * 14, D0], [i * 14 + 14, D0], [i * 14 + 14, D0 + DW], [i * 14, D0 + DW]], GRASS_B);
  }
  // diagonal stripes inside the infield diamond
  g.save(); g.beginPath(); [[0, 0], [63.6, 63.6], [0, 127.3], [-63.6, 63.6]].forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.clip();
  for (let i = -20; i < 20; i++){ if (i % 2) continue;
    const a = P(-120 + i * 9, 63.6 - 120), b = P(120 + i * 9, 63.6 + 120), c2 = P(120 + i * 9 + 9, 63.6 + 120), d2 = P(-120 + i * 9 + 9, 63.6 - 120);
    g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.lineTo(...c2); g.lineTo(...d2); g.closePath(); g.fillStyle = GRASS_C; g.fill(); }
  g.restore();
  // warning track and the dirt apron under the wall, all the way round
  const ring = []; for (let a = -150; a <= 150; a += 2){ const r = fenceR(park, a), t = a * D2R; ring.push([Math.sin(t) * r, Math.cos(t) * r]); }
  const inner = []; for (let a = 150; a >= -150; a -= 2){ const r = fenceR(park, a) - 15, t = a * D2R; inner.push([Math.sin(t) * r, Math.cos(t) * r]); }
  poly(ring.concat(inner), TRACK);
  // the infield dirt: a circle round the mound, a circle round the plate, and the base paths
  circ(0, 60.5, 95, DIRT);
  circ(0, 0, 14, DIRT);
  // the infield grass sits inside the diamond, leaving a strip of dirt along the base paths
  const ins = 7;                                                  // dirt path half-width, ft
  poly([[0, 14], [63.6 - ins * 1.4, 63.6], [0, 127.3 - ins * 1.4 - 8], [-63.6 + ins * 1.4, 63.6]], GRASS_A);
  g.save(); g.beginPath(); [[0, 14], [63.6 - ins * 1.4, 63.6], [0, 127.3 - ins * 1.4 - 8], [-63.6 + ins * 1.4, 63.6]].forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.clip();
  for (let i = -20; i < 20; i++){ if (i % 2) continue;
    const a = P(-120 + i * 8, 63.6 - 120), b = P(120 + i * 8, 63.6 + 120), c2 = P(120 + i * 8 + 8, 63.6 + 120), d2 = P(-120 + i * 8 + 8, 63.6 - 120);
    g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.lineTo(...c2); g.lineTo(...d2); g.closePath(); g.fillStyle = GRASS_C; g.fill(); }
  g.restore();
  // dirt cut-outs round second, a mound, and base circles
  circ(0, 127.3, 11, DIRT); circ(0, 60.5, 9.5, DIRT2); circ(63.6, 63.6, 8, DIRT); circ(-63.6, 63.6, 8, DIRT);
  // the foul lines run from the plate to the poles and a bit beyond
  const line = (a, b, w, col) => { const A = P(a[0], a[1]), B = P(b[0], b[1]); g.strokeStyle = col; g.lineWidth = w * S; g.lineCap = 'butt'; g.beginPath(); g.moveTo(...A); g.lineTo(...B); g.stroke(); };
  const rp = fenceR(park, 45), lp = fenceR(park, -45);
  line([3.7, 3.7], [Math.sin(45 * D2R) * rp, Math.cos(45 * D2R) * rp], .75, CHALK);          // they start at the top of the batter's boxes
  line([-3.7, 3.7], [-Math.sin(45 * D2R) * lp, Math.cos(45 * D2R) * lp], .75, CHALK);
  // batter's boxes (4 x 6 ft, six inches off the plate) and the catcher's box
  const box = (x0, x1, d0, d1) => { const a = P(x0, d1), b = P(x1, d0); g.strokeStyle = CHALK; g.lineWidth = .35 * S; g.strokeRect(a[0], a[1], b[0] - a[0], b[1] - a[1]); };
  box(-5.2, -1.2, -2.3, 3.7); box(1.2, 5.2, -2.3, 3.7);
  box(-3.6, 3.6, -9, -3);
  // 1st and 3rd base coaches' boxes
  box(70, 76, 60, 66); box(-76, -70, 60, 66);
  // texture: dirt grain and grass speckle so it never looks flat
  const sp = (n, cols, lat0, lat1, d0, d1, sz) => { for (let i = 0; i < n; i++){ g.fillStyle = cols[(rr() * cols.length) | 0]; const q = P(lat0 + rr() * (lat1 - lat0), d0 + rr() * (d1 - d0)); g.fillRect(q[0], q[1], sz, sz); } };
  sp(reg.near ? 30000 : 160000, ['#4a7a36', '#527f3b', '#46763a'], reg.x0, reg.x0 + reg.xw, reg.d0, reg.d0 + reg.dw, reg.near ? 2 : 1);
  g.save(); g.beginPath(); const q0 = P(0, 60.5); g.arc(q0[0], q0[1], 95 * S, 0, TAU); g.clip();
  sp(reg.near ? 40000 : 160000, ['#b57d49', '#a87240', '#bb824c', '#a06a3a'], -100, 100, -40, 160, reg.near ? 2 : 1); g.restore();
  if (reg.near){                                                  // feather the edges so the close-up blends into the wide ground
    g.globalCompositeOperation = 'destination-in';
    const fg = g.createLinearGradient(0, 0, 0, reg.h); const fgx = g.createLinearGradient(0, 0, reg.w, 0);
    const m = document.createElement('canvas'); m.width = reg.w; m.height = reg.h; const mg = m.getContext('2d');
    const rad = mg.createRadialGradient(reg.w / 2, reg.h / 2, Math.min(reg.w, reg.h) * .30, reg.w / 2, reg.h / 2, Math.min(reg.w, reg.h) * .50);
    rad.addColorStop(0, 'rgba(0,0,0,1)'); rad.addColorStop(1, 'rgba(0,0,0,0)'); mg.fillStyle = rad; mg.fillRect(0, 0, reg.w, reg.h);
    g.drawImage(m, 0, 0); g.globalCompositeOperation = 'source-over';
  }
  const t = new THREE.CanvasTexture(c); t.minFilter = reg.near ? THREE.NearestFilter : THREE.LinearMipmapLinearFilter; t.magFilter = THREE.NearestFilter; t.anisotropy = 4; t.generateMipmaps = !reg.near;
  return t;
}

// ── the crowd: a noisy strip of tiny coloured people ─────────────────────────────────────────────
function crowdTexture(c1, c2){
  const c = document.createElement('canvas'); c.width = 256; c.height = 64; const g = c.getContext('2d');
  g.fillStyle = '#343b50'; g.fillRect(0, 0, 256, 64);
  const cols = ['#9a96a0', '#8c7f86', '#7a8aa0', '#a09a78', '#8a7f9c', '#7f9a88', '#a08a7c', '#6a7488', '#aaa6a6', c1, c1, c2];
  for (let y = 0; y < 64; y += 4) for (let x = 0; x < 256; x += 4){
    if (rr() < .12) continue;
    g.fillStyle = cols[(rr() * cols.length) | 0]; g.fillRect(x, y, 3, 2);                      // shirt
    g.fillStyle = ['#e0b08a', '#c88e5e', '#8a5a38', '#f0c9a0'][(rr() * 4) | 0]; g.fillRect(x + 1, y - 1, 1, 1);   // head
  }
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function bannerTexture(park){
  const c = document.createElement('canvas'); c.width = 512; c.height = 64; const g = c.getContext('2d');
  g.fillStyle = park.wall; g.fillRect(0, 0, 512, 64);
  const cols = ['#c0392b', '#e0b32a', '#2f6fb5', '#d9d9d9', '#2f8f5b', '#7a3fa5'];
  for (let i = 0; i < 8; i++){ g.fillStyle = cols[(rr() * cols.length) | 0]; g.fillRect(20 + i * 62, 14, 44, 30); g.fillStyle = 'rgba(255,255,255,.55)'; g.fillRect(24 + i * 62, 22, 36, 3); g.fillRect(24 + i * 62, 30, 24, 3); }
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}

// ── build the park: ground, fence, stands, towers, sky ───────────────────────────────────────────
function buildPark(park, teamCols){
  if (GL.parkGroup){ GL.scene.remove(GL.parkGroup); GL.parkGroup.traverse(o => { if (o.geometry) o.geometry.dispose(); }); }
  const G = new THREE.Group(); GL.parkGroup = G; GL.scene.add(G);
  R_ = 7;
  // the ground
  const tex = paintGround(park);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(XW, DW), new THREE.MeshBasicMaterial({ map: tex }));
  ground.rotation.x = -Math.PI / 2; ground.position.set((X0 + XW / 2), 0, -(D0 + DW / 2)); G.add(ground);
  const nreg = { x0:-34, xw:68, d0:-22, dw:56, w:1024, h:844, near:true };
  const near = new THREE.Mesh(new THREE.PlaneGeometry(nreg.xw, nreg.dw), new THREE.MeshBasicMaterial({ map: paintGround(park, nreg), transparent: true, depthWrite: false }));
  near.rotation.x = -Math.PI / 2; near.position.set(nreg.x0 + nreg.xw / 2, .02, -(nreg.d0 + nreg.dw / 2)); G.add(near);
  // everything beyond the stands: dark concrete so nothing is ever see-through
  const under = new THREE.Mesh(new THREE.PlaneGeometry(2400, 2400), new THREE.MeshBasicMaterial({ color: 0x1b2230 }));
  under.rotation.x = -Math.PI / 2; under.position.y = -.3; G.add(under);

  // the fence and the seating bowl, as strips swept around the angle
  const crowd = crowdTexture(teamCols[0], teamCols[1]), banner = bannerTexture(park);
  const STEP = 3, A0 = -150, A1 = 150, n = (A1 - A0) / STEP;
  const wallH = 9.5;
  const strip = (profile, mat, uScale, vScale) => {               // profile: list of [dr, y] from the fence outward; one quad strip per consecutive pair
    const pos = [], uv = [], idx = [];
    for (let i = 0; i <= n; i++){
      const a = A0 + i * STEP, t = a * D2R, r0 = fenceR(park, a);
      profile.forEach((pt, j) => { const r = r0 + pt[0]; pos.push(Math.sin(t) * r, pt[1], -Math.cos(t) * r); uv.push(i * uScale, j * vScale); });
    }
    const m = profile.length;
    for (let i = 0; i < n; i++) for (let j = 0; j < m - 1; j++){ const a = i * m + j, b = a + m; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx);
    const mesh = new THREE.Mesh(geo, mat); G.add(mesh); return mesh;
  };
  const wallMat = new THREE.MeshBasicMaterial({ map: banner, side: THREE.DoubleSide });
  banner.wrapS = banner.wrapT = THREE.RepeatWrapping;
  strip([[0, 0], [0, wallH - 1.2]], new THREE.MeshBasicMaterial({ color: hex(park.wall), side: THREE.DoubleSide }), 1, 1);
  strip([[0, wallH - 1.2], [0, wallH]], new THREE.MeshBasicMaterial({ color: 0xf2c230, side: THREE.DoubleSide }), 1, 1);              // the yellow top line
  strip([[0.05, 1.2], [0.05, 6.6]], new THREE.MeshBasicMaterial({ map: banner, side: THREE.DoubleSide, transparent:true, opacity:.0 }), .5, 1);   // (reserved for ad boards)
  // padding along the bottom of the wall, a darker band
  strip([[-.05, 0], [-.05, 3.4]], new THREE.MeshBasicMaterial({ color: hex(park.wall).multiplyScalar(.62), side: THREE.DoubleSide }), 1, 1);
  // the seating: tiers rising away from the fence, crowd texture on every riser
  const crowdMat = new THREE.MeshBasicMaterial({ map: crowd, side: THREE.DoubleSide });
  crowd.repeat.set(1, 1);
  for (let k = 0; k < 7; k++){
    const r0 = 6 + k * 9, y0 = wallH + 2 + k * 6.2;
    strip([[r0, y0], [r0 + 9, y0 + 6.2]], crowdMat, 1.7, 1);                                                          // the sloped seating deck
    strip([[r0 + 9, y0 + 6.2], [r0 + 9, y0 + 6.2 + 1.3]], new THREE.MeshBasicMaterial({ color: k % 2 ? 0x2c3e5c : 0x34486a, side: THREE.DoubleSide }), 1, 1);   // the rail
  }
  // a back wall behind the top tier, then the city beyond it
  strip([[70, wallH + 2 + 7 * 6.2], [70, wallH + 2 + 7 * 6.2 + 12]], new THREE.MeshBasicMaterial({ color: 0x2a3550, side: THREE.DoubleSide }), 1, 1);
  for (let i = 0; i < 70; i++){
    const a = -100 + i * 200 / 69 + (rr() - .5) * 2, r = 560 + rr() * 140, h = 40 + rr() * 110, w = 26 + rr() * 40, t = a * D2R;
    const col = [0x5d7391, 0x6a809e, 0x4d6384, 0x7890ab][(rr() * 4) | 0];
    const bld = new THREE.Mesh(new THREE.BoxGeometry(w, h, w), new THREE.MeshBasicMaterial({ color: col })); bld.position.set(Math.sin(t) * r, h / 2 - 20, -Math.cos(t) * r); G.add(bld);
  }
  // soft clouds
  for (let i = 0; i < 9; i++){ const a = -80 + rr() * 160, t = a * D2R, r = 900, cl = new THREE.Mesh(new THREE.BoxGeometry(90 + rr() * 90, 10, 26), new THREE.MeshBasicMaterial({ color: 0xf4f9ff })); cl.position.set(Math.sin(t) * r, 190 + rr() * 150, -Math.cos(t) * r); G.add(cl); }
  // the dugout steps and outfield batter's eye
  const eye = new THREE.Mesh(new THREE.PlaneGeometry(90, 34), new THREE.MeshBasicMaterial({ color: 0x14382a, side: THREE.DoubleSide }));
  eye.position.set(0, wallH + 18, -(fenceR(park, 0) + 3.5)); G.add(eye);
  // the scoreboard above the centre-field seats
  const sb = new THREE.Mesh(new THREE.BoxGeometry(70, 30, 3), [0x10161f, 0x10161f, 0x10161f, 0x10161f, 0x18212e, 0x18212e].map(c => new THREE.MeshBasicMaterial({ color: c })));
  sb.position.set(0, 98, -(fenceR(park, 0) + 76)); G.add(sb);
  const sbf = new THREE.Mesh(new THREE.PlaneGeometry(62, 22), new THREE.MeshBasicMaterial({ color: 0x1c6b4a })); sbf.position.set(0, 98, -(fenceR(park, 0) + 74.4)); G.add(sbf);
  for (let i = 0; i < 18; i++){ const px = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.MeshBasicMaterial({ color: [0xffe27a, 0xff8a5a, 0xf4f1e6][i % 3] })); px.position.set(-26 + (i % 9) * 6.5, 102 - ((i / 9) | 0) * 7, -(fenceR(park, 0) + 74.3)); G.add(px); }
  // the light towers
  [-120, -62, 62, 120].forEach(a => {
    const r = fenceR(park, a) + 110, t = a * D2R, x = Math.sin(t) * r, z = -Math.cos(t) * r;
    const pole = new THREE.Mesh(new THREE.BoxGeometry(3, 150, 3), new THREE.MeshBasicMaterial({ color: 0x3a4658 })); pole.position.set(x, 75, z); G.add(pole);
    const bank = new THREE.Mesh(new THREE.BoxGeometry(34, 20, 4), new THREE.MeshBasicMaterial({ color: 0xcfd8e8 })); bank.position.set(x, 150, z); bank.lookAt(0, 150, 0); G.add(bank);
  });
  // the foul poles
  [-45, 45].forEach(a => { const r = fenceR(park, a), t = a * D2R;
    const p = new THREE.Mesh(new THREE.BoxGeometry(1.1, 52, 1.1), new THREE.MeshBasicMaterial({ color: 0xf2c230 })); p.position.set(Math.sin(t) * r, 26, -Math.cos(t) * r); G.add(p); });
  // bases, plate, rubber, mound
  const white = new THREE.MeshBasicMaterial({ color: 0xf6f3ea });
  const base = (x, z) => { const b = new THREE.Mesh(new THREE.BoxGeometry(1.5, .35, 1.5), white); b.position.set(x, .18, z); b.rotation.y = Math.PI / 4; G.add(b); };
  base(63.64, -63.64); base(0, -127.28); base(-63.64, -63.64);
  const plate = new THREE.Shape(); plate.moveTo(-.708, 0); plate.lineTo(.708, 0); plate.lineTo(.708, 0.708); plate.lineTo(0, 1.417); plate.lineTo(-.708, .708); plate.closePath();
  const pm = new THREE.Mesh(new THREE.ExtrudeGeometry(plate, { depth: .12, bevelEnabled: false }), white);
  pm.rotation.x = Math.PI / 2; pm.position.set(0, .13, 0); pm.scale.set(1, -1, 1); G.add(pm);
  const rub = new THREE.Mesh(new THREE.BoxGeometry(2, .25, .5), white); rub.position.set(0, .45, -60.5); G.add(rub);
  const mound = new THREE.Mesh(new THREE.CylinderGeometry(7.5, 9.5, .9, 24), new THREE.MeshBasicMaterial({ color: 0xb06a33 })); mound.position.set(0, .35, -60.5); G.add(mound);
  const moundTop = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 7.5, .5, 24), new THREE.MeshBasicMaterial({ color: 0xbb7a3e })); moundTop.position.set(0, .65, -60.5); G.add(moundTop);
  // sky
  const sky = document.createElement('canvas'); sky.width = 4; sky.height = 256; const sg = sky.getContext('2d');
  const gr = sg.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#3f86d8'); gr.addColorStop(.6, '#8cc4ee'); gr.addColorStop(1, '#d5ebfa'); sg.fillStyle = gr; sg.fillRect(0, 0, 4, 256);
  const st = new THREE.CanvasTexture(sky);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1500, 24, 16), new THREE.MeshBasicMaterial({ map: st, side: THREE.BackSide, fog: false })); dome.position.y = -250; G.add(dome);
  GL.parkKey = park;
}

// ── set up ───────────────────────────────────────────────────────────────────────────────────────
GL.init = function(canvas){
  GL.canvas = canvas;
  GL.renderer = new THREE.WebGLRenderer({ canvas, antialias:false, powerPreference:'default', stencil:false, alpha:false });
  GL.scene = new THREE.Scene(); GL.scene.background = hex('#8cc4ee');
  GL.cam = new THREE.PerspectiveCamera(40, 16 / 9, .5, 3000);
  GL.world = new THREE.Group(); GL.scene.add(GL.world);                            // players, ball
  GL.ready = true;
};
GL.setPark = function(park, teamCols){ buildPark(park, teamCols || ['#2c4a8a', '#c0392b']); GL.park = park; };
GL.resize = function(w, h){
  const rows = GL.rows, cols = Math.round(rows * w / h);
  GL.renderer.setSize(cols, rows, false);
  GL.canvas.style.width = w + 'px'; GL.canvas.style.height = h + 'px'; GL.canvas.style.imageRendering = 'pixelated';
  GL.cam.aspect = cols / rows; GL.cam.updateProjectionMatrix();
};
// the cameras: behind the plate looking out at the mound, or high above the park looking down
GL.setView = function(v){ GL.view = v; };
GL.placeCamera = function(){
  const c = GL.cam;
  if (GL.view === 'bat'){ c.fov = 33.4; c.up.set(0, 1, 0); c.position.set(.15, 8.4, 21.5); c.lookAt(.15, 8.4 - Math.tan(7.44 * D2R) * 100, 21.5 - 100); }
  else if (GL.view === 'free'){ const f = GL.freeCam; c.fov = f.fov; c.up.set(0, 1, 0); c.position.set(...f.pos); c.lookAt(...f.look); }
  else { c.fov = 46; c.up.set(0, 0, -1); c.position.set(0, 470, 78); c.lookAt(0, 0, -170); }
  c.updateProjectionMatrix();
};
GL.render = function(){ GL.placeCamera(); GL.renderer.render(GL.scene, GL.cam); };
})();
