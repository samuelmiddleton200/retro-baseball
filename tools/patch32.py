s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70]); s = s.replace(a, b)

rep("let colSort = 'ovr', colFilter = 'all', colSel = null, colScroll = 0, cardFlip = false;",
"""let colSort = 'ovr', colFilter = 'all', colSel = null, colScroll = 0, cardFlip = false;
// the Bench view: tap bench cards to select them (all of one colour); with 5 selected the button trades them for 1 random card of the next colour up
let benchSel = [];
function benchToggle(c){
  const t = tierIdx(c);
  if (benchSel.includes(c.id)){ benchSel = benchSel.filter(id => id !== c.id); return; }
  const first = benchSel.length ? cardById(benchSel[0]) : null;
  if (first && tierIdx(first) !== t) benchSel = [];                         // a different colour: start a new selection with this card
  if (benchSel.length < TRADE_N) benchSel.push(c.id);
}
function benchTrade(){
  const give = benchSel.map(cardById).filter(Boolean);
  if (give.length !== TRADE_N || give.some(c => inUse(c.id))) { benchSel = []; return; }
  const ti = tierIdx(give[0]);
  if (give.some(c => tierIdx(c) !== ti) || ti >= 5){ benchSel = []; return; }
  G.cards = G.cards.filter(c => !benchSel.includes(c.id));
  const c = rollCard('bronze', ti + 1);
  OPEN = { kind:'trade', cards:[c], i:0, t:0, spin:null, revealed:[], from:'bench', per:1, bspin:null };
  benchSel = []; menu = 'open'; save();
}""")
# selecting in bench mode instead of opening the card
rep("    btns.push({ x, y, w:cw, h:ch, fn: () => { colSel = c.id; cardFlip = false; menu = 'card'; } });\n  });\n  g.restore();",
"""    if (colFilter === 'bench'){
      const sel = benchSel.includes(c.id);
      if (sel){ R(x, y + ch - 3, cw, 3, '#54d67a'); g.strokeStyle = '#54d67a'; g.lineWidth = 1.5; g.strokeRect(x - .5, y - .5, cw + 1, ch + 1); textb('✓', x + cw / 2, y + 12, '#54d67a', 14, 'center'); }
      btns.push({ x, y, w:cw, h:ch, fn: () => benchToggle(c) });
    } else btns.push({ x, y, w:cw, h:ch, fn: () => { colSel = c.id; cardFlip = false; menu = 'card'; } });
  });
  g.restore();""")
rep("    btns.push({ x, y:22, w:58, h:14, fn: () => { colFilter = k; colScroll = 0; } });",
    "    btns.push({ x, y:22, w:58, h:14, fn: () => { colFilter = k; colScroll = 0; benchSel = []; } });")
rep("  button(W / 2 - 50, H - 22, 100, 18, 'TRADE IN 5→1', () => { menu = 'trade'; tradeSel = []; }, '#6a3aa8', '#fff', 8);",
"""  if (colFilter === 'bench'){
    const first = benchSel.length ? cardById(benchSel[0]) : null, ti = first ? tierIdx(first) : -1, ready = benchSel.length === TRADE_N && ti < 5;
    const label = ready ? `TRADE IN FOR 1 ${TIER_LABEL[ti + 1]} CARD` : ti === 5 ? 'RED IS THE TOP COLOUR' : first ? `PICK ${TRADE_N - benchSel.length} MORE ${TIER_LABEL[ti]}` : `PICK ${TRADE_N} OF ONE COLOUR`;
    button(W / 2 - 84, H - 22, 168, 18, label, ready ? benchTrade : () => {}, ready ? '#2a6a3a' : '#161b26', ready ? '#fff' : '#8896b3', 8);
    if (!list.length) textb('No bench cards: everybody is in your lineup.', W / 2, 90, '#ffffff', 8, 'center', W - 20);
    else text(`Tap ${TRADE_N} bench cards of one colour to trade them up  (${benchSel.length}/${TRADE_N})`, W - 12, 26, UI.ice, 6, 'right', W - 260);
  } else button(W / 2 - 50, H - 22, 100, 18, 'TRADE IN 5→1', () => { menu = 'trade'; tradeSel = []; }, '#6a3aa8', '#fff', 8);""")
# after the reveal, a bench trade goes back to the bench
rep("    if (OPEN.kind === 'trade') button(cx - 52, by, 104, 20, 'TRADE MORE', () => { OPEN = null; menu = 'trade'; }, '#2f6fe0', '#fff', 8);",
    "    if (OPEN.kind === 'trade') button(cx - 52, by, 104, 20, 'TRADE MORE', () => { const fb = OPEN.from === 'bench'; OPEN = null; menu = fb ? 'cards' : 'trade'; if (fb) colFilter = 'bench'; }, '#2f6fe0', '#fff', 8);")
s = s.replace("BUILD = '11-03o'", "BUILD = '11-03p'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
