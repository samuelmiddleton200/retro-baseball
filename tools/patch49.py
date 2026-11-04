import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# stats page: bigger type, no scroll arrows, a drawn triangle for the sort direction, RBI no longer clipped
rep("const nameW = Math.max(70, Math.round(W * .27)), x0 = 8, cx0 = x0 + 12 + nameW + 22, cw = Math.floor((W - 30 - cx0) / cols.length);",
    "const nameW = Math.max(70, Math.round(W * .25)), x0 = 8, cx0 = x0 + 12 + nameW + 26, cw = Math.floor((W - 10 - cx0) / cols.length), fs = cw >= 46 ? 9 : 8;\n  const tri = (x, y, up, col) => { g.fillStyle = col; g.beginPath(); if (up){ g.moveTo(x, y + 5); g.lineTo(x + 7, y + 5); g.lineTo(x + 3.5, y); } else { g.moveTo(x, y); g.lineTo(x + 7, y); g.lineTo(x + 3.5, y + 5); } g.closePath(); g.fill(); };")
rep("uiBox(4, 38, W - 34, H - 64);", "uiBox(4, 38, W - 8, H - 64);")
rep("textb('#', x0, hy, '#ffffff', 6); textb(statsBy === 'team' ? 'TEAM (COUNTS = PER-PLAYER AVG)' : statsView === 'bat' ? 'PLAYER' : 'PITCHER', x0 + 12, hy, '#ffffff', 5, 'left', nameW + 20);\n  if (statsBy === 'player') textb('TM', x0 + 12 + nameW, hy, '#ffffff', 6);",
    "textb('#', x0, hy, '#ffffff', 7); textb(statsBy === 'team' ? 'TEAM (AVG PER PLAYER)' : statsView === 'bat' ? 'PLAYER' : 'PITCHER', x0 + 12, hy, '#ffffff', 7, 'left', nameW + 20);\n  if (statsBy === 'player') textb('TM', x0 + 12 + nameW, hy, '#ffffff', 7);")
rep("""    const lab = c.h + (on ? (so.asc ? '^' : 'v') : '');
    if (on){ R(x + cw - 6 - lab.length * 6, hy - 3, lab.length * 6 + 5, 11, UI.yellow); text(lab, x + cw - 2, hy, '#241a00', 6, 'right'); }      // the column being ranked gets a yellow box
    else textb(lab, x + cw - 2, hy, '#ffffff', 6, 'right');""",
"""    if (on){ const bw = c.h.length * fs + 17; R(x + cw - bw + 2, hy - 4, bw, fs + 6, UI.yellow); text(c.h, x + cw - 12, hy - 1, '#241a00', fs, 'right'); tri(x + cw - 9, hy + 1, so.asc, '#241a00'); }      // the column being ranked gets a yellow box and a triangle: up = low first
    else textb(c.h, x + cw - 2, hy - 1, '#ffffff', fs, 'right');""")
rep("btns.push({ x:x - 2, y:hy - 3, w:cw, h:13,", "btns.push({ x:x - 2, y:hy - 4, w:cw, h:fs + 6,")
rep("const rh = 11, top = 54,", "const rh = fs + 5, top = 57,")
rep("g.rect(4, top - 3, W - 34, H - 26 - top);", "g.rect(4, top - 3, W - 8, H - 26 - top);")
rep("""    textb(String(i0 + i + 1), x0, y, tc, 6);
    textb(r.p.name, x0 + 12, y, tc, 6, 'left', (statsBy === 'team' ? nameW + 20 : nameW) - 4);
    if (statsBy === 'player') textb(r.t.ab, x0 + 12 + nameW, y, tc, 6);""",
"""    textb(String(i0 + i + 1), x0, y, tc, 7);
    textb(r.p.name, x0 + 12, y, tc, 8, 'left', (statsBy === 'team' ? nameW + 20 : nameW) - 4);
    if (statsBy === 'player') textb(r.t.ab, x0 + 12 + nameW, y, tc, 8);""")
rep("textb(txt, cx0 + j * cw + cw - 2, y, c === col ? UI.yellow : tc, 6, 'right');", "textb(txt, cx0 + j * cw + cw - 2, y, c === col ? UI.yellow : tc, fs, 'right');")
a = s.index("  if (maxScroll > 0){\n    button(W - 26, top - 2"); b = s.index("  textb('tap a column to rank by it, drag to scroll'")
s = s[:a] + s[b:]
rep("textb('tap a column to rank by it, drag to scroll', W / 2, H - 12, UI.ice, 6, 'center');", "textb('tap a column to rank by it, drag to scroll', W / 2, H - 12, UI.ice, 7, 'center');")
rep("textb('v', W - 16, 25, UI.yellow, 6, 'right');", "tri(W - 20, 27, false, UI.yellow);")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
