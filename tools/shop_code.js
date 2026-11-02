// ── the shop ───────────────────────────────────────────────────────────────
let shopSel = 'gold';

// a foil pack: a tall wrapper with a batter's silhouette behind the name
function drawPackArt(x, y, w, h, key, on, t){
  const Pk = PACKS[key];
  const c1 = mix(Pk.col, '#000000', .36), c2 = Pk.col, c3 = mix(Pk.col2, '#ffffff', .25);
  R(x - 1, y - 1, w + 2, h + 2, '#05070d');
  for (let i = 0; i < h; i++){                              // the foil gradient
    const f = i / h;
    R(x, y + i, w, 1, mix(mix(c3, c2, clamp(f * 1.7, 0, 1)), c1, clamp((f - .45) * 1.8, 0, 1)));
  }
  for (let i = 0; i < w; i += 3) R(x + i, y, 2, 4, mix(c3, '#ffffff', .4));     // the crimped top
  R(x, y + 4, w, 1, mix(c1, '#000000', .3));
  g.save(); g.beginPath(); g.rect(x + 2, y + 6, w - 4, h - 8); g.clip();          // a batter in silhouette
  const sil = sprite('SIL' + key, () => buildPlayer({
      crouch:0, lean:-1, hip:[54,56], chest:[55,34], neck:[55,27], head:[56,16],
      nSh:[50,31], fSh:[59,30], nEl:[46,39], nHa:[44,26], fEl:[49,41], fHa:[46,28],
      nKn:[48,76], nAn:[45,99], fKn:[62,75], fAn:[66,99], batA:-100, helmet:1 },
      { skin:'#2a3040', hair:'#2a3040', beard:0, bulk:1 },
      mix(Pk.col, '#000000', .55), mix(Pk.col, '#000000', .55), {}));
  const k = (h * .62) / RH;
  g.globalAlpha = .55;
  g.drawImage(sil, Math.round(x + w / 2 - 56 * k), Math.round(y + h * .10), Math.round(RW * k), Math.round(RH * k));
  g.globalAlpha = 1;
  for (let i = 0; i < h; i++){                              // a diagonal shine that drifts
    const sx = x + ((i * 1.5 + t / 40) % (w + h)) - h * .5;
    if (sx > x + 2 && sx < x + w - 3) R(sx, y + i, 3, 1, 'rgba(255,255,255,.16)');
  }
  g.restore();
  const ny = y + h - 30;
  R(x + 2, ny, w - 4, 20, 'rgba(7,11,20,.8)');
  text(Pk.n.toUpperCase(), x + w / 2, ny + 3, c3, 8, 'center');
  text('PACK', x + w / 2, ny + 12, c3, 7, 'center');
  g.strokeStyle = on ? '#ffffff' : mix(Pk.col, '#000000', .2); g.lineWidth = 1; g.strokeRect(x + .5, y + .5, w - 1, h - 1);
}

function drawShop(){
  btns = [];
  uiBg();
  // ── the bar across the top: where you are, what you can reach, what you have ──
  R(0, 0, W, 24, UI.blueDD); R(0, 24, W, 2, '#ffffff');
  button(6, 4, 44, 16, 'BACK', () => menu = 'title', '#1a2030', '#fff', 7);
  ptitle('SHOP', 58, 6, 11);
  coinText(G.coins, W - 8, 8, 9, UI.yellow, 'right');
  button(W - 188, 4, 62, 16, 'MY CARDS', () => menu = 'cards', '#1a2030', '#fff', 7);
  button(W - 252, 4, 60, 16, 'TRADE 5→1', () => { menu = 'trade'; tradeSel = []; }, '#1a2030', '#fff', 7);

  // ── the free daily pack: one clear strip ──
  const left = (G.freeAt || 0) - Date.now(), ready = left <= 0;
  uiBox(8, 31, W - 16, 24, ready ? '#1d6b3a' : UI.blueDD);
  ptitle('FREE DAILY PACK', 16, 36, 8, ready ? '#ffffff' : UI.ice, 'left');
  if (ready){
    text('a free bronze pack is waiting for you', 118, 38, '#c8ffd8', 7);
    button(W - 98, 34, 84, 18, 'OPEN FREE', freePack, '#2f6fe0', '#fff', 8);
  } else {
    const hrs = Math.floor(left / 3600000), mins = Math.floor(left % 3600000 / 60000);
    text(`next one in ${hrs}h ${String(mins).padStart(2, '0')}m`, 118, 38, UI.ice, 7);
    const fw = 90, fx = W - fw - 16;
    R(fx, 41, fw, 6, UI.navy); R(fx, 41, Math.round(fw * clamp(1 - left / 86400000, 0, 1)), 6, UI.yellow);
  }

  // ── the four packs, each with its price on it ──
  const keys = Object.keys(PACKS), gap = 6, pw = Math.floor((W - 16 - gap * 3) / 4), ph = 92, py = 60;
  keys.forEach((k, i) => {
    const x = 8 + i * (pw + gap), on = shopSel === k, Pk = PACKS[k];
    const lift = on ? -2 + Math.sin(frame / 14) * 1.2 : 0;
    uiBox(x, py + lift, pw, ph, on ? UI.blueD : UI.blueDD);
    if (on){ R(x + 2, py + lift + 2, pw - 4, 2, UI.yellow); }
    drawPackArt(x + 6, py + lift + 8, pw - 12, ph - 30, k, on, frame);
    coinText(Pk.price, x + pw / 2, py + lift + ph - 17, 9, on ? UI.yellow : '#ffffff', 'center');
    text('3 cards', x + pw / 2, py + lift + ph - 7, UI.ice, 6, 'center');
    btns.push({ x, y:py - 2, w:pw, h:ph + 4, fn: () => shopSel = k });
    if (on){ R(x + pw / 2 - 4, py - 7 + Math.sin(frame / 10) * 1.5, 8, 2, UI.yellow); R(x + pw / 2 - 2, py - 5 + Math.sin(frame / 10) * 1.5, 4, 2, UI.yellow); }
  });

  // ── what is in the selected pack: the odds, as six coloured chips ──
  const P3 = PACKS[shopSel], iy = py + ph + 6;
  uiBox(8, iy, W - 16, 38);
  ptitle(`${P3.n.toUpperCase()} PACK ODDS`, 16, iy + 5, 7, P3.col2, 'left');
  text('each card is rated 60-120, the colour is its tier', W - 16, iy + 6, UI.ice, 6, 'right');
  const cw6 = Math.floor((W - 16 - 16 - 5 * 4) / 6);
  P3.p.forEach((pp, ti) => {
    const x = 16 + ti * (cw6 + 4), T = TIERS[ti];
    R(x, iy + 16, cw6, 17, UI.navy); R(x, iy + 16, cw6, 3, T.col);
    text(`${Math.max(pp * 100 < 1 ? Math.round(pp * 1000) / 10 : Math.round(pp * 100), 0)}%`, x + cw6 / 2, iy + 22, '#ffffff', 7, 'center');
    text(TIER_LABEL[ti].slice(0, 5), x + cw6 / 2, iy + 29 - 1, T.col, 5, 'center');
  });

  // ── buy one, five or ten: always the whole row, and it says why a button is off ──
  const by = iy + 44, bw3 = Math.floor((W - 16 - 8) / 3);
  BULK.forEach(([n, mult], i) => {
    const cost = Math.round(P3.price * mult * n), can = G.coins >= cost, x = 8 + i * (bw3 + 4);
    button(x, by, bw3, 22, `BUY ${n}  ·  ${cost.toLocaleString()}`, () => buyPack(shopSel, n), can ? '#2f6fe0' : '#161b26', '#fff', 8);
    if (mult < 1) { R(x + bw3 - 30, by - 4, 30, 9, UI.green); text(`SAVE ${Math.round((1 - mult) * 100)}%`, x + bw3 - 15, by - 3, '#ffffff', 5, 'center'); }
    if (!can) text(`need ${(cost - G.coins).toLocaleString()} more`, x + bw3 / 2, by + 24, '#ffd2ce', 6, 'center');
    else text(`${n * 3} cards`, x + bw3 / 2, by + 24, UI.ice, 6, 'center');
  });
}

