s = open('index.html', encoding='utf-8').read()

def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)

# 1) a player's skin tone = the skin of the face on his card
rep("function nameHash(c){", """// the skin colour of a player's card (the painted face he was given), as a hex string: this is what the sprites wear
function skinHex(m){
  if (!m) return '';
  if (m._skinHex) return m._skinHex;
  if (!m.name || !PORT.some(p => p._ok)) return (m.look && m.look.skin) || '';
  const i = portraitFor(m); if (i < 0) return (m.look && m.look.skin) || '';
  const [r, gg, b] = portSkin(i), h = v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0');
  return m._skinHex = '#' + h(r) + h(gg) + h(b);
}
function nameHash(c){""")

# 2) the sprite recolour: skin pixels (hue 5-21, so the wooden bat and brown gloves are left alone) take the card's tone, keeping their shading
rep("function gpTint(img, key, c1){\n  const k = key + c1;", "let GPSK = '';                                       // the skin tone the next sprite is drawn with (set just before it is stamped)\nfunction gpTint(img, key, c1, skin = GPSK){\n  const k = key + c1 + skin;")
rep("    const im = x.getImageData(0, 0, cv.width, cv.height), d = im.data, [br, bg, bb] = hexRgb(c1);\n    for (let p = 0; p < d.length; p += 4){\n      if (d[p + 3] < 8) continue;\n      const r = d[p], gr = d[p + 1], b = d[p + 2];\n      if (r > 70 && b > 70 && gr < r * .66 && gr < b * .66 && Math.abs(r - b) < r * .42){",
    "    const im = x.getImageData(0, 0, cv.width, cv.height), d = im.data, [br, bg, bb] = hexRgb(c1), sk = skin ? hexRgb(skin) : null;\n    for (let p = 0; p < d.length; p += 4){\n      if (d[p + 3] < 8) continue;\n      const r = d[p], gr = d[p + 1], b = d[p + 2];\n      if (sk && r > 77 && r > gr && gr > b){\n        const hu = (gr - b) / (r - b), sa = (r - b) / r;\n        if (hu > .083 && hu < .36 && sa > .2 && sa < .75){\n          const k = clamp((.3 * r + .59 * gr + .11 * b) / 172, .3, 1.3);\n          d[p] = clamp(sk[0] * k, 0, 255); d[p + 1] = clamp(sk[1] * k, 0, 255); d[p + 2] = clamp(sk[2] * k, 0, 255);\n          continue;\n        }\n      }\n      if (r > 70 && b > 70 && gr < r * .66 && gr < b * .66 && Math.abs(r - b) < r * .42){")
rep("function gpScaled(img, key, c1, dw, dh){\n  const k = key + c1 + '|' + dw + 'x' + dh;", "function gpScaled(img, key, c1, dw, dh, skin = GPSK){\n  const k = key + c1 + skin + '|' + dw + 'x' + dh;")
rep("    const src = gpTint(img, key, c1); c = document.createElement('canvas'); c.width = dw; c.height = dh;", "    const src = gpTint(img, key, c1, skin); c = document.createElement('canvas'); c.width = dw; c.height = dh;")
rep("GP_SCALED.size > 120", "GP_SCALED.size > 260")

# 3) who is drawn: set the skin before each sprite
rep("const gxLook = m => ({ skin: (m.look && m.look.skin) || '#d9a577',", "const gxLook = m => ({ skin: skinHex(m) || (m.look && m.look.skin) || '#d9a577',")
rep("    if (p.sp && GPF.ready && GP.ready){", "    if (p.sp && GPF.ready && GP.ready){\n      GPSK = p.skin || '';")
rep("    return gpStamp(GPF.img[f], 'FD' + f, uni(fldTeam()), xL, yL,", "    GPSK = skinHex(fldTeam().lineup[i]);\n    return gpStamp(GPF.img[f], 'FD' + f, uni(fldTeam()), xL, yL,")
rep("    const X = tx(412), Y = ty(232);\n", "    const X = tx(412), Y = ty(232); GPSK = skinHex(curPitcher());\n")
rep("    const xL = lefty ? tx(478) : tx(300), yL = ty(449);\n", "    const xL = lefty ? tx(478) : tx(300), yL = ty(449); GPSK = skinHex(p);\n")
# test hooks
rep("runToggle, runBack, drawPlay,", "runToggle, runBack, drawPlay, skinHex, gpTint, get GPSK(){ return GPSK; }, set GPSK(v){ GPSK = v; }, GP,")
s = s.replace("BUILD = '11-03x'", "BUILD = '11-03y'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
