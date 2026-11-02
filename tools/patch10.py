s=open('index.html',encoding='utf-8').read()
a=s.index("function gpStamp(img, key, c1, xL, yL, hT, flip, figFrac, alpha, dxSrc){")
b=s.index("const phaseStep =")
new='''const GP_SCALED = new Map();
// the tinted frame resampled ONCE to the size it is drawn at, so each frame is a plain 1:1 blit (the swing no longer rescales a big
// image every frame)
function gpScaled(img, key, c1, dw, dh){
  const k = key + c1 + '|' + dw + 'x' + dh;
  let c = GP_SCALED.get(k);
  if (!c){
    const src = gpTint(img, key, c1); c = document.createElement('canvas'); c.width = dw; c.height = dh;
    const x = c.getContext('2d'); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high'; x.drawImage(src, 0, 0, dw, dh);
    GP_SCALED.set(k, c); if (GP_SCALED.size > 120) GP_SCALED.delete(GP_SCALED.keys().next().value);
  }
  return c;
}
// stamp one painted figure: feet at (xL, yL), about hT target pixels tall; `flip` mirrors him about his own feet
function gpStamp(img, key, c1, xL, yL, hT, flip, figFrac, alpha, dxSrc){
  const sc = gpTint(img, key, c1), s = (hT * TU) / (sc.height * (figFrac || .97)), dw = Math.round(sc.width * s), dh = Math.round(sc.height * s);
  const cv = gpScaled(img, key, c1, dw, dh);
  if (alpha == null || alpha >= 1){ g.fillStyle = 'rgba(20,14,6,.30)'; g.beginPath(); g.ellipse(Math.round(xL), Math.round(yL) - .5, Math.max(4, hT * TU * .20), Math.max(1.2, hT * TU * .04), 0, 0, 7); g.fill(); }
  g.save(); g.translate(Math.round(xL), Math.round(yL - dh)); if (flip) g.scale(-1, 1);
  if (alpha != null) g.globalAlpha = alpha;
  g.drawImage(cv, Math.round(-dw / 2 - (dxSrc || 0) * s), 0);
  g.restore();
}
'''
s=s[:a]+new+s[b:]
# warm everything for the batting club the first time the figure is drawn
old="    const xL = lefty ? tx(478) : tx(300), yL = ty(449);\n"
assert old in s
s=s.replace(old, old+"    if (GP.warm !== bt.c1){ GP.warm = bt.c1; for (let i = 0; i < 8; i++){ gpHead(i); gpScaled(GP.batter[i], 'B' + i, bt.c1, Math.round(GP.batter[i].naturalWidth * (196 * TU) / (GP.batter[i].naturalHeight * .97)), Math.round(196 * TU / .97)); } }\n")
open('index.html','w',encoding='utf-8').write(s)
