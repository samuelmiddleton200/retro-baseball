// ── trading cards in: 5 of one colour for 1 random card of the next colour up ──────────────────────
let tradeTier = 0, tradeSel = [];
const TRADE_N = 5, TRADE_PACK = { n:'Trade-in', col:'#9b59ff', col2:'#dcc2ff' };
const spareOf = ti => G.cards.filter(c => tierIdx(c) === ti && !inUse(c.id)).sort((a, b) => ovrOf(a) - ovrOf(b));
function doTrade(){
  if (tradeSel.length !== TRADE_N || tradeTier >= 5) return;
  const give = tradeSel.map(cardById).filter(Boolean);
  if (give.length !== TRADE_N || give.some(c => inUse(c.id) || tierIdx(c) !== tradeTier)){ tradeSel = []; return; }
  G.cards = G.cards.filter(c => !tradeSel.includes(c.id));
  const c = rollCard('bronze', tradeTier + 1);
  OPEN = { kind:'trade', cards:[c], i:0, t:0, spin:null, revealed:[], from:'trade' };
  tradeSel = []; menu = 'open'; save();
}
function drawTrade(){
  btns = [];
  R(0, 0, W, H, '#0b1018');
  textb('TRADE IN', 10, 6, '#ffd23f', 11);
  textb(`${TRADE_N} cards of one colour  →  1 random card of the next colour`, 10, 22, '#b9c2d2', 7);
  // one chip per colour: how many spare cards you have of it
  TIERS.forEach((T, ti) => {
    const n = spareOf(ti).length, on = tradeTier === ti, x = 10 + ti * 56;
    R(x, 33, 52, 20, on ? mix(T.col, '#0b1018', .35) : '#131924');
    R(x, 33, 52, 2, T.col);
    if (on){ g.strokeStyle = '#fff'; g.strokeRect(x + .5, 33.5, 51, 19); }
    text(TIER_LABEL[ti].slice(0, 7), x + 26, 38, on ? '#fff' : '#8e97a8', 6, 'center');
    text(ti === 5 ? 'max' : `${n} spare`, x + 26, 45, ti === 5 ? '#5c6473' : n >= TRADE_N ? '#9af0ae' : '#6c7587', 6, 'center');
    btns.push({ x, y:33, w:52, h:20, fn: () => { tradeTier = ti; tradeSel = []; } });
  });
  const list = spareOf(tradeTier), cw = 40, ch = 56, per = Math.floor((W - 16) / (cw + 4));
  if (tradeTier >= 5) textb('Red is the top colour: nothing to trade up to.', W / 2, 90, '#8e97a8', 8, 'center');
  else if (!list.length) textb('No spare cards of this colour (lineup cards cannot be traded).', W / 2, 90, '#8e97a8', 8, 'center');
  list.slice(0, per * 2).forEach((c, i) => {
    const x = 8 + (i % per) * (cw + 4), y = 60 + Math.floor(i / per) * (ch + 6), sel = tradeSel.includes(c.id);
    drawCard(x, y - (sel ? 4 : 0), c, cw, ch, frame);
    if (sel){ R(x, y + ch - 3, cw, 3, '#54d67a'); textb('✓', x + cw / 2, y + 14, '#54d67a', 14, 'center'); }
    btns.push({ x, y:y - 4, w:cw, h:ch + 4, fn: () => {
      if (sel) tradeSel = tradeSel.filter(id => id !== c.id); else if (tradeSel.length < TRADE_N) tradeSel.push(c.id); } });
  });
  if (list.length > per * 2) text(`+${list.length - per * 2} more (lowest shown first)`, W / 2, H - 52, '#6c7587', 6, 'center');
  const ready = tradeSel.length === TRADE_N && tradeTier < 5;
  const nextName = tradeTier < 5 ? TIER_LABEL[tradeTier + 1] : '';
  button(W / 2 - 100, H - 42, 200, 20, ready ? `TRADE ${TRADE_N} FOR 1 ${nextName}` : `PICK ${TRADE_N - tradeSel.length} MORE`,
    ready ? doTrade : () => {}, ready ? '#2a6a3a' : '#161b26', ready ? '#fff' : '#525c72', 8);
  button(W / 2 + 108, H - 42, 80, 20, 'AUTO PICK', () => { tradeSel = list.slice(0, TRADE_N).map(c => c.id); }, '#1a2030', '#fff', 7);
  button(10, H - 22, 70, 18, 'BACK', () => { menu = 'cards'; tradeSel = []; });
  button(W - 86, H - 22, 76, 18, 'SHOP', () => { menu = 'shop'; tradeSel = []; }, '#2f6fe0');
}

// ── best lineup: put the strongest card at every spot in one tap ──────────────────────────────────
let lineMsg = '', lineMsgT = 0;
function bestLineup(){
  const hit = G.cards.filter(c => !isPitcher(c)).sort((a, b) => ovrOf(b) - ovrOf(a));
  const spot = Array(9).fill(null), left = [];
  hit.forEach(c => { const i = POS.indexOf(c.pos); if (i >= 0 && !spot[i]) spot[i] = c; else left.push(c); });
  [8, 0, 1, 2, 3, 4, 5, 6, 7].forEach(i => { if (!spot[i] && left.length) spot[i] = left.shift(); });   // the best leftover bat takes DH first
  const pit = G.cards.filter(isPitcher).sort((a, b) => ovrOf(b) - ovrOf(a)), used = new Set();
  const take = pred => { const c = pit.find(p => !used.has(p.id) && pred(p)); if (c) used.add(c.id); return c; };
  const rot = [0, 1, 2, 3, 4].map(() => take(p => p.pos === 'SP') || take(() => true));
  const cp = take(p => p.pos === 'CP') || take(p => p.pos === 'RP') || take(() => true);
  const pen = [0, 1, 2, 3].map(() => take(p => p.pos === 'RP') || take(() => true));
  const keep = (arr, old) => arr.map((c, i) => c ? c.id : old[i]);
  G.slots.lineup = keep(spot, G.slots.lineup); G.slots.rot = keep(rot, G.slots.rot); G.slots.pen = keep(pen.concat([cp]), G.slots.pen);
  rebuildTeam(); save();
  const all = [...G.slots.lineup, ...G.slots.rot, ...G.slots.pen].map(cardById).filter(Boolean);
  lineMsg = `Best lineup set: team overall ${Math.round(all.reduce((s, c) => s + ovrOf(c), 0) / all.length)}`;
  lineMsgT = 2400;
}

