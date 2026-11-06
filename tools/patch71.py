import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# ── nothing you earn can be lost: coins save the moment they are earned, a pack's cards are yours the moment it is opened, and the game's snapshot carries the coin balance ──
rep("""const save = () => {
  try {
    // our own players live in G.cards; the team just points at them, so blank those
    // three lists before saving and build them again on load
    const me = G.teams[G.team], keep = { lineup:me.lineup, rot:me.rot, pen:me.pen };
    me.lineup = me.rot = me.pen = null;
    const txt = JSON.stringify(G);
    me.lineup = keep.lineup; me.rot = keep.rot; me.pen = keep.pen;
    localStorage.setItem(SAVE, txt);
  } catch(e){}
};""", """let saveFailed = false;
const save = () => {
  const me = G && G.teams && G.teams[G.team];
  const keep = me ? { lineup:me.lineup, rot:me.rot, pen:me.pen } : null;
  try {
    // our own players live in G.cards; the team just points at them, so blank those
    // three lists before saving and build them again on load
    me.lineup = me.rot = me.pen = null;
    const txt = JSON.stringify(G);
    me.lineup = keep.lineup; me.rot = keep.rot; me.pen = keep.pen;
    localStorage.setItem(SAVE, txt); saveFailed = false;
  } catch(e){ saveFailed = true; }
  finally { if (me && keep && !me.lineup){ me.lineup = keep.lineup; me.rot = keep.rot; me.pen = keep.pen; } }       // however it ended, the team is put back
};""")
rep("function earn(cat, amt, n = 1){ G.coins += amt; const e = (M.earn[cat] = M.earn[cat] || { n:0, c:0 }); e.n += n; e.c += amt; }",
    "function earn(cat, amt, n = 1){ G.coins += amt; const e = (M.earn[cat] = M.earn[cat] || { n:0, c:0 }); e.n += n; e.c += amt; save(); }      // saved the moment it is earned")
rep("t:Date.now(), coins0:M.coins0, earn:M.earn, rep:M.rep, ps:M.pitchSimmed }));", "t:Date.now(), coins0:M.coins0, coins:G.coins, earn:M.earn, rep:M.rep, ps:M.pitchSimmed }));")
rep("  if (d.coins0 != null) M.coins0 = d.coins0;", "  if (d.coins0 != null) M.coins0 = d.coins0;\n  if (d.coins != null && G.coins < d.coins){ G.coins = d.coins; save(); }                  // the coins you had earned by then are never lost to a reload")

# a pack's (or a trade's) cards are in your collection from the moment it opens; the spin only shows them
rep("""  OPEN = Object.assign({ phase:'pack', bi:0, t:0, ph0:0, revealed:[], newIds:new Set(), tr:{ a:null, b:null }, shake:0, sold:false, sellArmed:false }, o);
  if (o.kind !== 'pack') OPEN.phase = 'ready';""", """  OPEN = Object.assign({ phase:'pack', bi:0, t:0, ph0:0, revealed:[], newIds:new Set(), tr:{ a:null, b:null }, shake:0, sold:false, sellArmed:false }, o);
  if (o.kind !== 'pack') OPEN.phase = 'ready';
  if (!o.pre && (o.kind === 'pack' || o.kind === 'trade')){
    G.seen = G.seen || {};
    o.batches.forEach(b => b.cards.forEach(c => { if (!G.cards.includes(c)){ G.cards.push(c); if (!G.seen[c.name]) OPEN.newIds.add(c.id); G.seen[c.name] = 1; } }));
    OPEN.pre = true; save();
  }""")

# ── the daily pack: 10 cards, shown in two rows of 5 ──
rep("const batches = [{ tier:'bronze', cards:Array.from({ length:5 }, () => rollCard('bronze')) }];", "const batches = [{ tier:'bronze', cards:Array.from({ length:10 }, () => rollCard('bronze')) }];")
rep("    const n = O.sp.length, slotW = (W - 16) / n, k = Math.min(n === 1 ? .95 : .9, (W - 16) / (n * 200)), cy = 124;\n    O.sp.forEach((s, i) => drawSpinCard(s, 8 + slotW * (i + .5), cy, k));",
    """    const n = O.sp.length, rows = n > 5 ? 2 : 1, perRow = rows === 2 ? Math.ceil(n / 2) : n, slotW = (W - 16) / perRow;
    const k = rows === 2 ? Math.min(.62, slotW / 108) : Math.min(n === 1 ? .95 : .9, (W - 16) / (n * 200)), chR2 = 140 * k, cy1 = rows === 2 ? 26 + chR2 / 2 + 2 : 124;
    O.sp.forEach((s, i) => { const r = rows === 2 ? Math.floor(i / perRow) : 0, c = rows === 2 ? i % perRow : i; drawSpinCard(s, 8 + slotW * (c + .5), cy1 + r * (chR2 + 5), k); });""")

# the free daily pack is reset once for everybody whose last one glitched
rep("      if (!G.streak) G.streak = { day:0, last:'' };", "      if (!G.streak) G.streak = { day:0, last:'' };\n      if (G.packReset !== 1){ G.freeAt = 0; G.packReset = 1; }                    // one-time: the daily pack that glitched is available again")

# ── the main menu buttons are 50% bigger (the spacing between them stays the same) ──
a = s.index("        button(W / 2 - 108, 116, 150, 22, `RESUME ${nm}`"); b = s.index("      coinText(G.coins, W / 2, 192, 9, UI.yellow, 'center');")
old = s[a:b]
new = """        button(W / 2 - 162, 108, 225, 33, `RESUME ${nm}`, () => { if (!resumeMatch()) clearMatchSnap(); }, '#2f6fe0', '#fff', 12);
        button(W / 2 + 69, 108, 90, 33, 'RESTART', () => { clearMatchSnap(); if (G.day < G.seasonLen){ const s = G.sched[G.day]; startGame(s.opp, s.home); } }, '#2a1a1a', '#fff', 10);
      } else if (G.day < G.seasonLen) button(W / 2 - 105, 108, 210, 33, `PLAY GAME ${G.day + 1}/${G.seasonLen}`, () => {
        const sg = G.sched[G.day]; startGame(sg.opp, sg.home);
      }, '#2f6fe0', '#fff', 12);
      else if (!G.po) button(W / 2 - 105, 108, 210, 33, 'START PLAYOFFS', () => { startPlayoffs(); menu = 'playoffs'; }, '#2f6fe0', '#fff', 12);
      else if (poUserGame()) { const ug = poUserGame(); button(W / 2 - 105, 108, 210, 33, 'PLAY ' + PO_ROUNDS[G.po.round], () => { startGame(ug.a === G.team ? ug.b : ug.a, ug.a === G.team, { playoff:true }); }, '#2f6fe0', '#fff', 12); }
      else button(W / 2 - 105, 108, 210, 33, 'NEW SEASON', () => newSeason(), '#2f6fe0', '#fff', 12);
      button(W / 2 - 159, 145, 102, 27, 'MY CARDS', () => menu = 'cards', '#1a2230', '#fff', 11);
      button(W / 2 - 51, 145, 102, 27, 'SHOP', () => menu = 'shop', '#1a2230', '#fff', 11);
      button(W / 2 + 57, 145, 102, 27, 'LINEUP', () => menu = 'lineup', '#1a2230', '#fff', 11);
      button(W / 2 - 159, 176, 102, 27, 'STANDINGS', () => menu = 'stand', '#1a2230', '#fff', 10);
      button(W / 2 - 51, 176, 102, 27, 'MINIGAMES', () => menu = 'minigames', '#1a2230', '#fff', 10);
      button(W / 2 + 57, 176, 102, 27, 'LEADERS', () => { menu = 'stats'; statsScroll = 0; }, '#2f6fe0', '#fff', 10);
"""
s = s[:a] + new + s[b:]
rep("      coinText(G.coins, W / 2, 192, 9, UI.yellow, 'center');", "      coinText(G.coins, W / 2, 210, 9, UI.yellow, 'center');\n      if (saveFailed) text('SAVE FAILED - FREE UP SPACE', W / 2, 226, UI.red, 6, 'center');")

# the game's coins always add up: whatever was earned is in the balance when the game ends (a reload in the middle can never leave the rows without the coins)
rep("  G.coins += won ? 600 : 150;\n  M.shutBonus", "  { const es = Object.values(M.earn || {}).reduce((a, e) => a + e.c, 0); if (M.coins0 != null && G.coins < M.coins0 + es) G.coins = M.coins0 + es; }\n  G.coins += won ? 600 : 150;\n  M.shutBonus")
# defence pays more: a strikeout 125, a double play 175
rep("earn('k', 75 + 10 * (n - 1))", "earn('k', 125 + 10 * (n - 1))")
rep("if (res === 'dp') earn('dp', 125);", "if (res === 'dp') earn('dp', 175);")
s = s.replace("BUILD = '11-11r'", "BUILD = '11-11s'").replace("gl3d.js?v=11-11r", "gl3d.js?v=11-11s")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
