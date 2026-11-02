s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

# 1) variety: faces, flips, road jerseys
a = s.index("function portraitFor(c){")
b = s.index("// the metal frame; every tier up adds something")
s = s[:a] + open('tools/portrait_code2.js', encoding='utf-8').read() + s[b:]
# a bigger pool of faces on disk: allow up to 80
rep("const PORT_N = 40,", "const PORT_N = 80,")

# 2) text that always fits: shrink, then cut with an ellipsis
rep("function text(s, x, y, c = '#fff', size = 7, align = 'left'){\n  g.font = fontOf(size);",
    "// squeeze a string into maxW: smaller type first (down to 4.6px), then an ellipsis\nfunction fitText(s, size, maxW){\n  g.font = fontOf(size);\n  if (!maxW) return s;\n  let sz = size, w = g.measureText(s).width;\n  while (w > maxW && sz > 4.6){ sz -= .35; g.font = fontOf(sz); w = g.measureText(s).width; }\n  while (w > maxW && s.length > 1){ s = s.slice(0, -2) + '…'; w = g.measureText(s).width; if (s.length <= 2) break; }\n  return s;\n}\nfunction text(s, x, y, c = '#fff', size = 7, align = 'left', maxW){\n  s = fitText(String(s), size, maxW);")
rep("function textb(s, x, y, c = '#fff', size = 7, align = 'left'){",
    "function textb(s, x, y, c = '#fff', size = 7, align = 'left', maxW){")
rep("  // carry over the grass and the crowd. A heavy outline on small text reads as a smudge.\n  g.font = fontOf(size);",
    "  // carry over the grass and the crowd. A heavy outline on small text reads as a smudge.\n  s = fitText(String(s), size, maxW);")

# 3) the places where names and numbers must fit
rep("  text(nm.slice(0, 13), px + pw / 2, ny + Math.round(2.4 * k), '#ffffff', Math.max(5, Math.round(7 * k)), 'center');",
    "  text(nm, px + pw / 2, ny + Math.round(2.4 * k), '#ffffff', Math.max(5, Math.round(7 * k)), 'center', pw - 4);")
rep("  text(parts[parts.length - 1].toUpperCase().slice(0, 6), x + w / 2, ny + Math.max(1, (nh - 5) / 2), '#fff', 5, 'center');",
    "  text(parts[parts.length - 1].toUpperCase(), x + w / 2, ny + Math.max(1, (nh - 5) / 2), '#fff', 5, 'center', w - F * 2 - 2);")
rep("  textb(c.name.toUpperCase().slice(0, 14), x + w / 2, iy + 3 * k, '#ffffff', Math.max(6, Math.round(7.5 * k)), 'center');",
    "  textb(c.name.toUpperCase(), x + w / 2, iy + 3 * k, '#ffffff', Math.max(6, Math.round(7.5 * k)), 'center', iw - 4);")
rep("      textb(c.name.split(' ').pop().slice(0, 7), x + 19, y + 4, '#f2efe6', 7);\n      textb(String(ovrOf(c)), x + SW - 4, y + 3, colOf(ovrOf(c)), 8, 'right');",
    "      textb(c.name.split(' ').pop(), x + 19, y + 5, '#ffffff', 7, 'left', SW - 19 - 24);\n      textb(String(ovrOf(c)), x + SW - 5, y + 4, colOf(ovrOf(c)), 8, 'right');")
rep("    } else textb('empty', x + 19, y + 4, '#3d4659', 7);", "    } else textb('empty', x + 19, y + 5, UI.ice, 7);")
# the team badge on a card: dark or light text, whichever reads on the club colour
rep("    text(team.ab, px + 1 + bw / 2, py + 2 + Math.round(1 * k), mix(team.c2, '#ffffff', .65), Math.max(5, Math.round(5.5 * k)), 'center');",
    "    const lumB = (.3 * hexRgb(team.c1)[0] + .59 * hexRgb(team.c1)[1] + .11 * hexRgb(team.c1)[2]) / 255;\n    text(team.ab, px + 1 + bw / 2, py + 2 + Math.round(1 * k), lumB > .55 ? '#101010' : '#ffffff', Math.max(5, Math.round(5.5 * k)), 'center', bw - 3);")
open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
