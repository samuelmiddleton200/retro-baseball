// ── one card: upgrade a stat, sell, put him in the lineup ─────────────────────────────────────────
let upStat = 0, cardFlipA = 0;
const linkedStat = (c, i) => !isPitcher(c) && (i === 2 || i === 3);                        // a hitter's speed IS his fielding: the two rows move together
function upgradeCard(c){
  if (c.lvl >= 10) return;
  const cost = upCost(c); if (G.coins < cost) return;
  const key = statsOf(c)[upStat][1];
  if (linkedStat(c, upStat)){ if (c.fielding >= 120) return; G.coins -= cost; c.fielding = clamp(c.fielding + 1, 60, 120); c.speed = c.fielding; }
  else { if (c[key] >= 120) return; G.coins -= cost; c[key] = clamp(c[key] + 2, 60, 120); }
  c.lvl++; c.ovr = ovrOf(c); upFx = 600; save();
}
function drawCardView(){
  btns = [];
  uiBg();
  const c = cardById(colSel);
  if (!c){ menu = 'cards'; return; }
  const wide = W >= 430, cw = 84, chh = 118, cx = 10, cy = 32;
  R(0, 0, W, 21, UI.blueDD); R(0, 21, W, 2, '#ffffff');
  button(6, 3, 44, 15, 'BACK', () => menu = 'cards', '#1a2030', '#fff', 7);
  ptitle(c.name.toUpperCase(), 58, 5, 9, '#ffffff', 'left'); coinText(G.coins, W - 8, 6, 9, UI.yellow, 'right');
  // the front, and (room permitting) the back with his level on it; on a narrow screen tap the card to turn it over
  cardFlipA += clamp((cardFlip ? 1 : 0) - cardFlipA, -.085, .085);
  if (wide){
    drawCard(cx, cy, c, cw, chh, frame); drawCardBack(cx + cw + 6, cy, c, cw, chh, frame);
  } else {
    const fsx = Math.max(.03, Math.abs(Math.cos(cardFlipA * Math.PI)));
    g.save(); g.translate(cx + cw / 2, 0); g.scale(fsx, 1); g.translate(-(cx + cw / 2), 0);
    if (cardFlipA > .5) drawCardBack(cx, cy, c, cw, chh, frame); else drawCard(cx, cy, c, cw, chh, frame);
    g.restore();
    btns.push({ x:cx, y:cy, w:cw, h:chh, fn: () => cardFlip = !cardFlip });
    text(cardFlip ? 'TAP FOR THE FRONT' : 'TAP: LEVEL AND STATS', cx + cw / 2, cy + chh + 4, '#cfe0ff', 5, 'center', cw + 10);
  }
  const x0 = wide ? cx + 2 * (cw + 6) + 8 : cx + cw + 10, pw = W - 8 - x0;
  uiBox(x0, 28, pw, H - 32);
  ptitle('UPGRADE', x0 + 6, 33, 8.5, '#fff', 'left');
  text(`${c.pos}  OVERALL ${ovrOf(c)}  LEVEL ${c.lvl} OF 10`, x0 + 6, 46, colOf(ovrOf(c)), 6, 'left', pw - 10);
  const maxed = c.lvl >= 10;
  statsOf(c).forEach(([lbl, key], i) => {
    const y = 58 + i * 25, v = c[key], sel = !maxed && (upStat === i || (linkedStat(c, i) && linkedStat(c, upStat))), step = linkedStat(c, i) ? 1 : 2;
    R(x0 + 5, y, pw - 10, 22, sel ? '#2c3f95' : UI.navy);
    if (sel){ R(x0 + 5, y, pw - 10, 1, UI.yellow); R(x0 + 5, y + 21, pw - 10, 1, UI.yellow); R(x0 + 5, y, 1, 22, UI.yellow); R(x0 + pw - 6, y, 1, 22, UI.yellow); }
    if (sel) text('>', x0 + 8, y + 7, UI.yellow, 8);
    textb(lbl, x0 + 20, y + 7, '#fff', 7);
    textb(String(v), x0 + 52, y + 5, colOf(v), 10);
    const bx = x0 + 74, bw = Math.max(20, pw - 74 - 62);
    R(bx, y + 8, bw, 6, '#1b2a66'); R(bx, y + 8, Math.round(bw * clamp((v - 55) / 65, 0, 1)), 6, sel ? UI.yellow : '#6f8de8');
    text(sel && !maxed ? `${v} > ${Math.min(120, v + step)}` : `+${step}`, x0 + pw - 9, y + 7, sel ? UI.yellow : '#8aa0d0', 7, 'right');
    if (!maxed) btns.push({ x:x0 + 5, y, w:pw - 10, h:22, fn: () => upStat = i });
  });
  const by = 162;
  if (!maxed){
    const cost = upCost(c), can = G.coins >= cost;
    button(x0 + 5, by, pw - 10 - (inUse(c.id) ? 0 : 74), 22, `UPGRADE ${statsOf(c)[upStat][0]}  ${cost.toLocaleString()}`, () => upgradeCard(c), can ? '#2f6fe0' : '#161b26', '#fff', 7);
  } else text('FULLY UPGRADED', x0 + 10, by + 7, '#7fd38f', 8);
  if (!inUse(c.id)) button(x0 + pw - 5 - 70, by, 70, 22, `SELL ${fmt(sellPrice(c))}`, () => { G.coins += sellPrice(c); G.cards = G.cards.filter(z => z.id !== c.id); menu = 'cards'; save(); }, '#4a2030', '#fff', 7);
  else text('IN YOUR LINEUP', x0 + pw - 10, by + 28, '#54d67a', 5.5, 'right');
  text('EACH LEVEL ADDS TO ONE STAT', x0 + 6, by + 28, UI.ice, 5, 'left', pw - 10);
  if (upFx > 0){ upFx -= 16; R(cx - 3, cy - 3, cw + 6, chh + 6, `rgba(127,211,143,${clamp(upFx / 900, 0, .5)})`); }
}
let upFx = 0;

// ── trading cards in: 5 of one colour make one card of the next colour up, rated (their average + 10) ──
let tradeTier = 0, tradeSel = [];
const TRADE_PACK = { n:'Trade-in', col:'#9b59ff', col2:'#dcc2ff' };
const spareOf = ti => G.cards.filter(c => tierIdx(c) === ti && !inUse(c.id)).sort((a, b) => ovrOf(a) - ovrOf(b));
function doTrade(){
  if (tradeSel.length !== TRADE_N || tradeTier >= 5) return;
  const give = tradeSel.map(cardById).filter(Boolean);
  if (give.length !== TRADE_N || give.some(c => inUse(c.id) || tierIdx(c) !== tradeTier)){ tradeSel = []; return; }
  const c = makeCardAt(tradeRating(give));
  G.cards = G.cards.filter(z => !tradeSel.includes(z.id));
  tradeSel = []; startOpen({ kind:'trade', batches:[{ tier:null, cards:[c] }], from:'trade' }); save();
}
function drawTrade(){
  btns = [];
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');
  ptitle('TRADE IN', 10, 3, 10, '#ffffff', 'left');
  text(`${TRADE_N} cards of one colour  =  1 card rated their average + 10`, 100, 5, UI.ice, 7, 'left', W - 108);
  TIERS.forEach((T, ti) => {
    const n = spareOf(ti).length, on = tradeTier === ti, x = 10 + ti * 56;
    R(x, 33, 52, 20, on ? mix(T.col, '#0b1018', .35) : '#131924');
    R(x, 33, 52, 2, T.col);
    if (on){ g.strokeStyle = '#fff'; g.strokeRect(x + .5, 33.5, 51, 19); }
    text(TIER_LABEL[ti], x + 26, 38, on ? '#fff' : UI.ice, 6, 'center', 48);
    text(ti === 5 ? 'max' : `${n} spare`, x + 26, 45, ti === 5 ? '#8aa0d0' : n >= TRADE_N ? '#9af0ae' : '#ffffff', 6, 'center', 48);
    btns.push({ x, y:33, w:52, h:20, fn: () => { tradeTier = ti; tradeSel = []; } });
  });
  const list = spareOf(tradeTier), cw = 40, ch = 56, per = Math.floor((W - 16) / (cw + 4));
  if (tradeTier >= 5) textb('Red is the top colour: nothing to trade up to.', W / 2, 90, '#ffffff', 8, 'center');
  else if (!list.length) textb('No spare cards of this colour (lineup cards cannot be traded).', W / 2, 90, '#ffffff', 8, 'center', W - 20);
  list.slice(0, per * 2).forEach((c, i) => {
    const x = 8 + (i % per) * (cw + 4), y = 66 + Math.floor(i / per) * (ch + 6), sel = tradeSel.includes(c.id);
    drawCard(x, y - (sel ? 4 : 0), c, cw, ch, frame);
    if (sel){ R(x, y + ch - 3, cw, 3, '#54d67a'); textb('✓', x + cw / 2, y + 14, '#54d67a', 14, 'center'); }
    btns.push({ x, y:y - 4, w:cw, h:ch + 4, fn: () => {
      if (sel) tradeSel = tradeSel.filter(id => id !== c.id); else if (tradeSel.length < TRADE_N) tradeSel.push(c.id); } });
  });
  if (list.length > per * 2) text(`+${list.length - per * 2} more (lowest shown first)`, W / 2, H - 52, UI.ice, 6, 'center');
  const ready = tradeSel.length === TRADE_N && tradeTier < 5;
  const got = ready ? tradeRating(tradeSel.map(cardById).filter(Boolean)) : 0;
  button(W / 2 - 100, H - 42, 200, 20, ready ? `TRADE ${TRADE_N} FOR A ${got}` : `PICK ${TRADE_N - tradeSel.length} MORE`,
    ready ? doTrade : () => {}, ready ? '#2a6a3a' : '#161b26', ready ? '#fff' : '#525c72', 8);
  button(W / 2 + 108, H - 42, 80, 20, 'AUTO PICK', () => { tradeSel = list.slice(0, TRADE_N).map(c => c.id); }, '#1a2030', '#fff', 7);
  button(10, H - 22, 70, 18, 'BACK', () => { menu = 'cards'; tradeSel = []; });
  button(W - 86, H - 22, 76, 18, 'SHOP', () => { menu = 'shop'; shopTab = 'packs'; tradeSel = []; }, '#2f6fe0');
}

