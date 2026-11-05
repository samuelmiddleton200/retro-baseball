s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# when you throw by tapping, the men the computer would have used are already on their way: remember that plan
rep("  B.defManual = true; B.defKind = B.play; B.play = 'def'; B.thr = null;", "  B.defManual = true; B.defKind = B.play; B.play = 'def'; B.autoThr = B.thr; B.thr = null;")
rep("  if (B.thr && B.thr.catcher){ const bi =", "  const pthr = B.thr || B.autoThr;\n  if (pthr && pthr.catcher){ const bi =")
rep("Math.abs(q[0] - B.thr.to[0]) < 1 && Math.abs(q[1] - B.thr.to[1]) < 1); if (bi >= 0) send(B.thr.catcher,", "Math.abs(q[0] - pthr.to[0]) < 1 && Math.abs(q[1] - pthr.to[1]) < 1); if (bi >= 0) send(pthr.catcher,")
rep("  if (B.thr && B.thr.relays) B.thr.relays.forEach(r =>", "  if (pthr && pthr.relays) pthr.relays.forEach(r =>")

# infield: every man has his own bag, as on a real field
a = s.index("    // 2) the standing assignments"); b = s.index("    ['LF', 'CF', 'RF'].forEach(p => { const o = byPos(p); if (o){ const q = toward(o, { d:60")
s = s[:a] + """    // 2) the standing assignments: the man who fields it, everybody else goes to his own bag
    const first = byPos('1B'), second = byPos('2B'), short = byPos('SS'), third = byPos('3B');
    const bag = (f, n) => send(f, STAND[n][0], STAND[n][1], n);
    if (c === first){ bag(second, 1); bag(short, 2); bag(third, 3); }                            // down the first-base line: 1B fields it (and may run it to the bag), 2B covers first, SS second
    else if (c === second){ bag(first, 1); bag(short, 2); bag(third, 3); }                       // between first and second: 2B fields it, SS to second, 1B to first
    else if (c === short){ bag(first, 1); bag(second, 2); bag(third, 3); }                       // the hole: SS fields it, 2B to second
    else if (c === third){ bag(first, 1); bag(second, 2); bag(short, 3); }                       // down the third-base line: 3B fields it, SS covers third
    else { bag(first, 1); bag(second, 2); bag(third, 3); if (short){ const p = toward(short, { d:STAND[2][0], lat:0 }, .5); send(short, p[0], p[1], 0); } }
""" + s[b:]
# live relays only use a man where he is, or where he is heading
rep("      const d0 = dist(cur, tgt), mr = throwRange(m.man.fielding), spots = [live ? [m.x, m.y] : [m.d, m.lat]];\n      for (const fr of [.5, .65, .8, .9, .98]){",
    "      const d0 = dist(cur, tgt), mr = throwRange(m.man.fielding), spots = [live ? (m.go ? [m.go.x, m.go.y] : [m.x, m.y]) : [m.d, m.lat]];\n      if (!live) for (const fr of [.5, .65, .8, .9, .98]){")
rep("        const reach = live ? BALL.t + dist([m.x, m.y], sp) / (m.speed * CFG.ROUTE_EFF) : fldReach(m, dist([m.d, m.lat], sp));",
    "        const reach = live ? BALL.t + dist([m.x, m.y], sp) / (m.speed * CFG.ROUTE_EFF) + .12 : fldReach(m, dist([m.d, m.lat], sp));")
s = s.replace("BUILD = '11-11d'", "BUILD = '11-11e'").replace("gl3d.js?v=11-11d", "gl3d.js?v=11-11e")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
