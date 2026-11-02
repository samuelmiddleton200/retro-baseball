function nameHash(c){ let h = 7; for (const ch of c.name) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return h; }
// Every player gets his own face where there are enough: the faces nearest his skin tone, the least-used first, and it is
// remembered on the card (c.face) so he always looks the same. Mirrored copies and road-grey jerseys tell repeats apart.
function portraitFor(c){
  if (c.face != null && PORT[c.face] && PORT[c.face]._ok) return c.face;
  const ok = []; PORT.forEach((p, i) => { if (p._ok) ok.push(i); });
  if (!ok.length) return -1;
  const sk = hexRgb((c.look && c.look.skin) || '#d9a577');
  const ranked = ok.map(i => { const s = portSkin(i); return [Math.hypot(s[0] - sk[0], s[1] - sk[1], s[2] - sk[2]), i]; }).sort((a, b) => a[0] - b[0]);
  let pool = ranked.filter(r => r[0] <= ranked[0][0] + 55).slice(0, 12);
  if (pool.length < 4) pool = ranked.slice(0, Math.min(4, ranked.length));
  const used = {}; ((G && G.cards) || []).forEach(z => { if (z.face != null) used[z.face] = (used[z.face] || 0) + 1; });
  const h = nameHash(c);
  pool.sort((a, b) => (used[a[1]] || 0) - (used[b[1]] || 0) || ((h + a[1] * 7) % 13) - ((h + b[1] * 7) % 13));
  c.face = pool[0][1];
  return c.face;
}
// recolour: the cap in the club's colour; the jersey in the club's colour at home, road-grey on every third card
function portraitTinted(i, team, road){
  const key = i + team.c1 + (road ? 'r' : '');
  if (PORT_CACHE.has(key)) return PORT_CACHE.get(key);
  const src = PORT[i], cv = document.createElement('canvas'); cv.width = src.naturalWidth; cv.height = src.naturalHeight;
  const x = cv.getContext('2d'); x.drawImage(src, 0, 0);
  try {
    const im = x.getImageData(0, 0, cv.width, cv.height), d = im.data, cap = hexRgb(team.c1), jer = road ? [196, 202, 214] : cap;
    for (let p = 0; p < d.length; p += 4){
      if (d[p + 3] < 8) continue;
      const r = d[p], gr = d[p + 1], b = d[p + 2];
      if (r > 60 && b > 60 && gr < r * .62 && gr < b * .62 && Math.abs(r - b) < r * .4){
        const row = (p / 4 / cv.width) | 0, base = row > cv.height * .36 ? jer : cap;
        const lum = .3 * r + .59 * gr + .11 * b, t = clamp((lum - 34) / 74, 0, 1), f = (road && row > cv.height * .36 ? .55 : .36) + (road && row > cv.height * .36 ? .55 : .92) * t, hi = t > .86 ? 28 : 0;
        d[p] = clamp(base[0] * f + hi, 0, 255); d[p + 1] = clamp(base[1] * f + hi, 0, 255); d[p + 2] = clamp(base[2] * f + hi, 0, 255);
      }
    }
    x.putImageData(im, 0, 0);
  } catch (e){}
  PORT_CACHE.set(key, cv);
  return cv;
}
// the portrait window: his face, top-aligned so cap, eyes and chin are always in
function cardPortrait(c, team, px, py, pw, ph){
  const i = portraitFor(c);
  g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();
  if (i >= 0){
    const h = nameHash(c), flip = (h >> 3) % 2 === 1, road = h % 3 === 0;
    const cv = portraitTinted(i, team, road), sc = pw / cv.width * .86, dw = cv.width * sc, dh = cv.height * sc;
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    if (flip){ g.translate(px + pw / 2, 0); g.scale(-1, 1); g.translate(-(px + pw / 2), 0); }
    g.drawImage(cv, Math.round(px + (pw - dw) / 2), py + 2, Math.round(dw), Math.round(dh));
    g.imageSmoothingEnabled = false;
  } else {                                              // faces not loaded yet: the old hand-drawn bust
    const bust = cardBustRig(c, team), SRC = { x:39, y:2, w:34, h:36 }, sc = (pw / SRC.w) * 1.06;
    g.drawImage(bust, SRC.x, SRC.y, SRC.w, SRC.h, Math.round(px + pw / 2 - SRC.w * sc / 2), Math.round(py), Math.round(SRC.w * sc), Math.round(SRC.h * sc));
  }
  g.restore();
}

