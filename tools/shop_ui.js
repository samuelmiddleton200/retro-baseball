// ── shop pictures: the pack art, the tearing, the spinning card backs ──────────────────────────────
const SH = {};
function shopImg(n){ let im = SH[n]; if (!im){ im = SH[n] = new Image(); im.onload = () => { im._ok = true; }; im.src = SRC('assets/shop/' + n + '.png'); } return im; }
const imgOk = im => !!(im && im._ok && im.naturalWidth);
TIER_KEYS.forEach(t => { shopImg('p_' + t); for (let k = 0; k < 7; k++) shopImg(`t_${t}_${k}`); });
for (let k = 0; k < 7; k++) shopImg('s' + k);
// a picture standing on a line (cx, bottom) at scale s
function spriteAt(n, cx, bottom, s, alpha){
  const im = shopImg(n); if (!imgOk(im)) return null;
  const w = im.naturalWidth * s, h = im.naturalHeight * s;
  g.save(); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; if (alpha != null) g.globalAlpha = alpha;
  g.drawImage(im, cx - w / 2, bottom - h, w, h); g.restore(); return { w, h };
}
function spriteC(n, cx, cy, s, alpha){
  const im = shopImg(n); if (!imgOk(im)) return null;
  const w = im.naturalWidth * s, h = im.naturalHeight * s;
  g.save(); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; if (alpha != null) g.globalAlpha = alpha;
  g.drawImage(im, cx - w / 2, cy - h / 2, w, h); g.restore(); return { w, h };
}
const tornCv = document.createElement('canvas');
// the part of the wrapper that has been ripped so far, from fraction a to b of its width: the torn picture shows through a soft mask over the sealed one
function drawTorn(tier, cx, bottom, s, a, b){
  const im = shopImg(`t_${tier}_3`); if (!imgOk(im) || b - a < .02) return;
  const w = im.naturalWidth * s, h = im.naturalHeight * s, K = 2;
  tornCv.width = Math.ceil(w * K); tornCv.height = Math.ceil(h * K);
  const o = tornCv.getContext('2d'); o.clearRect(0, 0, tornCv.width, tornCv.height);
  o.imageSmoothingEnabled = true; o.drawImage(im, 0, 0, tornCv.width, tornCv.height);
  o.globalCompositeOperation = 'destination-in';
  const f = .06, gx = o.createLinearGradient(0, 0, tornCv.width, 0);
  if (a <= .02) gx.addColorStop(0, 'rgba(0,0,0,1)'); else { gx.addColorStop(Math.max(0, a - f), 'rgba(0,0,0,0)'); gx.addColorStop(a, 'rgba(0,0,0,1)'); }
  if (b >= .98) gx.addColorStop(1, 'rgba(0,0,0,1)'); else { gx.addColorStop(b, 'rgba(0,0,0,1)'); gx.addColorStop(Math.min(1, b + f), 'rgba(0,0,0,0)'); }
  o.fillStyle = gx; o.fillRect(0, 0, tornCv.width, tornCv.height);
  const gy = o.createLinearGradient(0, 0, 0, tornCv.height); gy.addColorStop(0, 'rgba(0,0,0,1)'); gy.addColorStop(.36, 'rgba(0,0,0,1)'); gy.addColorStop(.52, 'rgba(0,0,0,0)');
  o.fillStyle = gy; o.fillRect(0, 0, tornCv.width, tornCv.height);
  g.save(); g.imageSmoothingEnabled = true; g.drawImage(tornCv, cx - w / 2, bottom - h, w, h); g.restore();
}

// ── opening: tear the pack, the cards spin face down together, each turns over on its last turn ──
const T0 = 560;                                         // one full turn of a card, in ms
let OPEN = null;
const PK_S = .78, PK_CX = () => W / 2, PK_BOTTOM = 206;
const packBox = () => ({ x: PK_CX() - 161 * PK_S / 2, w: 161 * PK_S, top: PK_BOTTOM - 201 * PK_S, bottom: PK_BOTTOM });
function startOpen(o){
  OPEN = Object.assign({ phase:'pack', bi:0, t:0, ph0:0, revealed:[], newIds:new Set(), tr:{ a:null, b:null }, shake:0, sold:false, sellArmed:false }, o);
  if (o.kind !== 'pack') OPEN.phase = 'ready';
  menu = 'open';
}
function startSpin(){
  const O = OPEN, B = O.batches[O.bi];
  O.sp = B.cards.map(c => { const R = clamp(Math.round(3 + (ovrOf(c) - 60) / 10), 3, 9); return { c, ti:tierIdx(c), R, dur:R * T0, t:0, landed:false, flash:0 }; });
  O.phase = 'spin'; O.ph0 = 0;
}
function landCard(s){
  const O = OPEN, c = s.c; s.landed = true; s.flash = 700;
  if (!O.pre) G.cards.push(c);
  O.revealed.push(c); G.seen = G.seen || {};
  if (!O.pre && !G.seen[c.name]) O.newIds.add(c.id);
  G.seen[c.name] = 1;
  if (s.ti >= 4) O.shake = 520;
  save();
}
function openTick(dt){
  const O = OPEN; if (!O) return;
  O.t += dt; O.ph0 += dt; if (O.shake > 0) O.shake -= dt;
  if (O.phase === 'autotear'){
    const f = clamp(O.ph0 / 360, 0, 1);
    O.tr.a = O.tr.a0 * (1 - f); O.tr.b = O.tr.b0 + (1 - O.tr.b0) * f;
    if (f >= 1){ O.phase = 'burst'; O.ph0 = 0; }
  } else if (O.phase === 'burst'){ if (O.ph0 > 560) startSpin(); }
  else if (O.phase === 'ready'){ if (O.ph0 > 450) startSpin(); }
  else if (O.phase === 'spin'){
    let all = true;
    O.sp.forEach(s => { s.t += dt; if (!s.landed && s.t >= s.dur) landCard(s); if (s.landed) s.flash -= dt; else all = false; });
    if (all){ O.phase = 'hold'; O.ph0 = 0; }
  }
}
function openAdvance(){
  const O = OPEN;
  if (O.bi + 1 < O.batches.length){ O.bi++; O.sp = null; O.tr = { a:.5, b:.5, a0:.5, b0:.5 }; O.phase = 'autotear'; O.ph0 = 0; }
  else { O.phase = 'done'; O.ph0 = 0; }
}
function openLeave(){
  const O = OPEN; OPEN = null;
  if (O.from === 'bench'){ menu = 'cards'; colFilter = 'bench'; }
  else if (O.from === 'trade'){ menu = 'trade'; }
  else if (O.from === 'fuse'){ menu = 'shop'; shopTab = 'fuse'; }
  else { menu = 'shop'; if (shopTab === 'featured' && !O.free) shopTab = 'packs'; }
}
// a finger on the pack: it tears wherever the finger goes (from the left edge to the middle tears only that much); the whole way across opens it
function openPointer(kind, p){
  const O = OPEN; if (!O || O.phase !== 'pack') return false;
  const b = packBox(), fx = clamp((p.x - b.x) / b.w, 0, 1);
  if (kind === 'down'){
    if (p.x < b.x - 26 || p.x > b.x + b.w + 26 || p.y < b.top - 26 || p.y > b.bottom + 6) return false;
    O.drag = true; O.dragStart = fx;
    if (O.tr.a == null){ O.tr.a = fx; O.tr.b = fx; }
    else { if (fx < O.tr.a - .12 || fx > O.tr.b + .12) { /* a new stroke further along keeps what is already torn */ } }
    return true;
  }
  if (!O.drag) return false;
  if (p.y > b.top + (b.bottom - b.top) * .62) return true;                // the finger has wandered off the top of the pack
  if (O.tr.a == null){ O.tr.a = fx; O.tr.b = fx; }
  O.tr.a = Math.min(O.tr.a, fx); O.tr.b = Math.max(O.tr.b, fx);
  if (O.tr.a <= .07 && O.tr.b >= .93){ O.phase = 'burst'; O.ph0 = 0; O.drag = false; O.tr.a = 0; O.tr.b = 1; }
  return true;
}

function drawSpinCard(s, cx, cy, k){
  const O = OPEN, c = s.c, R = s.R, cwR = 100 * k, chR = 140 * k, T = TIERS[s.ti].col;
  const cl = (R - 1) * T0, u = clamp((s.t - cl) / T0, 0, 1);
  const h = s.t < cl ? 2 * s.t / T0 : 2 * R - 2 + (1 - Math.pow(1 - u, 3));               // half turns so far; the last half turn is slow and shows the front
  const e = h - (2 * R - 2);                                                          // 0..1 inside the last half turn
  const rgb = s.ti >= 5 ? '255,77,77' : s.ti >= 4 ? '255,210,63' : s.ti >= 3 ? '178,107,255' : s.ti >= 2 ? '74,163,255' : '255,255,255';
  if (!s.landed && e < .5){
    const frac = h - Math.floor(h), idx = clamp(Math.round(frac * 6), 0, 6);
    spriteC('s' + idx, cx, cy, k);
    return;
  }
  // the front turns into view, with light behind it
  const sx = s.landed ? 1 : Math.abs(Math.cos(Math.PI * e));
  const fl = s.landed ? clamp(s.flash / 700, 0, 1) : 0, grow = s.landed ? 1 : (e - .5) * 2;
  const rays = 14, rr = (chR * (.75 + .5 * (s.ti + 1) / 6)) * (.5 + .5 * grow), spin = O.t / 900;
  g.save(); g.beginPath(); g.rect(0, 0, W, H); g.clip();
  for (let r = 0; r < rays; r++){
    const a = r / rays * Math.PI * 2 + spin;
    g.fillStyle = `rgba(${rgb},${(.10 + .08 * s.ti / 5) * grow * (.6 + .4 * fl)})`;
    g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(a) * rr * 1.6, cy + Math.sin(a) * rr * 1.6); g.lineTo(cx + Math.cos(a + .11) * rr * 1.6, cy + Math.sin(a + .11) * rr * 1.6); g.fill();
  }
  const hg = g.createRadialGradient(cx, cy, 4, cx, cy, rr); hg.addColorStop(0, `rgba(${rgb},${.45 * grow})`); hg.addColorStop(1, `rgba(${rgb},0)`);
  g.fillStyle = hg; g.fillRect(cx - rr, cy - rr, rr * 2, rr * 2);
  g.restore();
  g.save(); g.translate(cx, 0); g.scale(Math.max(.03, sx), 1); g.translate(-cx, 0);
  drawCard(cx - cwR / 2, cy - chR / 2, c, cwR, chR, O.t);
  if (fl > 0) R2(cx - cwR / 2 - 2, cy - chR / 2 - 2, cwR + 4, chR + 4, `rgba(255,255,255,${fl * .5})`);
  g.restore();
  if (s.landed){
    if (s.ti >= 2) ptitle(TIER_LABEL[s.ti], cx, cy - chR / 2 - 11, s.ti >= 4 ? 8 : 7, T);
    if (O.newIds.has(c.id)){ R2(cx + cwR / 2 - 20, cy - chR / 2 - 11, 22, 9, UI.red); text('NEW', cx + cwR / 2 - 9, cy - chR / 2 - 10, '#ffffff', 5, 'center'); }
  }
}
const R2 = (x, y, w, h, c) => R(x, y, w, h, c);

function drawOpen(){
  btns = [];
  const O = OPEN, B = O.batches[O.bi] || O.batches[0], tier = B.tier || 'bronze', P2 = PACKS[tier] || PACKS.bronze;
  R(0, 0, W, H, UI.navy);
  const pool = g.createRadialGradient(W / 2, 118, 8, W / 2, 118, 230); pool.addColorStop(0, 'rgba(80,120,240,.55)'); pool.addColorStop(1, 'rgba(15,31,85,0)');
  g.fillStyle = pool; g.fillRect(0, 0, W, H);
  g.save();
  if (O.shake > 0){ const m = 3.2 * clamp(O.shake / 520, 0, 1); g.translate((Math.random() - .5) * m * 2, (Math.random() - .5) * m * 2); }
  const title = O.kind === 'pack' ? (O.batches.length > 1 ? `PACK ${O.bi + 1} OF ${O.batches.length}` : `${P2.n.toUpperCase()} PACK`) : O.kind === 'fuse' ? 'FUSED' : 'TRADE IN';
  if (O.phase !== 'done') ptitle(title, W / 2, 6, 11, O.kind === 'pack' ? P2.col2 : '#dcc2ff');
  const ph = O.phase;
  if (ph === 'pack'){
    const b = packBox(), pulse = .6 + .4 * Math.sin(O.t / 240);
    text('DRAG ACROSS THE TOP TO TEAR IT OPEN', W / 2, 26, `rgba(255,255,255,${.7 + .3 * pulse})`, 8, 'center', W - 20);
    const bob = O.tr.a == null ? Math.sin(O.t / 320) * 2 : 0;
    g.save(); g.translate(0, bob);
    spriteAt(`t_${tier}_0`, PK_CX(), PK_BOTTOM, PK_S);
    if (O.tr.a != null) drawTorn(tier, PK_CX(), PK_BOTTOM, PK_S, O.tr.a, O.tr.b);
    g.restore();
    if (O.tr.a == null){                                                         // a hint: a dashed line along the top, and an arrow
      g.fillStyle = 'rgba(255,255,255,.8)';
      for (let x = b.x; x < b.x + b.w - 6; x += 10) g.fillRect(x + ((O.t / 40) % 10), b.top + 24, 5, 1.5);
      text('>>', b.x - 14, b.top + 20, '#ffffff', 8, 'center');
    }
  } else if (ph === 'autotear'){
    spriteAt(`t_${tier}_0`, PK_CX(), PK_BOTTOM, PK_S); drawTorn(tier, PK_CX(), PK_BOTTOM, PK_S, O.tr.a, O.tr.b);
  } else if (ph === 'burst'){
    const f = O.ph0 < 160 ? 4 : O.ph0 < 320 ? 5 : 6;
    spriteAt(`t_${tier}_${f}`, PK_CX(), PK_BOTTOM + (f === 6 ? 4 : 0), PK_S);
  } else if (ph === 'ready'){
    text(O.kind === 'fuse' ? 'A NEW PLAYER' : 'WHAT DID YOU GET?', W / 2, 90, '#ffffff', 8, 'center');
  } else if (ph === 'spin' || ph === 'hold'){
    const n = O.sp.length, slotW = (W - 16) / n, k = Math.min(n === 1 ? .95 : .9, (W - 16) / (n * 200)), cy = 124;
    O.sp.forEach((s, i) => drawSpinCard(s, 8 + slotW * (i + .5), cy, k));
    if (ph === 'hold'){
      const pulse = .6 + .4 * Math.sin(O.t / 240);
      text('TAP TO CONTINUE', W / 2, H - 20, `rgba(255,255,255,${.7 + .3 * pulse})`, 8, 'center');
      if (O.ph0 > 380) btns.push({ x:0, y:0, w:W, h:H, fn: openAdvance });
    }
  } else if (ph === 'done'){
    drawOpenDone(O);
  }
  g.restore();
}
function drawOpenDone(O){
  const cx = W / 2, cards = O.revealed, n = cards.length;
  const top = cards.reduce((m, c) => Math.max(m, tierIdx(c)), 0);
  const ttl = top >= 4 ? `${TIER_LABEL[top]} PULL!` : O.kind === 'pack' ? 'ALL YOURS!' : O.kind === 'fuse' ? 'NEW PLAYER!' : 'YOUR NEW CARD';
  ptitle(ttl, cx, 6, 13, top >= 4 ? TIERS[top].col : UI.yellow);
  if (O.bonus) text(O.bonus, cx, 23, '#c8ffd8', 6, 'center', W - 20);
  const gap = 5, availH = H - 34 - 34;
  let cw = 24; for (let t = 74; t >= 24; t -= 2){ const pr = Math.min(n, Math.floor((W - 20) / (t + gap))); if (pr > 0 && Math.ceil(n / pr) * (Math.round(t * 1.4) + gap) <= availH){ cw = t; break; } }
  const ch = Math.round(cw * 1.4), per = Math.min(n, Math.floor((W - 20) / (cw + gap))), rows = Math.ceil(n / per);
  const x0 = cx - (per * (cw + gap) - gap) / 2, y0 = O.bonus ? 34 : 30;
  cards.forEach((c, i) => {
    const x = x0 + (i % per) * (cw + gap), y = y0 + Math.floor(i / per) * (ch + gap);
    drawCard(x, y, c, cw, ch, O.t);
    if (O.newIds.has(c.id)){ R(x - 1, y + 3, 18, 8, UI.red); text('NEW', x + 8, y + 4, '#ffffff', 5, 'center'); }
  });
  const by = H - 26, bn = 4, bw = Math.floor((W - 16 - (bn - 1) * 4) / bn);
  const sellable = cards.filter(c => G.cards.includes(c) && !inUse(c.id)), sv = sellable.reduce((s, c) => s + sellPrice(c), 0);
  if (O.kind === 'pack' || O.kind === 'trade'){
    button(8, by, bw, 20, O.sellArmed ? `SURE? +${fmt(sv)}` : sv ? `SELL ALL ${fmt(sv)}` : 'SELL ALL', () => {
      if (!sv) return;
      if (!O.sellArmed){ O.sellArmed = true; return; }
      G.coins += sv; const ids = new Set(sellable.map(c => c.id)); G.cards = G.cards.filter(c => !ids.has(c.id)); O.revealed = O.revealed.filter(c => !ids.has(c.id)); O.sellArmed = false; save();
    }, O.sellArmed ? '#4a2030' : sv ? '#1a2030' : '#161b26', sv ? '#fff' : '#8896b3', 6);
  } else button(8, by, bw, 20, 'MY CARDS', () => { OPEN = null; menu = 'cards'; }, '#1a2030', '#fff', 7);
  button(8 + (bw + 4), by, bw, 20, 'FUSE', () => { OPEN = null; menu = 'shop'; shopTab = 'fuse'; fuseSel = []; }, '#1a2030', '#fff', 7);
  const again = O.again, cost = againCost(again), can = again && G.coins >= cost;
  if (again) button(8 + 2 * (bw + 4), by, bw, 20, can ? `AGAIN ${fmt(cost)}` : 'NO COINS', () => { if (can) openAgain(again); }, can ? '#2f6fe0' : '#161b26', '#fff', 6);
  else button(8 + 2 * (bw + 4), by, bw, 20, 'SHOP', () => { OPEN = null; menu = 'shop'; }, '#1a2030', '#fff', 7);
  button(8 + 3 * (bw + 4), by, bw, 20, 'DONE', openLeave, '#2a6a3a', '#fff', 7);
}

// ── the shop: a row of tabs ────────────────────────────────────────────────
let shopTab = 'featured', shopMsg = '', shopMsgT = 0, fuseMode = 'face', fuseSel = [], fuseScroll = 0, fuseMax = 0, fuseRect = null, fuseRows = [];
function shopHeader(){
  R(0, 0, W, 21, UI.blueDD); R(0, 21, W, 2, '#ffffff');
  button(6, 3, 44, 15, 'BACK', () => menu = 'title', '#1a2030', '#fff', 7);
  ptitle('SHOP', 58, 5, 10, '#ffffff', 'left');
  coinText(G.coins, W - 8, 6, 9, UI.yellow, 'right');
  const tabs = [['featured', 'FEATURED'], ['packs', 'PACKS'], ['position', 'POSITION'], ['fuse', 'FUSE'], ['trade', 'TRADE-UP'], ['cards', 'MY CARDS']];
  const tw = Math.floor((W - 16 - (tabs.length - 1) * 3) / tabs.length);
  tabs.forEach(([k, l], i) => {
    const x = 8 + i * (tw + 3), on = shopTab === k;
    if (on) R(x, 26, tw, 14, UI.yellow); else uiBox(x, 26, tw, 14);
    text(l, x + tw / 2, 29, on ? '#241a00' : '#ffffff', 6, 'center', tw - 3);
    btns.push({ x, y:26, w:tw, h:14, fn: () => { if (k === 'trade'){ menu = 'trade'; tradeSel = []; } else if (k === 'cards') menu = 'cards'; else { shopTab = k; fuseSel = []; fuseScroll = 0; } } });
  });
  if (shopMsgT > 0){ shopMsgT -= 16; const w = 200; R(W / 2 - w / 2, 44, w, 14, 'rgba(15,31,85,.95)'); text(shopMsg, W / 2, 47, UI.yellow, 7, 'center', w - 6); }
}
const hoursLeftToday = () => { const n = new Date(), m = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1); return m - n; };
const hm = ms => `${Math.floor(ms / 3600000)}H ${String(Math.floor(ms % 3600000 / 60000)).padStart(2, '0')}M`;

function drawFeatured(){
  const y0 = 44, gap = 6, lw = Math.floor((W - 16 - gap) * .5), rw = W - 16 - gap - lw, ph = 66;
  // the free daily pack
  const left = (G.freeAt || 0) - Date.now(), ready = left <= 0;
  uiBox(8, y0, lw, ph, ready ? '#1d6b3a' : UI.blueDD);
  ptitle('FREE DAILY PACK', 14, y0 + 5, 8, '#ffffff', 'left');
  text('A BRONZE PACK WITH 5 CARDS', 70, y0 + 17, UI.ice, 5.5, 'left', lw - 76);
  spriteAt('p_bronze', 38, y0 + ph - 5, 44 / 237);
  if (ready) button(70, y0 + 28, lw - 70 - 6, 22, 'CLAIM NOW', freePack, '#2f6fe0', '#fff', 8);
  else {
    text(`NEXT ONE IN ${hm(left)}`, 70, y0 + 30, UI.ice, 6, 'left', lw - 76);
    const fw = lw - 82; R(70, y0 + 42, fw, 6, UI.navy); R(70, y0 + 42, Math.round(fw * clamp(1 - left / 86400000, 0, 1)), 6, UI.yellow);
  }
  // this week: the streak
  const sx = 8 + lw + gap; uiBox(sx, y0, rw, ph);
  ptitle('THIS WEEK', sx + 6, y0 + 5, 8, '#ffffff', 'left');
  const si = streakInfo();
  text('FREE GOLD PACK ON DAY 7', sx + 6, y0 + 17, UI.ice, 5.5, 'left', rw - 10);
  const bw = Math.floor((rw - 12 - 6 * 3) / 7);
  for (let d = 1; d <= 7; d++){
    const x = sx + 6 + (d - 1) * (bw + 3), y = y0 + 27, done = d <= si.run, nxt = !si.claimedToday && d === si.next;
    R(x, y, bw, 33, done ? '#2a3a8a' : UI.navy); if (nxt){ R(x, y, bw, 1, UI.yellow); R(x, y + 32, bw, 1, UI.yellow); R(x, y, 1, 33, UI.yellow); R(x + bw - 1, y, 1, 33, UI.yellow); }
    text('DAY ' + d, x + bw / 2, y + 3, done || nxt ? '#fff' : UI.ice, 5, 'center');
    text(d === 7 ? 'GOLD' : '+' + STREAK_COINS[d - 1], x + bw / 2, y + 13, UI.yellow, d === 7 ? 5.5 : 5.5, 'center', bw - 2);
    if (done) text('GOT', x + bw / 2, y + 23, '#7fd38f', 5, 'center');
  }
  // hot deals
  const y1 = y0 + ph + 5, hh = H - 4 - y1; uiBox(8, y1, W - 16, hh);
  ptitle('HOT DEALS', 16, y1 + 5, 8, '#ffffff', 'left');
  text(`NEW DEALS IN ${hm(hoursLeftToday())}`, W - 16, y1 + 7, UI.ice, 5.5, 'right');
  const D = dealsToday(), sw = Math.floor((W - 16 - 12) / 3), cw = clamp(Math.round(sw * .38), 34, 58), chh = Math.round(cw * 1.4);
  D.cards.forEach((c, i) => {
    const x = 14 + i * (sw + 2), y = y1 + 20, sold = D.sold[i], ov = ovrOf(c), price = dealPrice(c), full = Math.round(valueOf(ov)), off = ov >= 100 ? 10 : 20;
    drawCard(x, y, c, cw, chh, frame); if (sold) R(x, y, cw, chh, 'rgba(8,12,30,.65)');
    const ix = x + cw + 6, iw = sw - cw - 10;
    const fs = `${full.toLocaleString()}`; text(fs, ix, y + 2, '#ff9a8a', 6); R(ix, y + 5, Math.min(iw, fs.length * 6 * .62 * 1.0 + 1), 1, '#ff9a8a');
    coinText(price, ix, y + 13, 8, sold ? '#8896b3' : UI.yellow);
    R(ix, y + 26, 32, 9, UI.red); text(`${off}% OFF`, ix + 16, y + 27, '#ffffff', 5, 'center');
    const can = G.coins >= price && !sold;
    button(ix, y + 40, Math.min(iw, 62), 16, sold ? 'SOLD' : 'BUY', () => buyDeal(i), can ? '#2f6fe0' : '#161b26', '#fff', 7);
    if (!sold && !can) text(`NEED ${(price - G.coins).toLocaleString()}`, ix, y + 58, '#ffd2ce', 5, 'left', iw);
  });
}
function drawPacksTab(){
  const gap = 6, y0 = 44, pw = Math.floor((W - 16 - gap * 3) / 4), th = 118;
  TIER_KEYS.forEach((k, i) => {
    const x = 8 + i * (pw + gap), Pk = PACKS[k];
    uiBox(x, y0, pw, th);
    spriteAt('p_' + k, x + pw / 2, y0 + th - 8, Math.min(100 / 237, (pw - 14) / 190));
    coinText(Pk.price, x + pw / 2, y0 + th + 5, 8, '#ffffff', 'center');
    BULK.forEach(([n, mult], j) => {
      const cost = Math.round(Pk.price * mult * n), can = G.coins >= cost, by = y0 + th + 18 + j * 17;
      button(x, by, pw, 15, n === 1 ? 'BUY 1' : `BUY ${n}  ${cost.toLocaleString()}  -${Math.round((1 - mult) * 100)}%`, () => buyPack(k, n), can ? '#2f6fe0' : '#161b26', '#fff', n === 1 ? 6 : 5.5);
    });
  });
}
function drawPositionTab(){
  const gap = 6, y0 = 44, pw = Math.floor((W - 16 - gap * 3) / 4), th = 176;
  POSGROUPS.forEach((grp, i) => {
    const x = 8 + i * (pw + gap), today = grp.k === 'today';
    uiBox(x, y0, pw, th, today ? '#1b3a96' : UI.blueDD); if (today) R(x + 2, y0 + 2, pw - 4, 1, UI.yellow);
    ptitle(grp.n, x + pw / 2, y0 + 6, 7.5, '#ffffff'); text(grp.sub, x + pw / 2, y0 + 18, UI.ice, 5, 'center', pw - 4);
    const sb = y0 + 24 + 82, s = Math.min(78 / 237, (pw - 12) / 171), sp = spriteAt('p_gold', x + pw / 2, sb, s);
    if (today && sp){ const px = x + pw / 2 - sp.w * .32, py = sb - sp.h * .70, pw2 = sp.w * .64, ph2 = sp.h * .30;
      R(px, py, pw2, ph2, '#fff'); R(px + 1, py + 1, pw2 - 2, ph2 - 2, '#101a4a'); ptitle(todayPos(), px + pw2 / 2, py + ph2 * .22, Math.round(ph2 * .55), '#fff3d0'); }
    POSTIERS.forEach((t, j) => {
      const cost = posPackPrice(grp, t), can = G.coins >= cost, by = y0 + 112 + j * 21;
      button(x + 3, by, pw - 6, 20, `${t.toUpperCase()}  ${cost.toLocaleString()}`, () => buyPosPack(grp.k, t), can ? '#2f6fe0' : '#161b26', '#fff', 6);
    });
  });
}
function drawFuseTab(){
  const y0 = 44, gap = 6, lw = Math.floor((W - 16 - gap) * .52), rx = 8 + lw + gap, rw = W - 8 - rx, ph = H - 4 - y0;
  uiBox(8, y0, lw, ph); uiBox(rx, y0, rw, ph);
  // the two ways to fuse
  [['face', 'SAME FACE +5'], ['pos', 'SAME POS +3']].forEach(([k, l], i) => {
    const bw = Math.floor((lw - 14) / 2), x = 11 + i * (bw + 3), on = fuseMode === k;
    if (on) R(x, y0 + 5, bw, 14, UI.yellow); else uiBox(x, y0 + 5, bw, 14);
    text(l, x + bw / 2, y0 + 8, on ? '#241a00' : '#ffffff', 6, 'center', bw - 2);
    btns.push({ x, y:y0 + 5, w:bw, h:14, fn: () => { fuseMode = k; fuseSel = []; fuseScroll = 0; } });
  });
  const cw = clamp(Math.floor((lw - 20 - 2 * 12) / 3), 34, 54), chh = Math.round(cw * 1.4), sy = y0 + 28;
  const a = cardById(fuseSel[0]), b = cardById(fuseSel[1]), ok = canFuse(a, b, fuseMode), x1 = 12, x2 = 12 + cw + 12, x3 = 12 + 2 * (cw + 12);
  [[a, x1], [b, x2]].forEach(([c, x]) => { if (c) drawCard(x, sy, c, cw, chh, frame); else { uiBox(x, sy, cw, chh, UI.navy); text('PICK', x + cw / 2, sy + chh / 2 - 3, UI.ice, 6, 'center'); } });
  text('+', x1 + cw + 6, sy + chh / 2 - 4, '#fff', 10, 'center'); text('=', x2 + cw + 6, sy + chh / 2 - 4, '#fff', 10, 'center');
  uiBox(x3, sy, cw, chh, UI.navy);
  if (a && b){ const r = fuseRating(a, b, fuseMode); ptitle(String(r), x3 + cw / 2, sy + chh / 2 - 12, 15, colOf(r)); text('NEW PLAYER', x3 + cw / 2, sy + chh / 2 + 8, UI.ice, 5, 'center', cw - 2); }
  else text('?', x3 + cw / 2, sy + chh / 2 - 8, UI.ice, 16, 'center');
  const note = a && b && inUse(a.id) && inUse(b.id) ? 'ONE OF THEM MUST BE ON THE BENCH' : `BOTH IN THE SAME RANGE${a ? ' (' + bandText(bandOf(ovrOf(a))) + ')' : ''}`;
  text(note, 8 + lw / 2, sy + chh + 7, a && b && inUse(a.id) && inUse(b.id) ? '#ffd2ce' : UI.ice, 5.5, 'center', lw - 8);
  button(12, y0 + ph - 26, lw - 8, 20, 'FUSE', () => {
    if (!ok) return; const nc = doFuse(a, b, fuseMode); fuseSel = []; if (nc) startOpen({ kind:'fuse', batches:[{ tier:null, cards:[nc] }], pre:true, from:'fuse' });
  }, ok ? '#2f6fe0' : '#161b26', '#fff', 8);
  // the list of what you could fuse
  ptitle('YOUR MATCHES', rx + 6, y0 + 5, 7.5, '#fff', 'left');
  fuseRows = [];
  const groups = fuseGroups(fuseMode), ly = y0 + 18, lh = ph - 22, RH = 11;
  const rows = []; groups.forEach(gr => { rows.push({ head:gr }); gr.list.forEach(c => rows.push({ c, gr })); });
  fuseMax = Math.max(0, rows.length * RH - lh); fuseScroll = clamp(fuseScroll, 0, fuseMax); fuseRect = { x:rx, y:ly, w:rw, h:lh };
  g.save(); g.beginPath(); g.rect(rx + 3, ly, rw - 6, lh); g.clip();
  if (!rows.length) text('NO PAIRS YET', rx + rw / 2, ly + 20, UI.ice, 6, 'center', rw - 8);
  rows.forEach((r, i) => {
    const y = ly + i * RH - fuseScroll; if (y < ly - RH || y > ly + lh) return;
    if (r.head){
      const gr = r.head, label = fuseMode === 'face' ? `FACE ${gr.k.split('|')[0].replace(/^[fx]/, '')}` : gr.k.split('|')[0].slice(1);
      R(rx + 4, y, rw - 8, RH - 1, '#223a8a'); text(`${label}  ${bandText(gr.band)}`, rx + 7, y + 2, UI.yellow, 5.5, 'left', rw - 14);
    } else {
      const c = r.c, sel = fuseSel.includes(c.id), key = a ? fuseKey(a, fuseMode) : null, dim = a && !sel && fuseKey(c, fuseMode) !== key;
      if (sel) R(rx + 4, y, rw - 8, RH - 1, 'rgba(255,210,63,.28)');
      textb(String(ovrOf(c)), rx + 8, y + 2, dim ? '#6c7aa8' : colOf(ovrOf(c)), 6);
      text(c.pos, rx + 26, y + 2, dim ? '#6c7aa8' : UI.ice, 5.5); text(c.name, rx + 44, y + 2, dim ? '#6c7aa8' : '#fff', 5.5, 'left', rw - 74);
      text('L' + (c.lvl || 0), rx + rw - 8, y + 2, dim ? '#6c7aa8' : UI.ice, 5, 'right');
      const vy = Math.max(y, ly), vh = Math.min(y + RH, ly + lh) - vy;
      if (vh > 4) fuseRows.push({ x:rx + 4, y:vy, w:rw - 8, h:vh, fn: () => {
        if (sel) fuseSel = fuseSel.filter(id => id !== c.id);
        else if (fuseSel.length === 1 && canFuseKey(cardById(fuseSel[0]), c)) fuseSel.push(c.id);
        else fuseSel = [c.id];
      } });
    }
  });
  g.restore();
}
const canFuseKey = (a, c) => a && a.id !== c.id && fuseKey(a, fuseMode) === fuseKey(c, fuseMode);
function drawShop(){
  btns = [];
  uiBg(); shopHeader();
  if (shopTab === 'featured') drawFeatured(); else if (shopTab === 'packs') drawPacksTab(); else if (shopTab === 'position') drawPositionTab(); else if (shopTab === 'fuse') drawFuseTab();
}
