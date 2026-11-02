s = open('index.html', encoding='utf-8').read()
a = s.index("function batterFrame(rel, idle){")
b = s.index("const phaseStep =")
new = r'''function batterFrame(rel, idle){
  if (rel == null) return (idle % 90) < 7 ? 1 : 0;      // he waits in his stance; the bat gives a little waggle every 1.5 s
  if (rel < -100) return 2;
  if (rel < -50) return 3;
  if (rel < 0) return 4;
  if (rel < 50) return 5;
  if (rel < 100) return 6;
  return 7;
}
// one continuous motion: a fractional frame position along keyframes, so neighbouring painted frames cross-fade instead of popping
const SW_KEYS = [[-190, 0], [-135, 2], [-80, 3], [-35, 4], [8, 5], [55, 6], [110, 7]];
function batterPos(rel){
  if (rel <= SW_KEYS[0][0]) return 0;
  for (let i = 1; i < SW_KEYS.length; i++){
    const [t1, f1] = SW_KEYS[i], [t0, f0] = SW_KEYS[i - 1];
    if (rel < t1){ const u = (rel - t0) / (t1 - t0); return f0 + (f1 - f0) * (u * u * (3 - 2 * u)); }
  }
  return 7;
}
// the head's x in each frame (top of the figure), so the body stays put while the feet move through the stride
const GP_HEAD = [];
function gpHead(i){
  if (GP_HEAD[i] != null) return GP_HEAD[i];
  const im = GP.batter[i]; let hx = im.naturalWidth / 2;
  try {
    const cv = document.createElement('canvas'); cv.width = im.naturalWidth; cv.height = im.naturalHeight;
    const x = cv.getContext('2d'); x.drawImage(im, 0, 0); const d = x.getImageData(0, 0, cv.width, cv.height).data;
    let top = -1; for (let y = 0; y < cv.height && top < 0; y++) for (let xx = 0; xx < cv.width; xx++) if (d[(y * cv.width + xx) * 4 + 3] > 60){ top = y; break; }
    let sx = 0, n = 0; for (let y = top; y < top + cv.height * .16; y++) for (let xx = 0; xx < cv.width; xx++) if (d[(y * cv.width + xx) * 4 + 3] > 60){ sx += xx; n++; }
    if (n) hx = sx / n;
  } catch (e){}
  return GP_HEAD[i] = hx;
}
// stamp one painted figure: feet at (xL, yL), about hT target pixels tall; `flip` mirrors him about his own feet
function gpStamp(img, key, c1, xL, yL, hT, flip, figFrac, alpha, dxSrc){
  const cv = gpTint(img, key, c1), s = (hT * TU) / (cv.height * (figFrac || .97)), dw = cv.width * s, dh = cv.height * s;
  if (alpha == null || alpha >= 1){ g.fillStyle = 'rgba(20,14,6,.30)'; g.beginPath(); g.ellipse(Math.round(xL), Math.round(yL) - .5, Math.max(4, hT * TU * .20), Math.max(1.2, hT * TU * .04), 0, 0, 7); g.fill(); }
  g.save(); g.translate(Math.round(xL), Math.round(yL - dh)); if (flip) g.scale(-1, 1);
  if (alpha != null) g.globalAlpha = alpha;
  g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
  g.drawImage(cv, Math.round(-dw / 2 - (dxSrc || 0) * s), 0, Math.round(dw), Math.round(dh));
  g.imageSmoothingEnabled = false; g.restore();
}
'''
s = s[:a] + new + s[b:]
old = "    const f = batterFrame(rel, idle);\n    return gpStamp(GP.batter[f], 'B' + f, bt.c1, lefty ? tx(478) : tx(300), ty(449), 196, lefty);"
assert old in s
s = s.replace(old, '''    const xL = lefty ? tx(478) : tx(300), yL = ty(449);
    if (rel == null){ const f = batterFrame(rel, idle); return gpStamp(GP.batter[f], 'B' + f, bt.c1, xL, yL, 196, lefty, null, null, gpHead(f) - GP.batter[f].naturalWidth / 2 - (gpHead(0) - GP.batter[0].naturalWidth / 2)); }
    const pos = batterPos(rel), f0 = Math.floor(pos), f1 = Math.min(7, f0 + 1), u = pos - f0, ref = gpHead(0) - GP.batter[0].naturalWidth / 2;
    const dx = f => gpHead(f) - GP.batter[f].naturalWidth / 2 - ref;
    gpStamp(GP.batter[f0], 'B' + f0, bt.c1, xL, yL, 196, lefty, null, null, dx(f0));
    if (u > .02 && f1 !== f0) gpStamp(GP.batter[f1], 'B' + f1, bt.c1, xL, yL, 196, lefty, null, u, dx(f1));
    return;''')
open('index.html','w',encoding='utf-8').write(s)
