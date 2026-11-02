s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

def between(a_marker, b_marker, new):
    global s
    a = s.index(a_marker); b = s.index(b_marker, a)
    s = s[:a] + new + s[b:]

# 1) the pixel font: loaded from Google Fonts, used by every menu; cards keep the plain monospace
rep('<link rel="manifest" href="manifest.webmanifest">',
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&display=swap">\n<link rel="manifest" href="manifest.webmanifest">')
rep("function text(s, x, y, c = '#fff', size = 7, align = 'left'){\n  g.font = `${size}px ui-monospace, \"Courier New\", monospace`;",
    "const MONO = 'ui-monospace, \"Courier New\", monospace', PIXF = '\"Silkscreen\", \"Courier New\", monospace';\nlet FONT = PIXF;                                          // menus: the pixel font. Cards switch to MONO while they draw.\nconst fontOf = size => FONT === PIXF ? `${Math.max(5, size * .86).toFixed(1)}px ${PIXF}` : `${size}px ${MONO}`;\ntry { document.fonts.load('400 10px Silkscreen'); document.fonts.load('700 10px Silkscreen'); } catch (e) {}\nfunction text(s, x, y, c = '#fff', size = 7, align = 'left'){\n  g.font = fontOf(size);")
rep("  // carry over the grass and the crowd. A heavy outline on small text reads as a smudge.\n  g.font = `${size}px ui-monospace, \"Courier New\", monospace`;",
    "  // carry over the grass and the crowd. A heavy outline on small text reads as a smudge.\n  g.font = fontOf(size);")

# 2) the Retro Basket look: helpers + the new button, replacing the old button
old_btn_a = s.index("let menu = 'title', btns = [];\nfunction button(")
old_btn_b = s.index("function drawMenu(){")
s = s[:old_btn_a] + "let menu = 'title', btns = [];\n" + open('tools/ui_code.js', encoding='utf-8').read() + "\n" + s[old_btn_b:]

# 3) cards draw in the plain font whatever the screen's font is
rep("function drawCard(x, y, c, w = CARD_W, h = CARD_H, t = 0, o = {}){\n  const ovr = ovrOf(c)",
    "function drawCard(x, y, c, w = CARD_W, h = CARD_H, t = 0, o = {}){ const f0 = FONT; FONT = MONO; try { drawCardInner(x, y, c, w, h, t, o); } finally { FONT = f0; } }\nfunction drawCardInner(x, y, c, w, h, t, o){\n  const ovr = ovrOf(c)")
rep("function drawCardBack(x, y, c, w, h, t = 0){\n  const ovr = ovrOf(c)",
    "function drawCardBack(x, y, c, w, h, t = 0){ const f0 = FONT; FONT = MONO; try { drawCardBackInner(x, y, c, w, h, t); } finally { FONT = f0; } }\nfunction drawCardBackInner(x, y, c, w, h, t){\n  const ovr = ovrOf(c)")

# 4) shop and the opening ceremony
between("// ── the shop ───────────────────────────────────────────────────────────────\nlet shopSel", "// ── the collection ─────", open('tools/shop_code.js', encoding='utf-8').read())
between("function drawOpen(){", "// ── the shop ───", open('tools/open_code.js', encoding='utf-8').read())
rep("  OPEN = { kind, cards, i:0, t:0, spin:null, revealed:[] };\n  menu = 'open'; save();", "  OPEN = { kind, cards, i:0, t:0, spin:null, revealed:[], n };\n  menu = 'open'; save();")
rep("  OPEN = { kind:'bronze', cards:[rollCard('bronze'), rollCard('bronze'), rollCard('bronze')], i:0, t:0, spin:null, revealed:[] };",
    "  OPEN = { kind:'bronze', cards:[rollCard('bronze'), rollCard('bronze'), rollCard('bronze')], i:0, t:0, spin:null, revealed:[], n:1, free:true };")

# 5) the other menus: blue ground, boxes, titles
rep("function drawCards(){\n  btns = [];\n  R(0, 0, W, H, '#0b1018');\n  textb('MY CARDS', 10, 6, '#ffd23f', 11);\n  textb(`${G.cards.length} cards · ${G.coins.toLocaleString()} coins`, W - 10, 8, '#ffd23f', 8, 'right');",
    "function drawCards(){\n  btns = [];\n  uiBg();\n  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');\n  ptitle('MY CARDS', 10, 3, 10);\n  text(`${G.cards.length} cards`, W - 100, 5, UI.ice, 7, 'right'); coinText(G.coins, W - 8, 4, 8, UI.yellow, 'right');")
rep("    R(x, 20, 58, 14, on ? '#2f6fe0' : '#131924');\n    textb(l, x + 29, 23, on ? '#fff' : '#8e97a8', 7, 'center');",
    "    if (on) R(x, 22, 58, 14, UI.yellow); else uiBox(x, 22, 58, 14);\n    text(l, x + 29, 25, on ? '#241a00' : '#ffffff', 7, 'center');")
rep("    btns.push({ x, y:20, w:58, h:14, fn: () => { colFilter = k; colScroll = 0; } });", "    btns.push({ x, y:22, w:58, h:14, fn: () => { colFilter = k; colScroll = 0; } });")
rep("function drawCardView(){\n  btns = [];\n  R(0, 0, W, H, '#0b1018');", "function drawCardView(){\n  btns = [];\n  uiBg();")
rep("function drawTrade(){\n  btns = [];\n  R(0, 0, W, H, '#0b1018');\n  textb('TRADE IN', 10, 6, '#ffd23f', 11);\n  textb(`${TRADE_N} cards of one colour  →  1 random card of the next colour`, 10, 22, '#b9c2d2', 7);",
    "function drawTrade(){\n  btns = [];\n  uiBg();\n  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');\n  ptitle('TRADE IN', 10, 3, 10);\n  text(`${TRADE_N} cards of one colour  →  1 random card of the next colour`, 110, 5, UI.ice, 7);")
rep("function drawLineup(){\n  btns = [];\n  R(0, 0, W, H, '#0b1018');\n  textb('LINEUP', 10, 6, '#ffd23f', 11);",
    "function drawLineup(){\n  btns = [];\n  uiBg();\n  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');\n  ptitle('LINEUP', 10, 3, 10);")
rep("    R(x, y, SW, 16, '#131924');\n    R(x, y, 2, 16, '#2a3550');\n    textb(lbl, x + 4, y + 4, '#5c6473', 7);",
    "    uiBox(x, y, SW, 16);\n    textb(lbl, x + 5, y + 5, UI.yellow, 7);")
# 6) the title screen
rep("  btns = [];\n  R(0, 0, W, H, '#0b1018');\n  for (let i = 0; i < 60; i++) R(0, i, W, 1, `rgb(${11 + i / 3 | 0},${16 + i / 2 | 0},${24 + i | 0})`);\n  if (menu === 'title'){\n    textb('RETRO', W / 2, 30, '#ffd23f', 26, 'center');\n    textb('BASEBALL', W / 2, 58, '#fff', 26, 'center');\n    text('build ' + BUILD, W - 6, H - 10, '#3d4659', 6, 'right');",
    "  btns = [];\n  uiBg();\n  if (menu === 'title'){\n    ptitle('RETRO', W / 2, 22, 28, UI.yellow);\n    ptitle('BASEBALL', W / 2, 54, 28, '#ffffff');\n    text('build ' + BUILD, W - 6, H - 10, UI.ice, 6, 'right');")
rep("      textb(`${me.city} ${me.nick}   ${me.w}-${me.l}`, W / 2, 96, me.c2, 9, 'center');", "      ptitle(`${me.city} ${me.nick}   ${me.w}-${me.l}`, W / 2, 94, 8, '#ffffff');")
rep("      textb(`${G.coins.toLocaleString()} coins`, W / 2, 190, '#ffd23f', 9, 'center');", "      coinText(G.coins, W / 2, 192, 9, UI.yellow, 'center');")
open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
