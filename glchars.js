/* ───────────────────────────────────────────────────────────────────────────
   The people.  Every player is a skeleton of pivots with boxy limbs on it, bent by two-bone IK so
   hands reach for the bat or the ball and feet stay planted.  Local axes: +Z forward, +Y up,
   the player's LEFT is +X.  Units: feet.  A player is about 6 ft tall.
   ─────────────────────────────────────────────────────────────────────────── */
(function(){
'use strict';
const GL = window.GL3D, D2R = Math.PI / 180;
const lerp = (a, b, t) => a + (b - a) * t, clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

const BODY = { thigh:1.5, shin:1.5, upper:1.02, fore:0.98, torso:1.62, hipW:.36, shW:.82 };

// every colour gets a small hand-shaded texture: light from the top, a dark underside, a lit left edge, a few seams and speckle,
// so a flat patch of one colour becomes a surface with several tones (this is where the extra pixel detail comes from)
const shadeTexCache = {};
function shadeTex(color){
  if (shadeTexCache[color]) return shadeTexCache[color];
  const c = document.createElement('canvas'); c.width = 16; c.height = 32; const g = c.getContext('2d');
  const base = new THREE.Color(color), WH = new THREE.Color(1, 1, 1), L = (k) => '#' + (k <= 1 ? base.clone().multiplyScalar(k) : base.clone().lerp(WH, (k - 1) * .9)).getHexString();
  const bands = [1.22, 1.14, 1.06, 1.0, 1.0, .96, .92, .88, .84, .8, .76, .72];
  for (let y = 0; y < 32; y++){ g.fillStyle = L(bands[Math.min(bands.length - 1, Math.floor(y / 32 * bands.length))]); g.fillRect(0, y, 16, 1); }
  g.fillStyle = L(1.3); g.fillRect(0, 0, 1, 32); g.fillRect(1, 0, 1, 14);                  // a lit left edge
  g.fillStyle = L(.6); g.fillRect(15, 0, 1, 32); g.fillRect(14, 10, 1, 22);                // a dark right edge
  g.fillStyle = L(.68); g.fillRect(0, 31, 16, 1); g.fillRect(0, 27, 16, 1);                // a shadowed underside
  let sd = 3; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 26; i++){ g.fillStyle = L(rnd() < .5 ? 1.1 : .88); g.fillRect((rnd() * 16) | 0, (rnd() * 30) | 0, 1, 1); }   // fabric speckle
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; shadeTexCache[color] = t; return t;
}
const matCache = {};
const lam = c => matCache[c] || (matCache[c] = new THREE.MeshLambertMaterial({ color: 0xffffff, map: shadeTex(c) }));
const OUT = new THREE.MeshBasicMaterial({ color: 0x0b0d16, side: THREE.BackSide });

// a box limb part, with a dark inflated copy behind it for the pixel-art outline
function part(w, h, d, color, ox = 0, oy = 0, oz = 0, outline = true){
  const g = new THREE.BoxGeometry(w, h, d), m = new THREE.Mesh(g, lam(color));
  m.position.set(ox, oy, oz);
  if (outline){ const o = new THREE.Mesh(g, OUT); o.scale.set(1 + .09 / w * 2, 1 + .09 / h * 2, 1 + .09 / d * 2); m.add(o); }
  return m;
}
// a rounded part: a low-poly ellipsoid (or just its top half, for a dome), flat-shaded so it still reads as pixels
const flatCache = {};
const lamF = c => flatCache[c] || (flatCache[c] = new THREE.MeshLambertMaterial({ color: 0xffffff, map: shadeTex(c), flatShading: true }));
function blob(w, h, d, color, ox = 0, oy = 0, oz = 0, outline = true, dome = false){
  const g = dome ? new THREE.SphereGeometry(.5, 12, 6, 0, Math.PI * 2, 0, Math.PI / 2) : new THREE.SphereGeometry(.5, 12, 8);
  const m = new THREE.Mesh(g, lamF(color)); m.scale.set(w, h, d); m.position.set(ox, oy, oz);
  if (outline){ const o = new THREE.Mesh(g, OUT); o.scale.set(1 + .1 / w * 2, 1 + .1 / h * 2, 1 + .1 / d * 2); m.add(o); }
  return m;
}
const piv = (parent, x = 0, y = 0, z = 0) => { const o = new THREE.Object3D(); o.position.set(x, y, z); parent.add(o); return o; };

// a canvas used as the back of a jersey: team colour, a trim stripe, and the player's number
function backTexture(col, trim, num){
  const c = document.createElement('canvas'); c.width = 32; c.height = 32; const g = c.getContext('2d');
  g.fillStyle = col; g.fillRect(0, 0, 32, 32); g.fillStyle = 'rgba(0,0,0,.18)'; g.fillRect(0, 26, 32, 6); g.fillStyle = trim; g.fillRect(0, 0, 32, 2);
  g.fillStyle = '#f4f1e8'; g.font = 'bold 15px monospace'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(String(num || 7), 16, 15);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}
// the face: eyes with whites, irises and a highlight, brows, a shaded nose, a mouth, cheek blush and a jaw shadow, drawn pixel by pixel
const faceCache = {};
function faceTexture(skin, hair, mood){
  const key = skin + hair + (mood || ''); if (faceCache[key]) return faceCache[key];
  const c = document.createElement('canvas'); c.width = 24; c.height = 24; const g = c.getContext('2d');
  const sk = new THREE.Color(skin), sh = '#' + sk.clone().multiplyScalar(.74).getHexString(), lt = '#' + sk.clone().lerp(new THREE.Color(1, 1, 1), .22).getHexString(), bl = '#' + sk.clone().lerp(new THREE.Color('#e0605a'), .28).getHexString();
  const px = (x, y, w, h, col) => { g.fillStyle = col; g.fillRect(x, y, w, h); };
  px(0, 15, 24, 9, sh); px(1, 14, 22, 1, sh);                                  // the jaw falls into shadow
  px(3, 8, 3, 3, bl); px(18, 8, 3, 3, bl);                                       // cheeks
  px(9, 4, 6, 2, lt);                                                              // light on the brow ridge
  // eyes: white, iris, pupil, highlight, lid line
  [[5, 8], [15, 8]].forEach(([x, y]) => { px(x, y, 4, 4, '#f4f1ea'); px(x + 1, y, 3, 4, '#3a2a1c'); px(x + 2, y + 1, 1, 3, '#0c0a10'); px(x + 1, y, 1, 1, '#ffffff'); px(x, y - 1, 4, 1, sh); });
  px(4, 5, 5, 1, hair); px(15, 5, 5, 1, hair); px(5, 4, 3, 1, hair); px(16, 4, 3, 1, hair);   // brows
  px(11, 9, 2, 5, sh); px(10, 14, 4, 1, sh); px(12, 9, 1, 3, lt);                  // the nose
  px(8, 17, 8, 1, '#7a3a2e'); px(9, 18, 6, 1, '#a0584a'); px(8, 16, 1, 1, sh); px(15, 16, 1, 1, sh);   // the mouth
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; faceCache[key] = t; return t;
}
function frontTexture(col, trim, ab){
  const c = document.createElement('canvas'); c.width = 32; c.height = 32; const g = c.getContext('2d');
  g.fillStyle = col; g.fillRect(0, 0, 32, 32);
  g.fillStyle = 'rgba(255,255,255,.14)'; g.fillRect(0, 0, 32, 5); g.fillStyle = 'rgba(0,0,0,.2)'; g.fillRect(0, 25, 32, 7);
  g.fillStyle = trim; g.fillRect(14, 0, 4, 32); g.fillStyle = 'rgba(0,0,0,.35)'; g.fillRect(14, 0, 1, 32);   // the placket
  g.fillStyle = '#f4f1e8'; for (let y = 6; y < 28; y += 6){ g.fillRect(15, y, 2, 2); }                      // buttons
  g.fillStyle = '#f4f1e8'; g.font = 'bold 8px monospace'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText((ab || '').slice(0, 3), 8, 12); g.fillRect(2, 18, 12, 1);                                       // team letters on the chest
  g.fillStyle = trim; g.fillRect(0, 0, 32, 2);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}
function logoTexture(col, trim, letter){
  const c = document.createElement('canvas'); c.width = 16; c.height = 16; const g = c.getContext('2d');
  g.clearRect(0, 0, 16, 16); g.fillStyle = trim; g.beginPath(); g.arc(8, 8, 7, 0, 7); g.fill();
  g.fillStyle = '#f6f3ea'; g.font = 'bold 11px monospace'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(letter || 'N', 8, 9);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; return t;
}
const HEADK = 2.0;                                 // chibi: the head is big
GL.makePlayer = function(o){
  // o: { skin, hair, cap (jersey/cap colour), cap2 (trim), pants, kind: 'field'|'bat'|'catch'|'ump'|'pitch'|'run', number }
  const skin = o.skin || '#d9a577', jersey = o.shirt || o.cap || '#2c4a8a', trim = o.cap2 || '#d94a3c', pants = o.pants || '#dfe2ea', cap = o.cap || '#2c4a8a';
  const P = { o, root: new THREE.Group() };
  const root = P.root;
  P.body = new THREE.Group(); root.add(P.body); P.body.scale.set(.86, .86, .86);
  P.hips = piv(P.body, 0, 3, 0);
  P.hips.add(part(1.3, .5, .85, pants));
  P.spine = piv(P.hips, 0, .22, 0);
  // torso: jersey with a numbered back
  const dark = lam(jersey), back = new THREE.MeshLambertMaterial({ map: backTexture(jersey, trim, o.number) }), front = new THREE.MeshLambertMaterial({ map: frontTexture(jersey, trim, o.ab) });
  const tg = new THREE.BoxGeometry(1.5, 1.3, .92), torso = new THREE.Mesh(tg, [dark, dark, dark, dark, o.kind === 'catch' ? dark : front, back]); torso.position.set(0, .78, 0);
  const to = new THREE.Mesh(tg, OUT); to.scale.set(1.09, 1.1, 1.1); torso.add(to); P.spine.add(torso);
  P.spine.add(part(1.36, .2, .86, '#26262e', 0, .08, 0));                          // belt
  P.spine.add(part(.5, .12, .2, '#f4f1e8', 0, 1.46, .4, false));                  // collar / placket
  if (o.kind === 'catch'){
    P.spine.add(part(1.7, 1.2, .78, o.cap2 || '#2c4a8a', 0, .8, .16));                       // chest protector
    [-1, 1].forEach(sx => P.spine.add(part(.62, .5, .74, o.cap2 || '#2c4a8a', sx * 1.0, 1.28, .05)));   // shoulder pads
    P.spine.add(part(.16, 1.0, .1, '#e8edf8', -.42, .8, -.26, false)); P.spine.add(part(.16, 1.0, .1, '#e8edf8', .42, .8, -.26, false));   // straps
  }
  if (o.kind === 'ump') [-1, 1].forEach(sx => P.spine.add(part(.6, .42, .72, '#20242e', sx * .98, 1.28, .05)));
  P.neck = piv(P.spine, 0, 1.4, 0);
  P.head = piv(P.neck, 0, .06, 0);
  const hs = (o.kind === 'catch' || o.kind === 'ump') ? 1.55 : HEADK;
  P.head.add(blob(.7 * hs, .68 * hs, .66 * hs, skin, 0, .32 * hs, 0));
  // face: big eyes with a highlight, a brow, a nose and a mouth
  const face = new THREE.Mesh(new THREE.PlaneGeometry(.62 * hs, .62 * hs), new THREE.MeshLambertMaterial({ map: faceTexture(skin, o.hair || '#2a1c14'), transparent: true }));
  face.position.set(0, .31 * hs, .33 * hs + .015); P.head.add(face);
  if (o.kind === 'catch' || o.kind === 'ump'){
    P.head.add(part(.68 * hs, .66 * hs, .1, '#1b1f2a', 0, .3 * hs, .34 * hs, false));                 // the mask
    const hc = o.kind === 'catch' ? (o.helm || '#2547a8') : '#16191f';
    P.head.add(blob(.84 * hs, .8 * hs, .82 * hs, hc, 0, .38 * hs, -.03 * hs));                          // one round helmet over the whole head
    P.head.add(part(.5 * hs, .06 * hs, .4 * hs, '#e8edf8', 0, .74 * hs, -.03 * hs, false));               // a shine on top
  } else if (o.kind === 'bat' || o.kind === 'run'){
    const hc2 = o.cap || '#15204a'; const hel = blob(.8 * hs, .62 * hs, .76 * hs, hc2, 0, .5 * hs, -.01 * hs, true, true); P.head.add(hel);
    P.head.add(blob(.34 * hs, .12 * hs, .3 * hs, '#7f9ee4', -.1 * hs, .78 * hs, .08 * hs, false));  // a bright gloss on the dome
    P.head.add(part(.16 * hs, .42 * hs, .46 * hs, hc2, .36 * hs, .38 * hs, .02, false));         // ear flap
    P.head.add(part(.6 * hs, .06 * hs, .26 * hs, hc2, 0, .56 * hs, .42 * hs, false));            // short brim
  } else {
    P.head.add(blob(.76 * hs, .6 * hs, .74 * hs, cap, 0, .5 * hs, -.01 * hs, true, true));                  // the cap
    { const lg = new THREE.Mesh(new THREE.PlaneGeometry(.26 * hs, .26 * hs), new THREE.MeshLambertMaterial({ map: logoTexture(cap, trim, (o.ab || 'N')[0]), transparent: true })); lg.position.set(0, .7 * hs, .39 * hs); lg.rotation.x = -.18; P.head.add(lg); }   // the cap logo
    P.head.add(part(.6 * hs, .07 * hs, .46 * hs, cap, 0, .56 * hs, .42 * hs, false));                  // the brim
  }
  P.head.add(blob(.72 * hs, .5 * hs, .42 * hs, o.hair || '#2a1c14', 0, .4 * hs, -.2 * hs, false));
  // arms
  const arm = (side) => {                                                       // side: +1 is the player's left
    const sh = piv(P.spine, side * .96, 1.22, 0), el = piv(sh, 0, -BODY.upper, 0), wr = piv(el, 0, -BODY.fore, 0);
    sh.add(part(.5, BODY.upper + .1, .5, o.sleeve || jersey, 0, -BODY.upper / 2, 0));
    el.add(part(.42, BODY.fore + .06, .42, o.kind === 'bat' || o.kind === 'run' ? (o.sleeve || '#15204a') : skin, 0, -BODY.fore / 2, 0));
    const hand = blob(.46, .46, .46, o.kind === 'bat' || o.kind === 'run' ? '#f6f4ee' : skin, 0, -.16, 0); wr.add(hand);
    return { sh, el, wr, side, hand };
  };
  P.L = arm(1); P.R = arm(-1);
  const leg = (side) => {
    const hp = piv(P.hips, side * .42, -.2, 0), kn = piv(hp, 0, -BODY.thigh, 0), an = piv(kn, 0, -BODY.shin, 0);
    hp.add(part(.66, BODY.thigh + .08, .66, pants, 0, -BODY.thigh / 2, 0));
    hp.add(part(.07, BODY.thigh + .02, .5, trim, side * .34, -BODY.thigh / 2, 0, false));                  // the stripe down the pants
    kn.add(part(.56, BODY.shin + .06, .58, pants, 0, -BODY.shin / 2, 0));
    kn.add(part(.6, .55, .62, o.sock || pants, 0, -BODY.shin + .5, 0, false));
    kn.add(part(.62, .1, .64, trim, 0, -BODY.shin + .72, 0, false)); kn.add(part(.62, .1, .64, '#f1efe8', 0, -BODY.shin + .58, 0, false));   // stirrup bands
    an.add(part(.6, .24, 1.15, '#17151d', 0, -.04, .32)); an.add(part(.2, .05, .5, '#f1efe8', 0, .09, .5, false)); an.add(part(.04, .16, .5, '#f1efe8', side * .3, -.02, .32, false));   // laces and a side flash an.add(part(.62, .1, 1.18, '#f1efe8', 0, -.2, .32, false));   // a black shoe on a white sole
    return { hp, kn, an, side };
  };
  P.LL = leg(1); P.RL = leg(-1);
  if (o.kind === 'bat'){
    // a real bat: a thin handle that flares into a barrel (max 2.5 in across, about 34 in long), with a knob
    P.bat = new THREE.Group();
    const wood = '#dcab6c', tape = '#2b2b33';
    const seg = (r0, r1, y0, y1, col, outline) => { const g = new THREE.CylinderGeometry(r1, r0, y1 - y0, 8); const m = new THREE.Mesh(g, lamF(col)); m.position.y = (y0 + y1) / 2; if (outline){ const o = new THREE.Mesh(g, OUT); o.scale.set(1.35, 1.01, 1.35); m.add(o); } P.bat.add(m); };
    seg(.095, .095, -.12, 0, wood, true);                 // the knob
    seg(.055, .055, 0, 1.15, tape, true);                 // the taped handle
    seg(.055, .125, 1.15, 2.2, wood, true);               // it flares out
    seg(.125, .125, 2.2, 3.6, wood, true);                // the barrel
    const cap = new THREE.Mesh(new THREE.SphereGeometry(.125, 8, 5, 0, Math.PI * 2, 0, Math.PI / 2), lamF(wood)); cap.position.y = 3.6; P.bat.add(cap);
    seg(.13, .13, 3.0, 3.1, '#a8743a', false);            // a mark on the barrel
    P.body.add(P.bat);
  }
  if (o.glove){ P.glove = part(.8, .8, .62, '#8a5a2c', 0, -.36, .14); P.L.wr.add(P.glove); }
  const sh = new THREE.Mesh(new THREE.CircleGeometry(1.3, 14), new THREE.MeshBasicMaterial({ color: 0x0c1408, transparent: true, opacity: .34, depthWrite: false }));
  sh.rotation.x = -Math.PI / 2; sh.position.y = .05; sh.scale.set(1, .62, 1); root.add(sh); P.shadow = sh;
  P.pose = {};
  return P;
};

// ── two-bone IK: put the hand (or foot) at a target, bending the elbow (or knee) toward a hint ─────
const _a = V3(0, 0, 0), _b = V3(0, 0, 0), _c = V3(0, 0, 0), _d = V3(0, 0, 0), _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion();
const DOWN = V3(0, -1, 0);
function ik(parentObj, shoulder, elbow, wrist, L1, L2, targetW, hintW){
  // all of this works in the shoulder's parent frame
  parentObj.updateMatrixWorld(true);
  const T = parentObj.worldToLocal(targetW.clone()), H = parentObj.worldToLocal(hintW.clone()), S = shoulder.position.clone();
  const v = T.clone().sub(S); let d = v.length(); const maxD = L1 + L2 - .02;
  if (d > maxD){ v.multiplyScalar(maxD / d); d = maxD; }
  if (d < .15){ d = .15; v.set(0, -.15, 0); }
  const dir = v.clone().normalize();
  const a = (L1 * L1 - L2 * L2 + d * d) / (2 * d), h = Math.sqrt(Math.max(0, L1 * L1 - a * a));
  const hint = H.clone().sub(S); hint.addScaledVector(dir, -hint.dot(dir));
  if (hint.lengthSq() < 1e-6) hint.set(0, 0, 1);
  hint.normalize();
  const E = S.clone().addScaledVector(dir, a).addScaledVector(hint, h);
  shoulder.quaternion.setFromUnitVectors(DOWN, E.clone().sub(S).normalize());
  // forearm direction expressed in the upper arm's frame
  const fw = T.clone().sub(E).normalize();
  const inv = shoulder.quaternion.clone().invert();
  fw.applyQuaternion(inv);
  elbow.quaternion.setFromUnitVectors(DOWN, fw);
}

// ── a pose is plain numbers, so it can be blended; everything is in the player's own frame ────────
// hips:[x,y,z]  lean (deg, forward)  twist (deg)  side (deg)  head:[yaw,pitch]  hands L/R:[x,y,z]  feet L/R:[x,y,z]
// elbowHint/kneeHint: where the joint should point, in player space
const BASEPOSE = {
  hips:[0, 3.0, 0], lean:0, twist:0, side:0, headYaw:0, headPitch:0,
  L:[.95, 3.0, .15], R:[-.95, 3.0, .15], Lh:[.4, 0, -.5], Rh:[-.4, 0, -.5],
  LF:[.36, 0, 0], RF:[-.36, 0, 0], LFy:0, RFy:0, Lk:[.1, 0, 1], Rk:[-.1, 0, 1],
  bat:null, glove:0,
};
GL.BASEPOSE = BASEPOSE;
const lerpA = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
GL.blendPose = function(A, B, t){
  const o = {};
  for (const k in BASEPOSE){
    const a = A[k] !== undefined ? A[k] : BASEPOSE[k], b = B[k] !== undefined ? B[k] : BASEPOSE[k];
    if (Array.isArray(a) && Array.isArray(b)) o[k] = lerpA(a, b, t);
    else if (typeof a === 'number' && typeof b === 'number') o[k] = lerp(a, b, t);
    else o[k] = t < .5 ? a : b;
  }
  return o;
};
GL.applyPose = function(P, pose){
  const p = Object.assign({}, BASEPOSE, pose);
  P.pose = p;
  P.hips.position.set(p.hips[0], p.hips[1], p.hips[2]);
  P.spine.rotation.set(p.lean * D2R, p.twist * D2R, p.side * D2R);   // positive lean tips the chest toward the way he faces
  P.head.rotation.set(-p.headPitch * D2R, (p.headYaw - p.twist) * D2R, 0);
  P.root.updateMatrixWorld(true);
  const W = v => P.body.localToWorld(V3(v[0], v[1], v[2]));
  // legs first (the hips are already placed)
  [[P.LL, p.LF, p.Lk, p.LFy], [P.RL, p.RF, p.Rk, p.RFy]].forEach(([l, f, k, fy]) => {
    const hip = l.hp;
    hip.quaternion.identity(); l.kn.quaternion.identity();
    ik(P.hips, hip, l.kn, l.an, BODY.thigh, BODY.shin, W([f[0], f[1] + .1, f[2]]), W([f[0] + k[0], f[1] + 2 + k[1], f[2] + k[2] * 3]));
    l.an.rotation.set(0, 0, 0);
    // keep the foot level and pointing along fy
    P.root.updateMatrixWorld(true);
    const q = new THREE.Quaternion(); l.an.getWorldQuaternion(q);
    const want = new THREE.Quaternion().setFromAxisAngle(V3(0, 1, 0), fy * D2R);
    const par = new THREE.Quaternion(); l.an.parent.getWorldQuaternion(par);
    const rw = new THREE.Quaternion(); P.root.getWorldQuaternion(rw);
    l.an.quaternion.copy(par.invert()).multiply(rw).multiply(want);
  });
  // arms, from the torso
  P.spine.updateMatrixWorld(true);
  [[P.L, p.L, p.Lh], [P.R, p.R, p.Rh]].forEach(([a, tgt, hint]) => {
    a.sh.quaternion.identity(); a.el.quaternion.identity();
    ik(P.spine, a.sh, a.el, a.wr, BODY.upper, BODY.fore, W(tgt), W([tgt[0] + hint[0] * 2, tgt[1] + hint[1] * 2 - 1, tgt[2] + hint[2] * 2]));
  });
  P.root.updateMatrixWorld(true);
  if (P.bat){
    if (p.bat){
      const l = P.L.wr.getWorldPosition(V3(0, 0, 0)), r = P.R.wr.getWorldPosition(V3(0, 0, 0));
      const grip = l.clone().add(r).multiplyScalar(.5);
      P.bat.visible = true;
      const gl = P.body.worldToLocal(grip.clone());
      P.bat.position.copy(gl);
      const d = V3(p.bat[0], p.bat[1], p.bat[2]).normalize();
      P.bat.quaternion.setFromUnitVectors(V3(0, 1, 0), d);
    } else P.bat.visible = false;
  }
  if (P.glove) P.glove.visible = true;
};
// put the player somewhere in the park, facing a direction (yaw 0 faces +Z, toward the batter's camera)
GL.place = function(P, X, Z, yaw, scale){
  P.root.position.set(X, 0, Z); P.root.rotation.y = yaw; const s = scale || 1; P.root.scale.set(s, s, s);
};
})();
