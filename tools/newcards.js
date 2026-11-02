// ── card art ───────────────────────────────────────────────────────────────
// Five things make a card read at a glance, like the reference: a metal frame that gets fancier with the tier, a
// head-and-shoulders portrait that is THIS player (his own face, hair and team colours), the big rating on a plate,
// a team badge, and four ratings in the colour of their own band.
const TIER_LABEL = ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC'];
const CARD_PAL = [
  { frame:'#a9b3c7', lite:'#eef2fa', dark:'#3a4356', top:'#6b7890', bot:'#232b3b' },
  { frame:'#52d67b', lite:'#c4f7d3', dark:'#1b5632', top:'#33995c', bot:'#0f2c1e' },
  { frame:'#4aa3ff', lite:'#cbe4ff', dark:'#17457d', top:'#2f78c8', bot:'#0e2240' },
  { frame:'#ffd23f', lite:'#fff2b0', dark:'#7a5a10', top:'#c99a22', bot:'#3a2a0a' },
  { frame:'#ff9330', lite:'#ffd2a0', dark:'#8a3f08', top:'#d9661a', bot:'#40190a' },
  { frame:'#ff4d4d', lite:'#ffc2b0', dark:'#7d1414', top:'#d83030', bot:'#3b0b0b' },
];
const tierIdx = c => clamp(Math.floor((ovrOf(c) - 60) / 10), 0, 5);
// which club's colours he wears: pack players come from all 30 teams, your own roster wears yours
const cardTeam = c => (c.tm != null && G.teams[c.tm]) ? G.teams[c.tm] : G.teams[G.team];

// the old hand-drawn portrait, kept as the fallback when WebGL is not there
function cardBustRig(c, team){
  const key = `BU${lookKey(c.look)}|${team.c1}${team.c2}|${isPitcher(c) ? 'P' : 'H'}`;
  return sprite(key, () => buildPlayer({
      crouch:0, lean:0,
      hip:[56,58], chest:[56,36], neck:[56,28], head:[56,17],
      nSh:[46,32], fSh:[66,32],
      nEl:[42,46], nHa:[44,52], fEl:[70,46], fHa:[68,52],
      nKn:[50,76], nAn:[48,99], fKn:[62,76], fAn:[64,99],
    }, c.look, team.c1, team.c2, { front:1 }));
}
const CARD_FRAME3D = { w: 4.6, h: 3.3, base: -3.3 };     // feet shown: head and shoulders
// the portrait: the same 3D player the game uses, framed head and shoulders, so a card and the field agree
function cardPortrait(c, team, px, py, pw, ph){
  g.imageSmoothingEnabled = false;
  const L = gxLook(c);
  const o = { kind:'field', skin:L.skin, hair:L.hair, ab:'', cap:team.c1, cap2:team.c2, shirt:team.c1, sleeve:team.c1, pants:'#eceef3', glove:0 };
  let cv = null;
  try { if (window.GL3D && GL3D.bake) cv = GL3D.bake('CB|' + lookKey(c.look) + team.c1 + team.c2, o, GL3D.poseReady(0), 0, 56, CARD_FRAME3D); } catch (e){ cv = null; }
  g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();
  if (cv){
    const sc = Math.max(pw / cv.width, ph / cv.height), dw = cv.width * sc, dh = cv.height * sc;
    g.drawImage(cv, 0, 0, cv.width, cv.height, Math.round(px + (pw - dw) / 2), Math.round(py + ph - dh), Math.round(dw), Math.round(dh));
  } else {
    const bust = cardBustRig(c, team), SRC = { x:39, y:2, w:34, h:36 }, sc = (pw / SRC.w) * 1.06;
    g.drawImage(bust, SRC.x, SRC.y, SRC.w, SRC.h, Math.round(px + pw / 2 - SRC.w * sc / 2), Math.round(py), Math.round(SRC.w * sc), Math.round(SRC.h * sc));
  }
  g.restore();
}

// the metal frame; every tier up adds something
function cardFrame(x, y, w, h, ti, t, k){
  const P = CARD_PAL[ti], F = Math.max(2, Math.round(3 * k));
  // glow that spills outside the card for the top three tiers
  if (ti >= 3){
    const rgb = ti === 3 ? '255,210,63' : ti === 4 ? '255,147,48' : '255,77,77';
    const pulse = .5 + .5 * Math.sin(t / 340);
    for (let i = 4; i > 0; i--) R(x - i, y - i, w + i * 2, h + i * 2, `rgba(${rgb},${(.05 + .03 * pulse) * (5 - i) / 4 * (ti - 2)})`);
  }
  R(x, y, w, h, '#05070d');
  for (let i = 0; i < h - 2; i++) R(x + 1, y + 1 + i, w - 2, 1, mix(P.lite, P.frame, clamp(i / (h * .30), 0, 1)));
  for (let i = Math.round(h * .55); i < h - 2; i++) R(x + 1, y + 1 + i, w - 2, 1, mix(P.frame, P.dark, clamp((i - h * .55) / (h * .45), 0, 1)));
  R(x + 1, y + 1, w - 2, 1, 'rgba(255,255,255,.65)'); R(x + 1, y + 1, 1, h - 2, 'rgba(255,255,255,.33)');
  R(x + 1, y + h - 2, w - 2, 1, P.dark); R(x + w - 2, y + 1, 1, h - 2, P.dark);
  // chamfered corners
  [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([cx, cy]) => { const ax = cx ? x + w - 2 : x, ay = cy ? y + h - 2 : y; R(ax, ay, 2, 2, '#05070d'); });
  // tier ornaments
  const stud = (sx, sy) => { R(sx, sy, 2, 2, P.lite); R(sx + 1, sy + 1, 1, 1, P.dark); };
  if (ti >= 1){ stud(x + 3, y + 3); stud(x + w - 5, y + 3); stud(x + 3, y + h - 5); stud(x + w - 5, y + h - 5); }
  if (ti >= 2){
    [[x + 2, y + 2, 1, 1], [x + w - 3, y + 2, -1, 1], [x + 2, y + h - 3, 1, -1], [x + w - 3, y + h - 3, -1, -1]].forEach(([bx, by, dx, dy]) => {
      for (let i = 0; i < 5; i++){ R(bx + dx * i, by, 1, 1, P.lite); R(bx, by + dy * i, 1, 1, P.lite); } });
  }
  if (ti >= 3){
    R(x + 2, y + 2, w - 4, 1, P.lite); R(x + 2, y + h - 3, w - 4, 1, P.dark);
    const dia = (dx, dy) => { R(dx, dy - 1, 1, 3, P.lite); R(dx - 1, dy, 3, 1, P.lite); };
    dia(x + w / 2, y + 2); dia(x + w / 2, y + h - 3); dia(x + 2, y + h * .5); dia(x + w - 3, y + h * .5);
  }
  // a sheen that sweeps across the frame (faster on the rarer cards)
  const sp = ti >= 4 ? 22 : 34, sh = ti >= 3 ? .30 : .14;
  for (let i = 0; i < h; i++){
    const sx = x + ((i * 1.5 + t / sp) % (w + h * .8)) - h * .4;
    if (sx > x + 1 && sx < x + w - 3) R(sx, y + 1 + i, 2, 1, `rgba(255,255,255,${sh})`);
  }
  if (ti === 5){                                                  // red cards burn
    for (let i = 0; i < 12; i++){
      const fy = y + h - 2 - ((t / 70 + i * 9) % (h - 2)), wob = Math.sin(t / 60 + i * 1.7) * 1.6;
      R(x - 2 + wob, fy, 2, 3, i % 2 ? '#ff8a2a' : '#ffd23f'); R(x + w - wob, fy, 2, 3, i % 2 ? '#ffd23f' : '#ff8a2a');
    }
    R(x, y, w, 1, '#ffd23f'); R(x, y + h - 1, w, 1, '#ff6a2a');
  }
  return F;
}

function drawCard(x, y, c, w = CARD_W, h = CARD_H, t = 0, o = {}){
  const ovr = ovrOf(c), ti = tierIdx(c), P = CARD_PAL[ti], team = o.team || cardTeam(c);
  const k = w / CARD_W, mini = w < 34;
  const F = cardFrame(x, y, w, h, ti, t, k);

  // portrait window: the tier's colours, with a light burst behind the head on the good ones
  const px = x + F, py = y + F, pw = w - F * 2, ph = Math.round(h * .50);
  for (let i = 0; i < ph; i++) R(px, py + i, pw, 1, mix(P.top, P.bot, i / ph));
  if (ti >= 3 && !mini){
    g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();
    for (let r = 0; r < 9; r++){
      const a = (r / 9) * Math.PI * 2 + t / (ti === 5 ? 700 : 1400);
      g.fillStyle = `rgba(255,255,255,${.06 + (ti - 3) * .02})`;
      g.beginPath(); g.moveTo(px + pw / 2, py + ph * .55);
      g.lineTo(px + pw / 2 + Math.cos(a) * pw * 1.4, py + ph * .55 + Math.sin(a) * pw * 1.4);
      g.lineTo(px + pw / 2 + Math.cos(a + .17) * pw * 1.4, py + ph * .55 + Math.sin(a + .17) * pw * 1.4); g.fill();
    }
    g.restore();
  }
  cardPortrait(c, team, px, py, pw, ph);
  if (ti === 5 && !mini){                                          // holo shimmer sliding over the portrait
    g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();
    for (let i = -ph; i < pw + ph; i += 7){
      const sx = px + ((i + t / 30) % (pw + ph)), hue = (i * 9 + t / 8) % 360;
      g.fillStyle = `hsla(${hue},95%,70%,.13)`;
      g.beginPath(); g.moveTo(sx, py); g.lineTo(sx + 3, py); g.lineTo(sx + 3 - ph * .6, py + ph); g.lineTo(sx - ph * .6, py + ph); g.fill();
    }
    g.restore();
  }
  R(px, py + ph, pw, 1, P.dark);

  // team badge, top left
  if (!mini){
    const bw = Math.round(15 * k), bh = Math.round(9 * k);
    R(px + 1, py + 1, bw, bh, '#05070d'); R(px + 2, py + 2, bw - 2, bh - 2, team.c1);
    R(px + 2, py + 2, bw - 2, 1, 'rgba(255,255,255,.35)');
    text(team.ab, px + 1 + bw / 2, py + 2 + Math.round(1 * k), mix(team.c2, '#ffffff', .65), Math.max(5, Math.round(5.5 * k)), 'center');
    if (c.lvl) text(`+${c.lvl}`, px + 3, py + bh + 3, '#9af0ae', Math.max(5, Math.round(6 * k)));
  }
  // the big rating on a dark plate, top right, always whole
  const rs = Math.max(7, Math.round((mini ? 10 : 14) * k)), rw = Math.round((String(ovr).length * .62 * rs) + 5 * k);
  R(px + pw - rw - 1, py + 1, rw, rs + 3, 'rgba(5,7,13,.82)'); R(px + pw - rw - 1, py + rs + 4, rw, 1, P.frame);
  textb(String(ovr), px + pw - 3, py + 2, P.lite, rs, 'right');
  if (mini){ drawCardMiniName(x, y, w, h, c, ti, F, py + ph); return; }

  // position and handedness tabs on the portrait's lower edge
  const by = py + ph - Math.round(9 * k), bh2 = Math.round(9 * k), bw2 = Math.round(16 * k);
  [[px, c.pos], [px + pw - bw2, (isPitcher(c) ? (c.throws || 'R') + 'P' : (c.bats || 'R') + 'B')]].forEach(([tx0, s]) => {
    R(tx0, by, bw2, bh2, 'rgba(5,7,13,.88)'); R(tx0, by, bw2, 1, P.frame);
    text(s, tx0 + bw2 / 2, by + Math.round(1.5 * k), '#ffffff', Math.max(5, Math.round(6 * k)), 'center');
  });

  // name bar
  const ny = py + ph + 1, nh = Math.round(11 * k);
  R(px, ny, pw, nh, '#07090f'); R(px, ny + nh - 1, pw, 1, P.frame);
  const parts = c.name.split(' ');
  const nm = (parts[0][0] + '. ' + parts[parts.length - 1]).toUpperCase();
  text(nm.slice(0, 13), px + pw / 2, ny + Math.round(2.4 * k), '#ffffff', Math.max(5, Math.round(7 * k)), 'center');

  // the four ratings, each in the colour of its own band
  const sy = ny + nh, boxH = y + h - F - sy;
  R(px, sy, pw, boxH, '#0a0d16');
  const rowH = boxH / 4, fs = clamp(Math.round(rowH - 1.5), 5, 9);
  statsOf(c).forEach(([lbl, key], i) => {
    const ry = Math.round(sy + i * rowH + (rowH - fs) / 2 - .5);
    if (i) R(px + 2, Math.round(sy + i * rowH), pw - 4, 1, 'rgba(255,255,255,.06)');
    text(lbl, px + Math.round(3 * k), ry, mix(P.frame, '#ffffff', .35), fs);
    text(String(c[key]), px + pw - Math.round(3 * k), ry, colOf(c[key]), fs, 'right');
  });
  if (o.isNew){ R(x + 3, y + h * .30, 26 * k, 9 * k, '#e63946'); text('NEW!', x + 3 + 13 * k, y + h * .30 + 1.5 * k, '#fff', Math.max(5, 6 * k), 'center'); }
  if (o.badge) textb(o.badge, x + w / 2, y + h / 2 - 4, '#ffd23f', 8, 'center');
}
// the small version used in trays: portrait, rating and a last name
function drawCardMiniName(x, y, w, h, c, ti, F, below){
  const ny = below + 1, nh = y + h - F - ny;
  R(x + F, ny, w - F * 2, nh, '#07090f');
  const parts = c.name.split(' ');
  text(parts[parts.length - 1].toUpperCase().slice(0, 6), x + w / 2, ny + Math.max(1, (nh - 5) / 2), '#fff', 5, 'center');
}

// the back of a card: same frame, the season's numbers, what he's worth
function drawCardBack(x, y, c, w, h, t = 0){
  const ovr = ovrOf(c), ti = tierIdx(c), P = CARD_PAL[ti], k = w / CARD_W;
  const F = cardFrame(x, y, w, h, ti, t, k);
  const ix = x + F, iy = y + F, iw = w - F * 2, ih = h - F * 2;
  for (let i = 0; i < ih; i++) R(ix, iy + i, iw, 1, mix('#151d2e', '#0a0e17', i / ih));
  const fs = Math.max(5, Math.round(7 * k));
  textb(c.name.toUpperCase().slice(0, 14), x + w / 2, iy + 3 * k, '#ffffff', Math.max(6, Math.round(7.5 * k)), 'center');
  text(`${TIER_LABEL[ti]} · ${c.pos}`, x + w / 2, iy + 13 * k, P.frame, Math.max(5, Math.round(6 * k)), 'center');
  R(ix + 3, iy + 22 * k, iw - 6, 1, P.dark);
  const s = c.st || newStat();
  const rows = isPitcher(c)
    ? [['IP', s.ip], ['K', s.ko], ['ER', s.er], ['W-L', `${s.w}-${s.l}`]]
    : [['AB', s.ab], ['H', s.h], ['HR', s.hr], ['RBI', s.rbi], ['AVG', (s.ab ? s.h / s.ab : 0).toFixed(3).replace('0.', '.')]];
  text('THIS SEASON', x + w / 2, iy + 25 * k, '#7d89a3', Math.max(5, Math.round(5.5 * k)), 'center');
  rows.forEach((r, i) => {
    const ry = iy + (34 + i * 10.5) * k;
    text(r[0], ix + 5 * k, ry, '#8e97a8', fs); text(String(r[1]), ix + iw - 5 * k, ry, '#ffffff', fs, 'right');
  });
  const by = y + h - F - 22 * k;
  R(ix + 3, by - 2, iw - 6, 1, P.dark);
  text(`OVERALL ${ovr}`, x + w / 2, by + 2 * k, P.lite, Math.max(5, Math.round(6.5 * k)), 'center');
  text(`UPGRADE ${c.lvl || 0}/10`, x + w / 2, by + 11 * k, '#9af0ae', Math.max(5, Math.round(5.5 * k)), 'center');
}

