import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ── 1) a called strike: any part of the ball (as drawn) touching the zone ──────────────────────────────
rep("const inZone = () => Math.abs(P.tx) <= 1 && Math.abs(P.ty) <= 1;",
    "// a pitch is a strike if ANY part of the ball touches the zone: the ball is drawn with a radius of ballAt(1).r pixels at the plate, so the zone grows by that much on every side\nconst inZone = () => { const r = ballAt(1).r; return Math.abs(P.tx) <= 1 + r / (ZONE.w / 2) && Math.abs(P.ty) <= 1 + r / (ZONE.h / 2); };")

# ── 2) the whole league plays: every day the 14 other games are played with the same engine ───────────
rep("function gameOver(){\n  clearMatchSnap();\n  M.over = true; phase = 'over';\n  if (M.score.home !== M.score.away){                                      // the decisions\n    const hw = M.score.home > M.score.away, team = t => t.rot.concat(t.pen).filter(p => pg(p).used);\n    const wp = team(hw ? M.home : M.away).sort((x, y) => pg(y).po - pg(x).po)[0], lp = team(hw ? M.away : M.home).sort((x, y) => pg(y).r - pg(x).r || pg(y).po - pg(x).po)[0];\n    if (wp) wp.st.w = (wp.st.w || 0) + 1;\n    if (lp) lp.st.l = (lp.st.l || 0) + 1;\n  }\n",
"""// the win goes to the winning team's pitcher with the most outs, the loss to the losing team's pitcher who gave up the most runs
function giveDecisions(){
  if (M.score.home === M.score.away) return;
  const hw = M.score.home > M.score.away, team = t => t.rot.concat(t.pen).filter(p => pg(p).used);
  const wp = team(hw ? M.home : M.away).sort((x, y) => pg(y).po - pg(x).po)[0], lp = team(hw ? M.away : M.home).sort((x, y) => pg(y).r - pg(x).r || pg(y).po - pg(x).po)[0];
  if (wp) wp.st.w = (wp.st.w || 0) + 1;
  if (lp) lp.st.l = (lp.st.l || 0) + 1;
}
// one game between two other clubs, played pitch by pitch with the same rules and stats as yours, then put away without a trace on the game you are in
function simLeagueGame(hi, ai){
  const keep = { M, P, BALL, swing, phase, pitchSel }, pgKeep = new Map(PG); PG.clear();
  try {
    const home = G.teams[hi], away = G.teams[ai]; home._bi = 0; away._bi = 0;
    M = { home, away, meHome:false, league:true, inning:1, top:true, outs:0, bases:[null, null, null], score:{ home:0, away:0 }, balls:0, strikes:0, lineHome:0, lineAway:0,
          ls:{ away:[], home:[] }, H:{ away:0, home:0 }, E:{ away:0, home:0 }, pitcherHome:home.rot[(G.day + hi) % 5], pitcherAway:away.rot[(G.day + ai) % 5],
          pcHome:0, pcAway:0, line:[], mode:'sim', park:{}, msg:null, msgT:0, over:false, exc:0 };
    pg(M.pitcherHome).used = true; pg(M.pitcherAway).used = true;
    setupAtBat();
    let guard = 0; while (!M.over && guard++ < 4000) simPitch();
    if (!M.over) gameOver();
  } catch (e){ console.error(e); }
  finally { M = keep.M; P = keep.P; BALL = keep.BALL; swing = keep.swing; phase = keep.phase; pitchSel = keep.pitchSel; PG.clear(); pgKeep.forEach((v, k) => PG.set(k, v)); }
}
// the other 28 clubs: paired off at random every day (the same pairs on a reload of the same day)
function simLeagueDay(day, oppIdx){
  let seed = (day + 1) * 7919 + 13; const rnd2 = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const ids = G.teams.map((_, i) => i).filter(i => i !== G.team && i !== oppIdx);
  for (let i = ids.length - 1; i > 0; i--){ const j = Math.floor(rnd2() * (i + 1)); [ids[i], ids[j]] = [ids[j], ids[i]]; }
  for (let k = 0; k + 1 < ids.length; k += 2) day % 2 ? simLeagueGame(ids[k], ids[k + 1]) : simLeagueGame(ids[k + 1], ids[k]);
}
function gameOver(){
  if (M.league){                                                         // a game between two other clubs: decisions, the standings, nothing else
    M.over = true; giveDecisions();
    const hw = M.score.home > M.score.away; M.home[hw ? 'w' : 'l']++; M.away[hw ? 'l' : 'w']++; M.home.rs += M.score.home; M.home.ra += M.score.away; M.away.rs += M.score.away; M.away.ra += M.score.home;
    return;
  }
  clearMatchSnap();
  M.over = true; phase = 'over';
  giveDecisions();
""")
# my own game over: play the rest of the league's day, and keep the coins I made
rep("  const sg = G.sched[G.day]; if (sg){ sg.done = true; sg.rs = myRuns; sg.ra = oth; }\n  G.day++; G.rotIdx++;\n  save();",
    "  const sg = G.sched[G.day]; if (sg){ sg.done = true; sg.rs = myRuns; sg.ra = oth; }\n  simLeagueDay(G.day, sg ? sg.opp : -1);                                  // everybody else plays today too, and their players get stats\n  G.day++; G.rotIdx++;\n  save();")
# no coins for other clubs' hits
rep("  if (weBat()) G.coins += ({ single:25, double:40, triple:75, hr:200 })[res] || 0;\n  if (!weBat() && res === 'k') G.coins += 30;",
    "  if (!M.league){ if (weBat()) G.coins += ({ single:25, double:40, triple:75, hr:200 })[res] || 0;\n    if (!weBat() && res === 'k') G.coins += 30; }")

# ── 3) coins for the whole game, itemised, after it ends ──────────────────────────────────────────────
rep("  M.uni = pickUniforms(M.home, M.away);                          // who wears what, once, for the whole game\n  M.pitcherHome.st.ip",
    "  M.uni = pickUniforms(M.home, M.away);                          // who wears what, once, for the whole game\n  M.coins0 = G.coins;                                            // what you had when it began: the game's total is worked out from this\n  M.pitcherHome.st.ip")
rep("t:Date.now() }));\n  } catch (e){}", "t:Date.now(), coins0:M.coins0 }));\n  } catch (e){}") if "t:Date.now() }));\n  } catch (e){}" in s else None
s = s.replace("pgH:pitchers(M.home).map(p => pg(p)), pgA:pitchers(M.away).map(p => pg(p)), t:Date.now() }));", "pgH:pitchers(M.home).map(p => pg(p)), pgA:pitchers(M.away).map(p => pg(p)), t:Date.now(), coins0:M.coins0 }));")
rep("  if (d.pgH && d.pgA){", "  if (d.coins0 != null) M.coins0 = d.coins0;\n  if (d.pgH && d.pgA){")
a = s.index("function drawOver(){"); b = s.index("// in-game menu button")
s = s[:a] + """function drawOver(){
  btns = [];
  R(0, 0, W, H, '#0b1018ee');
  const my = M.meHome ? M.score.home : M.score.away, ot = M.meHome ? M.score.away : M.score.home, won = my > ot;
  const earned = Math.max(0, G.coins - (M.coins0 == null ? G.coins : M.coins0)), shut = ot === 0, bonus = (won ? 500 : 120) + (shut ? 500 : 0), play = Math.max(0, earned - bonus);
  textb(won ? 'WIN' : 'LOSS', W / 2, 30, won ? '#54d67a' : '#ff6b5a', 24, 'center');
  textb(`${M.away.ab} ${M.score.away}   -   ${M.home.ab} ${M.score.home}`, W / 2, 66, '#fff', 12, 'center');
  const rows = [['HITS, HOME RUNS AND STRIKEOUTS', play], [won ? 'WIN BONUS' : 'PLAYED THE GAME', won ? 500 : 120]]; if (shut) rows.push(['SHUTOUT', 500]);
  rows.forEach(([l, v], i) => { textb(l, W / 2 - 100, 92 + i * 12, UI.ice, 7, 'left'); textb('+' + v, W / 2 + 100, 92 + i * 12, '#ffffff', 7, 'right'); });
  R(W / 2 - 100, 92 + rows.length * 12, 200, 1, '#2a5ba6');
  textb('TOTAL EARNED', W / 2 - 100, 96 + rows.length * 12, '#ffd23f', 8, 'left'); textb('+' + earned + ' coins', W / 2 + 100, 96 + rows.length * 12, '#ffd23f', 9, 'right');
  button(W / 2 - 50, 150, 100, 22, 'CONTINUE', () => { M = null; phase = 'menu'; menu = 'title'; }, '#2f6fe0');
}

""" + s[b:]

# ── 4) the standings: all 30 clubs in their six divisions ────────────────────────────────────────────
a = s.index("  else if (menu === 'stand'){"); b = s.index("function drawOver(){") if False else s.index("\n}\nfunction drawStats", a) if "\n}\nfunction drawStats" in s[a:] else None
# find the end of the stand branch: it ends at the BACK button line followed by closing braces
end = s.index("    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');\n  }\n", a) + len("    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');\n  }\n")
new_stand = """  else if (menu === 'stand'){
    R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('STANDINGS', 10, 3, 9, '#ffffff', 'left');
    const colW = Math.floor((W - 30) / 2), RH = 10, pctOf = t => (t.w + t.l) ? t.w / (t.w + t.l) : 0;
    ['AL', 'NL'].forEach((lg, ci) => {
      const x0 = 10 + ci * (colW + 10); let y = 22;
      [['E', 'EAST'], ['C', 'CENTRAL'], ['W', 'WEST']].forEach(([dv, nm]) => {
        const list = G.teams.map((t, i) => ({ t, i })).filter(o => o.t.lg === lg && o.t.div === dv).sort((a, b) => pctOf(b.t) - pctOf(a.t) || b.t.w - a.t.w || a.i - b.i);
        R(x0, y, colW, 9, UI.blueDD); textb(lg + ' ' + nm, x0 + 3, y + 2, '#ffffff', 6, 'left');
        [['W', 74], ['L', 56], ['PCT', 32], ['GB', 7]].forEach(([h, dx]) => textb(h, x0 + colW - dx, y + 2, UI.ice, 6, 'right'));
        y += 10;
        const lead = list[0].t;
        list.forEach((o, k) => {
          const t = o.t, mine = o.i === G.team, c = mine ? UI.yellow : '#ffffff', gb = ((lead.w - t.w) + (t.l - lead.l)) / 2;
          if (mine) R(x0, y - 1, colW, RH, 'rgba(255,210,63,.18)');
          textb(t.ab, x0 + 3, y, c, 6, 'left'); textb(t.nick, x0 + 24, y, mine ? UI.yellow : UI.ice, 5, 'left', colW - 106);
          textb(String(t.w), x0 + colW - 74, y, c, 6, 'right'); textb(String(t.l), x0 + colW - 56, y, c, 6, 'right');
          textb(pctOf(t).toFixed(3).replace('0.', '.').replace('1.000', '1.000'), x0 + colW - 32, y, c, 6, 'right'); textb(k === 0 ? '-' : gb.toFixed(1), x0 + colW - 7, y, c, 6, 'right');
          y += RH;
        });
        y += 3;
      });
    });
    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');
  }
"""
s = s[:a] + new_stand + s[end:]

# ── 5) the stadium loads once, right as the game begins, and never again ─────────────────────────────
rep("  setTimeout(warmHitView, 400);", "  setTimeout(warmHitView, 30);")
rep("<meta charset", "<meta http-equiv=\"Cache-Control\" content=\"no-cache, must-revalidate\"><meta charset") if "<meta charset" in s and "Cache-Control" not in s else None
s = s.replace("BUILD = '11-06b'", "BUILD = '11-06c'")
s = re.sub(r"gl3d\.js\?v=11-06b", "gl3d.js?v=11-06c", s)
rep("runToggle, runBack, drawPlay, defTap,", "runToggle, runBack, drawPlay, simLeagueDay, simLeagueGame, inZone, defTap,")
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
