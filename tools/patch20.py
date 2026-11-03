s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# ── 1) the runner control block, rewritten ────────────────────────────────────────────────────────────────
a = s.index("let RUNCTL = {};")
b = s.index("function launchBall(ev, la, sa, qual){")
new_block = '''let RUNCTL = {};                                   // per runner: his own clock, the base he is told to stop at (cap), the times he reached each base
let RUNBTN = [];                                   // on-screen hit areas of this frame's diamonds
// a ball in play where YOU run the bases: every runner starts RED (stop at the next base); tap = green (go on through the base ahead)
const isManualPlay = B => !!B && userBats() && !B.hr && !B.foul && !B.isCatch && ['single', 'double', 'triple', 'error'].includes(B.play);
// the base he is heading for (feet along the path): the first one ahead of him, or the one he stands on once he has stopped there
const runAhead = c => {
  if (c.pos <= c.s0 + .5) return c.s0 + 90;
  const q = c.pos / 90; return Math.abs(q - Math.round(q)) < .012 ? c.pos : Math.ceil(q) * 90;
};
function runPosCtl(key, man, s0, s1){
  const manual = isManualPlay(BALL);
  const c = RUNCTL[key] || (RUNCTL[key] = { te:0, last:BALL.t, cap: manual ? Math.min(360, s0 + 90) : s1, s0, s1, pos:s0, man, manual, arr:{} });
  const dt = BALL.t - c.last; c.last = BALL.t; c.s1 = s1;
  if (dt > 0 && s0 + runDist(man.speed, c.te - CFG.RUN_START_DELAY) < c.cap - .01) c.te += dt;      // he only runs while he is short of the base he is held to
  c.pos = Math.min(c.cap, s0 + runDist(man.speed, c.te - CFG.RUN_START_DELAY));
  for (let k = 1; k <= 4; k++) if (c.arr[k] == null && 90 * k > s0 && c.pos >= 90 * k - .05) c.arr[k] = BALL.t;   // when he got to each base
  return c.pos;
}
function runToggle(key){
  const c = RUNCTL[key]; if (!c || !c.manual) return;
  const ah = runAhead(c);
  if (c.cap > ah) c.cap = Math.max(ah, c.pos);            // green -> red: stop at the base ahead
  else c.cap = Math.min(360, ah + 90);                    // red -> green: go on through it and stop at the next
}
const runnersSettled = () => Object.values(RUNCTL).every(c => c.pos >= c.cap - .05);
// kept for the old code path: every runner gets what the play gave him
function runnerGain(key, s0, n){ return n; }
function drawRunDiamond(key, sx, sy){
  const c = RUNCTL[key]; if (!c) return;
  const green = c.cap > runAhead(c), settled = c.pos >= c.cap - .05, rr = 2.6;
  g.save(); g.globalAlpha = settled ? .6 : 1; g.translate(sx, sy);
  g.beginPath(); g.moveTo(0, -rr); g.lineTo(rr, 0); g.lineTo(0, rr); g.lineTo(-rr, 0); g.closePath();
  g.fillStyle = green ? '#3ddc6a' : '#ff4d4d'; g.fill(); g.strokeStyle = '#ffffff'; g.lineWidth = .9; g.stroke(); g.restore();
  RUNBTN.push({ key, x: sx - 14, y: sy - 14, w: 28, h: 28 });                 // the tap area stays comfortable even though the diamond is small
}
'''
s = s[:a] + new_block + s[b:]

# ── 2) 3D drawing: runners use the new control, diamonds float a few feet over the head ─────────────────────
rep("      const cc = RUNCTL[key], held = cc && s >= Math.min(s1, cc.cap) - .05;", "      const cc = RUNCTL[key], held = cc && s >= cc.cap - .05;")
rep("      if (s1 > s0 && !B.isCatch && B.play !== 'groundout' && userBats()){ const q = GL3D.toScreen(X, 8.4, Z, W, H); runMarks.push([key, q.x, q.y]); }",
    "      if (isManualPlay(B)){ const q = GL3D.toScreen(X, 9.6, Z, W, H); runMarks.push([key, q.x, q.y]); }")
rep("    run('runB', b, 0, 90 * (B.runN || 1));\n    M.bases.forEach((p2, i) => { if (!p2) return; const adv = B.isCatch || B.play === 'groundout' ? 0 : (B.runN || 1); run('run' + i, p2, 90 * (i + 1), 90 * (i + 1) + adv * 90); });",
    "    const manual = isManualPlay(B);\n    run('runB', b, 0, manual ? 360 : 90 * (B.runN || 1));\n    M.bases.forEach((p2, i) => { if (!p2) return; const adv = B.isCatch || B.play === 'groundout' ? 0 : (B.runN || 1); run('run' + i, p2, 90 * (i + 1), manual ? 360 : 90 * (i + 1) + adv * 90); });")

# ── 3) what the fielders did, for judging extra-base tries ─────────────────────────────────────────────────
rep("  const tr = Math.hypot(pf[0], pf[1]) < 150 && !B.hr ? CFG.TRANSFER_GROUND : CFG.TRANSFER_AIR;\n  if (B.hr){",
    "  const tr = Math.hypot(pf[0], pf[1]) < 150 && !B.hr ? CFG.TRANSFER_GROUND : CFG.TRANSFER_AIR;\n  B.thrInfo = { tf, tr, pf, arm: c.armFps };                          // when and from where the throw can go: judges every extra-base try\n  if (B.hr){")

# ── 4) the play does not end while a runner is still running ────────────────────────────────────────────────
rep("    if ((B.judged && B.t > B.tEnd) || P.playT > 20000){", "    if ((B.judged && B.t > B.tEnd && (B.t > B.tEnd + 9 || runnersSettled())) || P.playT > 24000){")

# ── 5) the result: bases come from where each runner was held; extra bases must beat the throw ────────────
rep("function applyPlay(res){\n  const b = M.batter, st = b.st, p = curPitcher();\n  let runs = 0, out = 0, txt = '';\n  st.pa++;",
'''// You ran them: each runner ends on the base he was told to stop at. A base beyond the first one he gets for free is only safe if he got
// there before the throw could (the fielding spot, the transfer and the arm decide the throw).
function manualHit(res){
  const B = BALL, T = B.thrInfo, bases = [[63.64, 63.64], [127.28, 0], [63.64, -63.64], [0, 0]];
  const names = ['', 'single', 'double', 'triple', 'hr'];
  const entries = [{ key:'runB', man:M.batter, s0:0, batter:true }];
  M.bases.forEach((p2, i) => { if (p2) entries.push({ key:'run' + i, man:p2, s0:90 * (i + 1) }); });
  let outs = 0, runs = 0, batterBase = 1, thrownOut = false;
  const res2 = entries.map(e => {
    const c = RUNCTL[e.key]; let K = c ? c.cap : e.s0 + 90, out = false;
    for (let kk = e.s0 + 180; kk <= K; kk += 90){                        // every base past the free one
      const arr = c && c.arr[kk / 90];
      if (arr == null || !T) continue;
      const bd = Math.hypot(T.pf[0] - bases[kk / 90 - 1][0], T.pf[1] - bases[kk / 90 - 1][1]);
      if (arr + CFG.EXTRA_BASE_MARGIN >= T.tf + T.tr + bd / T.arm){ out = true; K = kk; break; }
    }
    return { e, K, out };
  });
  const nb = [null, null, null];
  res2.sort((a, b) => b.K - a.K).forEach(r => {                           // lead runner first, so a held runner blocks the one behind him
    if (r.out){ outs++; thrownOut = true; if (r.e.batter) batterBase = 1; return; }
    let k = Math.min(4, Math.round(r.K / 90));
    if (r.e.batter) batterBase = k;
    if (k >= 4){ runs++; score(r.e.man); return; }
    while (k > 1 && nb[k - 1]) k--;
    if (nb[k - 1]) k = 0;
    if (k >= 1) nb[k - 1] = r.e.man;
  });
  M.bases = nb;
  const out_ = thrownOut ? 'single' : names[Math.max(1, batterBase)];
  return { res: res === 'error' ? 'error' : out_, runs, outs, txt: thrownOut ? 'THROWN OUT TRYING FOR AN EXTRA BASE' : '' };
}
function applyPlay(res){
  const b = M.batter, st = b.st, p = curPitcher();
  let runs = 0, out = 0, txt = '';
  st.pa++;
  const manual = ['single', 'double', 'triple', 'error'].includes(res) && isManualPlay(BALL) && Object.keys(RUNCTL).length ? manualHit(res) : null;''')
rep("  switch(res){\n    case 'hr': { st.ab++; st.h++; st.hr++;",
'''  if (manual){
    res = manual.res; st.ab++; runs = manual.runs; out = manual.outs;
    if (res !== 'error'){ st.h++; if (res === 'hr') st.hr++; st.rbi += runs; }
    txt = manual.txt || ({ single:'BASE HIT', double:'DOUBLE!', triple:'TRIPLE!', hr:'INSIDE-THE-PARK HOME RUN!', error:'ERROR!' })[res]; M.exc = .8;
  } else switch(res){
    case 'hr': { st.ab++; st.h++; st.hr++;''')
s = s.replace("PLATE.src = 'assets/fields/plate_clean.png';", "PLATE.src = 'assets/fields/plate_clean.png?b=11-02h';")
s = s.replace("BUILD = '11-02g'", "BUILD = '11-02h'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
