s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── a position is played by the card in that position's slot (the fielders were matched by slot number, one off from the names) ──
rep("function lineupOf(team){ return team.lineup; }", "const posMan = (t, pos) => t.lineup[POS.indexOf(pos)] || t.lineup[0];       // who plays a position: the card in that position's slot\nfunction lineupOf(team){ return team.lineup; }")
rep("drawMini(p.x, p.y, (team.lineup[i] || team.lineup[0]).look,", "drawMini(p.x, p.y, posMan(team, pos).look,")
rep("    const man = ft.lineup[i] || ft.lineup[0];", "    const man = posMan(ft, pos);")
rep("ft.lineup[7] || ft.lineup[0]", "posMan(ft, 'C')", 4)
rep("throwFps(((fldTeam().lineup[7]) || c.man).fielding)", "throwFps((posMan(fldTeam(), 'C') || c.man).fielding)")
rep("S.people.push(gxPerson('f' + i, 'field', ft.lineup[i] || ft.lineup[0], ft, lat, -d, 0,", "S.people.push(gxPerson('f' + i, 'field', posMan(ft, pos), ft, lat, -d, 0,")
rep("GPSK = skinHex(fldTeam().lineup[i]);", "GPSK = skinHex(posMan(fldTeam(), pos));")
rep("man = ft.lineup[i] || ft.lineup[0], hT = hOver || figH(yL / TU);", "man = posMan(ft, pos), hT = hOver || figH(yL / TU);")

# ── the batting order is its own list: any of the nine positions can bat in any spot ──
rep("function curBatter(){ const t = batTeam(); return t.lineup[batterIdx(t) % 9]; }", "const IDENT9 = [0, 1, 2, 3, 4, 5, 6, 7, 8];\nconst orderOf = t => (t.order && t.order.length === 9) ? t.order : IDENT9;                 // batting order: slot numbers, first to ninth\nfunction curBatter(){ const t = batTeam(); return t.lineup[orderOf(t)[batterIdx(t) % 9]]; }")
rep("  me.lineup = G.slots.lineup.map(get);", "  me.lineup = G.slots.lineup.map(get);\n  if (!G.slots.order || G.slots.order.length !== 9) G.slots.order = IDENT9.slice();\n  me.order = G.slots.order;")
# best lineup also sets a batting order: the best bats first
rep("  rebuildTeam(); save();\n  const all = [...G.slots.lineup, ...G.slots.rot, ...G.slots.pen].map(cardById).filter(Boolean);\n  lineMsg = `Best lineup set:",
    "  { const bat = i => { const c = cardById(G.slots.lineup[i]); return c ? c.contact * .4 + c.power * .4 + spdOf(c) * .2 : 0; }; G.slots.order = IDENT9.slice().sort((a, b) => bat(b) - bat(a)); }\n  rebuildTeam(); save();\n  const all = [...G.slots.lineup, ...G.slots.rot, ...G.slots.pen].map(cardById).filter(Boolean);\n  lineMsg = `Best lineup set:")

# ── the lineup screen: each batter is labelled with his position, and an arrow moves him up or down the order ──
rep("""  textb('BATTING ORDER', 10, 24, UI.ice, 7);
  G.slots.lineup.forEach((id, i) => slot('lineup', i, String(i + 1), 10, 34 + i * 19));
  textb('ROTATION', 92, 24, UI.ice, 7);
  G.slots.rot.forEach((id, i) => slot('rot', i, 'SP', 92, 34 + i * 19));
  textb('BULLPEN', 174, 24, UI.ice, 7);
  G.slots.pen.forEach((id, i) => slot('pen', i, i === 4 ? 'CP' : 'RP', 174, 34 + i * 19));""",
"""  textb('BATTING ORDER', 10, 24, UI.ice, 7);
  if (!G.slots.order || G.slots.order.length !== 9) G.slots.order = IDENT9.slice();
  const BW = 120, ord = G.slots.order;
  ord.forEach((idx, k) => {                                            // the order he bats in; the label is the position he plays
    const x = 10, y = 34 + k * 19, c = cardById(G.slots.lineup[idx]);
    uiBox(x, y, BW, 16);
    textb(POS[idx], x + 5, y + 5, UI.yellow, 7);
    if (c){ textb(c.name.split(' ').pop(), x + 23, y + 5, '#ffffff', 7, 'left', BW - 23 - 44); textb(String(ovrOf(c)), x + BW - 29, y + 4, colOf(ovrOf(c)), 8, 'right'); }
    else textb('empty', x + 23, y + 5, UI.ice, 7);
    btns.push({ x, y, w:BW - 26, h:16, fn: () => lineSel = { where:'lineup', i:idx } });
    const arrow = (ax, up, on) => {                                      // a small triangle: move up / down the order
      g.fillStyle = on ? UI.yellow : 'rgba(255,255,255,.25)'; g.beginPath();
      if (up){ g.moveTo(ax + 5, y + 5); g.lineTo(ax + 10, y + 11); g.lineTo(ax, y + 11); } else { g.moveTo(ax, y + 5); g.lineTo(ax + 10, y + 5); g.lineTo(ax + 5, y + 11); }
      g.closePath(); g.fill();
      if (on) btns.push({ x:ax - 2, y, w:14, h:16, fn: () => { const j = k + (up ? -1 : 1); [ord[k], ord[j]] = [ord[j], ord[k]]; rebuildTeam(); save(); } });
    };
    arrow(x + BW - 26, true, k > 0); arrow(x + BW - 13, false, k < 8);
  });
  textb('ROTATION', 138, 24, UI.ice, 7);
  G.slots.rot.forEach((id, i) => slot('rot', i, 'SP', 138, 34 + i * 19));
  textb('BULLPEN', 220, 24, UI.ice, 7);
  G.slots.pen.forEach((id, i) => slot('pen', i, i === 4 ? 'CP' : 'RP', 220, 34 + i * 19));""")
rep("""  textb('TEAM', 262, 24, UI.ice, 7);
  ptitle(String(team), 262, 34, 22, UI.yellow, 'left');
  textb('overall', 262, 62, UI.ice, 7);
  textb('Tap a spot to swap in', 262, 82, '#ffffff', 7);
  textb('any spare card.', 262, 92, '#ffffff', 7);""",
"""  textb('TEAM', 306, 24, UI.ice, 7);
  ptitle(String(team), 306, 34, 22, UI.yellow, 'left');
  textb('overall', 306, 62, UI.ice, 7);
  textb('Tap a spot to swap in', 306, 82, '#ffffff', 7, 'left', W - 312);
  textb('any spare card.', 306, 92, '#ffffff', 7, 'left', W - 312);
  textb('Arrows move a batter', 306, 108, '#ffffff', 7, 'left', W - 312);
  textb('up or down the order.', 306, 118, '#ffffff', 7, 'left', W - 312);""")
s = s.replace("BUILD = '11-11v'", "BUILD = '11-11w'").replace("gl3d.js?v=11-11v", "gl3d.js?v=11-11w")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
