s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) rollCard can be told which colour to land on (for trade-ins)
rep("function rollCard(packKey){\n  const p = PACKS[packKey].p;\n  let r = Math.random(), a = 0, tier = 0;\n  for (let i = 0; i < 6; i++){ a += p[i]; if (r < a){ tier = i; break; } }",
    "function rollCard(packKey, forceTier){\n  let tier = 0;\n  if (forceTier != null) tier = forceTier;\n  else { const p = PACKS[packKey].p; let r = Math.random(), a = 0;\n    for (let i = 0; i < 6; i++){ a += p[i]; if (r < a){ tier = i; break; } } }")

# 2) the trade-in screen + best lineup, placed just before the lineup screen
new_code = open('tools/trade_lineup.js', encoding='utf-8').read()
rep("// ── setting the lineup ─────────────────────────────────────────────────────\n",
    new_code + "// ── setting the lineup ─────────────────────────────────────────────────────\n")

# 3) buttons: best lineup on the lineup screen, trade-in on cards
rep("  button(10, H - 22, 70, 18, 'BACK', () => menu = 'cards');\n  button(W - 86, H - 22, 76, 18, 'SHOP', () => menu = 'shop', '#2f6fe0');\n}",
    "  button(W / 2 - 55, H - 22, 110, 18, 'BEST LINEUP', bestLineup, '#2a6a3a', '#fff', 8);\n  if (lineMsgT > 0){ lineMsgT -= 16; textb(lineMsg, W / 2, H - 36, '#9af0ae', 7, 'center'); }\n  button(10, H - 22, 70, 18, 'BACK', () => menu = 'cards');\n  button(W - 86, H - 22, 76, 18, 'SHOP', () => menu = 'shop', '#2f6fe0');\n}")
rep("  button(10, H - 22, 70, 18, 'BACK', () => menu = 'title');\n  button(W - 86, H - 22, 76, 18, 'LINEUP', () => menu = 'lineup', '#2f6fe0');",
    "  button(10, H - 22, 70, 18, 'BACK', () => menu = 'title');\n  button(W / 2 - 50, H - 22, 100, 18, 'TRADE IN 5→1', () => { menu = 'trade'; tradeSel = []; }, '#6a3aa8', '#fff', 8);\n  button(W - 86, H - 22, 76, 18, 'LINEUP', () => menu = 'lineup', '#2f6fe0');")
rep("  else if (menu === 'open'){ drawOpen(); return; }", "  else if (menu === 'open'){ drawOpen(); return; }\n  else if (menu === 'trade'){ drawTrade(); return; }")

# 4) the opening screen must know the trade-in pseudo pack
rep("  const P2 = PACKS[OPEN.kind];\n  textb(`${P2.n.toUpperCase()} PACK`",
    "  const P2 = PACKS[OPEN.kind] || TRADE_PACK;\n  textb(`${P2.n.toUpperCase()}${OPEN.kind === 'trade' ? '' : ' PACK'}`")
rep("button(W / 2 - 50, H / 2 + 2, 100, 20, 'DONE', () => { OPEN = null; menu = 'shop'; }, '#2f6fe0');",
    "button(W / 2 - 50, H / 2 + 2, 100, 20, 'DONE', () => { const f = OPEN.from; OPEN = null; menu = f === 'trade' ? 'trade' : 'shop'; }, '#2f6fe0');")

# 5) debug hooks
rep("  newGame, startGame, doSwing, throwPitch, simRest, simPitch, menu: m => menu = m, btns: () => btns,",
    "  newGame, startGame, doSwing, throwPitch, simRest, simPitch, menu: m => menu = m, btns: () => btns,\n  setCol(id){ colSel = id; cardFlip = false; menu = 'card'; }, bestLineup, doTrade, get tradeSel(){ return tradeSel; }, set tradeSel(v){ tradeSel = v; }, set tradeTier(v){ tradeTier = v; },")

open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
