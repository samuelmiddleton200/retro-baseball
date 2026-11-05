import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:100]); s = s.replace(a, b)

# ── CFG: throws fly at 50 mph (60 fielding) to 70 mph (120); glove to release is 0.3 s off the ground, 0 in the air, plus 0.1 s per 40 ft; the batter's first leg takes 0.2 s longer ──
rep("  ARM_BASE: 70, ARM_SLOPE: 0.5, // throw mph = 70 + (fielding - 60) * 0.5: 60 throws 70 mph, 120 throws 100 mph",
    "  ARM_BASE: 50, ARM_SLOPE: 1 / 3, // the ball flies at 50 + (fielding - 60) / 3 mph: 50 mph at 60 fielding, 70 mph at 120")
rep("  THROW_EFFICIENCY: 0.85,       // every throw flies at 85% of the speed the rating says",
    "  THROW_EFFICIENCY: 1,          // (the rating's speed is the speed the ball flies)")
rep("  TRANSFER_GROUND: 0.65, TRANSFER_AIR: 0.40,   // glove to release",
    "  TRANSFER_GROUND: 0.3, TRANSFER_AIR: 0, GLOVE_PER_FT: 0.1 / 40,   // glove to release: 0.3 s fielding it off the ground, nothing extra catching it in the air, plus 0.1 s for every 40 ft of the throw (relay men too)")
rep("  RUNNER_ACCEL_T: 1.2, RUN_START_DELAY: 0.2,", "  RUNNER_ACCEL_T: 1.2, RUN_START_DELAY: 0.2, BATTER_EXTRA: 0.2,   // the batter's run to first starts 0.2 s later than a runner's: 4.6 s a 60, 3.96 s a 120;")
rep("const RELAY_TR = 0.55;                                     // an infielder catching it and throwing it on", "const RELAY_TR = 0;                                         // a relay man's glove time is the 0.1 s per 40 ft of his own throw, nothing flat")

# ── routeThrow: every throw's release waits 0.1 s per 40 ft of that throw ──
rep("  const leg = (a, b, ts, fps) => { const len = dist(a, b); return { from:a, to:b, t0:ts, t1:ts + len / fps, len }; };",
    "  const leg = (a, b, ts, fps) => { const len = dist(a, b), t0r = ts + len * CFG.GLOVE_PER_FT; return { from:a, to:b, t0:t0r, t1:t0r + len / fps, len }; };      // released 0.1 s per 40 ft after he has it")
# the throw to first/second/third: off the ground (0.3 s) unless the ball was caught in the air (that never reaches here)
rep("  const tr = Math.hypot(pf[0], pf[1]) < 150 && !B.hr ? CFG.TRANSFER_GROUND : CFG.TRANSFER_AIR;", "  const tr = CFG.TRANSFER_GROUND;                                    // fielded off the ground")

# ── the batter's first leg ──
rep("const runTime = (rate, S) => { const a = CFG.RUNNER_ACCEL_T, v = sprintFps(rate); return CFG.RUN_START_DELAY + (S <= .5 * v * a",
    "const runTime = (rate, S, batter) => { const a = CFG.RUNNER_ACCEL_T, v = sprintFps(rate); return CFG.RUN_START_DELAY + (batter ? CFG.BATTER_EXTRA : 0) + (S <= .5 * v * a")
rep("c.te = runTime(spdOf(man), c.pos - s0); c.back = null; }", "c.te = runTime(spdOf(man), c.pos - s0, c.bat); c.back = null; }")
rep("c.te = runTime(spdOf(c.man), c.pos - c.s0); c.cap", "c.te = runTime(spdOf(c.man), c.pos - c.s0, c.bat); c.cap")
rep("  if (dt > 0 && s0 + runDist(spdOf(man), c.te - CFG.RUN_START_DELAY) < c.cap - .01) c.te += dt;", "  const dly0 = CFG.RUN_START_DELAY + (c.bat ? CFG.BATTER_EXTRA : 0);\n  if (dt > 0 && s0 + runDist(spdOf(man), c.te - dly0) < c.cap - .01) c.te += dt;")
rep("  c.pos = Math.min(c.cap, s0 + runDist(spdOf(man), c.te - CFG.RUN_START_DELAY));", "  c.pos = Math.min(c.cap, s0 + runDist(spdOf(man), c.te - dly0));")
rep("forced, arr:{} };", "forced, arr:{}, bat: key === 'runB' };")
rep("    const a1 = throwArr(1, tr), t1 = runTime(spd, 90);", "    const a1 = throwArr(1, tr), t1 = runTime(spd, 90, true);")
rep("for (const k of [2, 3]) if (runTime(spd, 90 * k) + CFG.EXTRA_BASE_MARGIN", "for (const k of [2, 3]) if (runTime(spd, 90 * k, true) + CFG.EXTRA_BASE_MARGIN")
rep("  B.tEnd = Math.max(runTime(spd, 90 * n), tf) + .8;", "  B.tEnd = Math.max(runTime(spd, 90 * n, true), tf) + .8;")
rep("const arrive = B.def.entries.map(e => runTime(spdOf(e.man), 90 * e.D - e.s0));", "const arrive = B.def.entries.map(e => runTime(spdOf(e.man), 90 * e.D - e.s0, e.batter));")
rep("if (ta < runTime(spdOf(e.man), 90 * nb - e.s0)){", "if (ta < runTime(spdOf(e.man), 90 * nb - e.s0, e.batter)){")
rep("  const dly = CFG.RUN_START_DELAY, runMarks = []; GX.runMarks = runMarks;", "  const dly0 = CFG.RUN_START_DELAY, runMarks = []; GX.runMarks = runMarks;")
rep("      const dirYaw = Math.atan2(a2.lat - a.lat, -(a2.d - a.d));\n      const cc = RUNCTL[key], held",
    "      const dirYaw = Math.atan2(a2.lat - a.lat, -(a2.d - a.d)), dly = key === 'runB' ? dly0 + CFG.BATTER_EXTRA : dly0;\n      const cc = RUNCTL[key], held")
rep("  const bp = basePathPos(Math.min(batS, runDist(spdOf(M.batter), B.t - CFG.RUN_START_DELAY)));", "  const bp = basePathPos(Math.min(batS, runDist(spdOf(M.batter), B.t - CFG.RUN_START_DELAY - CFG.BATTER_EXTRA)));")
# the batter at the plate waits on the first leg's extra delay: his standing pose / the run-start use dly below; the rest of the code that reads `dly` lives inside run()

# ── the ball on the ground: no 3-ft lift, no shadow ──
rep("const LIFT = paintOn() ? BALL_LIFT : 0;", "const LIFT = paintOn() ? BALL_LIFT * clamp((B.h - .3) / 5, 0, 1) : 0;      // rolling on the ground it is not lifted")
rep("{ x:B.lat, y:B.h + .4 + LIFT, z:-B.d, r:.95 };", "{ x:B.lat, y:B.h + .4 + LIFT, z:-B.d, r:.95, ground: B.h < .6 };")
rep("    R(Math.round(gq.x - sw / 2), Math.round(gq.y), sw, 1, 'rgba(20,14,6,.38)');                              // its shadow on the grass, a flat pixel bar",
    "    if (!b.ground) R(Math.round(gq.x - sw / 2), Math.round(gq.y), sw, 1, 'rgba(20,14,6,.38)');                // its shadow on the grass, a flat pixel bar (none while it rolls)")
# the derby's ball too
for a, b in [("DTRAIL.push([B.lat, B.h + .4 + BALL_LIFT, -B.d]);", "DTRAIL.push([B.lat, B.h + .4 + BALL_LIFT * clamp((B.h - .3) / 5, 0, 1), -B.d]);"),
             ("q = derbyPt(B.d, B.lat, B.h + BALL_LIFT);", "q = derbyPt(B.d, B.lat, B.h + BALL_LIFT * clamp((B.h - .3) / 5, 0, 1));"),
             ("    R(Math.round(gq.x - 2), Math.round(gq.y), 4, 1, 'rgba(20,14,6,.4)');", "    if (B.h >= .6) R(Math.round(gq.x - 2), Math.round(gq.y), 4, 1, 'rgba(20,14,6,.4)');")]:
    rep(a, b)

s = s.replace("BUILD = '11-11b'", "BUILD = '11-11c'"); s = re.sub(r"gl3d\.js\?v=11-11b", "gl3d.js?v=11-11c", s)
open('index.html', 'w', encoding='utf-8').write(s)
d = open('tools/derby.js', encoding='utf-8').read()
for a, b in [("DTRAIL.push([B.lat, B.h + .4 + BALL_LIFT, -B.d]);", "DTRAIL.push([B.lat, B.h + .4 + BALL_LIFT * clamp((B.h - .3) / 5, 0, 1), -B.d]);"),
             ("q = derbyPt(B.d, B.lat, B.h + BALL_LIFT);", "q = derbyPt(B.d, B.lat, B.h + BALL_LIFT * clamp((B.h - .3) / 5, 0, 1));"),
             ("    R(Math.round(gq.x - 2), Math.round(gq.y), 4, 1, 'rgba(20,14,6,.4)');", "    if (B.h >= .6) R(Math.round(gq.x - 2), Math.round(gq.y), 4, 1, 'rgba(20,14,6,.4)');")]:
    assert d.count(a) == 1, a; d = d.replace(a, b)
open('tools/derby.js', 'w', encoding='utf-8').write(d)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
