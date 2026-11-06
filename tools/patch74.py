s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── stamina: a starter 50-85 pitches, a reliever 40-60, a closer 25-35 (STA 60 to 120), every pitch costs 1 ──
rep("const stamCap = p => 60 + (clamp(p.stamina, 60, 120) - 60) * 2 / 3;               // 60 stamina = 60 pitches, 120 = 100, in a straight line",
    "const stamCap = p => { const t = (clamp(p.stamina, 60, 120) - 60) / 60; return p.pos === 'CP' ? lerp(25, 35, t) : p.pos === 'RP' ? lerp(40, 60, t) : lerp(50, 85, t); };      // pitches he has in him at STA 60 to 120: a starter 50-85, a reliever 40-60, a closer 25-35\n// how much is left in the tank (0-1): in a game it is what he has left right now; outside one it is what he carries into the next game\nconst stamPct = (p, live) => live ? 1 - clamp(spOf(pg(p)) / stamCap(p), 0, 1) : (p.stam == null ? 1 : p.stam);\nconst stamHue = pct => 120 * clamp(pct, 0, 1);                                      // green > greenish yellow > yellow > orange > red, smoothly\nfunction stamBar(x, y, w, h, pct){ R(x, y, w, h, '#0a0d16'); R(x, y, Math.max(0, Math.round(w * clamp(pct, 0, 1))), h, `hsl(${stamHue(pct).toFixed(0)},88%,50%)`); R(x, y, w, 1, 'rgba(255,255,255,.22)'); }\n// what he gets back between games: a starter 20%, a reliever 25%, a closer 40% (a pitcher who is not used rests the same)\nconst restRate = p => p.pos === 'CP' ? .40 : p.pos === 'RP' ? .25 : .20;\nfunction restPitchers(){ G.cards.filter(isPitcher).forEach(p => { const g = PG.get(p), left = g && g.used ? 1 - clamp(spOf(g) / stamCap(p), 0, 1) : stamPct(p, false); p.stam = clamp(left + restRate(p), 0, 1); }); }")
rep("const pg = p => PG.get(p) || (PG.set(p, { pc:0, sp:0,", "const pg = p => PG.get(p) || (PG.set(p, { pc:0, sp:(p.stam != null && p.stam < 1 ? (1 - p.stam) * stamCap(p) : 0),")
rep("g0.sp = spOf(g0) + (type === 'FB' ? .8 : 1); g0.pc++;", "g0.sp = spOf(g0) + 1; g0.pc++;")
rep("g1.sp = spOf(g1) + n1 * .92; }", "g1.sp = spOf(g1) + n1; }")
rep("  if (g.po < 9) return;\n  if (spOf(g) >= stamCap(p) || g.r > g.pc / 10) changePitcher(t, pickReliever(t));", "  if (spOf(g) >= stamCap(p) || (g.po >= 9 && g.r > g.pc / 10)) changePitcher(t, pickReliever(t));       // out of gas, or getting hit hard after at least 3 innings")
rep("  M.coins0 = G.coins;                                            // what you had when it began", "  M.coins0 = G.coins;                                            // what you had when it began")

# ── the closer: 50% bigger breaking balls, and a change-up 5 mph slower than a starter's would be ──
rep("return type === 'FB' ? fbNow : type === 'CH' ? fbNow * .85 :", "return type === 'FB' ? fbNow : type === 'CH' ? fbNow * .85 - (p.pos === 'CP' ? 5 : 0) :")
rep("  P.br = [info.br[0] * lerp(.6, 1.3, (q - 60) / 60), info.br[1] * lerp(.6, 1.3, (q - 60) / 60)];", "  const bk = p.pos === 'CP' && (type === 'CV' || type === 'SL') ? 1.5 : 1;                      // a closer's curveball and slider break half as much again\n  P.br = [info.br[0] * lerp(.6, 1.3, (q - 60) / 60) * bk, info.br[1] * lerp(.6, 1.3, (q - 60) / 60) * bk];")

# ── resting after your game ──
rep("  clearMatchSnap();\n  M.over = true; phase = 'over';\n  giveDecisions();", "  clearMatchSnap();\n  M.over = true; phase = 'over';\n  giveDecisions(); restPitchers();                                                  // your pitchers get their rest back")
rep("  G.cards.forEach(p => { p.st = newStat(); });\n  G.day = 0;", "  G.cards.forEach(p => { p.st = newStat(); p.stam = 1; });\n  G.day = 0;")

# ── you pick who starts every game, in any order ──
rep("    pitcherHome: home ? me.rot[G.rotIdx % 5] : opp.rot[ri(0,4)],\n    pitcherAway: home ? opp.rot[ri(0,4)] : me.rot[G.rotIdx % 5],",
    "    pitcherHome: home ? myStarter(me) : opp.rot[ri(0,4)],\n    pitcherAway: home ? opp.rot[ri(0,4)] : myStarter(me),")
rep("function startGame(oppIdx, home, opts = {}){", "const myStarter = me => { const c = G.starter != null ? cardById(G.starter) : null; return c && isPitcher(c) && (me.rot.includes(c) || me.pen.includes(c)) ? c : me.rot[G.rotIdx % 5]; };\nfunction startGame(oppIdx, home, opts = {}){")

# one row of the pitcher lists: position, name, VEL / CTL / STA, a stamina bar
rep("// pick a reliever: only pitchers who have not been in yet", """function pitcherRow(p, x, y, w, on, live, tag, note, fn){
  R(x, y, w, 13, on ? '#1b3e78' : '#1a2030');
  textb(tag, x + 4, y + 3, on ? UI.yellow : '#667', 6);
  textb(p.name, x + 20, y + 3, on ? '#ffffff' : '#667', 7, 'left', 92);
  [['VEL', p.velocity], ['CTL', p.control], ['STA', p.stamina]].forEach(([l, v], j) => textb(l + ' ' + v, x + 116 + j * 38, y + 3, on ? '#cfe0ff' : '#667', 6));
  const pct = stamPct(p, live), bx = x + 232, bw = w - 232 - 34;
  stamBar(bx, y + 4, bw, 5, pct);
  textb(note || Math.round(pct * 100) + '%', x + w - 4, y + 3, note ? '#ff8a7a' : (on ? '#cfe0ff' : '#667'), 6, 'right');
  if (on && fn) btns.push({ x, y, w, h:13, fn });
}
// who starts: any pitcher, in any order; the number is what he has in the tank
let startCb = null;
function pickStarter(cb){ startCb = cb; menu = 'startpick'; }
function drawStartPick(){
  btns = [];
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('WHO STARTS?', 10, 3, 9, '#ffffff', 'left');
  const me = myTeam(), list = me.rot.concat(me.pen), rw = Math.min(344, W - 16), x = W / 2 - rw / 2;
  textb('Pick any pitcher. His bar is what he has left from his last game.', W / 2, 22, UI.ice, 6, 'center', W - 16);
  list.forEach((p, i) => pitcherRow(p, x, 34 + i * 15, rw, true, false, me.rot.includes(p) ? 'SP' : p === me.pen[me.pen.length - 1] ? 'CP' : 'RP', null, () => { G.starter = p.id; save(); const cb = startCb; startCb = null; if (cb) cb(); }));
  button(10, H - 22, 70, 18, 'BACK', () => { menu = 'title'; startCb = null; });
}
// pick a pitcher to bring in: anyone who has not pitched yet""")
a = s.index("function drawPitchPick(){"); b = s.index("// ── simulating ─────────────────")
s = s[:a] + """function drawPitchPick(){
  btns = [];
  R(0, 0, W, H, '#0b1018f0');
  const mine = M.meHome ? M.home : M.away, cur = M.meHome ? M.pitcherHome : M.pitcherAway;
  textb('BRING IN A PITCHER', W / 2, 8, '#ffd23f', 10, 'center');
  textb(`${cur.name} has thrown ${pg(cur).pc} pitches, ${Math.round(100 * stamPct(cur, true))}% stamina left. A pitcher who is taken out cannot come back.`, W / 2, 24, UI.ice, 6, 'center', W - 20);
  const list = mine.rot.concat(mine.pen).filter(p => p !== cur), rw = Math.min(344, W - 16), x = W / 2 - rw / 2;
  list.forEach((p, i) => {
    const on = !pg(p).used;
    pitcherRow(p, x, 36 + i * 15, rw, on, true, mine.rot.includes(p) ? 'SP' : p === mine.pen[mine.pen.length - 1] ? 'CP' : 'RP', pg(p).used ? 'USED' : null,
      () => { changePitcher(mine, p); phase = userPitches() ? 'pitching' : 'atbat'; nextPitch(); });
  });
  button(W / 2 - 40, H - 22, 80, 16, 'BACK', () => phase = 'gmenu');
}

""" + s[b:]
rep("const mine = M.meHome ? M.home : M.away, open = !(P && P.thrown) && mine.pen.some(p => !pg(p).used);", "const mine = M.meHome ? M.home : M.away, cur0 = M.meHome ? M.pitcherHome : M.pitcherAway, open = !(P && P.thrown) && mine.rot.concat(mine.pen).some(p => p !== cur0 && !pg(p).used);")
rep("  else if (menu === 'stats'){ drawStats(); return; }", "  else if (menu === 'stats'){ drawStats(); return; }\n  else if (menu === 'startpick'){ drawStartPick(); return; }")
# the game starts after you choose
rep("""      } else if (G.day < G.seasonLen) button(W / 2 - 105, 108, 210, 33, `PLAY GAME ${G.day + 1}/${G.seasonLen}`, () => {
        const sg = G.sched[G.day]; startGame(sg.opp, sg.home);
      }, '#2f6fe0', '#fff', 12);""", """      } else if (G.day < G.seasonLen) button(W / 2 - 105, 108, 210, 33, `PLAY GAME ${G.day + 1}/${G.seasonLen}`, () => {
        const sg = G.sched[G.day]; pickStarter(() => startGame(sg.opp, sg.home));
      }, '#2f6fe0', '#fff', 12);""")
rep("() => { startGame(ug.a === G.team ? ug.b : ug.a, ug.a === G.team, { playoff:true }); }, '#2f6fe0', '#fff', 12); }", "() => { pickStarter(() => startGame(ug.a === G.team ? ug.b : ug.a, ug.a === G.team, { playoff:true })); }, '#2f6fe0', '#fff', 12); }")
rep("() => { clearMatchSnap(); if (G.day < G.seasonLen){ const s = G.sched[G.day]; startGame(s.opp, s.home); } }, '#2a1a1a', '#fff', 10);", "() => { clearMatchSnap(); if (G.day < G.seasonLen){ const s = G.sched[G.day]; pickStarter(() => startGame(s.opp, s.home)); } }, '#2a1a1a', '#fff', 10);")
# lineup screen: a stamina bar under each pitcher
rep("      textb(String(ovrOf(c)), x + SW - 5, y + 4, colOf(ovrOf(c)), 8, 'right');\n    } else textb('empty', x + 19, y + 5, UI.ice, 7);\n    btns.push({ x, y, w:SW, h:16, fn: () => lineSel = { where, i } });",
    "      textb(String(ovrOf(c)), x + SW - 5, y + 4, colOf(ovrOf(c)), 8, 'right');\n      if (where !== 'lineup') stamBar(x + 3, y + 12, SW - 6, 2, stamPct(c, false));            // what he has left in the tank\n    } else textb('empty', x + 19, y + 5, UI.ice, 7);\n    btns.push({ x, y, w:SW, h:16, fn: () => lineSel = { where, i } });")
s = s.replace("BUILD = '11-11w'", "BUILD = '11-11x'").replace("gl3d.js?v=11-11w", "gl3d.js?v=11-11x")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
