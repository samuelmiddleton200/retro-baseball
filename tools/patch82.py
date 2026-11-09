s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── the computer's clubs: players of 80-120. Each club has its own level (84 to 112), its players sit within about 8 of it ──
rep("""  const teams = TEAMS.map(t => {
    const mine = t.ab === teamAb, q = rnd(101, 86);
    const lv = () => mine ? rnd(75, 60) : clamp(q + (bell() - .5) * 16, 80, 105);
    const hit = pos => { const L = lv(); return fitTo(makeHitter(L, pos), L); };
    const arm = (role, plus) => { const L = clamp(lv() + plus, 60, 108); return fitTo(makePitcher(L, role), L); };
    const lineup = POS.map(p => hit(p));
    const rot = [0,1,2,3,4].map(() => arm('SP', 0));
    const pen = [0,1,2,3].map(() => arm('RP', 0)).concat([arm('CP', 4)]);
    [...lineup, ...rot, ...pen].forEach(p => { p.num = ri(1, 72); });
    return { ...t, lineup, rot, pen, w:0, l:0, rs:0, ra:0, q };
  });""", """  const teams = TEAMS.map(t => {
    const mine = t.ab === teamAb, q = rnd(112, 84), r = makeRoster(mine, q);
    return { ...t, lineup:r.lineup, rot:r.rot, pen:r.pen, w:0, l:0, rs:0, ra:0, q };
  });""")
rep("function newGame(teamAb){", """// a whole roster: nine hitters, five starters, five relievers (the last is the closer, 4 better). The computer's players are 80-120 around the club's level q; yours start at 60-75.
function makeRoster(mine, q){
  const lv = () => mine ? rnd(75, 60) : clamp(q + (bell() - .5) * 16, 80, 120);
  const hit = pos => { const L = lv(); return fitTo(makeHitter(L, pos), L); };
  const arm = (role, plus) => { const L = clamp(lv() + plus, 60, 120); return fitTo(makePitcher(L, role), L); };
  const lineup = POS.map(p => hit(p));
  const rot = [0,1,2,3,4].map(() => arm('SP', 0));
  const pen = [0,1,2,3].map(() => arm('RP', 0)).concat([arm('CP', 4)]);
  [...lineup, ...rot, ...pen].forEach(p => { p.num = ri(1, 72); });
  return { lineup, rot, pen };
}
function newGame(teamAb){""")
# a new season: the computer's clubs get new rosters at the new levels
rep("  G.teams.forEach(t => { t.w = t.l = t.rs = t.ra = 0; [...t.lineup, ...t.rot, ...t.pen].forEach(p => { p.st = newStat(); }); });",
    "  G.teams.forEach((t, i) => { t.w = t.l = t.rs = t.ra = 0; if (i !== G.team){ t.q = rnd(112, 84); Object.assign(t, makeRoster(false, t.q)); } [...t.lineup, ...t.rot, ...t.pen].forEach(p => { p.st = newStat(); }); });")
s = s.replace("BUILD = '11-12k'", "BUILD = '11-12l'").replace("gl3d.js?v=11-12k", "gl3d.js?v=11-12l")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
