s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# ── ground balls: you run them too. Only a ball caught in the air makes anybody wait; here every runner may go whenever you send him ──
rep("const isManualPlay = B => !!B && userBats() && !B.hr && !B.foul && ((!B.isCatch && ['single', 'double', 'triple', 'error'].includes(B.play)) || !!B.tagUp);",
    "const isGPlay = B => !!B && ['groundout', 'dp', 'fc'].includes(B.play);                  // a ground ball the infield deals with: no base is a gift, every one has to be won\nconst isManualPlay = B => !!B && userBats() && !B.hr && !B.foul && ((!B.isCatch && ['single', 'double', 'triple', 'error', 'groundout', 'dp', 'fc'].includes(B.play)) || !!B.tagUp);")
rep("    const forced = !BALL.tagUp;                                              // tagging up on a caught fly: nobody is forced, everyone stands on his base until you send him",
    "    const gb = isGPlay(BALL), isF = key === 'runB' || (gb && M.bases.slice(0, s0 / 90 - 1).every(Boolean));\n    const forced = gb ? isF : !BALL.tagUp;                                   // on a ground ball only the forced men have to run; tagging up on a caught fly: nobody is forced, everyone stands on his base until you send him")
rep("c = RUNCTL[key] = { te:0, last:BALL.t, cap: BALL.tagUp ? (key === 'runB' ? s1 : s0) : manual ? Math.min(360, s0 + 90) : s1,",
    "c = RUNCTL[key] = { te:0, last:BALL.t, cap: BALL.tagUp ? (key === 'runB' ? s1 : s0) : manual ? (gb && !isF ? s0 : Math.min(360, s0 + 90)) : s1,")
# the throw: at the runner he has the best chance of getting
rep("""    let best = null;
    for (const key in RUNCTL){
      const c = RUNCTL[key]; if (c.out || (!c.back && c.pos >= c.cap - .05)) continue;
      const nb = c.cap, bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;                // throw to the base he is running to
      if (!best || c.pos > best.c.pos) best = { key, c, nb, bi, back:!!c.back };
    }
    if (!best) return;
    const to = BASE_XY[best.bi];
    const holder = P.first ? B.chaser : (FLD || []).reduce((a, f) => Math.hypot(f.x - P.x, f.y - P.y) < Math.hypot(a.x - P.x, a.y - P.y) ? f : a);
    const rt = routeThrow(holder, [P.x, P.y], B.t, to, 0, true), thr = mkThr(rt, [P.x, P.y], to);""",
"""    let best = null;
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
    if (!best) return;
    const to = BASE_XY[best.bi];
    const rt = best.rt || routeThrow(holder, [P.x, P.y], B.t, to, 0, true), thr = mkThr(rt, [P.x, P.y], to);""")
rep("    const c = P.run.c, extra = c.back || P.run.nb > c.s0 + (c.forced ? 90 : 0) + .5;", "    const c = P.run.c, extra = c.back || isGPlay(B) || P.run.nb > c.s0 + (c.forced ? 90 : 0) + .5;")
# the result
rep("""  const out_ = thrownOut ? 'single' : names[Math.max(1, batterBase)];
  return { res: res === 'error' ? 'error' : out_, runs, outs, txt: thrownOut ? 'THROWN OUT TRYING FOR AN EXTRA BASE' : '' };""",
"""  if (isGPlay(B)){                                                                          // a ground ball: who was put out decides what it was
    const batterOut = res2.some(r => r.e.batter && r.out);
    const r_ = batterOut ? (outs >= 2 ? 'dp' : 'groundout') : outs ? 'fc' : 'single';
    return { res: r_, runs, outs, txt: ({ dp:'DOUBLE PLAY', groundout:'GROUND OUT', fc:"FIELDER'S CHOICE", single:'INFIELD HIT' })[r_] };
  }
  const out_ = thrownOut ? 'single' : names[Math.max(1, batterBase)];
  return { res: res === 'error' ? 'error' : out_, runs, outs, txt: thrownOut ? 'THROWN OUT TRYING FOR AN EXTRA BASE' : '' };""")
# no run counts when the third out is made on a ground ball's force: count the outs before scoring
rep("  const nb = [null, null, null];\n  res2.sort((a, b) => b.K - a.K).forEach(r => {                           // lead runner first, so a held runner blocks the one behind him",
    "  const nb = [null, null, null], noRuns = isGPlay(B) && M.outs + res2.filter(r => r.out).length >= 3;       // the third out of the inning on a ground ball: nothing scores\n  res2.sort((a, b) => b.K - a.K).forEach(r => {                           // lead runner first, so a held runner blocks the one behind him")
rep("    if (k >= 4){ runs++; score(r.e.man); return; }\n    while (k > 1 && nb[k - 1]) k--;\n    if (nb[k - 1]) k = 0;\n    if (k >= 1) nb[k - 1] = r.e.man;\n  });\n  M.bases = nb;\n  if (isGPlay(B))",
    "    if (k >= 4){ if (!noRuns){ runs++; score(r.e.man); } return; }\n    while (k > 1 && nb[k - 1]) k--;\n    if (nb[k - 1]) k = 0;\n    if (k >= 1) nb[k - 1] = r.e.man;\n  });\n  M.bases = nb;\n  if (isGPlay(B))")
rep("  const manual = isDef ? defHit() : (['single', 'double', 'triple', 'error'].includes(res) && isManualPlay(BALL) && Object.keys(RUNCTL).length ? manualHit(res) : null);",
    "  const manual = isDef ? defHit() : ((['single', 'double', 'triple', 'error'].includes(res) || isGPlay(BALL)) && isManualPlay(BALL) && Object.keys(RUNCTL).length ? manualHit(res) : null);")
rep("    res = manual.res; st.ab++; runs = manual.runs; out = manual.outs;", "    if (!isDef && manual.res === 'single' && isGPlay(BALL)) M.H[M.top ? 'away' : 'home']++;\n    res = manual.res; st.ab++; runs = manual.runs; out = manual.outs;")
rep("  planOutcomeAuto(B, c);\n  if (!userPitches()", "  planOutcomeAuto(B, c);\n  if (userBats() && isGPlay(B)) B.tEnd = Math.max(B.tEnd, (B.tf || 0) + 2.5);                 // you may send a runner while the ball is in play\n  if (!userPitches()")
s = s.replace("BUILD = '11-11j'", "BUILD = '11-11k'").replace("gl3d.js?v=11-11j", "gl3d.js?v=11-11k")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
