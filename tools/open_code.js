function drawOpen(){
  btns = [];
  const P2 = PACKS[OPEN.kind] || TRADE_PACK, cx = W / 2, cy = 112, sp = OPEN.spin;
  // deep navy with a pool of light behind the action
  R(0, 0, W, H, UI.navy);
  const pool = g.createRadialGradient(cx, cy, 8, cx, cy, 190);
  pool.addColorStop(0, 'rgba(80,120,240,.55)'); pool.addColorStop(1, 'rgba(15,31,85,0)');
  g.fillStyle = pool; g.fillRect(0, 0, W, H);
  ptitle(`${P2.n.toUpperCase()}${OPEN.kind === 'trade' ? '' : ' PACK'}`, cx, 6, 11, P2.col2);
  if (!OPEN.done) text(`card ${Math.min(OPEN.i + 1, OPEN.cards.length)} of ${OPEN.cards.length}`, cx, 22, UI.ice, 7, 'center');

  // turning light rays behind the card; stronger for better pulls
  const rays = (strength, col) => {
    for (let r = 0; r < 12; r++){
      const a = r / 12 * Math.PI * 2 + OPEN.t / 1600;
      g.fillStyle = `rgba(${col},${.05 + strength * .09})`;
      g.beginPath(); g.moveTo(cx, cy);
      g.lineTo(cx + Math.cos(a) * 260, cy + Math.sin(a) * 260); g.lineTo(cx + Math.cos(a + .13) * 260, cy + Math.sin(a + .13) * 260); g.fill();
    }
  };

  // ── all done: every card from the pack on one screen ──
  if (OPEN.done){
    ptitle('ALL YOURS!', cx, 20, 14, UI.yellow);
    const n = OPEN.revealed.length, big = n <= 5, cw = big ? 54 : n <= 10 ? 40 : 28, ch = Math.round(cw * 1.4), gap = 5;
    const per = Math.min(n, Math.floor((W - 20) / (cw + gap))), rows = Math.ceil(n / per);
    const x0 = cx - (per * (cw + gap) - gap) / 2, y0 = 44;
    OPEN.revealed.forEach((c, i) => drawCard(x0 + (i % per) * (cw + gap), y0 + Math.floor(i / per) * (ch + gap), c, cw, ch, OPEN.t));
    const by = Math.min(H - 28, y0 + rows * (ch + gap) + 6);
    const again = OPEN.kind !== 'trade' && OPEN.n ? Math.round(PACKS[OPEN.kind].price * BULK.find(b => b[0] === OPEN.n)[1] * OPEN.n) : 0;
    const can = again > 0 && G.coins >= again;
    if (OPEN.kind === 'trade') button(cx - 52, by, 104, 20, 'TRADE MORE', () => { OPEN = null; menu = 'trade'; }, '#2f6fe0', '#fff', 8);
    else button(cx - 118, by, 112, 20, can ? `OPEN ANOTHER · ${fmt(again)}` : 'NOT ENOUGH COINS', () => { if (can){ const k = OPEN.kind, n = OPEN.n; buyPack(k, n); } }, can ? '#2f6fe0' : '#161b26', '#fff', 7);
    button(cx - 2 + 6, by, 56, 20, 'SHOP', () => { OPEN = null; menu = 'shop'; }, '#1a2030', '#fff', 8);
    button(cx + 66, by, 64, 20, 'MY CARDS', () => { OPEN = null; menu = 'cards'; }, '#1a2030', '#fff', 7);
    return;
  }

  // the cards already turned over, in a row along the bottom
  const shown = OPEN.revealed.slice(-10);
  shown.forEach((c, i) => { const w = 26, x = cx - (shown.length * 29) / 2 + i * 29; drawCard(x, H - 46, c, w, 36, OPEN.t); });

  const w = 76, h = 107;
  if (!sp){
    // the pack itself, waiting: tap to tear it open
    const bob = Math.sin(OPEN.t / 300) * 3;
    rays(.3, '255,255,255');
    if (OPEN.kind === 'trade' || OPEN.i > 0){
      // a face-down card
      uiBox(cx - w / 2, cy - h / 2 + bob, w, h, mix(UI.blueDD, P2.col, .35));
      g.fillStyle = P2.col2; g.beginPath(); g.arc(cx, cy + bob, 14, 0, 7); g.fill();
      g.fillStyle = UI.navy; g.fillRect(cx - 14, cy + bob - 1, 28, 2);
    } else drawPackArt(cx - w / 2, cy - h / 2 + bob, w, h, OPEN.kind, true, OPEN.t);
    const pulse = .6 + .4 * Math.sin(OPEN.t / 220);
    ptitle(OPEN.i === 0 && OPEN.kind !== 'trade' ? 'TAP TO OPEN' : 'TAP TO REVEAL', cx, cy + h / 2 + 8, 9, `rgba(255,255,255,${pulse})`);
    btns.push({ x: cx - w / 2, y: cy - h / 2, w, h, fn: revealNext });
    return;
  }

  // the spin: the card turns edge-on over and over, faster near the end
  const f = clamp(sp.t / sp.dur, 0, 1), eased = 1 - Math.pow(1 - f, 2.1);
  const ang = eased * sp.turns * Math.PI, sx = Math.abs(Math.cos(ang)), tc = TIERS[sp.ti].col;
  const rgb = sp.ti >= 5 ? '255,77,77' : sp.ti >= 4 ? '255,147,48' : sp.ti >= 3 ? '255,210,63' : '255,255,255';
  rays(sp.landed ? 1 : f * (sp.ti + 1) / 6, rgb);
  if (sp.ti >= 3){                                          // glow builds as the better cards spin
    const gl = f * (sp.ti - 2) / 3;
    for (let i = 6; i > 0; i--) R(cx - w / 2 - i * 2, cy - h / 2 - i * 2, w + i * 4, h + i * 4, `rgba(${rgb},${.05 * gl})`);
  }
  const cw = Math.max(2, Math.round(w * sx));
  if (sp.landed){
    drawCard(cx - w / 2, cy - h / 2, OPEN.cards[OPEN.i], w, h, OPEN.t);
    const fl = clamp(sp.flash / 420, 0, 1);
    if (fl > 0) R(cx - w / 2 - 4, cy - h / 2 - 4, w + 8, h + 8, `rgba(255,255,255,${fl * .55})`);
    if (sp.ti >= 2) ptitle(`${TIER_LABEL[sp.ti]} PULL!`, cx, cy - h / 2 - 18, sp.ti >= 4 ? 12 : 10, tc);
    if (sp.flash <= 0) ptitle('TAP', cx, cy + h / 2 + 8, 8, UI.ice);
    btns.push({ x:0, y:0, w:W, h:H, fn: () => { if (sp.flash < 260) sp.flash = -400; } });
  } else {
    const face = Math.cos(ang) > 0;                         // front or back of the card
    if (face){ g.save(); g.translate(cx, 0); g.scale(sx, 1); g.translate(-cx, 0);
      drawCard(cx - w / 2, cy - h / 2, OPEN.cards[OPEN.i], w, h, OPEN.t); g.restore(); }
    else { R(cx - cw / 2, cy - h / 2, cw, h, mix(UI.blueDD, tc, .45));
      g.strokeStyle = '#fff'; g.strokeRect(cx - cw / 2 + .5, cy - h / 2 + .5, cw - 1, h - 1); }
  }
}

