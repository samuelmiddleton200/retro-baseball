s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70]); s = s.replace(a, b)

rep("  if (benchSel.length < TRADE_N) benchSel.push(c.id);\n}", "  if (benchSel.length < TRADE_N * 5) benchSel.push(c.id);                   // up to 25: 5 for 1, 10 for 2, 15 for 3, 20 for 4, 25 for 5\n}")
rep("""  if (give.length !== TRADE_N || give.some(c => inUse(c.id))) { benchSel = []; return; }
  const ti = tierIdx(give[0]);
  if (give.some(c => tierIdx(c) !== ti) || ti >= 5){ benchSel = []; return; }
  G.cards = G.cards.filter(c => !benchSel.includes(c.id));
  const c = rollCard('bronze', ti + 1);
  OPEN = { kind:'trade', cards:[c], i:0, t:0, spin:null, revealed:[], from:'bench', per:1, bspin:null };""",
"""  if (give.length < TRADE_N || give.length % TRADE_N || give.some(c => inUse(c.id))) { benchSel = []; return; }
  const ti = tierIdx(give[0]), count = give.length / TRADE_N;
  if (give.some(c => tierIdx(c) !== ti) || ti >= 5){ benchSel = []; return; }
  G.cards = G.cards.filter(c => !benchSel.includes(c.id));
  const cards = []; for (let k = 0; k < count; k++) cards.push(rollCard('bronze', ti + 1));
  OPEN = { kind:'trade', cards, i:0, t:0, spin:null, revealed:[], from:'bench', per: count > 1 ? count : 1, bspin:null };""")
rep("const first = benchSel.length ? cardById(benchSel[0]) : null, ti = first ? tierIdx(first) : -1, ready = benchSel.length === TRADE_N && ti < 5;",
    "const first = benchSel.length ? cardById(benchSel[0]) : null, ti = first ? tierIdx(first) : -1, nSel = benchSel.length, cnt = Math.floor(nSel / TRADE_N), ready = nSel >= TRADE_N && nSel % TRADE_N === 0 && ti < 5;")
rep("const label = ready ? `TRADE IN FOR 1 ${TIER_LABEL[ti + 1]} CARD` : ti === 5 ? 'RED IS THE TOP COLOUR' : first ? `PICK ${TRADE_N - benchSel.length} MORE ${TIER_LABEL[ti]}` : `PICK ${TRADE_N} OF ONE COLOUR`;",
    "const label = ready ? `TRADE IN ${nSel} FOR ${cnt} ${TIER_LABEL[ti + 1]} CARD${cnt > 1 ? 'S' : ''}` : ti === 5 ? 'RED IS THE TOP COLOUR' : first ? `${TRADE_N - nSel % TRADE_N} MORE ${TIER_LABEL[ti]} FOR ${cnt + 1} ${TIER_LABEL[ti + 1]}` : `PICK ${TRADE_N} OF ONE COLOUR`;")
rep("button(W / 2 - 84, H - 22, 168, 18, label, ready ? benchTrade", "button(W / 2 - 96, H - 22, 192, 18, label, ready ? benchTrade")
rep("else text(`Tap ${TRADE_N} bench cards of one colour to trade them up  (${benchSel.length}/${TRADE_N})`, W / 2, H - 36, UI.ice, 6, 'center', W - 20);",
    "else text(`Tap bench cards of one colour:  5 for 1,  10 for 2,  15 for 3,  20 for 4,  25 for 5   (${benchSel.length} picked)`, W / 2, H - 36, UI.ice, 6, 'center', W - 20);")
# the batch reveal copes with 2 to 5 cards
rep("bw = OPEN.per === 3 ? 62 : 46, bh = Math.round(bw * 1.4), gp = OPEN.per === 3 ? 10 : 6;", "bw = OPEN.per <= 3 ? 62 : 46, bh = Math.round(bw * 1.4), gp = OPEN.per <= 3 ? 10 : 6;")
rep("OPEN.per === 5 ? ({ LEGENDARY:'LEGEND', UNCOMMON:'UNCOM' }[TIER_LABEL[b.ti]] || TIER_LABEL[b.ti]) : TIER_LABEL[b.ti], mx, y0 - 14, OPEN.per === 5 ? 6 : b.ti >= 4 ? 8 : 7, tcol);",
    "OPEN.per >= 4 ? ({ LEGENDARY:'LEGEND', UNCOMMON:'UNCOM' }[TIER_LABEL[b.ti]] || TIER_LABEL[b.ti]) : TIER_LABEL[b.ti], mx, y0 - 14, OPEN.per >= 4 ? 6 : b.ti >= 4 ? 8 : 7, tcol);")
# the end screen of a trade: just MY CARDS and SHOP, centred (kept from before)
s = s.replace("BUILD = '11-03r'", "BUILD = '11-03s'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
