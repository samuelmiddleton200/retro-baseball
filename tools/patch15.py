s=open('index.html',encoding='utf-8').read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(s.count(old),old[:80]); s=s.replace(old,new)

# 1) control state + helpers, placed before launchBall
rep("function launchBall(ev, la, sa, qual){", '''// ── runner control: a diamond over every runner; tap it to flip red (stop at the next base) / green (keep going) ──────────
let RUNCTL = {};                                   // per runner: his own clock, his go/stop flag and the distance he is held to
let RUNBTN = [];                                   // on-screen hit areas of this frame's diamonds
function runPosCtl(key, man, s0, s1){
  const c = RUNCTL[key] || (RUNCTL[key] = { te:0, last:BALL.t, go:true, cap:Infinity, s0, s1, pos:s0, man });
  const dt = BALL.t - c.last; c.last = BALL.t; c.s1 = s1;
  const lim = Math.min(s1, c.cap);
  if (dt > 0 && s0 + runDist(man.speed, c.te - CFG.RUN_START_DELAY) < lim - .01) c.te += dt;        // he only runs while he is short of where he is held
  return c.pos = Math.min(lim, s0 + runDist(man.speed, c.te - CFG.RUN_START_DELAY));
}
function runToggle(key){
  const c = RUNCTL[key]; if (!c) return;
  c.go = !c.go;
  if (c.go) c.cap = Infinity;
  else c.cap = c.pos <= c.s0 + .5 ? c.s0 + 90 : Math.ceil((c.pos - .5) / 90) * 90;       // red: he stops on the next base
}
// bases a runner gains on this play once the red/green holds are applied (n = what the play gives him)
function runnerGain(key, s0, n){ const c = RUNCTL[key]; return c && c.cap !== Infinity ? Math.max(0, Math.min(n, Math.round((c.cap - s0) / 90))) : n; }
function drawRunDiamond(key, sx, sy){
  const c = RUNCTL[key]; if (!c) return;
  const done = c.pos >= Math.min(c.s1, c.cap) - .05;                           // he has arrived: show it dimmed
  const col = c.go ? '#3ddc6a' : '#ff4d4d', rr = 7;
  g.save(); g.globalAlpha = done ? .55 : 1; g.translate(sx, sy);
  g.beginPath(); g.moveTo(0, -rr); g.lineTo(rr, 0); g.lineTo(0, rr); g.lineTo(-rr, 0); g.closePath();
  g.fillStyle = col; g.fill(); g.strokeStyle = '#ffffff'; g.lineWidth = 1.4; g.stroke(); g.restore();
  RUNBTN.push({ key, x: sx - 14, y: sy - 14, w: 28, h: 28 });
}
function launchBall(ev, la, sa, qual){
  RUNCTL = {};''')

# 2) 3D draw: runners use the controlled position and get a diamond
rep("      const s = Math.min(s1, s0 + runDist(man.speed, B.t - dly)), a = basePathPos(s), a2 = basePathPos(Math.min(360, s + 1.5));",
    "      const s = runPosCtl(key, man, s0, s1), a = basePathPos(s), a2 = basePathPos(Math.min(360, s + 1.5));")
rep("      S.people.push(gxPerson(key, 'run', man, bt, X, Z, dirYaw, B.t < dly ? GL3D.poseBatter(1, t) : (s >= s1 - .05 ? GL3D.poseReady(t) : GL3D.poseRun(mv.ph, man.speed)), {}));\n    };",
    "      const cc = RUNCTL[key], held = cc && s >= Math.min(s1, cc.cap) - .05;\n      S.people.push(gxPerson(key, 'run', man, bt, X, Z, dirYaw, B.t < dly ? GL3D.poseBatter(1, t) : (held ? GL3D.poseReady(t) : GL3D.poseRun(mv.ph, man.speed)), {}));\n      if (s1 > s0 && !B.isCatch && B.play !== 'groundout'){ const q = GL3D.toScreen(X, 8.4, Z, W, H); runMarks.push([key, q.x, q.y]); }\n    };")
rep("  const dly = CFG.RUN_START_DELAY;\n  if (!B.foul){\n    const run = (key, man, s0, s1) => {","  const dly = CFG.RUN_START_DELAY, runMarks = []; GX.runMarks = runMarks;\n  if (!B.foul){\n    const run = (key, man, s0, s1) => {")
# 3) draw the diamonds in the HUD pass and clear hit areas
rep("function gxPlayHud(B){\n","function gxPlayHud(B){\n  RUNBTN = []; (GX.runMarks || []).forEach(m => drawRunDiamond(m[0], m[1], m[2]));\n")
# 4) taps
rep("  for (const b of btns) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){ b.fn(); touch.used = true; return; }\n  if (phase === 'pitching'){",
    "  for (const b of btns) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){ b.fn(); touch.used = true; return; }\n  if (P && P.state === 'inplay') for (const b of RUNBTN) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){ runToggle(b.key); touch.used = true; return; }\n  if (phase === 'pitching'){")
# 5) resolution: hold flags change how far each runner gets
rep("""  for (let i = 2; i >= 0; i--){
    if (!b[i]) continue;
    const to = i + n;
    if (to >= 3){ runs++; score(b[i]); b[i] = null; }
    else { b[to] = b[i]; b[i] = null; }
  }
  if (batterSafe){ if (n - 1 >= 3){ runs++; score(M.batter); } else b[n - 1] = M.batter; }""",
"""  for (let i = 2; i >= 0; i--){
    if (!b[i]) continue;
    let to = i + runnerGain('run' + i, 90 * (i + 1), n);
    while (to < 3 && to > i && b[to]) to--;                                    // a held runner is in the way: stop behind him
    if (to >= 3){ runs++; score(b[i]); b[i] = null; }
    else if (to !== i){ b[to] = b[i]; b[i] = null; }
  }
  if (batterSafe){ let nb = Math.max(1, runnerGain('runB', 0, n)); while (nb < 4 && nb > 1 && b[nb - 1]) nb--; if (nb - 1 >= 3){ runs++; score(M.batter); } else b[nb - 1] = M.batter; }""")
s=s.replace("BUILD = '11-02a'","BUILD = '11-02b'")
open('index.html','w',encoding='utf-8').write(s)
print('ok')
