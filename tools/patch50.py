import re
s = open('index.html', encoding='utf-8').read()
econ = open('tools/shop_econ.js', encoding='utf-8').read()
ui = open('tools/shop_ui.js', encoding='utf-8').read()
card = open('tools/shop_card.js', encoding='utf-8').read()

def cut(a, b, new, keep_end=True):
    """replace from the start of a up to (not including) the start of b"""
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); i = s.index(a)
    assert s.count(b) >= 1, b[:60]; j = s.index(b, i)
    s = s[:i] + new + s[j:]
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# 1) prices, odds, values, fusing, hot deals, the streak, trading rules
cut("const PACKS = {", "let _cardId = 1;", econ + "\n")
rep("const sellPrice = c => Math.round(Math.pow(Math.max(0, ovrOf(c) - 55), 2) * 1.1);\n", "")
cut("// roll one card out of a pack\nfunction rollCard(packKey, forceTier){", "// ── card art", "")
# 2) opening a pack and the shop
cut("// ── opening a pack ─", "// ── the collection ─", ui + "\n")
# 3) the bench trade
cut("function benchTrade(){", "function myCards(){", """function benchTrade(){
  const give = benchSel.map(cardById).filter(Boolean);
  if (give.length < TRADE_N || give.length % TRADE_N || give.some(c => inUse(c.id))) { benchSel = []; return; }
  const ti = tierIdx(give[0]), count = give.length / TRADE_N;
  if (give.some(c => tierIdx(c) !== ti) || ti >= 5){ benchSel = []; return; }
  const cards = []; for (let k = 0; k < count; k++) cards.push(makeCardAt(tradeRating(give.slice(k * TRADE_N, (k + 1) * TRADE_N))));
  G.cards = G.cards.filter(c => !benchSel.includes(c.id));
  benchSel = []; startOpen({ kind:'trade', batches:[{ tier:null, cards }], from:'bench' }); save();
}
""")
# 4) the card screen and the trade screen
cut("// ── one card: upgrade, sell, put him in the lineup", "// ── best lineup:", card)
# the back of a card shows its level
rep("  text(`OVERALL ${ovr}`, x + w / 2, by + 2.5 * k, P.lite, Math.max(5, Math.round(5.5 * k)), 'center', iw - 4);\n}",
    """  text(`OVERALL ${ovr}`, x + w / 2, by + 2.5 * k, P.lite, Math.max(5, Math.round(5.5 * k)), 'center', iw - 4);
  const ly = by + 9 * k, lv = c.lvl || 0;                                                   // his upgrade level: ten pips
  text(`LEVEL ${lv} OF 10`, x + w / 2, ly, '#9fb0d8', Math.max(4.6, Math.round(5 * k)), 'center', iw - 4);
  for (let i = 0; i < 10; i++) R(ix + 3 + i * ((iw - 6) / 10), ly + 7 * k, Math.max(2, (iw - 6) / 10 - 1), Math.max(2, 2.4 * k), i < lv ? '#7fd38f' : '#2a3350');
}""")

# 5) a new game: 37,500 coins, nothing seen yet, and the streak at zero; old saves note the cards they already own
rep("coins:27500, gift25k:true,", "coins:37500, gift25k:true, seen:{}, streak:{ day:0, last:'' },")
rep("      rebuildTeam();\n      if (!G.gift25k){", "      rebuildTeam();\n      if (!G.seen){ G.seen = {}; G.cards.forEach(c => { G.seen[c.name] = 1; }); }\n      if (!G.streak) G.streak = { day:0, last:'' };\n      G.cards.forEach(c => { if (c.fz == null) c.fz = 0; });\n      if (!G.gift25k){")

# 6) coins in a game: the new table, played innings only, repeat bonuses
rep("  const b = M.batter, st = b.st, p = curPitcher();\n  let runs = 0, out = 0, txt = '';\n  st.pa++;",
    "  const b = M.batter, st = b.st, p = curPitcher();\n  let runs = 0, out = 0, txt = '';\n  st.pa++; const rbi0 = st.rbi;")
rep("""  if (!M.league){ if (weBat()) G.coins += ({ single:25, double:40, triple:75, hr:200 })[res] || 0;
    if (!weBat() && res === 'k') G.coins += 30; }""", "  payPlay(res, b, p, st.rbi - rbi0);")
rep("runs = walkAdvance(); } txt = 'WALK'; break;", "runs = walkAdvance(); st.rbi += runs; } txt = 'WALK'; break;")
rep("case 'hbp': st.hbp = (st.hbp || 0) + 1; runs = walkAdvance();", "case 'hbp': st.hbp = (st.hbp || 0) + 1; runs = walkAdvance(); st.rbi += runs;")
rep("function walkAdvance(){", """// coins for what you play: nothing for innings the game simulates. The same batter repeating a hit or a walk earns 15 more each time; a pitcher's repeat strikeouts 10 more.
let SIMMING = false;
function earn(cat, amt, n = 1){ G.coins += amt; const e = (M.earn[cat] = M.earn[cat] || { n:0, c:0 }); e.n += n; e.c += amt; }
function payPlay(res, b, p, rbi){
  if (M.league || SIMMING || !M.earn) return;
  if (weBat()){
    const base = ({ single:50, double:125, triple:350, hr:200, bb:65, hbp:65 })[res];
    if (base){ const cat = res === 'hbp' ? 'bb' : res, key = (b.id || b.name) + ':' + cat, n = (M.rep[key] || 0) + 1; M.rep[key] = n; earn(cat, base + 15 * (n - 1)); }
    if (rbi > 0) earn('rbi', rbi * 70, rbi);
  } else {
    if (res === 'k'){ const key = 'K:' + (p.id || p.name), n = (M.rep[key] || 0) + 1; M.rep[key] = n; earn('k', 75 + 10 * (n - 1)); }
    if (res === 'dp') earn('dp', 125);
  }
}
function walkAdvance(){""")
rep("function simPitch(){\n  // A quick at-bat with no animation.", "function simPitch(){\n  SIMMING = true; if (!weBat()) M.pitchSimmed = true;\n  try { return simPitchInner(); } finally { SIMMING = false; }\n}\nfunction simPitchInner(){\n  // A quick at-bat with no animation.")
rep("  M.coins0 = G.coins;                                            // what you had when it began: the game's total is worked out from this",
    "  M.coins0 = G.coins;                                            // what you had when it began: the game's total is worked out from this\n  M.earn = {}; M.rep = {}; M.pitchSimmed = false;                 // what you earned for what you played, repeat bonuses, and whether any of your pitching was simmed")
rep("t:Date.now(), coins0:M.coins0 }));", "t:Date.now(), coins0:M.coins0, earn:M.earn, rep:M.rep, ps:M.pitchSimmed }));")
rep("  if (d.coins0 != null) M.coins0 = d.coins0;", "  if (d.coins0 != null) M.coins0 = d.coins0;\n  if (d.earn) M.earn = d.earn; if (d.rep) M.rep = d.rep; if (d.ps) M.pitchSimmed = true;")
rep("""  G.coins += won ? 500 : 120;
  if (!M.meHome ? M.score.home === 0 : M.score.away === 0) G.coins += 500;      // shutout""",
    """  G.coins += won ? 600 : 150;
  M.shutBonus = oth === 0 && !M.pitchSimmed;                                 // a shutout pays only if you pitched every inning yourself
  if (M.shutBonus) G.coins += 850;""")
# the game-over screen: what you earned, line by line
a = s.index("function drawOver(){"); b = s.index("// in-game menu button")
s = s[:a] + """const EARN_ROWS = [['single', 'SINGLE', 'SINGLES'], ['double', 'DOUBLE', 'DOUBLES'], ['triple', 'TRIPLE', 'TRIPLES'], ['hr', 'HOME RUN', 'HOME RUNS'], ['bb', 'WALK', 'WALKS'], ['rbi', 'RBI', 'RBI'], ['k', 'STRIKEOUT', 'STRIKEOUTS'], ['dp', 'DOUBLE PLAY', 'DOUBLE PLAYS']];
function drawOver(){
  btns = [];
  R(0, 0, W, H, '#0b1018ee');
  const my = M.meHome ? M.score.home : M.score.away, ot = M.meHome ? M.score.away : M.score.home, won = my > ot;
  const earned = Math.max(0, G.coins - (M.coins0 == null ? G.coins : M.coins0));
  textb(won ? 'WIN' : 'LOSS', W / 2, 8, won ? '#54d67a' : '#ff6b5a', 20, 'center');
  textb(`${M.away.ab} ${M.score.away}   -   ${M.home.ab} ${M.score.home}`, W / 2, 34, '#fff', 10, 'center');
  const rows = EARN_ROWS.filter(r => M.earn && M.earn[r[0]]).map(r => { const e = M.earn[r[0]]; return [`${e.n} ${e.n === 1 ? r[1] : r[2]}`, e.c]; });
  rows.push([won ? 'WIN BONUS' : 'PLAYED THE GAME', won ? 600 : 150]); if (M.shutBonus) rows.push(['SHUTOUT', 850]);
  const sp = Math.min(12, Math.floor(112 / rows.length)), y0 = 52, lx = W / 2 - 110, rx = W / 2 + 110;
  rows.forEach(([l, v], i) => { textb(l, lx, y0 + i * sp, UI.ice, 7, 'left'); textb('+' + v.toLocaleString(), rx, y0 + i * sp, '#ffffff', 7, 'right'); });
  const ty = y0 + rows.length * sp + 3; R(lx, ty, 220, 1, '#2a5ba6');
  textb('TOTAL EARNED', lx, ty + 4, '#ffd23f', 8, 'left'); textb('+' + earned.toLocaleString() + ' coins', rx, ty + 3, '#ffd23f', 9, 'right');
  button(W / 2 - 50, Math.min(H - 30, ty + 24), 100, 22, 'CONTINUE', () => { M = null; phase = 'menu'; menu = 'title'; }, '#2f6fe0');
}

""" + s[b:]

# 7) the title menu: NEW SAVE, with a question first
rep("let menu = 'title', btns = [];", "let menu = 'title', btns = [], newSaveAsk = false;")
rep("      coinText(G.coins, W / 2, 192, 9, UI.yellow, 'center');\n    } else button(W / 2 - 70, 120, 140, 24, 'START', () => menu = 'pick', '#2f6fe0');",
    """      coinText(G.coins, W / 2, 192, 9, UI.yellow, 'center');
      button(6, H - 24, 62, 16, 'NEW SAVE', () => { newSaveAsk = true; }, '#1a2030', '#fff', 7);
      if (newSaveAsk){
        btns = []; R(0, 0, W, H, 'rgba(8,12,30,.78)');
        const bw = 220, bx = W / 2 - bw / 2, by = 70; uiBox(bx, by, bw, 92);
        ptitle('START OVER?', W / 2, by + 10, 11, UI.yellow); text('THIS ERASES YOUR CURRENT SAVE.', W / 2, by + 34, UI.ice, 6.5, 'center', bw - 12);
        text('A NEW SAVE STARTS WITH 37,500 COINS.', W / 2, by + 45, UI.ice, 6, 'center', bw - 12);
        button(bx + 12, by + 62, 96, 20, 'YES, ERASE', () => { newSaveAsk = false; menu = 'pick'; }, '#4a2030', '#fff', 7);
        button(bx + bw - 12 - 96, by + 62, 96, 20, 'NO', () => { newSaveAsk = false; }, '#2f6fe0', '#fff', 8);
      }
    } else button(W / 2 - 70, 120, 140, 24, 'START', () => menu = 'pick', '#2f6fe0');""")

# 8) input: tearing a pack, scrolling the fuse list
rep("  for (const b of btns) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){ b.fn(); touch.used = true; return; }\n  if (P && P.state === 'inplay' && BALL && BALL.defManual)",
    "  for (const b of btns) if (p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h){ b.fn(); touch.used = true; return; }\n  if (menu === 'open' && OPEN && openPointer('down', p)){ touch.used = true; touch.open = true; return; }\n  if (P && P.state === 'inplay' && BALL && BALL.defManual)")
rep("function move(e){ if (!touch) return; const p = toPix(e); touch.x = p.x; touch.y = p.y;",
    "function move(e){ if (!touch) return; const p = toPix(e); touch.x = p.x; touch.y = p.y;\n  if (touch.open){ openPointer('move', p); return; }\n  if (Math.abs(p.y - touch.y0) > 6 || Math.abs(p.x - touch.x0) > 6) touch.dragged = true;\n  if (menu === 'shop' && shopTab === 'fuse' && phase === 'menu' && !touch.used && fuseRect && touch.x0 >= fuseRect.x && touch.y0 >= fuseRect.y && touch.dragged){ if (touch.f0 === undefined) touch.f0 = fuseScroll; fuseScroll = clamp(touch.f0 + (touch.y0 - touch.y), 0, fuseMax); }")
rep("function up(){ touch = null; }",
    "function up(){\n  if (OPEN) OPEN.drag = false;\n  if (touch && menu === 'shop' && shopTab === 'fuse' && !touch.dragged && !touch.used) for (const r of fuseRows) if (touch.x >= r.x && touch.x <= r.x + r.w && touch.y >= r.y && touch.y <= r.y + r.h){ r.fn(); break; }\n  touch = null;\n}")
rep("cv.addEventListener('wheel', e => { if (menu === 'stats'",
    "cv.addEventListener('wheel', e => { if (menu === 'shop' && shopTab === 'fuse' && phase === 'menu'){ e.preventDefault(); fuseScroll = clamp(fuseScroll + Math.sign(e.deltaY) * 22, 0, fuseMax); } if (menu === 'stats'")

# 9) test hooks
rep("  buyPack, revealNext, rollCard, drawCard, ovrOf, cardById, openTick, get OPEN(){ return OPEN; },",
    "  buyPack, buyPosPack, freePack, rollCard, makeCardAt, valueOf, sellPrice, upCost, upgradeCard, doFuse, canFuse, fuseGroups, fuseRating, bandOf, dealsToday, buyDeal, streakInfo, tradeRating, doTrade, startOpen, openPointer, openAdvance, drawCard, ovrOf, cardById, openTick, get OPEN(){ return OPEN; },\n  get shopTab(){ return shopTab; }, set shopTab(v){ shopTab = v; }, get upStat(){ return upStat; }, set upStat(v){ upStat = v; }, set colSel(v){ colSel = v; }, set fuseMode(v){ fuseMode = v; }, get fuseSel(){ return fuseSel; }, set fuseSel(v){ fuseSel = v; }, tickOpen(ms){ openTick(ms); }, payPlay, earn, get SIMMING(){ return SIMMING; },")
s = s.replace("BUILD = '11-06d'", "BUILD = '11-07a'")
s = re.sub(r"gl3d\.js\?v=11-06d", "gl3d.js?v=11-07a", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
