import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ── 1) a throw to a base needs a man on the base; the man with the ball runs it there when he is the closest ──
rep("""  walk(from, throwRange(thrower.man.fielding), thrower.armFps, t0 + tr, [], [], []);
  if (!best){ const l = leg(from, tgt, t0 + tr, thrower.armFps); best = { legs:[l], arr:l.t1, relays:[] }; }
  return best;
}
const mkThr = (rt, from, to) => ({ t0: rt.legs[0].t0, t1: rt.legs[rt.legs.length - 1].t1, from, to, len: rt.legs.reduce((a, l) => a + l.len, 0), legs: rt.legs, relays: rt.relays });""",
"""  walk(from, throwRange(thrower.man.fielding), thrower.armFps, t0 + tr, [], [], []);
  if (!best){ const l = leg(from, tgt, t0 + tr, thrower.armFps); best = { legs:[l], arr:l.t1, relays:[] }; }
  // a base: the throw only counts once somebody is standing on it, and the closest man runs the ball there himself if that is quicker
  const bi = BASE_PTS4.findIndex(q => Math.abs(q[0] - tgt[0]) < 1 && Math.abs(q[1] - tgt[1]) < 1);
  if (bi >= 0){
    let cover = bi === 3 ? 0 : Infinity;                                                    // the catcher is always at the plate
    (FLD || []).forEach(f => {
      if (f === thrower || !BAG_COVER[bi] || !BAG_COVER[bi].includes(f.pos)) return;
      const D = Math.max(0, dist(live ? [f.x, f.y] : [f.d, f.lat], tgt) - 1.5);
      cover = Math.min(cover, live ? BALL.t + D / (f.speed * CFG.ROUTE_EFF) : fldReach(f, D));
    });
    const dBall = Math.max(0, dist(from, tgt) - 1.5);
    const closest = bi < 3 && (FLD || []).every(f => f === thrower || dist(live ? [f.x, f.y] : [f.d, f.lat], tgt) >= dBall - .01);
    const throwArr = Math.max(best.arr, Math.min(cover, 99));
    if (closest && dBall < 70){
      const fps = sprintFps(spdOf(thrower.man)) * .92, ts = t0 + .2, ca = ts + dBall / fps;
      if (ca < throwArr) return { legs:[{ from, to:tgt, t0:ts, t1:ts + dist(from, tgt) / fps, len:dist(from, tgt) }], arr:ca, relays:[], carry:true, carryF:thrower };
    }
    best.arr = throwArr;
  }
  return best;
}
const BAG_COVER = [['1B', '2B'], ['2B', 'SS'], ['3B', 'SS'], []];                       // who can stand on first, second, third (home is the catcher's)
const mkThr = (rt, from, to) => ({ t0: rt.legs[0].t0, t1: Math.max(rt.legs[rt.legs.length - 1].t1, rt.arr || 0), from, to, len: rt.legs.reduce((a, l) => a + l.len, 0), legs: rt.legs, relays: rt.relays, carry: !!rt.carry, carryF: rt.carryF || null });""")
# the man who carries the ball moves with it
rep("""  const c = BALL.chaser; if (!c) return;
  const tau = BALL.t - c.react,""", """  if (BALL.thr && BALL.thr.carry && BALL.thr.carryF && BALL.t >= BALL.thr.t0 && !BALL.hr){ const tp = thrPos(BALL.thr, BALL.t); BALL.thr.carryF.x = tp.d; BALL.thr.carryF.y = tp.lat; BALL.thr.carryF.carrying = true; }
  const c = BALL.chaser; if (!c) return;
  const tau = BALL.t - c.react,""")
# the carrying man keeps his place in the loop above (his x,y are set after everything else)
rep("""  c.x = lerp(c.d, c.tx, f); c.y = lerp(c.lat, c.ty, f);
}""", """  c.x = lerp(c.d, c.tx, f); c.y = lerp(c.lat, c.ty, f);
  if (BALL.thr && BALL.thr.carry && BALL.thr.carryF === c && BALL.t >= BALL.thr.t0 && !BALL.hr){ const tp = thrPos(BALL.thr, BALL.t); c.x = tp.d; c.y = tp.lat; }
}""")
# the pivot man's throw on a double play starts as the picture shows it (0.55 s after the ball arrives)
rep("const a1b = a2 + .9 + 90 / (c.armFps * .9);                              // the pivot man's throw from second to first is 90 ft",
    "const a1b = a2 + .55 + 90 / (c.armFps * .9);                             // the pivot man's throw from second to first is 90 ft, and it leaves .55 s after the ball gets there")

# ── 2) tagging up: a fly ball is caught with fewer than two out and men on: after the catch you tap a runner to send him ──
rep("const isManualPlay = B => !!B && userBats() && !B.hr && !B.foul && !B.isCatch && ['single', 'double', 'triple', 'error'].includes(B.play);",
    "const isManualPlay = B => !!B && userBats() && !B.hr && !B.foul && ((!B.isCatch && ['single', 'double', 'triple', 'error'].includes(B.play)) || !!B.tagUp);")
rep("  const manual = isManualPlay(BALL);\n  let c = RUNCTL[key];", "  const manual = isManualPlay(BALL) && !(BALL.tagUp && key === 'runB');\n  let c = RUNCTL[key];")
rep("    const forced = true;\n    c = RUNCTL[key] = { te:0, last:BALL.t, cap: manual ? Math.min(360, s0 + 90) : s1, s0, s1, pos:s0, man, manual, forced, arr:{} };",
    "    const forced = !BALL.tagUp;                                              // tagging up on a caught fly: nobody is forced, everyone stands on his base until you send him\n    c = RUNCTL[key] = { te:0, last:BALL.t, cap: BALL.tagUp ? (key === 'runB' ? s1 : s0) : manual ? Math.min(360, s0 + 90) : s1, s0, s1, pos:s0, man, manual, forced, arr:{} };")
rep("  const c = RUNCTL[key]; if (!c || !c.manual) return;\n  if (c.back){ c.back = null;", "  const c = RUNCTL[key]; if (!c || !c.manual) return;\n  if (BALL && BALL.tagUp && BALL.t < BALL.tf) return;                          // not until it is caught\n  if (c.back){ c.back = null;")
# the throws need the fielding spot even for a catch
rep("""  if (B.foul){                                                      // fielders chase foul balls too: caught in the air and in the park, it is an out
    const ang = Math.atan2(B.land.lat, B.land.d) * 180 / Math.PI, inPark = window.GL3D ? Math.hypot(B.land.d, B.land.lat) < GL3D.fenceR(M.park, ang) - 2 : true;
    if (inAir && inPark && B.land.d > -8){ B.foul = false; B.isCatch = true; B.play = 'flyout'; B.tJudge = tf; B.tEnd = tf + 1.0; B.runN = 0; }""",
"""  const tagOK = () => { if (userBats() && B.play === 'flyout' && M.outs < 2 && M.bases.some(Boolean)){ B.tagUp = true; B.tEnd = tf + 1.9; } };       // a caught fly, men on and under two out: you may send them
  B.thrInfo = { tf, tr: CFG.TRANSFER_AIR, pf, arm: c.armFps };
  if (B.foul){                                                      // fielders chase foul balls too: caught in the air and in the park, it is an out
    const ang = Math.atan2(B.land.lat, B.land.d) * 180 / Math.PI, inPark = window.GL3D ? Math.hypot(B.land.d, B.land.lat) < GL3D.fenceR(M.park, ang) - 2 : true;
    if (inAir && inPark && B.land.d > -8){ B.foul = false; B.isCatch = true; B.play = 'flyout'; B.tJudge = tf; B.tEnd = tf + 1.0; B.runN = 0; tagOK(); }""")
rep("    B.isCatch = true; B.play = B.la > CFG.LINE_MAX_LA ? 'flyout' : 'lineout'; B.tJudge = tf; B.tEnd = tf + 1.0; B.runN = 0; return;",
    "    B.isCatch = true; B.play = B.la > CFG.LINE_MAX_LA ? 'flyout' : 'lineout'; B.tJudge = tf; B.tEnd = tf + 1.0; B.runN = 0; tagOK(); return;")
# drawing: the batter is out and stays put, the others get their diamonds
rep("    run('runB', b, 0, manual ? 360 : 90 * (B.runN || 1));", "    run('runB', b, 0, manual && !B.tagUp ? 360 : 90 * (B.runN || 1));")
rep("      if (isManualPlay(B) && !(cc && cc.out)){ const q = GL3D.toScreen(X, 26, Z, W, H); runMarks.push([key, q.x, q.y]); }",
    "      if (isManualPlay(B) && cc && cc.manual && !cc.out){ const q = GL3D.toScreen(X, 26, Z, W, H); runMarks.push([key, q.x, q.y]); }")
rep("  gxSprites(crowd, B);\n}", """  gxSprites(crowd, B);
  if (B.tagUp && B.t >= B.tf && B.t < B.tf + 2.2 && !Object.values(RUNCTL).some(c => c.manual && c.cap > c.s0 + .5)){ const pulse = .7 + .3 * Math.sin(B.t * 9); textb('TAP A RUNNER TO TAG UP', W / 2, 46, `rgba(255,210,63,${pulse})`, 8, 'center'); }
}""")
# the result: whoever you sent is safe or out; no random sacrifice fly
rep("""      st.ab++; out = 1;
      if (res === 'flyout' && M.bases[2] && M.outs < 2 && chance(.55)){""", """      st.ab++; out = 1;
      if (res === 'flyout' && BALL && BALL.tagUp){
        const r = tagUpHit(); out += r.outs; runs += r.runs; M.bases = r.bases;
        if (r.runs){ st.rbi += r.runs; st.ab--; st.sf = (st.sf || 0) + 1; txt = r.outs ? 'SAC FLY, BUT TAGGED OUT' : 'SAC FLY'; } else txt = r.outs ? 'TAGGED OUT TRYING TO ADVANCE' : 'FLY OUT';
        if (r.advanced && !r.runs && !r.outs) txt = 'FLY OUT, TAGGED UP';
      }
      else if (res === 'flyout' && M.bases[2] && M.outs < 2 && chance(.55)){""")
rep("function applyPlay(res){", """// what your tag-ups made of a caught fly: who got to the next base, who was thrown out, and whether a run counts (not if the third out came first)
function tagUpHit(){
  const nb = [null, null, null]; let runs = 0, outs = 0, advanced = false; const list = [], outTimes = [];
  M.bases.forEach((p, i) => { if (!p) return; const c = RUNCTL['run' + i]; list.push({ p, i, c }); if (c && c.out){ outs++; outTimes.push(c.outT || 0); } });
  const need = 3 - (M.outs + 1);                                               // tag-outs that would make the third out
  const thirdAt = outs >= need && need > 0 ? outTimes.slice().sort((a, b) => a - b)[need - 1] : Infinity;
  list.sort((a, b) => ((b.c ? b.c.pos : 90 * (b.i + 1)) - (a.c ? a.c.pos : 90 * (a.i + 1)))).forEach(r => {
    const c = r.c; if (c && c.out) return;
    const pos = c ? c.pos : 90 * (r.i + 1);
    if (c && pos > c.s0 + .5) advanced = true;
    if (pos >= 360 - .05){ if (!c || c.arr[4] == null || c.arr[4] < thirdAt){ runs++; score(r.p); } return; }
    let k = Math.max(0, Math.min(2, Math.round(pos / 90) - 1));
    while (k > 0 && nb[k]) k--;
    if (nb[k]) k = Math.min(2, k + 1);
    nb[k] = r.p;
  });
  return { runs, outs, bases:nb, advanced };
}
function applyPlay(res){""")
s = s.replace("BUILD = '11-07h'", "BUILD = '11-07i'"); s = re.sub(r"gl3d\.js\?v=11-07h", "gl3d.js?v=11-07i", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
