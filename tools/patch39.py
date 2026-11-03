s = open('index.html', encoding='utf-8').read()

def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)

# ── contact reach: how far outside the strike zone a batter can still hit it, by his contact rating ──
rep("const inZone = () =>", """// Zone units -> inches: the zone is the plate plus a ball's width (19.9 in) wide and 26.4 in tall, so one unit is 9.95 in across and 13.2 in up.
const IN_X = 9.95, IN_Y = 13.2;
// how far outside the zone (in inches) a hitter can still reach, by contact rating: 60-69 = 0, 70-79 = 1, 80-89 = 2, 90-99 = 3.5, 100-109 = 5, 110-120 = 6
const reachIn = con => con < 70 ? 0 : con < 80 ? 1 : con < 90 ? 2 : con < 100 ? 3.5 : con < 110 ? 5 : 6;
const outsideIn = (tx, ty) => Math.hypot(Math.max(0, Math.abs(tx) - 1) * IN_X, Math.max(0, Math.abs(ty) - 1) * IN_Y);   // 0 when the pitch is anywhere in the zone
// a pitch that touches the batter: on his side, a few inches off the plate out to the far side of his body (he stands in the box)
function hitsBatter(){
  const b = M.batter, side = b.bats === 'L' ? 1 : -1, lateral = P.tx * side;
  return lateral > 1.45 && lateral < 3.4 && P.ty > -1.5 && P.ty < 1.25;
}
const inZone = () =>""")
rep("  const vMiss = Math.max(0, Math.abs(P.ty - plane) - batH);\n  const hMiss = Math.max(0, Math.abs(P.tx) - reach);\n  const sN = (vMiss + hMiss) / .62;",
    "  const sN = outsideIn(P.tx, P.ty) > reachIn(b.contact) + .001 ? 2 : 0;       // he cannot get the barrel to a pitch further out of the zone than his contact reaches")
# a pitch that touches him, with no swing, is a hit by pitch: first base
rep("        P.result = inZone() ? 'called' : 'ball';\n        say(P.result === 'called' ? 'STRIKE' : 'BALL');",
    "        P.result = inZone() ? 'called' : hitsBatter() ? 'hbp' : 'ball';\n        say(P.result === 'called' ? 'STRIKE' : P.result === 'hbp' ? 'HIT BY PITCH' : 'BALL');")
# the computer does not throw at the batter on purpose
rep("  const ax = strike ? rnd(.8, -.8) : (chance(.5) ? rnd(1.9, 1.15) : rnd(-1.15, -1.9));",
    "  const bs = b.bats === 'L' ? 1 : -1, outer = chance(.5) ? 1 : -1;\n  const ax = strike ? rnd(.8, -.8) : (outer === bs ? bs * rnd(1.38, 1.12) : outer * rnd(1.9, 1.15));      // on the batter's side a miss stays just off the plate")
s = s.replace("BUILD = '11-03z'", "BUILD = '11-04a'")
rep("runToggle, runBack, drawPlay,", "runToggle, runBack, drawPlay, reachIn, outsideIn, hitsBatter,")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
