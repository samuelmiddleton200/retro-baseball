import re
def patch(path):
    s = open(path, encoding='utf-8').read()
    i = s.index("  statsOf(c).forEach(([lbl, key], i) => {\n    const y = 58 + i * 25")
    j = s.index("  const by = 162;")
    new = """  // a hitter's speed IS his fielding, so they are one row; a pitcher has four
  const rows = isPitcher(c) ? statsOf(c).map(([lbl, key], i) => ({ lbl, key, i })) : [{ lbl:'CON', key:'contact', i:0 }, { lbl:'POW', key:'power', i:1 }, { lbl:'SPD+FLD', key:'fielding', i:2, link:true }];
  const RH = rows.length === 3 ? 33 : 25, RT = RH - 3;
  rows.forEach((row, ri) => {
    const y = 58 + ri * RH, v = c[row.key], sel = !maxed && (upStat === row.i || (row.link && linkedStat(c, upStat))), step = row.link ? 1 : 2;
    R(x0 + 5, y, pw - 10, RT, sel ? '#2c3f95' : UI.navy);
    if (sel){ R(x0 + 5, y, pw - 10, 1, UI.yellow); R(x0 + 5, y + RT - 1, pw - 10, 1, UI.yellow); R(x0 + 5, y, 1, RT, UI.yellow); R(x0 + pw - 6, y, 1, RT, UI.yellow); }
    const ty = y + Math.round((RT - 8) / 2);
    if (sel) text('>', x0 + 8, ty, UI.yellow, 8);
    textb(row.lbl, x0 + 20, ty, '#fff', row.link ? 6.5 : 7);
    textb(String(v), x0 + (row.link ? 62 : 52), ty - 2, colOf(v), 10);
    const bx = x0 + 84, bw = Math.max(20, pw - 84 - 62);
    R(bx, ty + 1, bw, 6, '#1b2a66'); R(bx, ty + 1, Math.round(bw * clamp((v - 55) / 65, 0, 1)), 6, sel ? UI.yellow : '#6f8de8');
    text(sel && !maxed ? `${v} > ${Math.min(120, v + step)}` : `+${step}`, x0 + pw - 9, ty, sel ? UI.yellow : '#8aa0d0', 7, 'right');
    if (!maxed) btns.push({ x:x0 + 5, y, w:pw - 10, h:RT, fn: () => upStat = row.i });
  });
"""
    s = s[:i] + new + s[j:]
    a = "`UPGRADE ${statsOf(c)[upStat][0]}  ${cost.toLocaleString()}`"
    assert a in s
    s = s.replace(a, "`UPGRADE ${isPitcher(c) ? statsOf(c)[upStat][0] : linkedStat(c, upStat) ? 'SPD+FLD' : statsOf(c)[upStat][0]}  ${cost.toLocaleString()}`")
    open(path, 'w', encoding='utf-8').write(s)
patch('index.html'); patch('tools/shop_card.js')
s = open('index.html', encoding='utf-8').read()
s = s.replace("BUILD = '11-07c'", "BUILD = '11-07d'"); s = re.sub(r"gl3d\.js\?v=11-07c", "gl3d.js?v=11-07d", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
