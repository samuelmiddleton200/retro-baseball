s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) the throw: the ball really flies from the fielder to a base, and a runner who has not got there yet is OUT
rep('''function stepBall(dt){
  const B = BALL; if (!B || B.done) return;
  B.t += dt / 1000;
  const p = ballPos(B, B.t); B.d = p.d; B.lat = p.lat; B.h = p.h;
  if (B.t >= B.T) B.landed = true;
}''', '''const BASE_XY = [[63.64, 63.64], [127.28, 0], [63.64, -63.64], [0, 0]];       // [depth, lat] of 1B, 2B, 3B, home
function stepBall(dt){
  const B = BALL; if (!B || B.done) return;
  B.t += dt / 1000;
  const p = ballPos(B, B.t); B.d = p.d; B.lat = p.lat; B.h = p.h;
  if (B.t >= B.T) B.landed = true;
  if (isManualPlay(B)) manualThrow(B);
  else if (B.thr && B.t >= B.thr.t0 && !B.hr){                     // the planned throw (a ground out, a single): the ball flies to the base and stays there
    const u = clamp((B.t - B.thr.t0) / Math.max(.05, B.thr.t1 - B.thr.t0), 0, 1);
    B.d = lerp(B.thr.from[0], B.thr.to[0], u); B.lat = lerp(B.thr.from[1], B.thr.to[1], u); B.h = 4 + Math.sin(u * Math.PI) * Math.min(16, B.thr.len * .09);
  }
}
// You run the bases, so the defence has to decide where to throw: at the lead runner who is still running, at the base he is heading for.
// If the throw gets there before he does and that base was an extra one (past the base the hit gave him), he is thrown out.
function manualThrow(B){
  const T = B.thrInfo; if (!T || B.hr) return;
  if (!B.pass){ if (B.t < T.tf + T.tr) return; B.pass = { ph:'hold', x:T.pf[0], y:T.pf[1], t0:B.t }; }
  const P = B.pass;
  if (P.ph === 'hold'){
    B.d = P.x; B.lat = P.y; B.h = 4;
    if (B.t < P.t0) return;                                                     // the transfer: glove to hand
    let best = null;
    for (const key in RUNCTL){
      const c = RUNCTL[key]; if (c.out || c.pos >= c.cap - .05) continue;
      const nb = runAhead(c), bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;
      if (!best || c.pos > best.c.pos) best = { key, c, nb, bi };
    }
    if (!best) return;
    const to = BASE_XY[best.bi], len = Math.hypot(to[0] - P.x, to[1] - P.y);
    B.pass = { ph:'fly', fr:[P.x, P.y], to, len, t0:B.t, t1:B.t + len / T.arm, run:best };
    return;
  }
  const u = clamp((B.t - P.t0) / Math.max(.05, P.t1 - P.t0), 0, 1);
  B.d = lerp(P.fr[0], P.to[0], u); B.lat = lerp(P.fr[1], P.to[1], u); B.h = 4 + Math.sin(u * Math.PI) * Math.min(16, P.len * .09);
  if (B.t >= P.t1){
    const c = P.run.c, extra = P.run.nb > c.s0 + 90 + .5;                         // only a base beyond the free one can be lost
    if (extra && !c.out && c.pos < P.run.nb - .05){ c.out = true; c.cap = c.pos; c.outT = B.t; say('OUT!'); }
    B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t + .5 };
  }
}''')

# 2) a runner who is out stops, then leaves the field; no diamond for him
rep("      if (isManualPlay(B)){ const q = GL3D.toScreen(X, 9.6, Z, W, H); runMarks.push([key, q.x, q.y]); }",
    "      if (isManualPlay(B) && !(cc && cc.out)){ const q = GL3D.toScreen(X, 9.6, Z, W, H); runMarks.push([key, q.x, q.y]); }")
rep("      const X = a.lat, Z = -a.d, mv = gxMover(key, X, Z);\n      const dirYaw",
    "      const X = a.lat, Z = -a.d, mv = gxMover(key, X, Z);\n      if (RUNCTL[key] && RUNCTL[key].out && B.t > RUNCTL[key].outT + .9) return;       // thrown out: he walks off\n      const dirYaw")

# 3) the result uses who was actually thrown out
a = s.index("  const res2 = entries.map(e => {")
b = s.index("  const nb = [null, null, null];\n  res2.sort(")
s = s[:a] + '''  const res2 = entries.map(e => {
    const c = RUNCTL[e.key];
    return { e, K: c ? c.cap : e.s0 + 90, out: !!(c && c.out) };
  });
''' + s[b:]
s = s.replace("BUILD = '11-02n'", "BUILD = '11-02o'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
