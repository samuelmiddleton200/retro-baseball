s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# ── a runner you control moves like a body: he accelerates, brakes before he turns round, and runs back at the same speed ──
rep("s0, s1, pos:s0, man, manual, forced, arr:{}, bat: key === 'runB' };\n  }\n  const dt = BALL.t - c.last; c.last = BALL.t; c.s1 = s1;\n  if (c.back){",
    """s0, s1, pos:s0, man, manual, forced, arr:{}, bat: key === 'runB', v:0, dir:1, dly: CFG.RUN_START_DELAY + (key === 'runB' ? CFG.BATTER_EXTRA : 0) };
  }
  const dt = BALL.t - c.last; c.last = BALL.t; c.s1 = s1;
  if (c.manual){
    const vmax = sprintFps(spdOf(man)), acc = vmax / CFG.RUNNER_ACCEL_T, dec = acc * 2;      // braking is twice as quick as getting going; speed is the same both ways
    let left = Math.max(0, dt);
    while (left > 1e-6){
      const h = Math.min(left, .02); left -= h;
      const tgt = c.back ? c.back.to : c.cap, want = tgt > c.pos + .01 ? 1 : tgt < c.pos - .01 ? -1 : 0;
      if (want === 0){ c.v = 0; if (c.back){ c.pos = c.back.to; c.cap = c.back.to; c.back = null; } continue; }
      if (c.dly > 0 && c.v === 0){ c.dly -= h; continue; }                                  // the start: his reaction
      const sv = Math.sign(c.v);
      if (sv !== 0 && sv !== want){ c.v -= sv * dec * h; if (Math.sign(c.v) !== sv) c.v = 0; }     // braking before he can turn
      else c.v = clamp(c.v + want * acc * h, -vmax, vmax);
      c.pos += c.v * h;
      if (c.v > 0 && !c.back && c.pos >= c.cap){ c.pos = c.cap; c.v = 0; }
      else if (c.v < 0 && c.back && c.pos <= c.back.to){ c.pos = c.back.to; c.v = 0; c.cap = c.back.to; c.back = null; }
      else if (c.v > 0 && c.back && c.pos >= 360){ c.pos = 360; c.v = 0; }
      c.pos = clamp(c.pos, c.s0 > 0 ? 0 : 0, 360);
      if (c.v) c.dir = Math.sign(c.v);
    }
    for (let k = 1; k <= 4; k++) if (c.arr[k] == null && 90 * k > s0 && c.pos >= 90 * k - .05) c.arr[k] = BALL.t;
    return c.pos;
  }
  if (c.back){""")
# turning round no longer moves the stop: his cap stays until he gets to the base behind him
rep("  c.back = { to }; c.cap = to;\n}", "  c.back = { to };\n}")
rep("if (c.back){ c.back = null; c.te = runTime(spdOf(c.man), c.pos - c.s0, c.bat); c.cap = Math.min(360, Math.ceil((c.pos + .5) / 90) * 90); return; }",
    "if (c.back){ c.back = null; c.cap = Math.min(360, Math.ceil((c.pos + .5) / 90) * 90); return; }")
rep("const runnersSettled = () => Object.values(RUNCTL).every(c => !c.back && c.pos >= c.cap - .05);", "const runnersSettled = () => Object.values(RUNCTL).every(c => !c.back && c.pos >= c.cap - .05 && !(c.manual && Math.abs(c.v) > .01));")
# facing: running back he faces back down the line, and he turns round when he does
rep("      const a2 = basePathPos(Math.min(360, s + 1.5)), cc0 = RUNCTL[key];", "      const cc0 = RUNCTL[key], ds = cc0 && cc0.manual ? (cc0.v < -.01 ? -1 : cc0.v > .01 ? 1 : cc0.dir || 1) : 1, a2 = basePathPos(clamp(s + ds * 1.5, 0, 360));")
rep("const cc = RUNCTL[key], held = cc && s >= cc.cap - .05 && over < .3;", "const cc = RUNCTL[key], held = cc && s >= cc.cap - .05 && over < .3 && !(cc.manual && (cc.back || Math.abs(cc.v) > .01));")
s = s.replace("BUILD = '11-11i'", "BUILD = '11-11j'").replace("gl3d.js?v=11-11i", "gl3d.js?v=11-11j")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
