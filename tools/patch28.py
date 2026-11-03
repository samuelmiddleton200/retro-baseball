s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) moving back: a runner between bases can be turned round and sent to the base he left
rep("  const dt = BALL.t - c.last; c.last = BALL.t; c.s1 = s1;\n  if (dt > 0 && s0 + runDist",
"""  const dt = BALL.t - c.last; c.last = BALL.t; c.s1 = s1;
  if (c.back){                                                                  // turned round: he runs back toward the base he left
    c.pos = Math.max(c.back.to, c.pos - sprintFps(man.speed) * Math.max(0, dt));
    if (c.pos <= c.back.to + .01){ c.pos = c.back.to; c.cap = c.back.to; c.te = runTime(man.speed, c.pos - s0); c.back = null; }
    return c.pos;
  }
  if (dt > 0 && s0 + runDist""")
rep("function runToggle(key){\n  const c = RUNCTL[key]; if (!c || !c.manual) return;\n",
"""function runBack(key){                                                         // double-tap: turn round and go back to the base behind him
  const c = RUNCTL[key]; if (!c || !c.manual || c.out || c.back) return;
  const to = Math.floor((c.pos - .5) / 90) * 90;
  if (to < 90 || to < c.s0) return;                                              // nothing behind him but home plate
  c.back = { to }; c.cap = to;
}
function runToggle(key){
  const c = RUNCTL[key]; if (!c || !c.manual) return;
  if (c.back){ c.back = null; c.te = runTime(c.man.speed, c.pos - c.s0); c.cap = Math.min(360, Math.ceil((c.pos + .5) / 90) * 90); return; }     // changed his mind: forward again
""")
rep("const runnersSettled = () => Object.values(RUNCTL).every(c => c.pos >= c.cap - .05);", "const runnersSettled = () => Object.values(RUNCTL).every(c => !c.back && c.pos >= c.cap - .05);")
rep("  const green = c.cap > runAhead(c), settled = c.pos >= c.cap - .05, rr = 2.6;", "  const green = c.cap > runAhead(c), settled = !c.back && c.pos >= c.cap - .05, rr = 2.6;")
rep("  g.fillStyle = green ? '#3ddc6a' : '#ff4d4d'; g.fill(); g.strokeStyle = '#ffffff'; g.lineWidth = .9; g.stroke(); g.restore();",
    "  g.fillStyle = c.back ? '#4aa3ff' : green ? '#3ddc6a' : '#ff4d4d'; g.fill(); g.strokeStyle = '#ffffff'; g.lineWidth = .9; g.stroke(); g.restore();      // blue = going back")

# 2) the defence also tags a runner who is running back
rep("      const c = RUNCTL[key]; if (c.out || c.pos >= c.cap - .05) continue;\n      const nb = c.cap, bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;",
    "      const c = RUNCTL[key]; if (c.out || (!c.back && c.pos >= c.cap - .05)) continue;\n      const nb = c.cap, bi = Math.round(nb / 90) - 1; if (bi < 0 || bi > 3) continue;")
rep("    const c = P.run.c, extra = P.run.nb > c.s0 + (c.forced ? 90 : 0) + .5;           // only a base beyond the one he has to take can be lost\n    if (extra && !c.out && c.pos < P.run.nb - .05){ B.pass = { ph:'wait', x:P.to[0], y:P.to[1], run:P.run }; return; }",
    "    const c = P.run.c, extra = c.back || P.run.nb > c.s0 + (c.forced ? 90 : 0) + .5;   // only a base beyond the one he has to take can be lost; going back is always a tag play\n    if (extra && !c.out && (c.back ? c.pos > P.run.nb + .05 : c.pos < P.run.nb - .05)){ B.pass = { ph:'wait', x:P.to[0], y:P.to[1], run:P.run }; return; }")
rep("    if (c.pos >= P.run.nb - .05){ c.out = true; c.cap = c.pos; c.outT = B.t; say('TAGGED OUT!');",
    "    if (c.back ? c.pos <= P.run.nb + .05 : c.pos >= P.run.nb - .05){ c.out = true; c.back = null; c.cap = c.pos; c.outT = B.t; say('TAGGED OUT!');")

# 3) the double-tap
rep("  if (P && P.state === 'inplay') for (const b of RUNBTN) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){ runToggle(b.key); touch.used = true; return; }",
"""  if (P && P.state === 'inplay') for (const b of RUNBTN) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){
    const c = RUNCTL[b.key], now = performance.now();
    if (c && c.lastTap && now - c.lastTap < 330){ runToggle(b.key); runBack(b.key); c.lastTap = 0; }      // two quick taps: turn round (the first tap's flip is undone)
    else { runToggle(b.key); if (c) c.lastTap = now; }
    touch.used = true; return;
  }""")
s = s.replace("BUILD = '11-02z'", "BUILD = '11-03a'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
