s = open('index.html', encoding='utf-8').read()
a = s.index("function pickTarget(B, holder, px, py){"); b = s.index("const ballDist = () =>")
new = r"""// ── the defence reads what the runners are PHYSICALLY doing: the way each one is moving and the base ahead of him in that direction, never the colour of his diamond.
// It only throws where the throw can beat him there (so it never feeds you a hopeless throw to turn around on), and it throws at the runner it has the best chance of getting. ──
const runHeading = c => { const v = c.v || 0; if (Math.abs(v) > .5) return Math.sign(v); return c.forced && !c.out && c.pos < c.cap - .05 ? 1 : 0; };      // +1 toward the next base, -1 back toward the last, 0 standing
const runBase = (c, dir) => dir > 0 ? Math.floor(c.pos / 90 + 1e-6) * 90 + 90 : Math.ceil(c.pos / 90 - 1e-6) * 90 - 90;                                   // the next base in the direction he is going
const onBag = c => Math.abs(c.pos / 90 - Math.round(c.pos / 90)) < .004;
function tRunTo(c, rem){                                                                                                                                // seconds for him to cover rem feet from the speed he is at now
  const vmax = sprintFps(spdOf(c.man)), acc = vmax / CFG.RUNNER_ACCEL_T, v0 = Math.min(vmax, Math.abs(c.v || 0)), dly = v0 < .5 && c.dly > 0 ? c.dly : 0;
  const dA = (vmax * vmax - v0 * v0) / (2 * acc);
  return dly + (rem <= dA ? (Math.sqrt(v0 * v0 + 2 * acc * rem) - v0) / acc : (vmax - v0) / acc + (rem - dA) / vmax);
}
const baseS = (px, py) => { for (let i = 0; i < 4; i++) if (Math.hypot(px - BASE_XY[i][0], py - BASE_XY[i][1]) < 4) return (i + 1) * 90; return null; };      // where on the base path the man with the ball stands (null: not on a bag)
function pickTarget(B, holder, px, py){
  let best = null;
  for (const key in RUNCTL){
    const c = RUNCTL[key]; if (c.out) continue;
    const dir = runHeading(c); if (!dir) continue;
    const nb = runBase(c, dir), bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;
    if (!(dir < 0 || isGPlay(B) || nb > c.s0 + (c.forced ? 90 : 0) + .5)) continue;                       // a base the hit gave him cannot be lost
    const rt = routeThrow(holder, [px, py], B.t, BASE_XY[bi], 0, true), margin = B.t + tRunTo(c, Math.abs(nb - c.pos)) - rt.arr;
    if (margin <= .05) continue;                                                                          // that throw cannot get him: they hold it instead
    if (!best || margin > best.margin) best = { key, c, nb, bi, back: dir < 0, margin, rt };
  }
  return best;
}
function manualThrow(B){
  const T = B.thrInfo; if (!T || B.hr) return;
  if (!B.pass){ if (B.t < T.tf + T.tr) return; B.pass = { ph:'hold', x:T.pf[0], y:T.pf[1], t0:B.t, first:true }; }
  const P = B.pass;
  if (P.ph === 'hold'){
    B.d = P.x; B.lat = P.y; B.h = 4;
    // the man with the ball on a bag tags anybody who runs into him (not one who is standing on the bag)
    const sh = baseS(P.x, P.y);
    if (sh != null) for (const key in RUNCTL){
      const c = RUNCTL[key]; if (c.out) continue;
      const near = Math.min(Math.abs(c.pos - sh), sh === 360 ? Math.abs(c.pos) : 1e9);
      if (near <= 2.5 && !(Math.abs(c.v || 0) < .5 && onBag(c))){ c.out = true; c.cap = c.pos; c.v = 0; c.back = null; c.outT = B.t; say('TAGGED OUT!'); }
    }
    if (B.t < P.t0) return;                                                     // the transfer: glove to hand
    const holder = P.first ? B.chaser : (FLD || []).reduce((a, f) => Math.hypot(f.x - P.x, f.y - P.y) < Math.hypot(a.x - P.x, a.y - P.y) ? f : a);
    const best = pickTarget(B, holder, P.x, P.y);
    if (!best){ P.t0 = B.t + .08; return; }                                     // nothing he can win: he holds it and looks again
    const to = BASE_XY[best.bi];
    const rt = best.rt || routeThrow(holder, [P.x, P.y], B.t, to, 0, true), thr = mkThr(rt, [P.x, P.y], to);
    B.pass = { ph:'fly', thr, to, t1:thr.t1, run:best, fl:true };
    return;
  }
  if (P.ph === 'wait'){                                                          // he holds the ball on the base until the runner arrives, then tags him
    B.d = P.x; B.lat = P.y; B.h = 4;
    const c = P.run.c, dir = runHeading(c);
    if (!c.out && (P.run.back ? c.pos <= P.run.nb + .05 : c.pos >= P.run.nb - .05)){ c.out = true; c.back = null; c.cap = c.pos; c.v = 0; c.outT = B.t; say('TAGGED OUT!'); B.pass = { ph:'hold', x:P.x, y:P.y, t0:B.t }; return; }
    // the runner changed course, or stopped short of the base: the ball is no use waiting here, he looks again
    if (c.out || (dir !== 0 && (dir < 0) !== P.run.back) || (dir === 0 && Math.abs(c.pos - P.run.nb) > .1)){ B.pass = { ph:'hold', x:P.x, y:P.y, t0:B.t + .1 }; return; }
    return;
  }
  if (P.thr.relays && P.thr.relays.length){
    const legs = P.thr.legs;
    for (let k = 0; k < legs.length - 1; k++){
      if (B.t < legs[k].t1 || (P.rr && P.rr[k])) continue;
      P.rr = P.rr || {}; P.rr[k] = true;                                                 // the ball has just got to a relay man: he looks again
      const rel = P.thr.relays[k] && P.thr.relays[k].f; if (!rel) break;
      const px = legs[k].to[0], py = legs[k].to[1], nb = pickTarget(B, rel, px, py);
      if (nb && (nb.key !== P.run.key || nb.nb !== P.run.nb || !!nb.back !== !!P.run.back)){
        const to2 = BASE_XY[nb.bi], rt2 = nb.rt || routeThrow(rel, [px, py], B.t, to2, 0, true), thr2 = mkThr(rt2, [px, py], to2);
        B.pass = { ph:'fly', thr:thr2, to:to2, t1:thr2.t1, run:nb, fl:true, rr:{} }; return;      // he throws to the base the runner is going to NOW
      }
    }
  }
  const tp = thrPos(P.thr, B.t); P.fl = tp.flying;
  B.d = tp.d; B.lat = tp.lat; B.h = tp.flying ? 4 + Math.sin(tp.u * Math.PI) * Math.min(16, tp.len * .09) : 4;
  if (B.t >= P.t1){
    const c = P.run.c;
    // a FORCE play: the runner has to go and nobody who pushes him has been put out, so the out is made the moment the man on the bag has the ball. No waiting, and he can turn it
    const behind = Object.keys(RUNCTL).filter(k => k !== P.run.key && (k === 'runB' || RUNCTL[k].s0 < c.s0));
    if (isGPlay(B) && !P.run.back && !c.out && c.forced && P.run.nb === c.s0 + 90 && c.pos < P.run.nb - .05 && behind.every(k => !RUNCTL[k].out)){
      c.out = true; c.cap = c.pos; c.v = 0; c.outT = B.t; say('OUT!'); B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t }; return;
    }
    const extra = P.run.back || isGPlay(B) || P.run.nb > c.s0 + (c.forced ? 90 : 0) + .5;   // only a base beyond the one he has to take can be lost; going back is always a tag play
    if (extra && !c.out && (P.run.back ? c.pos > P.run.nb + .05 : c.pos < P.run.nb - .05)){ B.pass = { ph:'wait', x:P.to[0], y:P.to[1], run:P.run }; return; }
    B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t + .1 };
  }
}
"""
s = s[:a] + new + s[b:]
s = s.replace("BUILD = '11-12f'", "BUILD = '11-12g'").replace("gl3d.js?v=11-12f", "gl3d.js?v=11-12g")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
