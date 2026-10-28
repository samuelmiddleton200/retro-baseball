/* The stage: takes a plain description of the moment (who is where, doing what) and puts the 3D
   people, the ball and the camera in place, then draws it.  The game's engine never touches three.js;
   it only fills in the description each frame.                                                       */
(function(){
'use strict';
const GL = window.GL3D, D2R = Math.PI / 180, lerp = (a, b, t) => a + (b - a) * t, clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const ents = {};                                 // every person on the field, by key
let trailPts = null, seen = new Set(), lightsOn = false, ballMesh = null, shadowMesh = null, dots = [], zoneBox = null, trailLine = null, poolBall = null;

function lightsInit(){
  if (lightsOn) return; lightsOn = true;
  GL.scene.add(new THREE.AmbientLight(0xffffff, .72));
  const d = new THREE.DirectionalLight(0xfff0d8, .55); d.position.set(-40, 80, 60); GL.scene.add(d);
  // the ball
  const c = document.createElement('canvas'); c.width = 64; c.height = 32; const g = c.getContext('2d');
  g.fillStyle = '#f7f4ea'; g.fillRect(0, 0, 64, 32); g.fillStyle = '#e9e4d6'; g.fillRect(0, 22, 64, 10);
  g.strokeStyle = '#cf3a30'; g.lineWidth = 2.4;
  for (let i = 0; i < 2; i++){ g.beginPath(); for (let k = 0; k <= 16; k++){ const x = 8 + i * 32 + Math.sin(k / 16 * Math.PI) * 6 * (i ? -1 : 1) * -1, y = k * 2; k ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); }
  g.fillStyle = '#cf3a30'; for (let k = 2; k < 16; k += 2){ g.fillRect(8 + Math.sin(k / 16 * Math.PI) * 6 - 2, k * 2, 4, 1); g.fillRect(40 - Math.sin(k / 16 * Math.PI) * 6 - 2, k * 2, 4, 1); }
  const tex = new THREE.CanvasTexture(c); tex.magFilter = THREE.NearestFilter; tex.minFilter = THREE.NearestFilter;
  ballMesh = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 9), new THREE.MeshBasicMaterial({ map: tex })); GL.scene.add(ballMesh);
  ballMesh.add(new THREE.Mesh(new THREE.SphereGeometry(1, 12, 9), new THREE.MeshBasicMaterial({ color: 0x1a1d2b, side: THREE.BackSide }))).scale.set(1.12, 1.12, 1.12);
  shadowMesh = new THREE.Mesh(new THREE.CircleGeometry(1, 14), new THREE.MeshBasicMaterial({ color: 0x0a1206, transparent: true, opacity: .45, depthWrite: false }));
  shadowMesh.rotation.x = -Math.PI / 2; GL.scene.add(shadowMesh);
  for (let i = 0; i < 14; i++){ const m = new THREE.Mesh(new THREE.SphereGeometry(1, 6, 5), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true })); m.visible = false; GL.scene.add(m); dots.push(m); }
  // the strike zone: an outline over the plate
  const pts = [[-.95, 1.35], [.95, 1.35], [.95, 3.75], [-.95, 3.75]].map(p => new THREE.Vector3(p[0], p[1], -.7));
  const zg = new THREE.Group(); zg.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .55 })));
  const gl = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(-.317, 1.35, -.7), new THREE.Vector3(-.317, 3.75, -.7), new THREE.Vector3(.317, 1.35, -.7), new THREE.Vector3(.317, 3.75, -.7),
    new THREE.Vector3(-.95, 2.15, -.7), new THREE.Vector3(.95, 2.15, -.7), new THREE.Vector3(-.95, 2.95, -.7), new THREE.Vector3(.95, 2.95, -.7)]),
    new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .22 }));
  zg.add(gl); zoneBox = zg; GL.scene.add(zg);
  const tp = []; for (let i = 0; i < 300; i++) tp.push(new THREE.Vector3());
  trailLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(tp), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .9 })); trailLine.frustumCulled = false; GL.scene.add(trailLine);
  trailPts = new THREE.Points(trailLine.geometry, new THREE.PointsMaterial({ color: 0xffffff, size: 3, sizeAttenuation: false })); trailPts.frustumCulled = false; GL.scene.add(trailPts);
}

function sig(o){ return [o.kind, o.skin, o.hair, o.cap, o.cap2, o.pants, o.shirt, o.sleeve, o.helm, o.ab, o.glove ? 1 : 0].join('|'); }
// find or build the person called `key`; rebuilt if his look changes
function ent(key, o){
  let e = ents[key]; const s = sig(o);
  if (!e || e.sig !== s){
    if (e) GL.world.remove(e.P.root);
    e = ents[key] = { P: GL.makePlayer(o), sig: s }; GL.world.add(e.P.root);
  }
  seen.add(key); e.P.root.visible = true; return e;
}
const toPlayer = (yaw, dx, dz) => [dx * Math.cos(yaw) - dz * Math.sin(yaw), dx * Math.sin(yaw) + dz * Math.cos(yaw)];   // world offset -> his own frame

GL.toScreen = function(x, y, z, W, H){
  const v = new THREE.Vector3(x, y, z); v.project(GL.cam); return { x: (v.x * .5 + .5) * W, y: (-v.y * .5 + .5) * H };
};

/* S: { view, park, parkCols, scale,
        people: [ { key, kind, look:{skin,hair}, cap, cap2, pants, glove, x, z, y, yaw, pose } ... ],   pose = a pose object
        ball:{x,y,z,r}|null, shadow:bool, trail:[[x,y,z]...], trailMode:'dots'|'line', zone:bool, time }                        */
GL.frame = function(S){
  lightsInit();
  if (S.view !== GL.view) GL.setView(S.view);
  if (S.park !== GL.park || S.parkKey !== GL.parkKeyStr){ GL.setPark(S.park, S.parkCols); GL.parkKeyStr = S.parkKey; }
  seen = new Set();
  S.people.forEach(p => {
    const e = ent(p.key, p);
    GL.applyPose(e.P, p.pose);
    GL.place(e.P, p.x, p.z, p.yaw, (S.scale || 1) * (p.scale || 1));
    e.P.root.position.y = p.y || 0;
    e.P.shadow.visible = true;
  });
  for (const k in ents) if (!seen.has(k)) ents[k].P.root.visible = false;
  // the ball
  if (S.ball){
    ballMesh.visible = true; ballMesh.position.set(S.ball.x, S.ball.y, S.ball.z); ballMesh.scale.set(S.ball.r, S.ball.r, S.ball.r); ballMesh.rotation.y = S.time * 9;
    shadowMesh.visible = S.shadow !== false; shadowMesh.position.set(S.ball.x, .08, S.ball.z);
    const sr = S.ball.r * (1.2 + clamp(S.ball.y / 90, 0, 1)); shadowMesh.scale.set(sr, sr, sr);
  } else { ballMesh.visible = false; shadowMesh.visible = false; }
  const dm = S.trailMode === 'dots';
  dots.forEach((m, i) => { const t = S.trail && dm ? S.trail[i] : null; if (!t){ m.visible = false; return; } m.visible = true; m.position.set(t[0], t[1], t[2]); const r = S.dotR || .07; m.scale.set(r, r, r); m.material.opacity = .85 * (1 - i / 16); });
  if (S.trail && S.trailMode === 'line' && S.trail.length > 1){
    trailLine.visible = true; trailPts.visible = true; const a = trailLine.geometry.attributes.position, n = Math.min(300, S.trail.length);
    for (let i = 0; i < 300; i++){ const t = S.trail[Math.min(i, n - 1)]; a.setXYZ(i, t[0], t[1], t[2]); }
    a.needsUpdate = true;
  } else { trailLine.visible = false; trailPts.visible = false; }
  zoneBox.visible = !!S.zone;
  GL.render();
};
})();
