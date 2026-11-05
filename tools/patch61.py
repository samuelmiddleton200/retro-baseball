s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:100]); s = s.replace(a, b)
# a throw to a base is a throw to the man covering it: picked here, sent to the bag in planCover, and the ball is only caught when HE is there
i = s.index("    let cover = bi === 3 ? 0 : Infinity;"); j = s.index("    const dBall = Math.max(0, dist(from, tgt) - 1.5);")
s = s[:i] + """    let cover = bi === 3 ? 0 : Infinity, catcher = null;                                    // the catcher is always at the plate
    if (bi < 3){
      const glove = STAND[bi + 1], isRelay = f => best.relays.some(r => r.f === f);
      const pick = list => list.forEach(f => {
        const D = Math.max(0, dist(live ? [f.x, f.y] : [f.d, f.lat], glove) - .5);
        const tt = (live ? BALL.t + D / (f.speed * CFG.ROUTE_EFF) : fldReach(f, D)) + .12;     // the same walk stepFielders draws
        if (tt < cover){ cover = tt; catcher = f; }
      });
      pick((FLD || []).filter(f => f !== thrower && BAG_COVER[bi].includes(f.pos) && !isRelay(f)));
      if (!catcher) pick((FLD || []).filter(f => f !== thrower && BAG_COVER[bi].includes(f.pos)));
    }
""" + s[j:]
rep("    const throwArr = Math.max(best.arr, Math.min(cover, 99));", "    const throwArr = Math.max(best.arr, Math.min(cover, 99));\n    best.catcher = catcher;")
rep("legs: rt.legs, relays: rt.relays, carry: !!rt.carry,", "legs: rt.legs, relays: rt.relays, catcher: rt.catcher || null, carry: !!rt.carry,")
rep("        if (reach > l1.t1) continue;", "        if (reach + .25 > l1.t1) continue;")
# planCover: the planned catcher goes to the bag, whichever branch
rep("  const toward = (f, t, k) => [f.d + (t.d - f.d) * k, f.lat + (t.lat - f.lat) * k];\n",
    "  const toward = (f, t, k) => [f.d + (t.d - f.d) * k, f.lat + (t.lat - f.lat) * k];\n  if (B.thr && B.thr.catcher){ const bi = [[63.64, 63.64], [127.28, 0], [63.64, -63.64]].findIndex(q => Math.abs(q[0] - B.thr.to[0]) < 1 && Math.abs(q[1] - B.thr.to[1]) < 1); if (bi >= 0) send(B.thr.catcher, STAND[bi + 1][0], STAND[bi + 1][1], bi + 1); }\n")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
# a man covering the bag the throw is going to is never also a relay man on that throw
s = open('index.html', encoding='utf-8').read()
a = "  const mates = (FLD || []).filter(f => f !== thrower && ['1B', '2B', 'SS', '3B'].includes(f.pos));"
b = "  const bi0 = BASE_PTS4.findIndex(q => Math.abs(q[0] - tgt[0]) < 1 && Math.abs(q[1] - tgt[1]) < 1);\n  const mates = (FLD || []).filter(f => f !== thrower && ['1B', '2B', 'SS', '3B'].includes(f.pos) && !(bi0 >= 0 && bi0 < 3 && BAG_COVER[bi0].includes(f.pos)));      // the man on the bag is the catcher, never a relay"
assert s.count(a) == 1; s = s.replace(a, b)
open('index.html', 'w', encoding='utf-8').write(s)
