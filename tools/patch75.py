s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── CHANGE BATTING ORDER: the nine cards in a row, numbered 1-9; tap one (it lifts and glows), tap another and they swap ──
fn = """// ── the batting order screen: pick a batter up, then tap the one he trades places with ──
let orderSel = -1, orderFlash = null;
function orderTap(k){
  if (orderSel < 0){ orderSel = k; return; }
  if (orderSel === k){ orderSel = -1; return; }
  const ord = G.slots.order, a = orderSel; [ord[a], ord[k]] = [ord[k], ord[a]];
  orderFlash = { a, b:k, t:0 }; orderSel = -1; rebuildTeam(); save();
}
const ORDER_NOTE = ['LEADOFF', '', '', 'CLEANUP', '', '', '', '', 'LAST'];
function drawOrder(){
  btns = [];
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('BATTING ORDER', 10, 3, 9, '#ffffff', 'left');
  if (!G.slots.order || G.slots.order.length !== 9) G.slots.order = IDENT9.slice();
  const ord = G.slots.order, gap = 4, cw = Math.min(46, Math.floor((W - 12 - 8 * gap) / 9)), ch = Math.round(cw * 1.4), x0 = W / 2 - (9 * cw + 8 * gap) / 2, pulse = .55 + .45 * Math.sin(frame / 9);
  // what to do, in words: it changes with what you have done
  const msg = orderSel < 0 ? '1. TAP A BATTER' : '2. NOW TAP THE BATTER TO SWAP WITH';
  R(W / 2 - 150, 24, 300, 14, orderSel < 0 ? UI.blueD : '#2a6a3a'); textb(msg, W / 2, 28, orderSel < 0 ? '#ffffff' : UI.yellow, 8, 'center', 292);
  textb('They bat in this order, left to right', W / 2, 42, UI.ice, 6, 'center');
  if (orderFlash){ orderFlash.t += 16; if (orderFlash.t > 700) orderFlash = null; }
  ord.forEach((idx, k) => {
    const c = cardById(G.slots.lineup[idx]), sel = orderSel === k, x = x0 + k * (cw + gap), y = 78 - (sel ? 8 : 0);
    const fl = orderFlash && (orderFlash.a === k || orderFlash.b === k) ? 1 - orderFlash.t / 700 : 0;
    // the batting spot, big
    R(x, 52, cw, 14, sel ? UI.yellow : '#17348a'); R(x, 52, cw, 1, 'rgba(255,255,255,.5)');
    textb(String(k + 1), x + cw / 2, 54, sel ? UI.navy : '#ffffff', 10, 'center');
    if (ORDER_NOTE[k]) textb(ORDER_NOTE[k], x + cw / 2, 68, UI.ice, 5, 'center', cw + 2);
    if (c) drawCard(x, y, c, cw, ch, frame);
    if (sel){ g.strokeStyle = `rgba(255,210,63,${.5 + .5 * pulse})`; g.lineWidth = 2; g.strokeRect(x - 2, y - 2, cw + 4, ch + 4); }
    if (fl > 0){ R(x, y, cw, ch, `rgba(120,255,160,${fl * .45})`); }
    textb(POS[idx], x + cw / 2, y + ch + 4 + (sel ? 8 : 0), sel ? UI.yellow : '#ffffff', 7, 'center');
    btns.push({ x:x - 2, y:50, w:cw + 4, h:ch + 40, fn: () => orderTap(k) });
  });
  if (orderSel >= 0) button(W / 2 - 40, H - 44, 80, 16, 'CANCEL', () => { orderSel = -1; }, '#1a2030', '#fff', 7);
  button(W / 2 - 50, H - 22, 100, 18, 'DONE', () => { orderSel = -1; menu = 'lineup'; }, '#2a6a3a', '#fff', 8);
}
"""
rep("let lineSel = null;    // { where:'lineup'|'rot'|'pen', i }", fn + "let lineSel = null;    // { where:'lineup'|'rot'|'pen', i }")
rep("  else if (menu === 'stats'){ drawStats(); return; }", "  else if (menu === 'stats'){ drawStats(); return; }\n  else if (menu === 'order'){ drawOrder(); return; }")
rep("""  button(W / 2 - 55, H - 22, 110, 18, 'BEST LINEUP', bestLineup, '#2a6a3a', '#fff', 8);
  if (lineMsgT > 0){ lineMsgT -= 16; textb(lineMsg, W / 2, H - 36, '#9af0ae', 7, 'center'); }
  button(10, H - 22, 70, 18, 'BACK', () => menu = 'cards');
  button(W - 86, H - 22, 76, 18, 'SHOP', () => menu = 'shop', '#2f6fe0');""",
"""  const bx = W / 2 - 175;
  button(8, H - 22, 60, 18, 'BACK', () => menu = 'cards');
  button(bx + 70, H - 22, 100, 18, 'BEST LINEUP', bestLineup, '#2a6a3a', '#fff', 8);
  button(bx + 178, H - 22, 168, 18, 'CHANGE BATTING ORDER', () => { orderSel = -1; menu = 'order'; }, '#2f6fe0', '#fff', 7);
  button(W - 68, H - 22, 60, 18, 'SHOP', () => menu = 'shop');
  if (lineMsgT > 0){ lineMsgT -= 16; textb(lineMsg, W / 2, H - 36, '#9af0ae', 7, 'center'); }""")
s = s.replace("BUILD = '11-11y'", "BUILD = '11-11z'").replace("gl3d.js?v=11-11y", "gl3d.js?v=11-11z")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
