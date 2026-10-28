/* Baking: draw one 3D player, in one pose, into a small transparent canvas so the 2D scene can stamp it onto the
   painted field at the exact spot and size the target picture puts him.  The player keeps all his shading and
   outline, and because the canvas is small and drawn with nearest-neighbour scaling he gets the target's chunky pixels. */
(function(){
'use strict';
const GL = window.GL3D;
const B = { ready:false, pool:{}, cache:new Map(), ppf:1 };
GL.bakeInit = function(){
  if (B.ready) return true;
  try {
    B.canvas = document.createElement('canvas'); B.canvas.width = 64; B.canvas.height = 64;
    B.r = new THREE.WebGLRenderer({ canvas: B.canvas, antialias: false, alpha: true, preserveDrawingBuffer: true });
    B.r.setClearColor(0x000000, 0);
    B.scene = new THREE.Scene();
    B.scene.add(new THREE.AmbientLight(0xffffff, .78));
    const d = new THREE.DirectionalLight(0xfff0d8, .6); d.position.set(-14, 28, 22); B.scene.add(d);
    B.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, .1, 200);
    B.ready = true;
  } catch (e){ B.ready = false; }
  return B.ready;
};
const sigOf = o => [o.kind, o.skin, o.hair, o.cap, o.cap2, o.pants, o.shirt, o.sleeve, o.helm, o.ab, o.glove ? 1 : 0].join('|');
// o: the player's look (same fields as makePlayer). pose: a pose object. yaw: which way he faces (0 = toward the camera at +z).
// wFt/hFt: the box in feet that is drawn into the canvas; px: how many pixels tall the canvas is
GL.bake = function(cacheKey, o, pose, yaw, px, ext){
  if (!GL.bakeInit()) return null;
  if (cacheKey && B.cache.has(cacheKey)) return B.cache.get(cacheKey);
  const e = Object.assign({ w: 9, h: 11, base: .6 }, ext || {});               // feet shown: width, height, and the space below his feet
  const ppf = px / e.h, W = Math.max(8, Math.round(e.w * ppf)), H = Math.max(8, Math.round(px));
  const s = sigOf(o); let P = B.pool[s];
  if (!P){ P = B.pool[s] = GL.makePlayer(o); B.scene.add(P.root); }
  for (const k in B.pool) B.pool[k].root.visible = (k === s);
  GL.applyPose(P, pose); GL.place(P, 0, 0, yaw, 1); P.shadow.visible = false;
  B.r.setSize(W, H, false);
  B.cam.left = -e.w / 2; B.cam.right = e.w / 2; B.cam.top = e.h - e.base; B.cam.bottom = -e.base; B.cam.updateProjectionMatrix();
  const tilt = 9 * Math.PI / 180, dist = 60;
  B.cam.position.set(0, dist * Math.sin(tilt), dist * Math.cos(tilt)); B.cam.lookAt(0, 0, 0);
  B.r.render(B.scene, B.cam);
  const out = document.createElement('canvas'); out.width = W; out.height = H;
  const c = out.getContext('2d'); c.drawImage(B.canvas, 0, 0, W, H);
  // snap the soft edge pixels: a pixel is in or out, like hand-drawn sprites
  try { const im = c.getImageData(0, 0, W, H), d = im.data; for (let i = 3; i < d.length; i += 4) d[i] = d[i] > 110 ? 255 : 0; c.putImageData(im, 0, 0); } catch (err) {}
  out._e = e; out._ppf = ppf;
  if (cacheKey){ B.cache.set(cacheKey, out); if (B.cache.size > 600) B.cache.delete(B.cache.keys().next().value); }
  return out;
};
// live: render now and hand back the shared canvas (valid until the next call), for people who change pose every frame
GL.bakeLive = function(o, pose, yaw, px, ext){
  if (!GL.bakeInit()) return null;
  const e = Object.assign({ w: 9, h: 11, base: .6 }, ext || {}), ppf = px / e.h, W = Math.max(8, Math.round(e.w * ppf)), H = Math.max(8, Math.round(px));
  const s = sigOf(o); let P = B.pool[s];
  if (!P){ P = B.pool[s] = GL.makePlayer(o); B.scene.add(P.root); }
  for (const k in B.pool) B.pool[k].root.visible = (k === s);
  GL.applyPose(P, pose); GL.place(P, 0, 0, yaw, 1); P.shadow.visible = false;
  B.r.setSize(W, H, false);
  B.cam.left = -e.w / 2; B.cam.right = e.w / 2; B.cam.top = e.h - e.base; B.cam.bottom = -e.base; B.cam.updateProjectionMatrix();
  const tilt = 28 * Math.PI / 180, dist = 60; B.cam.position.set(0, dist * Math.sin(tilt), dist * Math.cos(tilt)); B.cam.lookAt(0, 0, 0);
  B.r.render(B.scene, B.cam);
  return { c: B.canvas, w: W, h: H, ppf, base: e.base };
};
})();
