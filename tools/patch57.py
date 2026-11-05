import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:100]); s = s.replace(a, b)

# ── the painted hit view: feet on the field -> a pixel in the picture ──
block = """// ── the painted hit view (ChatGPT's picture of the same park as the batter's view). Every figure and the ball are placed on it by feet from home plate. ──
const HITP = new Image(); HITP.src = 'assets/fields/hit_painted.png?b=11-09g';
// picture 1697 x 927: home plate at the bottom centre; depth -> picture row is a measured table, sideways feet shrink with distance (kx / (depth + c))
const PH = { IW:1697, IH:927, px:848, YD:[[-10, 855], [0, 808], [60.5, 521], [127.3, 375], [233.3, 238], [400, 185], [700, 168]], kx:1186, c:130.5, hs:.85 };
const paintOn = () => ready(HITP) && !window.__noPaint && !(M && M.derby);
function paintPt(d, lat, h){
  const T = PH.YD; let y = T[T.length - 1][1];
  for (let i = 1; i < T.length; i++) if (d <= T[i][0]){ const a = T[i - 1], b = T[i]; y = lerp(a[1], b[1], (d - a[0]) / (b[0] - a[0])); break; }
  const s = PH.kx / (Math.max(d, -40) + PH.c), sc = H / PH.IH, x0 = W / 2 - PH.IW * sc / 2;
  return { x: x0 + (PH.px + lat * s) * sc, y: (y - h * s * PH.hs) * sc, s: s * sc };
}
const toScr = (x, y, z, w, h) => paintOn() ? paintPt(-z, x, y) : GL3D.toScreen(x, y, z, w, h);
function drawPaintBG(){
  const sc = H / PH.IH, iw = PH.IW * sc, x0 = W / 2 - iw / 2;
  g.fillStyle = '#05070b'; g.fillRect(0, 0, W, H); g.imageSmoothingEnabled = false;
  g.drawImage(HITP, x0, 0, iw, H);
  if (x0 > 0){                                                       // a phone wider than the picture: the stands carry on, mirrored
    const sw = x0 / sc;
    g.save(); g.translate(x0, 0); g.scale(-1, 1); g.drawImage(HITP, 0, 0, sw, PH.IH, 0, 0, x0, H); g.restore();
    g.save(); g.translate(W, 0); g.scale(-1, 1); g.drawImage(HITP, PH.IW - sw, 0, sw, PH.IH, 0, 0, x0, H); g.restore();
  }
}
function gxSprites(list, B){"""
rep("function gxSprites(list, B){", block)
rep("GL3D.toScreen(b[1], 0, -b[0], W, H)", "toScr(b[1], 0, -b[0], W, H)")
rep("const q = GL3D.toScreen(X, 26, Z, W, H); runMarks.push", "const q = toScr(X, paintOn() ? 16 : 26, Z, W, H); runMarks.push")
rep("  gxParkBG(S);                                                      // the stadium and the camera never change: it is rendered ONCE, then only copied\n  g.imageSmoothingEnabled = false; g.drawImage(GX.bg, 0, 0, GX.bg.width, GX.bg.height, 0, 0, W, H);",
    "  if (paintOn()) drawPaintBG();\n  else {\n  gxParkBG(S);                                                      // the stadium and the camera never change: it is rendered ONCE, then only copied\n  g.imageSmoothingEnabled = false; g.drawImage(GX.bg, 0, 0, GX.bg.width, GX.bg.height, 0, 0, W, H); }")
rep("  const P = (x, y, z) => GL3D.toScreen(x, y, z, W, H);\n  if (S.trail", "  const P = (x, y, z) => toScr(x, y, z, W, H);\n  if (S.trail")
rep("const rows = list.map(p => ({ p, q: GL3D.toScreen(p.x, 0, p.z, W, H) }))", "const rows = list.map(p => ({ p, q: toScr(p.x, 0, p.z, W, H) }))")
rep("const head = GL3D.toScreen(p.x, 6.2, p.z, W, H), hPx", "const head = toScr(p.x, paintOn() ? 12 : 6.2, p.z, W, H), hPx")
rep("    gxSize(); gxParkBG(S);", "    if (!paintOn()){ gxSize(); gxParkBG(S); }")

s = s.replace("BUILD = '11-09f'", "BUILD = '11-09g'"); s = re.sub(r"gl3d\.js\?v=11-09f", "gl3d.js?v=11-09g", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
