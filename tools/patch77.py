s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── THE PERFECT GAME (minigame): bottom of the 9th, up 1-0, runners on first and second, nobody out. A 60 reliever and a 60 defence against an endless line of 120 hitters.
# 3 outs with the lead: win 2,000. 3 outs with the game tied (one run in): tie 1,000. The moment they take the lead: loss 500. Unlimited plays. ──
fn = """
function perfectStart(){
  if (!G) return false;
  const me = myTeam(), opp0 = G.teams.find(t => t !== me && t.lg !== me.lg) || G.teams[(G.team + 1) % G.teams.length];
  const mk = (L, pos) => { const c = fitTo(makeHitter(L, pos), L); c.contact = c.power = c.fielding = c.speed = L; c.ovr = ovrOf(c); c.st = newStat(); c.id = null; return c; };
  const rp = fitTo(makePitcher(60, 'RP'), 60); rp.pos = 'RP'; rp.velocity = rp.control = rp.stamina = 60; rp.pitches = { FB:60, CV:60, SL:60, CH:60 }; rp.st = newStat(); rp.stam = 1; rp.id = null;
  me.lineup = POS.map(p => mk(60, p)); me.rot = [rp, rp, rp, rp, rp]; me.pen = [];                 // your side for this game only: 60s everywhere; rebuildTeam() puts your real team back
  const opp = Object.assign({}, opp0, { lineup: POS.map(p => mk(120, p)), _bi: 0 });
  M = {
    home: opp, away: me, meHome: false,
    inning:9, top:false, outs:0, bases:[opp.lineup[7], opp.lineup[6], null], score:{ home:0, away:1 },
    balls:0, strikes:0, lineHome:0, lineAway:0, ls:{ away:[0, 0, 0, 0, 0, 0, 0, 0, 1], home:[0, 0, 0, 0, 0, 0, 0, 0] }, H:{ away:0, home:0 }, E:{ away:0, home:0 },
    pitcherHome: opp0.rot[0], pitcherAway: rp, pcHome:0, pcAway:0, line:[], mode:'defense',
    park: makePark(opp), msg:null, msgT:0, over:false, exc:0, perfect:true,
  };
  M.uni = pickUniforms(M.home, M.away); M.stad = (G.day || 0) % STADIUMS.length;
  Object.assign(M.park, { lf:330, cf:400, rf:330 });
  M.coins0 = G.coins; M.earn = null; M.rep = {}; M.pitchSimmed = false;                              // no per-play coins here: the result pays
  PG.clear(); pg(M.pitcherHome).used = true; pg(M.pitcherAway).used = true;
  swing = null; BALL = null; P = null;
  phase = 'atbat'; setupAtBat();
  setTimeout(warmHitView, 30);
  return true;
}
function perfectEnd(){
  if (!M || M.over) return;
  const a = M.score.away, h = M.score.home, kind = h > a ? 'loss' : h === a ? 'tie' : 'win', coins = { win:2000, tie:1000, loss:500 }[kind];
  M.over = true; phase = 'over'; M.perfectRes = { kind, coins }; G.coins += coins;
  const pf = G.perfect || (G.perfect = { plays:0, wins:0, ties:0, losses:0 }); pf.plays++; pf[kind === 'win' ? 'wins' : kind === 'tie' ? 'ties' : 'losses']++;
  rebuildTeam(); save();                                                                              // your real team is back
}
function perfectQuit(){ rebuildTeam(); M = null; phase = 'menu'; menu = 'minigames'; }
function drawPerfectPause(){
  btns = [];
  R(0, 0, W, H, '#0b1018e8');
  textb('PAUSED', W / 2, 36, '#fff', 18, 'center');
  textb('THE PERFECT GAME: HOLD THE 1-0 LEAD', W / 2, 66, UI.ice, 8, 'center', W - 20);
  button(W / 2 - 80, 100, 160, 22, 'RESUME', () => { phase = userPitches() ? 'pitching' : 'atbat'; }, '#2f6fe0');
  button(W / 2 - 80, 130, 160, 18, 'QUIT (NO COINS)', () => perfectQuit(), '#2a1a1a', '#fff', 7);
}
function drawPerfectOver(){
  btns = [];
  R(0, 0, W, H, '#0b1018ee');
  const F = M.perfectRes || { kind:'loss', coins:0 }, col = F.kind === 'win' ? '#54d67a' : F.kind === 'tie' ? UI.yellow : '#ff6b5a';
  textb(F.kind === 'win' ? 'YOU HELD IT!' : F.kind === 'tie' ? 'TIE GAME' : 'THEY TOOK THE LEAD', W / 2, 10, col, 18, 'center', W - 16);
  textb(`${M.away.ab} ${M.score.away}   -   ${M.home.ab} ${M.score.home}`, W / 2, 38, '#fff', 10, 'center');
  const pf = G.perfect || { plays:0, wins:0, ties:0, losses:0 };
  textb(`WINS ${pf.wins}   TIES ${pf.ties}   LOSSES ${pf.losses}`, W / 2, 56, UI.ice, 7, 'center');
  const y0 = 76, lx = W / 2 - 110, rx = W / 2 + 110;
  textb(F.kind === 'win' ? 'SHUTDOWN' : F.kind === 'tie' ? 'TIED IT UP' : 'PLAYED IT OUT', lx, y0, UI.ice, 7, 'left'); textb('+' + F.coins.toLocaleString(), rx, y0, '#ffffff', 7, 'right');
  R(lx, y0 + 14, 220, 1, '#2a5ba6');
  textb('TOTAL EARNED', lx, y0 + 18, '#ffd23f', 8, 'left'); textb('+' + F.coins.toLocaleString() + ' coins', rx, y0 + 17, '#ffd23f', 9, 'right');
  button(W / 2 - 108, y0 + 42, 100, 22, 'PLAY AGAIN', () => { M = null; perfectStart(); }, '#2f6fe0');
  button(W / 2 + 8, y0 + 42, 100, 22, 'CONTINUE', () => { M = null; phase = 'menu'; menu = 'minigames'; }, '#1a2030', '#fff', 8);
}
"""
rep("// ── the playoffs ──", fn + "// ── the playoffs ──")
# the game ends the way the minigame says
rep("function endHalf(){\n", "function endHalf(){\n  if (M.perfect) return perfectEnd();                                                  // three outs: the lead held, or the game is tied\n")
rep("  say(txt);\n  payPlay(res, b, p, st.rbi - rbi0);\n  nextBatter();", "  say(txt);\n  payPlay(res, b, p, st.rbi - rbi0);\n  if (M.perfect && M.score.home > M.score.away) return perfectEnd();                 // they took the lead: it is over\n  nextBatter();")
rep("function drawGameMenu(){\n  if (M.derby) return drawDerbyPause();", "function drawGameMenu(){\n  if (M.derby) return drawDerbyPause();\n  if (M.perfect) return drawPerfectPause();")
rep("function drawOver(){\n  if (M.derby) return drawDerbyOver();", "function drawOver(){\n  if (M.perfect) return drawPerfectOver();\n  if (M.derby) return drawDerbyOver();")
rep("if (!M || M.over || M.derby || !G || phase === 'menu' || phase === 'over') return;", "if (!M || M.over || M.derby || M.perfect || !G || phase === 'menu' || phase === 'over') return;")
# the minigames menu: a second card
rep("  button(10, H - 22, 70, 18, 'BACK', () => menu = 'title');\n}\n// ── league leaders:", "  button(10, H - 22, 70, 18, 'BACK', () => menu = 'title');\n}\n// ── league leaders:") if False else None
a = s.index("function drawMinigames(){"); b = s.index("button(10, H - 22, 70, 18, 'BACK', () => menu = 'title');", a)
s = s[:b] + """  const by2 = by + 78 + 6, pf = G.perfect || { plays:0, wins:0, ties:0, losses:0 };
  uiBox(bx, by2, bw, 76);
  ptitle('THE PERFECT GAME', W / 2, by2 + 6, 12, UI.yellow);
  text('BOTTOM 9TH. UP 1-0. RUNNERS ON 1ST AND 2ND, NO OUTS.', W / 2, by2 + 24, UI.ice, 6, 'center', bw - 12);
  text('YOUR 60 PITCHER AND 60 DEFENCE VS ENDLESS 120 HITTERS.', W / 2, by2 + 33, UI.ice, 6, 'center', bw - 12);
  text('WIN 2,000    TIE 1,000    LOSS 500', W / 2, by2 + 43, '#ffffff', 6.5, 'center', bw - 12);
  button(bx + bw / 2 - 50, by2 + 54, 100, 18, 'PLAY', () => { perfectStart(); }, '#2f6fe0', '#fff', 8);
  """ + s[b:]
rep("  const bw = Math.min(300, W - 40), bx = W / 2 - bw / 2, by = 34;\n  uiBox(bx, by, bw, 78);", "  const bw = Math.min(300, W - 40), bx = W / 2 - bw / 2, by = 24;\n  uiBox(bx, by, bw, 78);")
s = s.replace("BUILD = '11-12a'", "BUILD = '11-12b'").replace("gl3d.js?v=11-12a", "gl3d.js?v=11-12b")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
