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
  const GRASS_A = '#4c7c37', GRASS_B = '#3f6c2e', GRASS_C = '#578944', DIRT = '#b17846', DIRT2 = '#a66b3d', TRACK = '#a9743f', CHALK = '#f1ede2';
  // base grass, with wide mowing stripes running out from home
  g.fillStyle = GRASS_A; g.fillRect(0, 0, reg.w, reg.h);
  for (let i = -24; i < 24; i++){
    if (i % 2) continue;
    poly([[i * 14, D0], [i * 14 + 14, D0], [i * 14 + 14, D0 + DW], [i * 14, D0 + DW]], GRASS_B);
  }
  const sp = (n, cols, lat0, lat1, d0, d1, sz) => { for (let i = 0; i < n; i++){ g.fillStyle = cols[(rr() * cols.length) | 0]; const q = P(lat0 + rr() * (lat1 - lat0), d0 + rr() * (d1 - d0)); g.fillRect(q[0], q[1], sz, sz); } };
  sp(reg.near ? 30000 : 160000, ['#4a7a35', '#4e7e39', '#477434'], reg.x0, reg.x0 + reg.xw, reg.d0, reg.d0 + reg.dw, reg.near ? 2 : 1);
  // diagonal stripes inside the infield diamond
  g.save(); g.beginPath(); [[0, 0], [63.6, 63.6], [0, 127.3], [-63.6, 63.6]].forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.clip();
  for (let i = -20; i < 20; i++){ if (i % 2) continue;
    const a = P(-120 + i * 9, 63.6 - 120), b = P(120 + i * 9, 63.6 + 120), c2 = P(120 + i * 9 + 9, 63.6 + 120), d2 = P(-120 + i * 9 + 9, 63.6 - 120);
    g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.lineTo(...c2); g.lineTo(...d2); g.closePath(); g.fillStyle = GRASS_C; g.fill(); }
  g.restore();
  // warning track and the dirt apron under the wall, all the way round
  const ring = []; for (let a = -150; a <= 150; a += 2){ const r = fenceR(park, a), t = a * D2R; ring.push([Math.sin(t) * r, Math.cos(t) * r]); }
  const inner = []; for (let a = 150; a >= -150; a -= 2){ const r = fenceR(park, a) - 4, t = a * D2R; inner.push([Math.sin(t) * r, Math.cos(t) * r]); }
  poly(ring.concat(inner), TRACK);
  // the infield dirt: a circle round the mound, a circle round the plate, and the base paths
  circ(0, 60.5, 95, DIRT);
  circ(0, 0, 14, DIRT2);
  g.save(); g.beginPath(); const q0 = P(0, 60.5); g.arc(q0[0], q0[1], 95 * S, 0, TAU); g.clip();
  sp(reg.near ? 40000 : 160000, ['#b57d49', '#a87240', '#bb824c', '#a06a3a'], -100, 100, -40, 160, reg.near ? 2 : 1); g.restore();
  // the infield grass sits inside the diamond, leaving a strip of dirt along the base paths
  const ins = 7;                                                  // dirt path half-width, ft
  poly([[-6, 9], [6, 9], [63.6 - 3, 63.6], [0, 127.3 - 14], [-63.6 + 3, 63.6]], GRASS_A);
  g.save(); g.beginPath(); [[-6, 9], [6, 9], [63.6 - 3, 63.6], [0, 127.3 - 14], [-63.6 + 3, 63.6]].forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.clip();
  for (let i = -20; i < 20; i++){ if (i % 2) continue;
    const a = P(-120 + i * 8, 63.6 - 120), b = P(120 + i * 8, 63.6 + 120), c2 = P(120 + i * 8 + 8, 63.6 + 120), d2 = P(-120 + i * 8 + 8, 63.6 - 120);
    g.beginPath(); g.moveTo(...a); g.lineTo(...b); g.lineTo(...c2); g.lineTo(...d2); g.closePath(); g.fillStyle = GRASS_C; g.fill(); }
  g.restore();
  // dirt cut-outs round second, a mound, and base circles
  circ(0, 127.3, 11, DIRT); circ(0, 60.5, 9.5, DIRT2); circ(63.6, 63.6, 8, DIRT); circ(-63.6, 63.6, 8, DIRT);
  // the foul lines run from the plate to the poles and a bit beyond
  const line = (a, b, w, col) => { const A = P(a[0], a[1]), B = P(b[0], b[1]); g.strokeStyle = col; g.lineWidth = w * S; g.lineCap = 'butt'; g.beginPath(); g.moveTo(...A); g.lineTo(...B); g.stroke(); };
  const rp = fenceR(park, 45), lp = fenceR(park, -45);
  line([3.7, 3.7], [Math.sin(45 * D2R) * rp, Math.cos(45 * D2R) * rp], 1.15, CHALK);          // they start at the top of the batter's boxes
  line([-3.7, 3.7], [-Math.sin(45 * D2R) * lp, Math.cos(45 * D2R) * lp], 1.15, CHALK);
  // batter's boxes (4 x 6 ft, six inches off the plate) and the catcher's box
  const box = (x0, x1, d0, d1) => { const a = P(x0, d1), b = P(x1, d0); g.strokeStyle = CHALK; g.lineWidth = .5 * S; g.strokeRect(a[0], a[1], b[0] - a[0], b[1] - a[1]); };
  box(-5.2, -1.2, -2.3, 3.7); box(1.2, 5.2, -2.3, 3.7);
  box(-3.6, 3.6, -9, -3);
  // 1st and 3rd base coaches' boxes
  box(70, 76, 60, 66); box(-76, -70, 60, 66);
  // texture: dirt grain and grass speckle so it never looks flat

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
function wallTexture(col){
  const c = document.createElement('canvas'); c.width = 128; c.height = 32; const g = c.getContext('2d'); const base = new THREE.Color(col);
  g.fillStyle = '#' + base.getHexString(); g.fillRect(0, 0, 128, 32);
  g.fillStyle = 'rgba(255,255,255,.07)'; g.fillRect(0, 0, 128, 5);
  g.fillStyle = 'rgba(0,0,0,.28)'; for (let x = 0; x < 128; x += 32) g.fillRect(x, 0, 2, 32);
  g.fillStyle = 'rgba(0,0,0,.18)'; g.fillRect(0, 24, 128, 8);
  g.fillStyle = 'rgba(255,255,255,.1)'; for (let x = 5; x < 128; x += 32){ g.fillRect(x, 9, 20, 2); g.fillRect(x, 15, 14, 2); }
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}
function boardTexture(big){
  const c = document.createElement('canvas'); c.width = 128; c.height = big ? 64 : 40; const g = c.getContext('2d');
  g.fillStyle = '#0c1014'; g.fillRect(0, 0, c.width, c.height);
  if (big){
    g.fillStyle = '#1c2e6e'; g.fillRect(34, 14, 30, 36); g.fillStyle = '#c0332c'; g.fillRect(64, 14, 30, 36);
    g.fillStyle = '#f4f1e8'; g.beginPath(); g.arc(64, 30, 10, 0, 7); g.fill(); g.fillStyle = '#cf3a30'; g.fillRect(58, 28, 12, 2);
    g.strokeStyle = '#2f6a58'; g.lineWidth = 2; g.strokeRect(1, 1, c.width - 2, c.height - 2);
  } else {
    for (let y = 4; y < c.height - 3; y += 6) for (let x = 4; x < c.width - 4; x += 4){ if (rr() < .55) { g.fillStyle = ['#5d7a6a', '#486457', '#7d9a86'][(rr() * 3) | 0]; g.fillRect(x, y, 3, 3); } }
  }
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}
function flagTexture(){
  const c = document.createElement('canvas'); c.width = 26; c.height = 16; const g = c.getContext('2d');
  for (let i = 0; i < 8; i++){ g.fillStyle = i % 2 ? '#f3f1ee' : '#c8372f'; g.fillRect(0, i * 2, 26, 2); }
  g.fillStyle = '#24449a'; g.fillRect(0, 0, 11, 9);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}
function adTexture(){
  const c = document.createElement('canvas'); c.width = 104; c.height = 30; const g = c.getContext('2d');
  g.fillStyle = '#f2f0ee'; g.fillRect(0, 0, 104, 30); g.fillStyle = '#c0332c'; g.fillRect(0, 0, 40, 30); g.fillStyle = '#1f55b8'; g.fillRect(40, 0, 64, 30);
  g.fillStyle = '#f2f0ee'; g.fillRect(48, 10, 46, 4); g.fillRect(48, 18, 30, 4); g.fillRect(8, 11, 24, 8);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}
function crowdTexture(c1, c2){
  const c = document.createElement('canvas'); c.width = 256; c.height = 64; const g = c.getContext('2d');
  g.fillStyle = '#2b313a'; g.fillRect(0, 0, 256, 64);
  const cols = ['#8b8d94', '#a5a7ad', '#3e5155', '#c8c4bd', '#3e5155', '#2f3844', '#b4443c', '#4a62a8', '#8b8d94', '#d8d4cc', '#3e5155'];
  for (let y = 1; y < 64; y += 4) for (let x = 0; x < 256; x += 3){
    if (rr() < .1) continue;
    g.fillStyle = cols[(rr() * cols.length) | 0]; g.fillRect(x, y + 1, 3, 3);
    g.fillStyle = ['#e8b88e', '#c88e5e', '#8a5a38', '#f4d0a6', '#3a2a22'][(rr() * 5) | 0]; g.fillRect(x + 1, y, 1, 1);
  }
  g.fillStyle = 'rgba(30,36,50,.35)'; for (let y = 3; y < 64; y += 16) g.fillRect(0, y, 256, 1);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
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
  const near = new THREE.Mesh(new THREE.PlaneGeometry(nreg.xw, nreg.dw), new THREE.MeshBasicMaterial({ map: paintGround(park, nreg), transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 }));
  near.rotation.x = -Math.PI / 2; near.position.set(nreg.x0 + nreg.xw / 2, .02, -(nreg.d0 + nreg.dw / 2)); G.add(near);
  // everything beyond the stands: dark concrete so nothing is ever see-through
  const under = new THREE.Mesh(new THREE.PlaneGeometry(2400, 2400), new THREE.MeshBasicMaterial({ color: 0x1b2230 }));
  under.rotation.x = -Math.PI / 2; under.position.y = -4; G.add(under);

  // the fence and the seating bowl, as strips swept around the angle
  const crowd = crowdTexture(teamCols[0], teamCols[1]);
  const STEP = 3, A0 = -150, A1 = 150, n = (A1 - A0) / STEP;
  const wallH = 8.5;
  // each strip is a ribbon around the park; u runs along the fence in feet so textures keep their size
  const strip = (profile, mat, uFeet, vFeet) => {                // profile: [[dr, y], ...] from the fence outward
    const pos = [], uv = [], idx = [];
    let run = 0, last = null;
    for (let i = 0; i <= n; i++){
      const a = A0 + i * STEP, t = a * D2R, r0 = fenceR(park, a), px = Math.sin(t) * r0, pz = -Math.cos(t) * r0;
      if (last) run += Math.hypot(px - last[0], pz - last[1]); last = [px, pz];
      profile.forEach((pt, j) => { const r = r0 + pt[0]; pos.push(Math.sin(t) * r, pt[1], -Math.cos(t) * r); uv.push(run / uFeet, (pt[1] - profile[0][1]) / (vFeet || 1)); });
    }
    const m = profile.length;
    for (let i = 0; i < n; i++) for (let j = 0; j < m - 1; j++){ const a = i * m + j, b = a + m; idx.push(a, b, a + 1, b, b + 1, a + 1); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx);
    const mesh = new THREE.Mesh(geo, mat); G.add(mesh); return mesh;
  };
  const basic = (c, extra) => new THREE.MeshBasicMaterial(Object.assign({ color: c, side: THREE.DoubleSide }, extra || {}));
  // the wall: padded panels with a lighter cap and a yellow top line
  const wtex = wallTexture(park.wall);
  strip([[0, 0], [0, wallH - 1]], new THREE.MeshBasicMaterial({ map: wtex, side: THREE.DoubleSide }), 32, wallH - 1);
  strip([[0, wallH - 1], [0, wallH]], basic(0xf0c53a), 1, 1);
  // the seating: two tiers of crowd with a dark aisle band between them, then the back wall
  const crowdMat = new THREE.MeshBasicMaterial({ map: crowd, side: THREE.DoubleSide });
  strip([[1.5, wallH + .2], [40, wallH + 9]], crowdMat, 96, 12);                        // the seats rising away from the wall
  strip([[40, wallH + 9], [40, wallH + 13]], basic(0x203a40), 1, 1);                    // the rail
  strip([[40, wallH + 13], [84, wallH + 30]], crowdMat, 96, 12);                        // a second, higher section
  strip([[84, wallH + 30], [84, wallH + 36]], basic(0x1f3a3a), 1, 1);                   // back wall
  strip([[84, wallH + 36], [88, wallH + 37]], basic(0x2f5a52), 1, 1);                   // its cap
  // the batter's eye behind centre field: a plain green wall in front of the lower deck
  const eye = new THREE.Mesh(new THREE.PlaneGeometry(64, 17), new THREE.MeshBasicMaterial({ map: wallTexture('#2f6a48'), side: THREE.DoubleSide }));
  eye.position.set(0, wallH + 8.5, -(fenceR(park, 0) + 1.2)); G.add(eye);
  const frameMat = new THREE.MeshBasicMaterial({ color: 0x2b5a46 }), edgeMat = new THREE.MeshBasicMaterial({ color: 0x3c8a66 });
  const board = (x, y, z, w, h, big) => {
    const grp = new THREE.Group(); grp.position.set(x, y, z); grp.lookAt(0, y, 0);
    grp.add(new THREE.Mesh(new THREE.BoxGeometry(w, h, 4), frameMat));
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(w - 8, h - 6), new THREE.MeshBasicMaterial({ map: boardTexture(big), side: THREE.DoubleSide })); scr.position.z = 2.2; grp.add(scr);
    const top = new THREE.Mesh(new THREE.BoxGeometry(w + 2, 1.4, 4.6), edgeMat); top.position.y = h / 2; grp.add(top);
    const leg = new THREE.Mesh(new THREE.BoxGeometry(w * .7, y - h / 2, 2.4), new THREE.MeshBasicMaterial({ color: 0x244c3c })); leg.position.set(0, -(y / 2), -1.5); grp.add(leg);
    G.add(grp);
  };
  const rc = fenceR(park, 0);
  board(14, 56, -(rc + 105), 66, 40, true);
  board(-62, 38, -(rc + 105), 60, 15, false); board(92, 38, -(rc + 105), 60, 15, false);
  // flags on tall poles
  const flag = (x, y, z) => {
    const pole = new THREE.Mesh(new THREE.BoxGeometry(.5, 20, .5), new THREE.MeshBasicMaterial({ color: 0xcfd6e0 })); pole.position.set(x, y + 10, z); G.add(pole);
    const f = new THREE.Mesh(new THREE.PlaneGeometry(6.4, 4), new THREE.MeshBasicMaterial({ map: flagTexture(), side: THREE.DoubleSide })); f.position.set(x + 3.2, y + 17, z); G.add(f);
  };
  flag(-14, 76, -(rc + 105)); flag(14, 78, -(rc + 105)); flag(42, 76, -(rc + 105));
  flag(-62, 48, -(rc + 100)); flag(92, 48, -(rc + 100));
  // an advertising board off to the right, and the lighting towers
  { const ad = new THREE.Mesh(new THREE.PlaneGeometry(50, 14), new THREE.MeshBasicMaterial({ map: adTexture(), side: THREE.DoubleSide })); ad.position.set(150, 34, -(rc + 105)); G.add(ad); }
  [-120, -62, 62, 118].forEach(a => {
    const r = fenceR(park, a) + 100, t = a * D2R, x = Math.sin(t) * r, z = -Math.cos(t) * r;
    for (const dx of [-3, 3]) for (const dz of [-3, 3]){ const leg = new THREE.Mesh(new THREE.BoxGeometry(.7, 130, .7), new THREE.MeshBasicMaterial({ color: 0x2e3848 })); leg.position.set(x + dx, 65, z + dz); G.add(leg); }
    for (let k = 1; k < 9; k++){ const cr = new THREE.Mesh(new THREE.BoxGeometry(7, .5, .5), new THREE.MeshBasicMaterial({ color: 0x2e3848 })); cr.position.set(x, k * 14, z + 3); G.add(cr); }
    const bank = new THREE.Mesh(new THREE.BoxGeometry(30, 18, 3), new THREE.MeshBasicMaterial({ color: 0xcfd8e8 })); bank.position.set(x, 134, z); bank.lookAt(0, 134, 0); G.add(bank);
  });
  // the city beyond: grey-blue towers, then soft clouds
  for (let i = 0; i < 90; i++){
    const a = -95 + i * 190 / 89 + (rr() - .5) * 2, r = 760 + rr() * 220, h = 30 + rr() * 90 + (Math.abs(a) < 40 ? 20 : 0), w = 22 + rr() * 34, t = a * D2R;
    const col = [0x6e86ab, 0x5d759c, 0x7c93b4, 0x4f6890][(rr() * 4) | 0];
    const bld = new THREE.Mesh(new THREE.BoxGeometry(w, h, w), new THREE.MeshBasicMaterial({ color: col })); bld.position.set(Math.sin(t) * r, h / 2 - 6, -Math.cos(t) * r); G.add(bld);
  }
  [[-22, 175, 80], [14, 185, 120], [48, 168, 70], [-48, 150, 90], [70, 190, 100]].forEach(([a, h, w]) => {
    const t = a * D2R, r = 900, cx = Math.sin(t) * r, cz = -Math.cos(t) * r;
    [[0, 0, w, 9], [-w * .1, 7, w * .6, 7], [w * .18, 12, w * .3, 6]].forEach(([dx, dy, ww, hh]) => { const cl = new THREE.Mesh(new THREE.BoxGeometry(ww, hh, 12), new THREE.MeshBasicMaterial({ color: dy ? 0xffffff : 0xe9f2ff })); cl.position.set(cx + dx, h + dy, cz); cl.lookAt(0, h + dy, 0); G.add(cl); });
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
  // sky: deep blue overhead, pale at the horizon
  const sky = document.createElement('canvas'); sky.width = 4; sky.height = 256; const sg = sky.getContext('2d');
  const gr = sg.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#173070'); gr.addColorStop(.3, '#284b9e'); gr.addColorStop(.44, '#336cf2'); gr.addColorStop(.5, '#6ea2f6'); gr.addColorStop(1, '#a9ccf8'); sg.fillStyle = gr; sg.fillRect(0, 0, 4, 256);
  const st = new THREE.CanvasTexture(sky);
  const dome = new THREE.Mesh(new THREE.SphereGeometry(1500, 24, 16), new THREE.MeshBasicMaterial({ map: st, side: THREE.BackSide, fog: false })); G.add(dome);
  GL.parkKey = park;
}

// ── set up ───────────────────────────────────────────────────────────────────────────────────────
GL.init = function(canvas){
  GL.canvas = canvas;
  GL.renderer = new THREE.WebGLRenderer({ canvas, antialias:false, powerPreference:'default', stencil:false, alpha:false });
  GL.scene = new THREE.Scene(); GL.scene.background = hex('#8cc4ee');
  GL.cam = new THREE.PerspectiveCamera(40, 16 / 9, 3, 3300);
  GL.world = new THREE.Group(); GL.scene.add(GL.world);                            // players, ball
  // the pixel-art pass: the scene is drawn small, then re-coloured with a limited palette and a fine dither
  GL.rt = new THREE.WebGLRenderTarget(4, 4, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
  try { GL.rt.depthTexture = new THREE.DepthTexture(4, 4); GL.rt.depthTexture.type = THREE.UnsignedIntType; } catch (e) {}              // a 24-bit depth buffer, so the ground never flickers
  GL.postMat = new THREE.ShaderMaterial({
    uniforms: { t: { value: GL.rt.texture }, res: { value: new THREE.Vector2(4, 4) }, levels: { value: 16 }, dith: { value: .45 } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
    fragmentShader: `uniform sampler2D t; uniform vec2 res; uniform float levels; uniform float dith; varying vec2 vUv;
      float bayer(vec2 p){ vec2 q = floor(p); float x1 = mod(q.x, 2.), y1 = mod(q.y, 2.), x2 = mod(floor(q.x / 2.), 2.), y2 = mod(floor(q.y / 2.), 2.);
        return (abs(x1 - y1) * 8. + y1 * 4. + abs(x2 - y2) * 2. + y2) / 16.; }
      void main(){ vec3 c = texture2D(t, vUv).rgb; float b = bayer(vUv * res) - .5;
        c = clamp(c + b * dith / levels, 0., 1.); c = floor(c * levels + .5) / levels;
        gl_FragColor = vec4(c, 1.); }`,
    depthTest: false, depthWrite: false });
  GL.postScene = new THREE.Scene(); GL.postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  GL.postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), GL.postMat));
  GL.ready = true;
};
GL.setPark = function(park, teamCols){ buildPark(park, teamCols || ['#2c4a8a', '#c0392b']); GL.park = park; };
GL.resize = function(w, h){
  const rows = GL.rows, cols = Math.round(rows * w / h);
  GL.renderer.setSize(cols, rows, false); GL.rt.setSize(cols, rows); GL.postMat.uniforms.res.value.set(cols, rows);
  GL.canvas.style.width = w + 'px'; GL.canvas.style.height = h + 'px'; GL.canvas.style.imageRendering = 'pixelated';
  GL.cam.aspect = cols / rows; GL.cam.updateProjectionMatrix();
};
// the cameras: behind the plate looking out at the mound, or high above the park looking down
GL.setView = function(v){ GL.view = v; };
GL.placeCamera = function(){
  const c = GL.cam;
  if (GL.view === 'bat'){ c.fov = 33.4; c.up.set(0, 1, 0); c.position.set(.15, 8.4, 21.5); c.lookAt(.15, 8.4 - Math.tan(7.44 * D2R) * 100, 21.5 - 100); }
  else if (GL.view === 'free'){ const f = GL.freeCam; c.fov = f.fov; c.up.set(0, 1, 0); c.position.set(...f.pos); c.lookAt(...f.look); }
  else if (GL.view === 'top'){ c.fov = 46; c.up.set(0, 0, -1); c.position.set(0, 470, 78); c.lookAt(0, 0, -170); }
  else { c.fov = 60; c.up.set(0, 1, 0); c.position.set(0, 100, 50); c.lookAt(0, 0, -112); }          // the press box: 100 ft up, 50 ft behind the plate
  c.updateProjectionMatrix();
};
GL.render = function(){
  GL.placeCamera();
  if (GL.post === false){ GL.renderer.render(GL.scene, GL.cam); return; }
  GL.renderer.setRenderTarget(GL.rt); GL.renderer.render(GL.scene, GL.cam);
  GL.renderer.setRenderTarget(null); GL.renderer.render(GL.postScene, GL.postCam);
};
})();
