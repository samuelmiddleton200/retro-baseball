import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# ── the season: 24 games = 8 three-game series. Five of them are the division round robin (everyone plays each of the 4 others 3 times, in a random order; the odd team out plays a team from another division), three more are against clubs outside the division ──
a = s.index("function makeSchedule(){"); b = s.index("const save = () => {")
s = s[:a] + """function makeLeagueSchedule(){
  const N = G.teams.length, shuf = a => { for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const divOf = i => G.teams[i].lg + G.teams[i].div, divs = {};
  G.teams.forEach((t, i) => (divs[divOf(i)] = divs[divOf(i)] || []).push(i));
  const key = (x, y) => x < y ? x + '-' + y : y + '-' + x, seen = new Set(), dk = Object.keys(divs);
  // each division: 5 teams, 5 rounds of two series (one team sits out each round)
  const rr = {};
  dk.forEach(k => {
    const arr = [-1].concat(shuf(divs[k].slice())), rounds = [];
    for (let r = 0; r < 5; r++){
      const rot = arr.slice(1), a = [arr[0]].concat(rot.map((_, i) => rot[(i - r + 5) % 5])), pairs = []; let bye = -1;
      for (let i = 0; i < 3; i++){ const x = a[i], y = a[5 - i]; if (x === -1) bye = y; else if (y === -1) bye = x; else pairs.push([x, y]); }
      rounds.push({ pairs, bye });
    }
    rr[k] = shuf(rounds);
  });
  const divSlots = shuf([0, 1, 2, 3, 4, 5, 6, 7]).slice(0, 5).sort((p, q) => p - q), rounds = [];
  for (let slot = 0; slot < 8; slot++){
    const pairs = []; const j = divSlots.indexOf(slot);
    if (j >= 0){
      dk.forEach(k => rr[k][j].pairs.forEach(p => pairs.push(p.slice())));
      let byes; for (let tryN = 0; tryN < 60; tryN++){ byes = shuf(dk.map(k => rr[k][j].bye)); if (byes.every((_, i) => i % 2 || !seen.has(key(byes[i], byes[i + 1])))) break; }
      for (let i = 0; i < byes.length; i += 2){ pairs.push([byes[i], byes[i + 1]]); seen.add(key(byes[i], byes[i + 1])); }   // the idle clubs play each other
    } else {
      for (let tryN = 0; tryN < 400; tryN++){                                         // everybody plays a club from another division, nobody twice
        const ids = shuf(Array.from({ length:N }, (_, i) => i)), used = new Set(), out = []; let ok = true;
        for (const i of ids){
          if (used.has(i)) continue;
          const o = ids.find(q => q !== i && !used.has(q) && divOf(q) !== divOf(i) && !seen.has(key(i, q)));
          if (o === undefined){ ok = false; break; }
          used.add(i); used.add(o); out.push([i, o]);
        }
        if (ok){ out.forEach(p => { pairs.push(p); seen.add(key(p[0], p[1])); }); break; }
      }
    }
    pairs.forEach(p => { if (Math.random() < .5) p.reverse(); });                    // who is home in games 1 and 3
    rounds.push(pairs);
  }
  return rounds;
}
function makeSchedule(){
  G.rounds = makeLeagueSchedule();
  G.sched = [];
  for (let d = 0; d < G.seasonLen; d++){
    const pair = (G.rounds[Math.floor(d / 3)] || []).find(p => p.includes(G.team)), k = d % 3;
    const opp = pair ? (pair[0] === G.team ? pair[1] : pair[0]) : (G.team + 1) % G.teams.length, first = !pair || pair[0] === G.team;
    G.sched.push({ opp, home: k === 1 ? !first : first, done:false, rs:0, ra:0 });
  }
}
""" + s[b:]
rep("seasonLen:25,", "seasonLen:24,")
# the rest of the league plays the same series
rep("function simLeagueDay(day, oppIdx){\n", "function simLeagueDay(day, oppIdx){\n  if (G.rounds && G.rounds[Math.floor(day / 3)]){\n    const k = day % 3;\n    G.rounds[Math.floor(day / 3)].forEach(([x, y]) => { if (x === G.team || y === G.team) return; k === 1 ? simLeagueGame(y, x) : simLeagueGame(x, y); });\n    return;\n  }\n")

# playoff games between other clubs do not touch the standings; they report who won
rep("function simLeagueGame(hi, ai){", "function simLeagueGame(hi, ai, po){\n  let homeWon = true;")
rep("pcHome:0, pcAway:0, line:[], mode:'sim', park:{}, msg:null, msgT:0, over:false, exc:0 };\n    pg(M.pitcherHome).used = true;", "pcHome:0, pcAway:0, line:[], mode:'sim', park:{}, msg:null, msgT:0, over:false, exc:0, po:!!po };\n    pg(M.pitcherHome).used = true;")
rep("    if (!M.over) gameOver();\n  } catch (e){ console.error(e); }", "    if (!M.over) gameOver();\n    homeWon = M.score.home > M.score.away;\n  } catch (e){ console.error(e); }")
rep("  finally { M = keep.M; P = keep.P; BALL = keep.BALL; swing = keep.swing; phase = keep.phase; pitchSel = keep.pitchSel; PG.clear(); pgKeep.forEach((v, k) => PG.set(k, v)); }\n}",
    "  finally { M = keep.M; P = keep.P; BALL = keep.BALL; swing = keep.swing; phase = keep.phase; pitchSel = keep.pitchSel; PG.clear(); pgKeep.forEach((v, k) => PG.set(k, v)); }\n  return { homeWon };\n}")
rep("    const hw = M.score.home > M.score.away; M.home[hw ? 'w' : 'l']++;", "    if (M.po) return;                                                    // a playoff game: no standings\n    const hw = M.score.home > M.score.away; M.home[hw ? 'w' : 'l']++;")

# your playoff game: no standings, no schedule day
rep("  me[won ? 'w' : 'l']++; me.rs += myRuns; me.ra += oth;\n  G.coins += won ? 600 : 150;", "  if (!M.playoff){ me[won ? 'w' : 'l']++; me.rs += myRuns; me.ra += oth; }\n  G.coins += won ? 600 : 150;")
rep("  const sg = G.sched[G.day]; if (sg){ sg.done = true; sg.rs = myRuns; sg.ra = oth; }\n  simLeagueDay(G.day, sg ? sg.opp : -1);                                  // everybody else plays today too, and their players get stats\n  G.day++; G.rotIdx++;\n  save();",
    "  if (M.playoff){ poUserDone(won); G.rotIdx++; save(); return; }\n  const sg = G.sched[G.day]; if (sg){ sg.done = true; sg.rs = myRuns; sg.ra = oth; }\n  simLeagueDay(G.day, sg ? sg.opp : -1);                                  // everybody else plays today too, and their players get stats\n  G.day++; G.rotIdx++;\n  save();")
rep("    pcHome:0, pcAway:0, line:[], mode: opts.mode || 'full',       // full | offense | defense", "    pcHome:0, pcAway:0, line:[], mode: opts.mode || 'full', playoff: !!opts.playoff,       // full | offense | defense")

# ── the playoffs: only after game 24. Single games: wild card (4 v 5, 3 v 6), division series (1 v the 4/5 winner, 2 v the 3/6 winner), league series, World Series ──
a = s.index("// ── the playoff picture:")
s = s[:a] + """// ── the playoffs ──
const PO_ROUNDS = ['WILD CARD', 'DIVISION SERIES', 'LEAGUE SERIES', 'WORLD SERIES'];
function poPct(i){ const t = G.teams[i]; return (t.w + t.l) ? t.w / (t.w + t.l) : 0; }
function poBuildRound(){
  const P = G.po, r = P.round, S = P.seeds, out = [], seedOf = (lg, i) => S[lg].indexOf(i);
  const best = (lg, x, y) => seedOf(lg, x) < seedOf(lg, y) ? [x, y] : [y, x];
  if (r === 0) ['AL', 'NL'].forEach(lg => { const s6 = S[lg]; out.push({ lg, a:s6[3], b:s6[4], w:-1 }); out.push({ lg, a:s6[2], b:s6[5], w:-1 }); });
  else if (r === 1) ['AL', 'NL'].forEach(lg => { const w0 = P.g[0].filter(x => x.lg === lg); out.push({ lg, a:S[lg][0], b:w0[0].w, w:-1 }); out.push({ lg, a:S[lg][1], b:w0[1].w, w:-1 }); });
  else if (r === 2) ['AL', 'NL'].forEach(lg => { const w1 = P.g[1].filter(x => x.lg === lg), [h, v] = best(lg, w1[0].w, w1[1].w); out.push({ lg, a:h, b:v, w:-1 }); });
  else { const al = P.g[2].find(x => x.lg === 'AL').w, nl = P.g[2].find(x => x.lg === 'NL').w, h = poPct(al) >= poPct(nl) ? [al, nl] : [nl, al]; out.push({ lg:'WS', a:h[0], b:h[1], w:-1 }); }
  P.g[r] = out;
}
const poUserGame = () => { const P = G.po; if (!P || P.champ >= 0) return null; return (P.g[P.round] || []).find(x => x.w < 0 && (x.a === G.team || x.b === G.team)) || null; };
function poAdvance(){                                                      // simulate every game that is not yours; stop when it is your turn
  const P = G.po; let guard = 0;
  while (P.champ < 0 && guard++ < 10){
    (P.g[P.round] || []).forEach(gm => { if (gm.w >= 0 || gm.a === G.team || gm.b === G.team) return; gm.w = simLeagueGame(gm.a, gm.b, true).homeWon ? gm.a : gm.b; });
    if (poUserGame()) return;
    if (P.round >= 3){ P.champ = P.g[3][0].w; G.champs = (G.champs || 0) + (P.champ === G.team ? 1 : 0); return; }
    P.round++; poBuildRound();
  }
}
function startPlayoffs(){
  G.po = { round:0, seeds:{ AL:playoffSeeds('AL').slice(0, 6).map(o => o.i), NL:playoffSeeds('NL').slice(0, 6).map(o => o.i) }, g:[[], [], [], []], champ:-1 };
  poBuildRound(); poAdvance(); save();
}
function poUserDone(won){
  const gm = poUserGame(); if (!gm) return;
  gm.w = won ? G.team : (gm.a === G.team ? gm.b : gm.a);
  poAdvance();
}
function newSeason(){
  G.teams.forEach(t => { t.w = t.l = t.rs = t.ra = 0; [...t.lineup, ...t.rot, ...t.pen].forEach(p => { p.st = newStat(); }); });
  G.cards.forEach(p => { p.st = newStat(); });
  G.day = 0; G.seasonLen = 24; G.po = null; G.season = (G.season || 1) + 1; makeSchedule(); save();
}
// ── the playoff picture: the top 6 of each league. 4 v 5 and 3 v 6 play a wild-card game; the winners play the 1 and 2 seeds; then the league series and the World Series ──
""" + s[s.index("function playoffSeeds(lg){"):]

# the picture: the real thing once the playoffs are on
rep("  textb('IF THE SEASON ENDED TODAY', W - 8, 5, UI.ice, 6, 'right');", "  const PO = G.po, tm = i => i >= 0 ? { t:G.teams[i], i } : null;\n  textb(PO ? (PO.champ >= 0 ? 'CHAMPIONS: ' + G.teams[PO.champ].nick.toUpperCase() : PO_ROUNDS[PO.round] + ' ROUND') : 'IF THE SEASON ENDED TODAY', W - 8, 5, PO && PO.champ >= 0 ? UI.yellow : UI.ice, 6, 'right');")
rep("    const L = playoffSeeds(lg).slice(0, 6), sd = k => L[k - 1] || null, dir = side === 0 ? 1 : -1;", "    const L = PO ? PO.seeds[lg].map(tm) : playoffSeeds(lg).slice(0, 6), sd = k => L[k - 1] || null, dir = side === 0 ? 1 : -1;\n    const gl = r => PO ? PO.g[r].filter(x => x.lg === lg) : [], won = (r, k) => gl(r)[k] && gl(r)[k].w >= 0 ? tm(gl(r)[k].w) : null;     // who won a game of this league\n    const wcW = [won(0, 0), won(0, 1)], dsW = [won(1, 0), won(1, 1)];")
rep("    tile(col(1), yDS[0], null, 0, 'WC WINNER'); tile(col(1), yDS[1], sd(1), 1);\n    tile(col(1), yB(yDS[1]), sd(2), 2); tile(col(1), yB(yDS[0]), null, 0, 'WC WINNER');",
    "    tile(col(1), yDS[0], wcW[0], 0, 'WC WINNER'); tile(col(1), yDS[1], sd(1), 1);\n    tile(col(1), yB(yDS[1]), sd(2), 2); tile(col(1), yB(yDS[0]), wcW[1], 0, 'WC WINNER');")
rep("    tile(col(2), yL[0], null, 0, 'TBD'); tile(col(2), yL[1], null, 0, 'TBD');", "    tile(col(2), yL[0], dsW[0], 0, 'TBD'); tile(col(2), yL[1], dsW[1], 0, 'TBD');")
rep("    // your place in this league\n    if (G.team >= 0 && G.teams[G.team].lg === lg){", "    // your place in this league\n    if (PO && G.teams[G.team].lg === lg){\n      const sk = PO.seeds[lg].indexOf(G.team); G._poNote = PO.champ >= 0 ? (PO.champ === G.team ? 'YOUR TEAM WON THE WORLD SERIES!' : 'THE PLAYOFFS ARE OVER') : sk < 0 ? 'YOUR TEAM MISSED THE PLAYOFFS' : poUserGame() ? 'YOU ARE THE ' + lg + ' #' + (sk + 1) + ' SEED: YOUR GAME IS NEXT' : 'YOUR SEASON IS OVER';\n    } else if (G.team >= 0 && G.teams[G.team].lg === lg){")
rep("  textb('WORLD', cx, cyMid - 7, UI.yellow, 6, 'center'); textb('SERIES', cx, cyMid + 1, UI.yellow, 6, 'center');",
    "  const wsg = PO && PO.g[3][0], wsT = wsg ? [wsg.a, wsg.b].map(i => G.teams[i].ab).join(' v ') : '', chp = PO && PO.champ >= 0 ? G.teams[PO.champ] : null;\n  textb('WORLD', cx, cyMid - 7, UI.yellow, 6, 'center'); textb('SERIES', cx, cyMid + 1, UI.yellow, 6, 'center');\n  if (chp){ R(cx - wsW / 2, cyMid + 11, wsW, 11, UI.yellow); textb(chp.ab, cx, cyMid + 13, UI.navy, 7, 'center'); } else if (wsT) textb(wsT, cx, cyMid + 12, UI.ice, 6, 'center');")

# the main menu: the playoffs after game 24
a = s.index("      } else button(W / 2 - 70, 116, 140, 22, G.day < G.seasonLen ?"); b = s.index("      button(W / 2 - 108, 142, 68, 18, 'MY CARDS'")
s = s[:a] + """      } else if (G.day < G.seasonLen) button(W / 2 - 70, 116, 140, 22, `PLAY GAME ${G.day + 1}/${G.seasonLen}`, () => {
        const sg = G.sched[G.day]; startGame(sg.opp, sg.home);
      }, '#2f6fe0');
      else if (!G.po) button(W / 2 - 70, 116, 140, 22, 'START PLAYOFFS', () => { startPlayoffs(); menu = 'playoffs'; }, '#2f6fe0');
      else if (poUserGame()) { const ug = poUserGame(); button(W / 2 - 70, 116, 140, 22, 'PLAY ' + PO_ROUNDS[G.po.round], () => { startGame(ug.a === G.team ? ug.b : ug.a, ug.a === G.team, { playoff:true }); }, '#2f6fe0'); }
      else button(W / 2 - 70, 116, 140, 22, 'NEW SEASON', () => newSeason(), '#2f6fe0');
""" + s[b:]
s = s.replace("BUILD = '11-11m'", "BUILD = '11-11n'").replace("gl3d.js?v=11-11m", "gl3d.js?v=11-11n")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
