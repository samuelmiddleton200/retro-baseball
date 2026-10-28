/* The animations: every pose is a handful of numbers (see BASEPOSE in glchars.js), blended between keyframes.
   Local frame: +Z forward, +Y up, the player's left is +X. Feet. */
(function(){
'use strict';
const GL = window.GL3D, clamp = (v, a, b) => v < a ? a : v > b ? b : v, lerp = (a, b, t) => a + (b - a) * t;
const ease = t => t * t * (3 - 2 * t);
// pick the pose at time t from a list of [time, pose] keyframes
function kf(keys, t){
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]){
    const a = keys[i - 1], b = keys[i], u = ease((t - a[0]) / (b[0] - a[0])); return GL.blendPose(a[1], b[1], u);
  }
  return keys[keys.length - 1][1];
}
const mk = o => Object.assign({}, GL.BASEPOSE, o);

// ── standing in: a fielder's ready crouch, hands on the knees, glove low ──────────────────────────
GL.poseReady = function(t){
  const b = Math.sin(t * 2.2) * .04;
  return mk({ hips:[0, 2.3 + b, -.1], lean:26, LF:[.95, 0, .15], RF:[-.95, 0, .15], headPitch:-26,
    L:[.85, 2.0, 1.1], R:[-.75, 1.95, 1.0], Lh:[.6, 0, 0], Rh:[-.6, 0, 0], Lk:[.2, 0, 1], Rk:[-.2, 0, 1] });
};
GL.poseGrab = function(u){                    // scooping a ground ball: bends low and reaches out front
  return GL.blendPose(GL.poseReady(0), mk({ hips:[0, 1.7, .5], lean:46, LF:[1.0, 0, .9], RF:[-.9, 0, -.3], headPitch:-40,
    L:[.55, .45, 2.3], R:[-.35, .6, 2.1], Lh:[.4, 0, 0], Rh:[-.4, 0, 0] }), ease(clamp(u, 0, 1)));
};
GL.poseCatch = function(u){                   // reaching up for a fly ball
  return GL.blendPose(GL.poseReady(0), mk({ hips:[0, 2.9, 0], lean:-4, LF:[.4, 0, .1], RF:[-.4, 0, -.1], headPitch:30,
    L:[.55, 6.2, .9], R:[-.45, 5.4, .6], Lh:[.2, 0, 0], Rh:[-.2, 0, 0] }), ease(clamp(u, 0, 1)));
};
// a run cycle; phase is in strides (one stride = both legs once)
GL.poseRun = function(phase, speed){
  const A = 1.15 * clamp(speed / 24, .4, 1.25), B = 1.1;
  const leg = s => { s = ((s % 1) + 1) % 1; if (s < .5) return [A - 2 * A * (s / .5), 0]; const u = (s - .5) / .5; return [-A + 2 * A * u, B * Math.sin(Math.PI * u)]; };
  const l = leg(phase), r = leg(phase + .5), bob = Math.abs(Math.sin(phase * Math.PI * 2)) * .14;
  return mk({ hips:[0, 2.55 + bob, 0], lean:16, headPitch:-10,
    LF:[.4, l[1], l[0]], RF:[-.4, r[1], r[0]], Lk:[.1, 0, 1], Rk:[-.1, 0, 1],
    L:[.75, 3.5 + l[1] * .1, -r[0] * .9 + .2], R:[-.75, 3.5 + r[1] * .1, -l[0] * .9 + .2], Lh:[.7, 0, -.4], Rh:[-.7, 0, -.4] });
};
// throwing: u 0 = ball in glove, .45 = arm cocked, .7 = release, 1 = finished
GL.poseThrow = function(u){
  const rdy = mk({ hips:[0, 2.8, 0], lean:4, LF:[.5, 0, .2], RF:[-.5, 0, -.2], L:[.5, 4.0, .6], R:[-.4, 4.0, .6] });
  return kf([[0, rdy],
    [.40, mk({ hips:[0, 2.75, -.1], lean:-6, twist:-30, LF:[.9, 0, .8], RF:[-.6, 0, -.3], headYaw:30, L:[.9, 4.7, 1.0], R:[-1.4, 5.0, -1.0], Rh:[-1, 0, -1] })],
    [.66, mk({ hips:[0, 2.55, .5], lean:24, twist:25, LF:[.7, 0, 1.6], RF:[-.6, 0, -.4], L:[.8, 3.6, .4], R:[-.45, 5.6, 1.7] })],
    [1, mk({ hips:[0, 2.4, .8], lean:44, twist:30, LF:[.6, 0, 1.8], RF:[-.4, .7, .3], L:[.8, 3.0, .3], R:[.3, 3.0, 1.3] })]], u);
};

// ── the pitcher: set, leg lift, stride, release, follow-through ───────────────────────────────────
GL.posePitcher = function(u){
  return kf([
    [0,   mk({ hips:[0, 3.0, 0], lean:2, LF:[.5, 0, .1], RF:[-.45, 0, 0], L:[.2, 4.0, .6], R:[-.15, 4.0, .6], headPitch:0 })],
    [.30, mk({ hips:[0, 3.0, -.1], lean:-5, LF:[.35, 2.1, .9], RF:[-.45, 0, 0], L:[.25, 4.9, .6], R:[-.2, 4.8, .6] })],
    [.56, mk({ hips:[0, 2.6, 1.1], lean:8, twist:-12, LF:[.55, 0, 3.6], RF:[-.5, 0, -.5], L:[1.0, 4.2, 1.7], R:[-1.5, 4.6, -.7], Rh:[-1, 0, -1] })],
    [.74, mk({ hips:[0, 2.4, 1.9], lean:34, twist:14, LF:[.6, 0, 4.3], RF:[-.5, .5, .4], L:[.7, 3.4, .5], R:[-.45, 6.0, 2.4], headPitch:-8 })],
    [1,   mk({ hips:[0, 2.4, 2.1], lean:52, twist:20, LF:[.6, 0, 4.4], RF:[-.4, 1.0, 1.8], L:[.8, 3.0, .4], R:[.5, 3.2, 1.6] })],
  ], u);
};

// ── the batter, in his own frame (facing the plate; pitcher is on his left, +X) ─────────────────────
const BAT_IDLE = [-.8, 1, -.3], BAT_LOAD = [-.95, .75, -.2], BAT_HIT = [.15, .08, 1], BAT_FOLLOW = [.8, .85, -.25];
GL.poseBatter = function(swingT, t){
  const b = Math.sin(t * 2.4) * .05, w = Math.sin(t * 3.1) * .12;
  const idle = mk({ hips:[0, 2.28 + b, 0], lean:18, twist:-8, LF:[1.45, 0, .15], RF:[-1.45, 0, -.1], Lk:[.6, 0, 1], Rk:[-.6, 0, 1], headYaw:-30, headPitch:6,
    L:[-.2, 3.7 + b, .5], R:[-.62, 3.9 + b, .3], Lh:[.4, 0, 0], Rh:[-.6, 0, 0], bat:[BAT_IDLE[0] + w, BAT_IDLE[1], BAT_IDLE[2]] });
  if (swingT == null) return idle;
  const load = mk({ hips:[-.15, 2.55, 0], lean:8, twist:-18, LF:[1.35, .25, .05], RF:[-1.3, 0, 0], headYaw:20,
    L:[-.7, 4.55, .12], R:[-1.0, 4.72, 0], Rh:[-.6, 0, -.3], bat:BAT_LOAD });
  const swing = mk({ hips:[.25, 2.55, .1], lean:12, twist:38, LF:[1.8, 0, .05], RF:[-1.1, .2, 0], headYaw:40,
    L:[.55, 3.7, 1.55], R:[.1, 3.75, 1.7], Lh:[0, 0, 0], Rh:[.2, 0, 0], bat:BAT_HIT });
  const fol = mk({ hips:[.35, 2.7, .1], lean:6, twist:105, LF:[1.85, 0, .05], RF:[-.8, .45, -.2], headYaw:50,
    L:[.55, 4.95, .55], R:[.15, 4.7, .55], bat:BAT_FOLLOW });
  return kf([[0, idle], [.20, load], [.46, swing], [1, fol]], swingT);
};

// ── the catcher and the umpire ─────────────────────────────────────────────────────────────────────
GL.poseCatcher = function(gx, gy, t){        // gx, gy: where the glove is set (feet, in the catcher's own frame)
  const b = Math.sin(t * 2) * .03;
  return mk({ hips:[0, 1.75 + b, -.8], lean:24, LF:[1.05, 0, .65], RF:[-1.05, 0, .65], Lk:[.7, 0, 1], Rk:[-.7, 0, 1], headPitch:-10,
    L:[gx, gy, 1.9], R:[-.5, 1.6, .3], Lh:[.4, 0, 0], Rh:[-.4, 0, 0] });
};
GL.poseUmp = function(t){
  return mk({ hips:[0, 2.3, -.1], lean:22, LF:[.9, 0, .45], RF:[-.9, 0, .4], headPitch:-14,
    L:[.65, 2.3, .6], R:[-.65, 2.3, .6], Lh:[.5, 0, 0], Rh:[-.5, 0, 0] });
};
})();
// a left-handed batter is the same pose seen in a mirror: swap sides and flip everything across the body
(function(){
const GL = window.GL3D;
GL.mirrorPose = function(p){
  const f = v => Array.isArray(v) ? [-v[0], v[1], v[2]] : v, o = {};
  for (const k in p) o[k] = p[k];
  const swap = (a, b) => { o[a] = f(p[b]); o[b] = f(p[a]); };
  swap('L', 'R'); swap('Lh', 'Rh'); swap('LF', 'RF'); swap('Lk', 'Rk'); swap('LFy', 'RFy');
  ['hips'].forEach(k => o[k] = f(p[k]));
  o.twist = -(p.twist || 0); o.side = -(p.side || 0); o.headYaw = -(p.headYaw || 0);
  if (p.bat) o.bat = f(p.bat);
  return o;
};
})();
