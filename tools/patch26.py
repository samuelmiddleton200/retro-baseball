s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) strike zone: rulebook size (17 in plate + a ball's width each side, about 2.2 ft tall), same centre as before
rep("  ZONE.w = 44 * TU; ZONE.h = 64 * TU; ZONE.x = tx(392) - ZONE.w / 2; ZONE.y = ty(318);",
    "  ZONE.w = 54 * TU; ZONE.h = 70 * TU; ZONE.x = tx(392) - ZONE.w / 2; ZONE.y = ty(318) - 3 * TU;      // 17 in plate + a ball's width, about 2.2 ft tall")

# 2) the batter-runner who stops at first runs through the bag, slows, and walks back to it
rep("      const s = runPosCtl(key, man, s0, s1), a = basePathPos(s), a2 = basePathPos(Math.min(360, s + 1.5));\n      const X = a.lat, Z = -a.d, mv = gxMover(key, X, Z);",
"""      const s = runPosCtl(key, man, s0, s1); let a = basePathPos(s), over = 0;
      const a2 = basePathPos(Math.min(360, s + 1.5)), cc0 = RUNCTL[key];
      if (cc0 && cc0.manual && !cc0.out && s0 === 0 && cc0.cap === 90 && s >= 90 - .05){          // stopping at first: he runs on past the bag, slows, then walks back to it
        if (cc0.arrT == null) cc0.arrT = B.t;
        const dt = B.t - cc0.arrT, RUN = 13, SLOW = .8, BACK = 1.1;
        over = dt < SLOW ? RUN * (1 - (1 - dt / SLOW) * (1 - dt / SLOW)) : dt < SLOW + BACK ? RUN * (1 - (dt - SLOW) / BACK) : 0;
        a = { d: 63.64 + over * .7071, lat: 63.64 + over * .7071 };                               // straight on along the line from home through first
      }
      const X = a.lat, Z = -a.d, mv = gxMover(key, X, Z);""")
rep("      const cc = RUNCTL[key], held = cc && s >= cc.cap - .05;","      const cc = RUNCTL[key], held = cc && s >= cc.cap - .05 && over < .3;")
s = s.replace("BUILD = '11-02w'", "BUILD = '11-02x'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
