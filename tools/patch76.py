s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── at the plate and on the mound ──
rep("const base = ({ single:50, double:125, triple:350, hr:200, bb:65, hbp:65 })[res];", "const base = ({ single:75, double:175, triple:450, hr:275, bb:75, hbp:75 })[res];")
rep("earn(cat, base + 15 * (n - 1)); }", "earn(cat, base + 25 * (n - 1)); }")
rep("if (rbi > 0) earn('rbi', rbi * 70, rbi);", "if (rbi > 0) earn('rbi', rbi * 100, rbi);")
rep("earn('k', 125 + 10 * (n - 1))", "earn('k', 150 + 25 * (n - 1))")
rep("if (res === 'dp') earn('dp', 175);", "if (res === 'dp') earn('dp', 225);")

# ── the end of a game: win 850 / loss 250 (playoffs 1,500 / 450), a shutout 1,850 whoever pitched ──
rep("  G.coins += won ? 600 : 150;\n  M.shutBonus = oth === 0 && !M.pitchSimmed;                                 // a shutout pays only if you pitched every inning yourself\n  if (M.shutBonus) G.coins += 850;",
    "  M.gamePay = M.playoff ? (won ? 1500 : 450) : (won ? 850 : 250); G.coins += M.gamePay;\n  M.shutBonus = oth === 0;                                                   // a shutout pays 1,850, however you pitched it\n  if (M.shutBonus) G.coins += 1850;")
rep("  rows.push([won ? 'WIN BONUS' : 'PLAYED THE GAME', won ? 600 : 150]); if (M.shutBonus) rows.push(['SHUTOUT', 850]);",
    "  rows.push([M.playoff ? (won ? 'PLAYOFF WIN' : 'PLAYOFF LOSS') : (won ? 'WIN BONUS' : 'PLAYED THE GAME'), M.gamePay || (won ? 850 : 250)]); if (M.shutBonus) rows.push(['SHUTOUT', 1850]);")

# ── selling pays 35% ──
rep("const sellPrice = c => Math.round(valueOf(ovrOf(c)) * .4);                              // selling pays 40% of what a card is worth", "const sellPrice = c => Math.round(valueOf(ovrOf(c)) * .35);                             // selling pays 35% of what a card is worth")

# ── the derby: 150 a home run, total feet / 4 ──
rep("const D = M.derby, hrCoins = D.hr * 100, distCoins = Math.round(D.dist / 5);", "const D = M.derby, hrCoins = D.hr * 150, distCoins = Math.round(D.dist / 4);")

# ── the daily streak: coins on days 1, 2, 4, 6; a silver pack on day 3, a gold pack on day 5, a 5-card gold pack on day 7 ──
rep("const STREAK_COINS = [500, 1000, 1500, 2000, 2500, 3000];", "const STREAK_COINS = [500, 1000, 0, 2000, 0, 3000];                     // days 3, 5 and 7 are packs instead\nconst STREAK_PACK = { 3:['silver', 3, 'SILVER PACK'], 5:['gold', 3, 'GOLD PACK'], 7:['gold', 5, '5-CARD GOLD PACK'] };")
rep("  if (day >= 7) batches.push({ tier:'gold', cards:Array.from({ length:3 }, () => rollCard('gold')) });\n  else { G.coins += STREAK_COINS[day - 1]; bonus = 'DAY ' + day + ' STREAK  +' + STREAK_COINS[day - 1].toLocaleString() + ' COINS'; }",
    "  const sp = STREAK_PACK[day];\n  if (sp){ batches.push({ tier:sp[0], cards:Array.from({ length:sp[1] }, () => rollCard(sp[0])) }); bonus = 'DAY ' + day + ' STREAK  +' + sp[2]; }\n  else { G.coins += STREAK_COINS[day - 1]; bonus = 'DAY ' + day + ' STREAK  +' + STREAK_COINS[day - 1].toLocaleString() + ' COINS'; }")
rep("  text('FREE GOLD PACK ON DAY 7', sx + 6, y0 + 17, UI.ice, 5.5, 'left', rw - 10);", "  text('FREE PACKS ON DAYS 3, 5 AND 7', sx + 6, y0 + 17, UI.ice, 5.5, 'left', rw - 10);")
rep("    text(d === 7 ? 'GOLD' : '+' + STREAK_COINS[d - 1], x + bw / 2, y + 13, UI.yellow, d === 7 ? 5.5 : 5.5, 'center', bw - 2);", "    text(STREAK_PACK[d] ? (d === 3 ? 'SILVER' : d === 5 ? 'GOLD' : 'GOLD x5') : '+' + STREAK_COINS[d - 1], x + bw / 2, y + 13, UI.yellow, 5.5, 'center', bw - 2);")

# ── the season's big prizes: winning your division 10,000, winning the World Series 50,000 ──
rep("  G.po = { round:0, seeds:{ AL:playoffSeeds('AL').slice(0, 6).map(o => o.i), NL:playoffSeeds('NL').slice(0, 6).map(o => o.i) }, g:[[], [], [], []], champ:-1 };",
    "  G.po = { round:0, seeds:{ AL:playoffSeeds('AL').slice(0, 6).map(o => o.i), NL:playoffSeeds('NL').slice(0, 6).map(o => o.i) }, g:[[], [], [], []], champ:-1 };\n  { const me = G.teams[G.team], dv = playoffSeeds(me.lg).filter(o => o.t.div === me.div); if (dv.length && dv[0].i === G.team){ G.po.divWon = true; G.coins += 10000; } }      // you won your division")
rep("    if (P.round >= 3){ P.champ = P.g[3][0].w; G.champs = (G.champs || 0) + (P.champ === G.team ? 1 : 0); return; }",
    "    if (P.round >= 3){ P.champ = P.g[3][0].w; G.champs = (G.champs || 0) + (P.champ === G.team ? 1 : 0); if (P.champ === G.team){ P.wsWon = true; G.coins += 50000; } return; }")
rep("  textb(G._poNote || '', 8, H - 17, UI.yellow, 6, 'left', W - 76);",
    "  textb(G._poNote || '', 8, H - 17, UI.yellow, 6, 'left', W - 76);\n  if (PO && (PO.divWon || PO.wsWon)) textb((PO.divWon ? 'DIVISION CHAMPS +10,000' : '') + (PO.divWon && PO.wsWon ? '   ' : '') + (PO.wsWon ? 'WORLD SERIES +50,000' : ''), 8, H - 28, '#9af0ae', 6, 'left', W - 76);")
s = s.replace("BUILD = '11-11z'", "BUILD = '11-12a'").replace("gl3d.js?v=11-11z", "gl3d.js?v=11-12a")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
