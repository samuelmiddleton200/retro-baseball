s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── My Cards: a FILTER button after Bench. Pick a position and the list shows only that position. ──
rep("let colSort = 'ovr', colFilter = 'all', colSel = null, colScroll = 0, cardFlip = false;",
    "let colSort = 'ovr', colFilter = 'all', colSel = null, colScroll = 0, cardFlip = false;\nlet colPos = null, colPosMenu = false;                         // the position filter: null shows everybody; the picker is its own screen\nconst FILTER_POS = ['SP', 'RP', 'CP', 'CF', 'LF', 'RF', '1B', '2B', '3B', 'SS', 'C', 'DH'];")
rep("  if (colFilter === 'bench') list = list.filter(c => !inUse(c.id));\n  list.sort(", "  if (colFilter === 'bench') list = list.filter(c => !inUse(c.id));\n  if (colPos) list = list.filter(c => c.pos === colPos);                        // a position picked: only that position\n  list.sort(")
rep("""function drawCards(){
  btns = [];
  uiBg();""", """function drawPosPicker(){
  btns = [];
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('PICK A POSITION', 10, 3, 9, '#ffffff', 'left');
  text('The list will show only that position.', W / 2, 24, UI.ice, 7, 'center', W - 16);
  const bw = 62, bh = 30, gp = 6, per = 6, x0 = W / 2 - (per * bw + (per - 1) * gp) / 2;
  FILTER_POS.forEach((p, i) => {
    const x = x0 + (i % per) * (bw + gp), y = 40 + Math.floor(i / per) * (bh + gp), n = G.cards.filter(c => c.pos === p).length, on = colPos === p;
    if (on) R(x, y, bw, bh, UI.yellow); else uiBox(x, y, bw, bh);
    textb(p, x + bw / 2, y + 5, on ? '#241a00' : '#ffffff', 10, 'center');
    text(n + (n === 1 ? ' card' : ' cards'), x + bw / 2, y + 19, on ? '#241a00' : (n ? UI.ice : '#6c7aa3'), 6, 'center');
    btns.push({ x, y, w:bw, h:bh, fn: () => { colPos = p; colFilter = 'all'; colScroll = 0; benchSel = []; colPosMenu = false; } });
  });
  button(W / 2 - 80, 40 + 2 * (bh + gp) + 6, 160, 20, 'ALL POSITIONS', () => { colPos = null; colScroll = 0; colPosMenu = false; }, '#2f6fe0', '#fff', 8);
  button(10, H - 22, 70, 18, 'BACK', () => { colPosMenu = false; });
}
function drawCards(){
  if (colPosMenu) return drawPosPicker();
  btns = [];
  uiBg();""")
rep("""    btns.push({ x, y:22, w:58, h:14, fn: () => { colFilter = k; colScroll = 0; benchSel = []; } });
  });""", """    btns.push({ x, y:22, w:58, h:14, fn: () => { colFilter = k; colPos = null; colScroll = 0; benchSel = []; } });
  });
  { const x = 10 + 4 * 62, on = !!colPos;                                       // FILTER: pick one position to look at
    if (on) R(x, 22, 58, 14, UI.yellow); else uiBox(x, 22, 58, 14);
    text(colPos ? colPos : 'Filter', x + 29, 25, on ? '#241a00' : '#ffffff', 7, 'center');
    btns.push({ x, y:22, w:58, h:14, fn: () => { colPosMenu = true; } }); }""")
rep("  if (colFilter === 'bench' && !list.length) textb('No bench cards: everybody is in your lineup.', W / 2, 90, '#ffffff', 8, 'center', W - 20);",
    "  if (colFilter === 'bench' && !list.length) textb('No bench cards: everybody is in your lineup.', W / 2, 90, '#ffffff', 8, 'center', W - 20);\n  else if (colPos && !list.length) textb('No ' + colPos + ' cards yet.', W / 2, 90, '#ffffff', 8, 'center', W - 20);")
s = s.replace("BUILD = '11-12o'", "BUILD = '11-12p'").replace("gl3d.js?v=11-12o", "gl3d.js?v=11-12p")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
