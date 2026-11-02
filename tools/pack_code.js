// a foil pack: crimped wrapper, a real player's face in a burst of light, the name on a ribbon
const PACK_FACE = { bronze:5, silver:0, gold:10, diamond:17 };           // a rookie, a youngster, a veteran, a star
function drawPackArt(x, y, w, h, key, on, t){
  const Pk = PACKS[key], dark = mix(Pk.col, '#000000', .55), mid = Pk.col, lite = mix(Pk.col2, '#ffffff', .30);
  // wrapper body: a smooth metallic gradient with the corners knocked off
  R(x + 1, y, w - 2, h, '#05070d'); R(x, y + 1, w, h - 2, '#05070d');
  const body = g.createLinearGradient(x, y, x + w, y + h);
  body.addColorStop(0, lite); body.addColorStop(.35, mid); body.addColorStop(.7, dark); body.addColorStop(1, mix(dark, '#000000', .35));
  g.fillStyle = body; g.fillRect(x + 1, y + 1, w - 2, h - 2);
  // crimped top and bottom edges
  for (let i = 0; i < w - 2; i += 3){
    R(x + 1 + i, y + 1, 2, 4, i % 6 ? mix(lite, '#ffffff', .5) : mid);
    R(x + 1 + i, y + h - 5, 2, 4, i % 6 ? dark : mix(dark, '#000000', .4));
  }
  R(x + 1, y + 5, w - 2, 1, mix(dark, '#000000', .3)); R(x + 1, y + h - 6, w - 2, 1, mix(lite, '#ffffff', .3));
  // the window: a burst of light and a face
  const wx = x + 5, wy = y + 9, ww = w - 10, wh = Math.round(h * .50);
  g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip();
  const bg = g.createRadialGradient(wx + ww / 2, wy + wh * .45, 3, wx + ww / 2, wy + wh * .45, ww * .8);
  bg.addColorStop(0, mix(Pk.col2, '#ffffff', .6)); bg.addColorStop(.45, Pk.col2); bg.addColorStop(1, mix(dark, '#000000', .3));
  g.fillStyle = bg; g.fillRect(wx, wy, ww, wh);
  for (let r = 0; r < 10; r++){                                       // rays
    const a = r / 10 * Math.PI * 2 + t / 2400;
    g.fillStyle = 'rgba(255,255,255,.13)'; g.beginPath(); g.moveTo(wx + ww / 2, wy + wh * .5);
    g.lineTo(wx + ww / 2 + Math.cos(a) * ww, wy + wh * .5 + Math.sin(a) * ww); g.lineTo(wx + ww / 2 + Math.cos(a + .2) * ww, wy + wh * .5 + Math.sin(a + .2) * ww); g.fill();
  }
  const fi = PACK_FACE[key];
  if (PORT[fi] && PORT[fi]._ok){
    const cv = portraitTinted(fi, { c1: mix(Pk.col, '#101a40', .35) }, false), sc = ww / cv.width * 1.0, dw = cv.width * sc, dh = cv.height * sc;
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    g.drawImage(cv, Math.round(wx + (ww - dw) / 2), wy + 3, Math.round(dw), Math.round(dh));
    g.imageSmoothingEnabled = false;
  }
  // a shine that sweeps across the window
  for (let i = 0; i < wh; i++){
    const sx = wx + ((i * 1.4 + t / 36) % (ww + wh)) - wh * .5;
    if (sx > wx && sx < wx + ww - 2) R(sx, wy + i, 3, 1, 'rgba(255,255,255,.22)');
  }
  g.restore();
  R(wx - 1, wy - 1, ww + 2, 1, '#05070d'); R(wx - 1, wy + wh, ww + 2, 1, '#05070d'); R(wx - 1, wy, 1, wh, '#05070d'); R(wx + ww, wy, 1, wh, '#05070d');
  // the ribbon with the name, and a "3 cards" star
  const ry = wy + wh + 4, rh = Math.max(16, h - (ry - y) - 11);
  R(x + 2, ry, w - 4, rh, '#0b1230'); R(x + 2, ry, w - 4, 1, lite); R(x + 2, ry + rh - 1, w - 4, 1, dark);
  const fs = Math.min(10, Math.max(7, w / 9));
  ptitle(Pk.n.toUpperCase(), x + w / 2, ry + 2, fs, '#ffffff');
  text('PACK', x + w / 2, ry + 3 + fs * 1.15, lite, Math.max(5, fs * .75), 'center');
  R(x + w - 19, y + 8, 16, 11, '#e63946'); R(x + w - 19, y + 8, 16, 1, '#ff8f98');
  text('x3', x + w - 11, y + 10, '#ffffff', 6, 'center');
  // little sparkles
  for (let i = 0; i < 4; i++){
    const sp = (t / 500 + i * .27) % 1, sx = x + 6 + ((i * 53) % (w - 14)), sy = wy + 6 + ((i * 29) % Math.max(10, wh - 14));
    if (sp < .35){ const a = Math.sin(sp / .35 * Math.PI); R(sx - 1, sy, 3, 1, `rgba(255,255,255,${a})`); R(sx, sy - 1, 1, 3, `rgba(255,255,255,${a})`); }
  }
  g.strokeStyle = on ? '#ffffff' : mix(Pk.col, '#000000', .1); g.lineWidth = 1; g.strokeRect(x + .5, y + .5, w - 1, h - 1);
}

