import re
new_torn = r"""const tornCv = document.createElement('canvas'); let tornKey = '';
// the part of the wrapper that has been ripped so far, from fraction a to b of its width: the torn picture shows through a soft mask over the sealed one.
// The mask is only redrawn when the tear itself changes (a slow drag used to redo it every frame), and at the picture's own size.
function drawTorn(tier, cx, bottom, s, a, b){
  const im = shopImg(`t_${tier}_3`); if (!imgOk(im) || b - a < .02) return;
  const nw = im.naturalWidth, nh = im.naturalHeight, key = tier + '|' + a.toFixed(3) + '|' + b.toFixed(3);
  if (key !== tornKey || tornCv.width !== nw){
    tornKey = key; tornCv.width = nw; tornCv.height = nh;
    const o = tornCv.getContext('2d'); o.clearRect(0, 0, nw, nh);
    o.drawImage(im, 0, 0);
    o.globalCompositeOperation = 'destination-in';
    const f = .06, gx = o.createLinearGradient(0, 0, nw, 0);
    if (a <= .02) gx.addColorStop(0, 'rgba(0,0,0,1)'); else { gx.addColorStop(Math.max(0, a - f), 'rgba(0,0,0,0)'); gx.addColorStop(a, 'rgba(0,0,0,1)'); }
    if (b >= .98) gx.addColorStop(1, 'rgba(0,0,0,1)'); else { gx.addColorStop(b, 'rgba(0,0,0,1)'); gx.addColorStop(Math.min(1, b + f), 'rgba(0,0,0,0)'); }
    o.fillStyle = gx; o.fillRect(0, 0, nw, nh);
    const gy = o.createLinearGradient(0, 0, 0, nh); gy.addColorStop(0, 'rgba(0,0,0,1)'); gy.addColorStop(.36, 'rgba(0,0,0,1)'); gy.addColorStop(.52, 'rgba(0,0,0,0)');
    o.fillStyle = gy; o.fillRect(0, 0, nw, nh);
  }
  const w = nw * s, h = nh * s;
  g.save(); g.imageSmoothingEnabled = true; g.drawImage(tornCv, cx - w / 2, bottom - h, w, h); g.restore();
}

"""
def patch(path):
    s = open(path, encoding='utf-8').read()
    i = s.index("const tornCv = document.createElement('canvas');"); j = s.index("// ── opening: tear the pack")
    s = s[:i] + new_torn + s[j:]
    old = "  if (p.y > b.top + (b.bottom - b.top) * .62) return true;                // the finger has wandered off the top of the pack\n"
    assert old in s
    s = s.replace(old, "  if (p.y < b.top - 40 || p.y > b.bottom + 14) return true;                // the finger has left the pack\n")
    old2 = "if (O.tr.a <= .07 && O.tr.b >= .93){"
    assert old2 in s
    s = s.replace(old2, "if (O.tr.a <= .12 && O.tr.b >= .88){")
    open(path, 'w', encoding='utf-8').write(s)
patch('index.html'); patch('tools/shop_ui.js')
s = open('index.html', encoding='utf-8').read()
s = s.replace("BUILD = '11-07b'", "BUILD = '11-07c'"); s = re.sub(r"gl3d\.js\?v=11-07b", "gl3d.js?v=11-07c", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
