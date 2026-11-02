s = open('index.html', encoding='utf-8').read()

# replace the old 3D-bust portrait (CARD_FRAME3D .. end of cardPortrait) with the painted portraits
a = s.index("const CARD_FRAME3D")
b = s.index("// the metal frame; every tier up adds something")
s = s[:a] + open('tools/portrait_code.js', encoding='utf-8').read() + "\n" + s[b:]

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# a taller portrait window, and the light burst becomes a soft glow behind the head
rep("const px = x + F, py = y + F, pw = w - F * 2, ph = Math.round(h * .50);", "const px = x + F, py = y + F, pw = w - F * 2, ph = Math.round(h * .52);")
a = s.index("  if (ti >= 3 && !mini){\n    g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();\n    for (let r = 0; r < 9; r++){")
b = s.index("  cardPortrait(c, team, px, py, pw, ph);")
s = s[:a] + """  if (ti >= 3 && !mini){                                          // a soft glow behind the head
    const gr = g.createRadialGradient(px + pw / 2, py + ph * .45, 2, px + pw / 2, py + ph * .45, pw * .75);
    gr.addColorStop(0, `rgba(255,255,255,${.30 + (ti - 3) * .08})`); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(px, py, pw, ph);
  }
""" + s[b:]

# the rating: big outlined number, no plate
a = s.index("  // the big rating on a dark plate, top right, always whole")
b = s.index("  if (mini){ drawCardMiniName(x, y, w, h, c, ti, F, py + ph); return; }")
s = s[:a] + """  // the big rating, top right, white with a dark outline
  const rs = Math.max(7, Math.round((mini ? 11 : 15) * k));
  textb(String(ovr), px + pw - 2, py + 1, '#ffffff', Math.max(10, rs), 'right');
""" + s[b:]
open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
