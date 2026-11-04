import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ── defence: you pick the base to throw to ──────────────────────────────────────────────────────────────
# The computer still plans the play (who runs how far); when you field, the throw is yours: tap a base (even before the ball is fielded) and the man with the ball throws there the
# moment he has it; tap another while it is in the air and the man who catches it throws it on. Nothing is thrown unless you tap. Any base can be picked.

# 1) planning: keep the computer's plan for the runners, drop its throw
rep("function planOutcome(B, c){", "function planOutcomeAuto(B, c){")
rep("const judgePlay = () => BALL && BALL.play;", """// the base each runner is heading for in the computer's plan (D = the base he ends on if nobody throws), with his own start and speed
function defEntries(B){
  const e = [{ key:'runB', man:M.batter, s0:0, D:Math.max(1, Math.min(4, (B.defKind === 'groundout' || B.defKind === 'dp' || B.defKind === 'fc') ? 1 : (B.runN || 1))), batter:true }];
  M.bases.forEach((p, i) => { if (p) e.push({ key:'run' + i, man:p, s0:90 * (i + 1), D:Math.min(4, i + 1 + runnerAdv(B, i)) }); });
  return e;
}
function planOutcome(B, c){
  planOutcomeAuto(B, c);
  if (!userPitches() || B.hr || B.foul || B.isCatch || !['single', 'double', 'triple', 'error', 'groundout', 'dp', 'fc'].includes(B.play)) return;
  B.defManual = true; B.defKind = B.play; B.play = 'def'; B.thr = null;
  B.def = { queue:[], pass:null, outs:[], entries:defEntries(B), last:-1 };
  const arrive = B.def.entries.map(e => runTime(spdOf(e.man), 90 * e.D - e.s0));
  B.tEnd = Math.max((B.tf || 0) + 1.5, ...arrive) + .7;
}
const DEF_BASES = [[63.64, 63.64], [127.28, 0], [63.64, -63.64], [0, 0]];                 // first, second, third, home: [depth, lat]
// a tap on a base while the ball is in play on defence: the screen square round each base is about half an inch
function defBaseAt(p){
  if (!window.GL3D || !GL3D.toScreen) return null;
  GL3D.setView('air'); GL3D.placeCamera(); GL3D.cam.updateMatrixWorld(true);
  let best = null, bd = 1e9;
  DEF_BASES.forEach((b, i) => { const q = GL3D.toScreen(b[1], 0, -b[0], W, H), dx = Math.abs(p.x - q.x), dy = Math.abs(p.y - q.y); if (dx <= 26 && dy <= 26 && dx + dy < bd){ bd = dx + dy; best = i; } });
  return best;
}
function defTap(bi){
  const B = BALL; if (!B || !B.defManual || B.done) return;
  const d = B.def, last = d.queue.length ? d.queue[d.queue.length - 1] : (d.pass && d.pass.ph === 'fly' ? d.pass.base : null);
  if (last === bi) return;
  d.queue.push(bi);
}
// a throw reaches base bi at time ta: a runner heading for that base who would get there later is out
function defResolve(B, bi, ta){
  const nb = bi + 1, d = B.def;
  d.entries.forEach(e => {
    if (d.outs.includes(e.key) || 90 * nb <= e.s0 || nb > e.D) return;
    if (ta < runTime(spdOf(e.man), 90 * nb - e.s0)){ d.outs.push(e.key); const c = RUNCTL[e.key]; if (c){ c.out = true; c.outT = B.t; } say(e.batter ? 'OUT AT ' + ['FIRST', 'SECOND', 'THIRD', 'HOME'][bi] + '!' : 'OUT!'); }
  });
}
// the ball after it is fielded: held, thrown where you tapped, caught, held again
function defStep(B){
  const T = B.thrInfo, d = B.def; if (!T) return;
  if (!d.pass){ if (B.t < T.tf + T.tr) return; d.pass = { ph:'hold', x:T.pf[0], y:T.pf[1], t0:B.t, first:true }; }
  const Pz = d.pass;
  if (Pz.ph === 'hold'){
    B.d = Pz.x; B.lat = Pz.y; B.h = 4; B.heldAfter = true;
    if (B.t < Pz.t0 || !d.queue.length) return;
    const bi = d.queue.shift(), to = DEF_BASES[bi];
    const holder = Pz.first ? B.chaser : (FLD || []).reduce((a, f) => Math.hypot(f.x - Pz.x, f.y - Pz.y) < Math.hypot(a.x - Pz.x, a.y - Pz.y) ? f : a);
    const rt = routeThrow(holder, [Pz.x, Pz.y], B.t, to, 0, true), thr = mkThr(rt, [Pz.x, Pz.y], to);
    B.thr = thr; d.pass = { ph:'fly', thr, to, t1:thr.t1, base:bi };
    return;
  }
  const tp = thrPos(Pz.thr, B.t);
  B.d = tp.d; B.lat = tp.lat; B.h = tp.flying ? 4 + Math.sin(tp.u * Math.PI) * Math.min(16, tp.len * .09) : 4;
  if (tp.flying) B.inFlightThrow = true; else B.heldAfter = true;
  if (B.t >= Pz.t1){ defResolve(B, Pz.base, Pz.t1); d.pass = { ph:'hold', x:Pz.to[0], y:Pz.to[1], t0:B.t + .5 }; B.heldAfter = true; B.inFlightThrow = false; }
}
const judgePlay = () => BALL && BALL.play;""")

# 2) the ball and the throws
rep("  if (isManualPlay(B)){ manualThrow(B); if (B.pass){ if (B.pass.ph === 'fly' && B.pass.fl) B.inFlightThrow = true; else B.heldAfter = true; } }\n  else if (B.thr && B.t >= B.thr.t0 && !B.hr){",
    "  if (isManualPlay(B)){ manualThrow(B); if (B.pass){ if (B.pass.ph === 'fly' && B.pass.fl) B.inFlightThrow = true; else B.heldAfter = true; } }\n  else if (B.defManual){ defStep(B); }\n  else if (B.thr && B.t >= B.thr.t0 && !B.hr){")
# the play is over once the runners have settled, the throws are done and nothing is queued
rep("if ((B.judged && B.t > B.tEnd && (B.t > B.tEnd + 9 || (runnersSettled() && !B.inFlightThrow))) || P.playT > 24000){",
    "if ((B.judged && B.t > B.tEnd && (B.t > B.tEnd + 9 || (runnersSettled() && !B.inFlightThrow && !(B.defManual && B.def.queue.length)))) || P.playT > 24000){")
# the runners follow the computer's plan whatever the play is called
rep("function runnerAdv(B, i){\n  if (B.isCatch) return 0;\n  if (B.play === 'groundout' || B.play === 'dp' || B.play === 'fc'){",
    "function runnerAdv(B, i){\n  if (B.isCatch) return 0;\n  const kind = B.play === 'def' ? B.defKind : B.play;\n  if (kind === 'groundout' || kind === 'dp' || kind === 'fc'){")

# 3) the result of your throws
rep("function applyPlay(res){", """// what your throws made of the computer's plan: who is out, where everyone ends up
function defHit(){
  const B = BALL, d = B.def, names = ['', 'single', 'double', 'triple', 'single'];
  const nb = [null, null, null]; let runs = 0, outs = 0, batterBase = 0, batterOut = false;
  d.entries.slice().sort((a, b) => b.D - a.D).forEach(e => {
    if (d.outs.includes(e.key)){ outs++; if (e.batter) batterOut = true; return; }
    let k = e.D;
    if (e.batter) batterBase = Math.min(3, k);
    if (k >= 4){ runs++; score(e.man); if (e.batter) batterBase = 4; return; }
    while (k > 1 && nb[k - 1]) k--;
    if (nb[k - 1]) k = 0;
    if (k >= 1) nb[k - 1] = e.man;
  });
  M.bases = nb;
  const runnerOut = d.outs.some(k => k !== 'runB');
  let res, txt;
  if (batterOut){ res = outs >= 2 ? 'dp' : 'groundout'; txt = outs >= 2 ? 'DOUBLE PLAY' : (B.defKind === 'single' || B.defKind === 'double' || B.defKind === 'triple' ? 'THROWN OUT' : 'GROUND OUT'); }
  else if (runnerOut && (B.defKind === 'groundout' || B.defKind === 'dp' || B.defKind === 'fc')){ res = 'fc'; txt = "FIELDER'S CHOICE"; }
  else if (B.defKind === 'error'){ res = 'error'; txt = 'ERROR!'; }
  else { res = names[Math.max(1, batterBase)]; txt = ({ single:'BASE HIT', double:'DOUBLE!', triple:'TRIPLE!' })[res]; if (runnerOut) txt = 'OUT ON THE BASES'; }
  return { res, runs, outs, txt };
}
function applyPlay(res){""")
rep("  const manual = ['single', 'double', 'triple', 'error'].includes(res) && isManualPlay(BALL) && Object.keys(RUNCTL).length ? manualHit(res) : null;",
    "  const isDef = res === 'def' && BALL && BALL.defManual;\n  const manual = isDef ? defHit() : (['single', 'double', 'triple', 'error'].includes(res) && isManualPlay(BALL) && Object.keys(RUNCTL).length ? manualHit(res) : null);")
rep("    res = manual.res; st.ab++; runs = manual.runs; out = manual.outs;\n    if (res !== 'error'){ st.h++;",
    "    res = manual.res; st.ab++; runs = manual.runs; out = manual.outs;\n    if (isDef && ['single', 'double', 'triple'].includes(res)) M.H[M.top ? 'away' : 'home']++;\n    if (isDef && res === 'error') M.E[M.top ? 'home' : 'away']++;\n    if (!['error', 'groundout', 'dp', 'fc'].includes(res)){ st.h++;")
rep("txt = manual.txt || ({ single:'BASE HIT',", "txt = manual.txt || ({ single:'BASE HIT',")

# 4) the tap
rep("  if (P && P.state === 'inplay') for (const b of RUNBTN.filter(", "  if (P && P.state === 'inplay' && BALL && BALL.defManual){ const bi = defBaseAt(p); if (bi !== null){ defTap(bi); touch.used = true; return; } }\n  if (P && P.state === 'inplay') for (const b of RUNBTN.filter(")
rep("runToggle, runBack, drawPlay,", "runToggle, runBack, drawPlay, defTap, defBaseAt, defHit, get BALL(){ return BALL; },")
s = s.replace("BUILD = '11-06a'", "BUILD = '11-06b'")
s = re.sub(r"gl3d\.js\?v=11-06a", "gl3d.js?v=11-06b", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
