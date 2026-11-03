s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# forced runners must run; the others may stand on their base until you send them
rep("  if (c.pos <= c.s0 + .5) return c.s0 + 90;\n  const q = c.pos / 90;",
    "  if (c.pos <= c.s0 + .5) return c.forced ? c.s0 + 90 : c.s0;      // a forced runner is running to the next base; a free one is standing on his\n  const q = c.pos / 90;")
rep("const c = RUNCTL[key] || (RUNCTL[key] = { te:0, last:BALL.t, cap: manual ? Math.min(360, s0 + 90) : s1, s0, s1, pos:s0, man, manual, arr:{} });",
    """let c = RUNCTL[key];
  if (!c){
    // forced = he has to run because the runner behind him pushes him: the batter always; first base's runner always; second's if first is taken; third's if first and second are
    const bs = M.bases, forced = key === 'runB' || key === 'run0' || (key === 'run1' && !!bs[0]) || (key === 'run2' && !!(bs[0] && bs[1]));
    c = RUNCTL[key] = { te:0, last:BALL.t, cap: manual ? Math.min(360, s0 + (forced ? 90 : 0)) : s1, s0, s1, pos:s0, man, manual, forced, arr:{} };
  }""")
# the throw: a force play is made on the base; anyone else has to be TAGGED, so the fielder waits for him
rep("  const u = clamp((B.t - P.t0) / Math.max(.05, P.t1 - P.t0), 0, 1);\n  B.d = lerp(P.fr[0], P.to[0], u);",
    """  if (P.ph === 'wait'){                                                          // he holds the ball on the base until the runner arrives, then tags him
    B.d = P.x; B.lat = P.y; B.h = 4;
    const c = P.run.c;
    if (c.pos >= P.run.nb - .05){ c.out = true; c.cap = c.pos; c.outT = B.t; say('TAGGED OUT!'); B.pass = { ph:'hold', x:P.x, y:P.y, t0:B.t + .5 }; }
    return;
  }
  const u = clamp((B.t - P.t0) / Math.max(.05, P.t1 - P.t0), 0, 1);
  B.d = lerp(P.fr[0], P.to[0], u);""")
rep("""    const c = P.run.c, extra = P.run.nb > c.s0 + 90 + .5;                         // only a base beyond the free one can be lost
    if (extra && !c.out && c.pos < P.run.nb - .05){ c.out = true; c.cap = c.pos; c.outT = B.t; say('OUT!'); }
    B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t + .5 };""",
"""    const c = P.run.c, extra = P.run.nb > c.s0 + (c.forced ? 90 : 0) + .5;           // only a base beyond the one he has to take can be lost
    if (extra && !c.out && c.pos < P.run.nb - .05){ B.pass = { ph:'wait', x:P.to[0], y:P.to[1], run:P.run }; return; }
    B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t + .5 };""")
rep("  runToggle, get RUNCTL(){ return RUNCTL; },", "  runToggle, drawPlay, get RUNCTL(){ return RUNCTL; },")
s = s.replace("BUILD = '11-02p'", "BUILD = '11-02q'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
