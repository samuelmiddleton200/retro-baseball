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

const matCache = {};
const lam = c => matCache[c] || (matCache[c] = new THREE.MeshLambertMaterial({ color: c }));
const OUT = new THREE.MeshBasicMaterial({ color: 0x0b0d16, side: THREE.BackSide });

// a box limb part, with a dark inflated copy behind it for the pixel-art outline
function part(w, h, d, color, ox = 0, oy = 0, oz = 0, outline = true){
  const g = new THREE.BoxGeometry(w, h, d), m = new THREE.Mesh(g, lam(color));
  m.position.set(ox, oy, oz);
  if (outline){ const o = new THREE.Mesh(g, OUT); o.scale.set(1 + .09 / w * 2, 1 + .09 / h * 2, 1 + .09 / d * 2); m.add(o); }
  return m;
}
const piv = (parent, x = 0, y = 0, z = 0) => { const o = new THREE.Object3D(); o.position.set(x, y, z); parent.add(o); return o; };

GL.makePlayer = function(o){
  // o: { skin, hair, cap (jersey colour), cap2 (trim), pants, kind: 'field'|'bat'|'catch'|'ump'|'pitch'|'run', number, lefty }
  const skin = o.skin || '#d9a577', jersey = o.shirt || o.cap || '#2c4a8a', trim = o.cap2 || '#d94a3c', pants = o.pants || '#dfe2ea', cap = o.cap || '#2c4a8a';
  const P = { o, root: new THREE.Group() };
  const root = P.root;
  P.hips = piv(root, 0, 3, 0);
  P.hips.add(part(1.12, .5, .68, pants));
  P.spine = piv(P.hips, 0, .22, 0);
  // torso: a chest and a belly, jersey over a belt
  P.spine.add(part(1.3, 1.28, .78, jersey, 0, .78, 0));
  P.spine.add(part(1.18, .22, .72, '#2a2a33', 0, .09, 0));                       // belt
  if (o.kind === 'catch'){ P.spine.add(part(1.36, 1.1, .6, o.cap2 || '#2c4a8a', 0, .8, .1)); }   // chest protector
  P.neck = piv(P.spine, 0, 1.55, 0);
  P.head = piv(P.neck, 0, .18, 0);
  P.head.add(part(.64, .66, .66, skin, 0, .32, 0));
  // face: two eyes
  const eyeM = lam('#1b1520');
  [-.15, .15].forEach(x => { const e = new THREE.Mesh(new THREE.BoxGeometry(.1, .1, .04), eyeM); e.position.set(x, .38, .34); P.head.add(e); });
  const mouth = new THREE.Mesh(new THREE.BoxGeometry(.16, .05, .03), lam('#8a4a3a')); mouth.position.set(0, .14, .34); P.head.add(mouth);
  if (o.kind === 'catch' || o.kind === 'ump'){
    // a mask: dark bars over the face, and a hard hat
    P.head.add(part(.7, .7, .1, '#20242e', 0, .3, .4, false));
    P.head.add(part(.72, .36, .7, o.kind === 'catch' ? cap : '#16191f', 0, .62, 0));
  } else if (o.kind === 'bat'){
    P.head.add(part(.76, .42, .76, '#16203a', 0, .62, 0));                       // helmet dome
    P.head.add(part(.14, .34, .5, '#16203a', .38, .38, .02, false));             // ear flap (left)
    P.head.add(part(.7, .08, .3, '#16203a', 0, .5, .46, false));                 // short brim
  } else {
    P.head.add(part(.72, .3, .72, cap, 0, .62, 0));                              // the cap
    P.head.add(part(.64, .07, .5, cap, 0, .5, .46, false));                      // the brim
  }
  const hair = part(.68, .22, .12, o.hair || '#2a1c14', 0, .5, -.34, false); P.head.add(hair);
  // arms
  const arm = (side) => {                                                       // side: +1 is the player's left
    const sh = piv(P.spine, side * BODY.shW, 1.3, 0), el = piv(sh, 0, -BODY.upper, 0), wr = piv(el, 0, -BODY.fore, 0);
    sh.add(part(.38, BODY.upper + .1, .38, jersey, 0, -BODY.upper / 2, 0));
    el.add(part(.32, BODY.fore + .06, .32, o.long ? jersey : skin, 0, -BODY.fore / 2, 0));
    const hand = part(.3, .3, .3, skin, 0, -.14, 0); wr.add(hand);
    return { sh, el, wr, side, hand };
  };
  P.L = arm(1); P.R = arm(-1);
  // legs
  const leg = (side) => {
    const hp = piv(P.hips, side * BODY.hipW, -.2, 0), kn = piv(hp, 0, -BODY.thigh, 0), an = piv(kn, 0, -BODY.shin, 0);
    hp.add(part(.5, BODY.thigh + .08, .5, pants, 0, -BODY.thigh / 2, 0));
    kn.add(part(.42, BODY.shin + .06, .44, pants, 0, -BODY.shin / 2, 0));
    kn.add(part(.44, .5, .46, o.sock || trim, 0, -BODY.shin + .5, 0, false));  // the sock showing
    an.add(part(.46, .26, .95, '#17151d', 0, -.12, .26));                           // the shoe
    return { hp, kn, an, side };
  };
  P.LL = leg(1); P.RL = leg(-1);
  // props
  if (o.kind === 'bat'){
    P.bat = new THREE.Group();
    const barrel = part(.36, 1.7, .36, '#d7a15a', 0, 2.2, 0); P.bat.add(barrel);
    P.bat.add(part(.18, 1.6, .18, '#d7a15a', 0, .8, 0)); P.bat.add(part(.3, .3, .3, '#d7a15a', 0, -.1, 0, false));
    P.bat.add(part(.2, .5, .2, '#2b2b33', 0, .35, 0, false));                                // the tape
    root.add(P.bat);
  }
  if (o.glove){ P.glove = part(.62, .62, .5, '#8a5a2c', 0, -.3, .12); P.L.wr.add(P.glove); }
  // soft shadow on the ground
  const sh = new THREE.Mesh(new THREE.CircleGeometry(1.15, 14), new THREE.MeshBasicMaterial({ color: 0x0c1408, transparent: true, opacity: .34, depthWrite: false }));
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
  P.spine.rotation.set(-p.lean * D2R, p.twist * D2R, p.side * D2R);
  P.head.rotation.set(-p.headPitch * D2R, (p.headYaw - p.twist) * D2R, 0);
  P.root.updateMatrixWorld(true);
  const W = v => P.root.localToWorld(V3(v[0], v[1], v[2]));
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
      const gl = P.root.worldToLocal(grip.clone());
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
