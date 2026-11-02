// ── painted gameplay figures (ChatGPT sheets, cut by tools/slice_batter.py): one image per animation frame, all on a common
// canvas with the feet at the bottom centre.  Magenta kit is recoloured to the club, like the card portraits. ────────────
const GP = { batter: [], ready: false };
for (let i = 0; i < 8; i++){
  const im = new Image(); im.onload = () => { im._ok = true; GP.ready = GP.batter.every(f => f._ok); }; im.onerror = () => {};
  im.src = `assets/gp/batter${i}.png`; GP.batter.push(im);
}
const GP_CACHE = new Map();
// every magenta pixel (helmet, jersey) takes the club's colour and keeps its shading
function gpTint(img, key, c1){
  const k = key + c1;
  if (GP_CACHE.has(k)) return GP_CACHE.get(k);
  const cv = document.createElement('canvas'); cv.width = img.naturalWidth; cv.height = img.naturalHeight;
  const x = cv.getContext('2d'); x.drawImage(img, 0, 0);
  try {
    const im = x.getImageData(0, 0, cv.width, cv.height), d = im.data, [br, bg, bb] = hexRgb(c1);
    for (let p = 0; p < d.length; p += 4){
      if (d[p + 3] < 8) continue;
      const r = d[p], gr = d[p + 1], b = d[p + 2];
      if (r > 70 && b > 70 && gr < r * .66 && gr < b * .66 && Math.abs(r - b) < r * .42){
        const lum = .3 * r + .59 * gr + .11 * b, t = clamp((lum - 34) / 90, 0, 1), f = .34 + .95 * t, hi = t > .85 ? 30 : 0;
        d[p] = clamp(br * f + hi, 0, 255); d[p + 1] = clamp(bg * f + hi, 0, 255); d[p + 2] = clamp(bb * f + hi, 0, 255);
      }
    }
    x.putImageData(im, 0, 0);
  } catch (e){}
  GP_CACHE.set(k, cv);
  return cv;
}
// which frame of the swing: 0/1 wait (the bat waggles), 2 load, 3 stride, 4 swing, 5 contact, 6 follow-through, 7 finish
const SWING_AT = [0, .14, .30, .46, .58, .76];
function batterFrame(swingT, idle){
  if (swingT == null) return Math.floor(idle / 38) % 2;
  let f = 0; SWING_AT.forEach((t, i) => { if (swingT >= t) f = i; });
  return 2 + f;
}
// stamp one painted figure: feet at (xL, yL), about hT target pixels tall; `flip` mirrors him about his own feet
function gpStamp(img, key, c1, xL, yL, hT, flip, figFrac){
  const cv = gpTint(img, key, c1), s = (hT * TU) / (cv.height * (figFrac || .97)), dw = cv.width * s, dh = cv.height * s;
  g.fillStyle = 'rgba(20,14,6,.30)'; g.beginPath(); g.ellipse(Math.round(xL), Math.round(yL) - .5, Math.max(4, hT * TU * .20), Math.max(1.2, hT * TU * .04), 0, 0, 7); g.fill();
  g.save(); g.translate(Math.round(xL), Math.round(yL - dh)); if (flip) g.scale(-1, 1);
  g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
  g.drawImage(cv, Math.round(-dw / 2), 0, Math.round(dw), Math.round(dh));
  g.imageSmoothingEnabled = false; g.restore();
}
