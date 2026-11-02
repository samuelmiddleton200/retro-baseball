// the portraits: painted in ChatGPT, 240 x ~318 each (assets/portraits/pNN.png), caps and jerseys in magenta so
// they can be recoloured to any club. A player always gets the same face: the three that match his skin tone best, one picked from his name.
const PORT_N = 40, PORT = [], PORT_CACHE = new Map();
for (let i = 0; i < PORT_N; i++){
  const im = new Image(); im.onload = () => { im._ok = true; }; im.onerror = () => {};
  im.src = `assets/portraits/p${String(i).padStart(2, '0')}.png`; PORT.push(im);
}
const hexRgb = h => { const n = parseInt(h.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; };
function portSkin(i){                                   // the average skin colour in the middle of the face
  const p = PORT[i]; if (p._skin) return p._skin;
  const cv = document.createElement('canvas'); cv.width = 24; cv.height = 24; const x = cv.getContext('2d');
  x.drawImage(p, p.naturalWidth * .40, p.naturalHeight * .46, p.naturalWidth * .20, p.naturalHeight * .12, 0, 0, 24, 24);
  let r = 0, gg = 0, b = 0;
  try { const d = x.getImageData(0, 0, 24, 24).data; for (let k = 0; k < d.length; k += 4){ r += d[k]; gg += d[k + 1]; b += d[k + 2]; } r /= 576; gg /= 576; b /= 576; }
  catch (e){ r = 200; gg = 150; b = 110; }
  return p._skin = [r, gg, b];
}
function portraitFor(c){
  const ok = []; PORT.forEach((p, i) => { if (p._ok) ok.push(i); });
  if (!ok.length) return -1;
  const sk = hexRgb((c.look && c.look.skin) || '#d9a577');
  const ranked = ok.map(i => { const s = portSkin(i); return [Math.hypot(s[0] - sk[0], s[1] - sk[1], s[2] - sk[2]), i]; })
                   .sort((a, b) => a[0] - b[0]).slice(0, Math.min(3, ok.length));
  let h = 7; for (const ch of c.name) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return ranked[h % ranked.length][1];
}
// recolour: every magenta pixel becomes the club's colour, keeping its shading
function portraitTinted(i, team){
  const key = i + team.c1;
  if (PORT_CACHE.has(key)) return PORT_CACHE.get(key);
  const src = PORT[i], cv = document.createElement('canvas'); cv.width = src.naturalWidth; cv.height = src.naturalHeight;
  const x = cv.getContext('2d'); x.drawImage(src, 0, 0);
  try {
    const im = x.getImageData(0, 0, cv.width, cv.height), d = im.data, [br, bg, bb] = hexRgb(team.c1);
    for (let p = 0; p < d.length; p += 4){
      if (d[p + 3] < 8) continue;
      const r = d[p], gr = d[p + 1], b = d[p + 2];
      if (r > 60 && b > 60 && gr < r * .62 && gr < b * .62 && Math.abs(r - b) < r * .4){
        const lum = .3 * r + .59 * gr + .11 * b, t = clamp((lum - 34) / 74, 0, 1), f = .36 + .92 * t, hi = t > .86 ? 28 : 0;
        d[p] = clamp(br * f + hi, 0, 255); d[p + 1] = clamp(bg * f + hi, 0, 255); d[p + 2] = clamp(bb * f + hi, 0, 255);
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
    const cv = portraitTinted(i, team), sc = pw / cv.width * 1.04, dw = cv.width * sc, dh = cv.height * sc;
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    g.drawImage(cv, Math.round(px + (pw - dw) / 2), py + 1, Math.round(dw), Math.round(dh));
    g.imageSmoothingEnabled = false;
  } else {                                              // faces not loaded yet: the old hand-drawn bust
    const bust = cardBustRig(c, team), SRC = { x:39, y:2, w:34, h:36 }, sc = (pw / SRC.w) * 1.06;
    g.drawImage(bust, SRC.x, SRC.y, SRC.w, SRC.h, Math.round(px + pw / 2 - SRC.w * sc / 2), Math.round(py), Math.round(SRC.w * sc), Math.round(SRC.h * sc));
  }
  g.restore();
}
