s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── a relay man can change his mind: where the throw goes is chosen again each time the ball is in somebody's hands ──
rep("""    let best = null;
    const holder = P.first ? B.chaser : (FLD || []).reduce((a, f) => Math.hypot(f.x - P.x, f.y - P.y) < Math.hypot(a.x - P.x, a.y - P.y) ? f : a);
    for (const key in RUNCTL){
      const c = RUNCTL[key]; if (c.out || (!c.back && c.pos >= c.cap - .05 && Math.abs(c.v || 0) < .01)) continue;
      const nb = c.back ? c.back.to : c.cap, bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;                // throw to the base he is running to (or back to)
      if (isGPlay(B)){                                                                        // a ground ball: the throw goes where the out is likeliest (the runner he can beat by the most)
        const rt = routeThrow(holder, [P.x, P.y], B.t, BASE_XY[bi], 0, true), rem = Math.abs(nb - c.pos);
        const margin = B.t + rem / (sprintFps(spdOf(c.man)) * .9) - rt.arr;
        if (!best || margin > best.margin) best = { key, c, nb, bi, back:!!c.back, margin, rt };
      } else if (!best || c.pos > best.c.pos) best = { key, c, nb, bi, back:!!c.back };
    }
    if (!best) return;""", """    const holder = P.first ? B.chaser : (FLD || []).reduce((a, f) => Math.hypot(f.x - P.x, f.y - P.y) < Math.hypot(a.x - P.x, a.y - P.y) ? f : a);
    const best = pickTarget(B, holder, P.x, P.y);
    if (!best) return;""")
rep("function manualThrow(B){", """// who the man holding the ball at (px, py) throws at right now: the lead runner who is still running, or on a ground ball the runner he can beat by the most
function pickTarget(B, holder, px, py){
  let best = null;
  for (const key in RUNCTL){
    const c = RUNCTL[key]; if (c.out || (!c.back && c.pos >= c.cap - .05 && Math.abs(c.v || 0) < .01)) continue;
    const nb = c.back ? c.back.to : c.cap, bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;                // throw to the base he is running to (or back to)
    if (isGPlay(B)){
      const rt = routeThrow(holder, [px, py], B.t, BASE_XY[bi], 0, true), rem = Math.abs(nb - c.pos);
      const margin = B.t + rem / (sprintFps(spdOf(c.man)) * .9) - rt.arr;
      if (!best || margin > best.margin) best = { key, c, nb, bi, back:!!c.back, margin, rt };
    } else if (!best || c.pos > best.c.pos) best = { key, c, nb, bi, back:!!c.back };
  }
  return best;
}
function manualThrow(B){""")
# in flight: when the ball reaches a relay man, he looks again at where the runners are, and may throw somewhere else
rep("  const tp = thrPos(P.thr, B.t); P.fl = tp.flying;\n  B.d = tp.d; B.lat = tp.lat; B.h = tp.flying ? 4 + Math.sin(tp.u * Math.PI) * Math.min(16, tp.len * .09) : 4;\n  if (B.t >= P.t1){\n    const c = P.run.c;",
"""  if (P.thr.relays && P.thr.relays.length){
    const legs = P.thr.legs;
    for (let k = 0; k < legs.length - 1; k++){
      if (B.t < legs[k].t1 || (P.rr && P.rr[k])) continue;
      P.rr = P.rr || {}; P.rr[k] = true;                                                 // the ball has just got to a relay man: he looks again
      const rel = P.thr.relays[k] && P.thr.relays[k].f; if (!rel) break;
      const px = legs[k].to[0], py = legs[k].to[1], nb = pickTarget(B, rel, px, py);
      if (nb && (nb.key !== P.run.key || nb.nb !== P.run.nb || !!nb.back !== !!P.run.back)){
        const to2 = BASE_XY[nb.bi], rt2 = nb.rt || routeThrow(rel, [px, py], B.t, to2, 0, true), thr2 = mkThr(rt2, [px, py], to2);
        B.thr = thr2; B.pass = { ph:'fly', thr:thr2, to:to2, t1:thr2.t1, run:nb, fl:true, rr:{} }; return;      // he throws to the base the runner is going to NOW
      }
    }
  }
  const tp = thrPos(P.thr, B.t); P.fl = tp.flying;
  B.d = tp.d; B.lat = tp.lat; B.h = tp.flying ? 4 + Math.sin(tp.u * Math.PI) * Math.min(16, tp.len * .09) : 4;
  if (B.t >= P.t1){
    const c = P.run.c;""")
s = s.replace("BUILD = '11-12e'", "BUILD = '11-12f'").replace("gl3d.js?v=11-12e", "gl3d.js?v=11-12f")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
