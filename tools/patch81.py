s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── in the infield the ball goes where an out is most likely; a tie goes to the base nearer home (home > 3rd > 2nd > 1st) ──
rep("    if (!best || margin > best.margin) best = { key, c, nb, bi, back: dir < 0, margin, rt };\n  }\n  return best;",
    "    if (!best || margin > best.margin + .15 || (Math.abs(margin - best.margin) <= .15 && bi > best.bi)) best = { key, c, nb, bi, back: dir < 0, margin, rt };      // the likeliest out; a tie goes to the base nearer home\n  }\n  return best;")
# ── an outfielder never sits on the ball: if no throw wins he throws it in to the cut-off man, right away ──
rep("    if (!best){ P.t0 = B.t + .08; return; }                                     // nothing he can win: he holds it and looks again",
"""    if (!best){
      if (Math.hypot(P.x, P.y) > 145){                                          // in the outfield: never hold it there, get it into the infield (the cut-off man at the edge of the dirt)
        const roles = outfieldRoles({ d:P.x, lat:P.y }), cutter = (FLD || []).find(f => f.pos === roles.cutPos && f !== holder) || (FLD || []).filter(f => f !== holder && ['1B', '2B', 'SS', '3B'].includes(f.pos)).sort((a, b) => Math.hypot(a.x - P.x, a.y - P.y) - Math.hypot(b.x - P.x, b.y - P.y))[0];
        if (cutter){
          const to = cutter.go ? [cutter.go.x, cutter.go.y] : [cutter.x, cutter.y], rt = routeThrow(holder, [P.x, P.y], B.t, to, 0, true), thr = mkThr(rt, [P.x, P.y], to);
          B.pass = { ph:'fly', thr, to, t1:thr.t1, toMan:true, fl:true };
          return;
        }
      }
      P.t0 = B.t + .08; return;                                                 // in the infield he can hold it and look again
    }""")
rep("  if (P.thr.relays && P.thr.relays.length){\n    const legs = P.thr.legs;", "  if (!P.toMan && P.thr.relays && P.thr.relays.length){\n    const legs = P.thr.legs;")
rep("  if (B.t >= P.t1){\n    const c = P.run.c;\n    // a FORCE play:", "  if (B.t >= P.t1){\n    if (P.toMan){ B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t }; return; }                  // it is in the infield now\n    const c = P.run.c;\n    // a FORCE play:")
s = s.replace("BUILD = '11-12i'", "BUILD = '11-12j'").replace("gl3d.js?v=11-12i", "gl3d.js?v=11-12j")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
