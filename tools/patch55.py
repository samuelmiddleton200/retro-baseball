import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ── stamina: a fastball costs 0.8, every other pitch 1; the circle is 7-12 in (14-24 in when spent) ──
rep("const pg = p => PG.get(p) || (PG.set(p, { pc:0, r:0, po:0, used:false }), PG.get(p));",
    "const pg = p => PG.get(p) || (PG.set(p, { pc:0, sp:0, r:0, po:0, used:false, nT:0, nS:0, nB:0, nC:0 }), PG.get(p));       // pc = pitches thrown, sp = stamina spent; nT/nS/nB/nC = what the batters have seen from him this game\nconst spOf = g => g.sp != null ? g.sp : g.pc;")
rep("function fatigue(){ const p = curPitcher(); return clamp(pg(p).pc / stamCap(p), 0, 1); }",
    "function fatigue(){ const p = curPitcher(); return clamp(spOf(pg(p)) / stamCap(p), 0, 1); }")
rep("  if (g.pc >= stamCap(p) || g.r > g.pc / 10) changePitcher(t, pickReliever(t));", "  if (spOf(g) >= stamCap(p) || g.r > g.pc / 10) changePitcher(t, pickReliever(t));")
rep("function circleIn(p){ return lerp(10, 5, clamp((p.control - 60) / 60, 0, 1)) * (1 + fatigue()); }",
    "function circleIn(p){ return lerp(12, 7, clamp((p.control - 60) / 60, 0, 1)) * (1 + fatigue()); }")
rep("// the circle the ball can land in, as a diameter in inches: 120 control = 5 in, 60 control = 10 in, straight line between.\n// Tiredness widens it in a straight line too: half his stamina gone = 1.5x (7.5 and 15 in), all of it = 2x",
    "// the circle the ball can land in, as a diameter in inches: 120 control = 7 in, 60 control = 12 in, straight line between.\n// Tiredness widens it in a straight line too: half his stamina gone = 1.5x, all of it = 2x (14 and 24 in). A fastball costs 0.8 stamina, any other pitch 1.")
rep("  pg(curPitcher()).pc++; if (M.top) M.pcHome++; else M.pcAway++;\n  // the computer's batter makes up its mind as the ball comes in\n  if (!userBats()) cpuDecide();",
    """  { const g0 = pg(curPitcher()); g0.sp = spOf(g0) + (type === 'FB' ? .8 : 1); g0.pc++; }
  if (M.top) M.pcHome++; else M.pcAway++;
  // the computer's batter makes up its mind as the ball comes in (from what he has seen from this pitcher so far); then this pitch goes in the book
  if (!userBats()) cpuDecide();
  { const g0 = pg(curPitcher()), strike = Math.abs(P.tx) <= 1 && Math.abs(P.ty) <= 1; g0.nT = (g0.nT || 0) + 1; if (strike) g0.nS = (g0.nS || 0) + 1; else g0.nB = (g0.nB || 0) + 1; if (strike && Math.abs(P.tx) >= .5 && Math.abs(P.ty) >= .5) g0.nC = (g0.nC || 0) + 1; }""")
rep("  pg(p).pc += ri(3, 5);\n", "  { const g1 = pg(p), n1 = ri(3, 5); g1.pc += n1; g1.sp = spOf(g1) + n1 * .92; }\n")
rep("${cur.name} has thrown ${pg(cur).pc} pitches (limit ${Math.round(stamCap(cur))}). A pitcher who is taken out cannot come back.",
    "${cur.name} has thrown ${pg(cur).pc} pitches, ${Math.round(100 * (1 - clamp(spOf(pg(cur)) / stamCap(cur), 0, 1)))}% stamina left. A pitcher who is taken out cannot come back.")

# ── the batter reads the pitch off the first half of its flight, and learns what this pitcher throws (this game, this pitcher) ──
a = s.index("function cpuDecide(){"); b = s.index("  // his timing is off by an amount that shrinks as contact goes up.")
new = """function cpuDecide(){
  const b = M.batter, g0 = pg(curPitcher());
  const con = clamp((b.contact - 60) / 60, 0, 1);
  const eye = clamp((b.contact * .6 + b.power * .4 - 60) / 60, 0, 1);
  // He judges the pitch from the first half of its flight and assumes it keeps going straight. A fastball is what it looks like (and is read more exactly);
  // a curve or slider looks like it ends somewhere else than it does: higher or wider, so it looks like a strike and then drops off.
  const blur = lerp(.62, .16, eye) * (P.type === 'FB' ? .75 : 1);
  const projX = P.tx - CFG.READ_BREAK * P.br[0] / (ZONE.w / 2), projY = P.ty - CFG.READ_BREAK * P.br[1] / (ZONE.h / 2);
  const seenX = projX + (bell() - .5) * 2 * blur, seenY = projY + (bell() - .5) * 2 * blur;
  const looksStrike = Math.abs(seenX) <= 1 && Math.abs(seenY) <= 1;
  const close = Math.abs(seenX) <= 1.45 && Math.abs(seenY) <= 1.45;
  // how eager he is, by count
  let want = looksStrike ? .74 : close ? .26 : .06;
  if (M.strikes === 2) want = looksStrike ? .93 : close ? .72 : .22;     // protect the plate
  if (M.balls === 3 && M.strikes < 2) want *= .62;                        // take the walk
  want *= lerp(.82, 1.12, clamp((b.power - 60) / 60, 0, 1));              // sluggers hack more
  // what he has seen from this pitcher today: mostly strikes and they swing more (15% when strikes lead by one, 30% by two or more); mostly balls and they swing less, the same way
  if ((g0.nT || 0) >= 6){ const d = (g0.nS || 0) - (g0.nB || 0), mag = Math.abs(d) >= 2 ? .30 : Math.abs(d) === 1 ? .15 : 0; want *= 1 + Math.sign(d) * mag; }
  // and if most of them have been on the corners, they go after what is headed for a corner (up to 30% more)
  if ((g0.nT || 0) >= 10 && Math.abs(seenX) >= .5 && Math.abs(seenY) >= .5 && Math.abs(seenX) <= 1.25 && Math.abs(seenY) <= 1.25) want *= 1 + clamp(((g0.nC || 0) / g0.nT - .35) / .35, 0, 1) * .30;
  if (!chance(clamp(want, .02, .97))) return;                             // he takes it
"""
s = s[:a] + new + s[b:]
rep("  PIVOT: 0.55, ", "  READ_BREAK: 3.2,               // how far a breaking pitch's early path misleads a hitter about where it ends (zone units per unit of break)\n  MID_SWEET: 1.2,               // the middle 4 x 4 inches of the plate: hits there are this much likelier to leave on the home run angle\n  PIVOT: 0.55, ")
# the middle of the plate: a home run is likelier (when you pitch to the computer's hitters)
rep("  const pSweet = lerp(.03, .30, Math.pow(skill, 1.1));",
    "  const mid = userPitches() && Math.abs(P.tx) <= 2 / IN_X && Math.abs(P.ty) <= 2 / IN_Y;        // a pitch right down the middle (4 x 4 inches) is easier to drive\n  const pSweet = lerp(.03, .30, Math.pow(skill, 1.1)) * (mid ? CFG.MID_SWEET : 1);")
rep("get shopTab(){ return shopTab; },", "get shopTab(){ return shopTab; }, makeContact2: makeContact, cpuDecide,")
s = s.replace("BUILD = '11-07j'", "BUILD = '11-08a'"); s = re.sub(r"gl3d\.js\?v=11-07j", "gl3d.js?v=11-08a", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
