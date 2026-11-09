s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── a one-time upgrade for a save made before the stronger league: new computer clubs, the season picks up at game 17 of 24 with you at 10-7, and every player's stats start from zero ──
fn = """
function injectLeague(){
  G.teams.forEach((t, i) => { t.w = t.l = t.rs = t.ra = 0; if (i !== G.team){ t.q = rnd(112, 84); Object.assign(t, makeRoster(false, t.q)); } });      // new, stronger computer clubs
  G.seasonLen = 24; G.po = null; G.season = (G.season || 1) + 1;
  makeSchedule();                                                                          // a fresh 24-game schedule
  const myRes = Array.from({ length:17 }, (_, i) => i < 10);                               // you are 10-7 after 17 games, in a random order
  for (let i = myRes.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); [myRes[i], myRes[j]] = [myRes[j], myRes[i]]; }
  const pWin = (a, b) => 1 / (1 + Math.exp(-(G.teams[a].q - G.teams[b].q) / 12));         // everyone else: the better club wins more often
  for (let d = 0; d < 17; d++){
    (G.rounds[Math.floor(d / 3)] || []).forEach(([a, b]) => {
      const aw = a === G.team ? myRes[d] : b === G.team ? !myRes[d] : Math.random() < pWin(a, b);
      const wr = ri(3, 9), lr = ri(0, wr - 1), w = aw ? a : b, l = aw ? b : a;
      G.teams[w].w++; G.teams[l].l++; G.teams[w].rs += wr; G.teams[w].ra += lr; G.teams[l].rs += lr; G.teams[l].ra += wr;
      if (a === G.team || b === G.team){ const sg = G.sched[d], won = w === G.team; if (sg){ sg.done = true; sg.rs = won ? wr : lr; sg.ra = won ? lr : wr; } }
    });
  }
  G.day = 17;
  G.teams.forEach(t => [...(t.lineup || []), ...(t.rot || []), ...(t.pen || [])].forEach(p => { p.st = newStat(); }));      // every stat back to zero
  G.cards.forEach(p => { p.st = newStat(); p.stam = 1; });
  G.leagueV = 3;
  try { localStorage.removeItem('retrobaseball.match.v1'); } catch (e){}                  // a game in progress from the old league cannot be resumed
  save();
}
"""
rep("const load = () => {", fn + "const load = () => {")
rep("      if (G.packReset !== 2){ G.freeAt = 0; G.packReset = 2; }                    // one-time: the daily pack that glitched is available again",
    "      if (G.packReset !== 2){ G.freeAt = 0; G.packReset = 2; }                    // one-time: the daily pack that glitched is available again\n      if (G.leagueV !== 3) injectLeague();                                        // one-time: the stronger league, game 17 of 24 at 10-7, stats reset")
# a new save is already on the new league
rep("  makeSchedule();\n  save();\n}\n// point the team at whatever cards are in the slots right now", "  makeSchedule();\n  G.leagueV = 3;\n  save();\n}\n// point the team at whatever cards are in the slots right now")
s = s.replace("BUILD = '11-12m'", "BUILD = '11-12n'").replace("gl3d.js?v=11-12m", "gl3d.js?v=11-12n")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
