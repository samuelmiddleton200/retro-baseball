s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

# 1) no upgrade count on the card, front or back (it stays on the upgrade screen, where it is useful)
rep("    if (c.lvl) text(`+${c.lvl}`, px + 3, py + bh + 3, '#9af0ae', Math.max(5, Math.round(6 * k)));\n", "")
rep("  text(`UPGRADE ${c.lvl || 0}/10`, x + w / 2, by + 9 * k, '#9af0ae', Math.max(5, Math.round(5 * k)), 'center', iw - 4);\n", "")

# 2) roster and standings: laid out from the screen width, so nothing runs off a narrower screen
a = s.index("  else if (menu === 'roster'){")
b = s.index("  else if (menu === 'shop'){ drawShop(); return; }")
s = s[:a] + """  else if (menu === 'roster'){
    const me = myTeam(), cw = Math.floor((W - 24) / 2), L = 8, Rt = 16 + cw, sw = 19;
    R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');
    ptitle(`${me.city} ${me.nick}`, 10, 3, 9, '#ffffff', 'left');
    const side = (x0, title, heads, rows, n) => {
      const xr = x0 + cw - 2, firstStat = xr - 22 - (n - 1) * sw;
      textb(title, x0, 24, UI.yellow, 6);
      heads.forEach((h, j) => textb(h, xr - 22 - (n - 1 - j) * sw, 24, UI.ice, 5, 'right'));
      textb('OVR', xr, 24, UI.ice, 5, 'right');
      rows.forEach((r, i) => {
        const y = 34 + i * 12;
        textb(r.pos, x0, y, r.posCol, 6);
        textb(r.name, x0 + 15, y, '#ffffff', 7, 'left', firstStat - sw + 3 - (x0 + 15));
        r.vals.forEach((v, j) => textb(String(v), xr - 22 - (n - 1 - j) * sw, y, colOf(v), 6, 'right'));
        textb(String(r.ovr), xr, y, colOf(r.ovr), 7, 'right');
      });
    };
    side(L, 'LINEUP', ['CON', 'POW', 'SPD', 'FLD'], me.lineup.map(p => ({ pos:p.pos, posCol:UI.yellow, name:p.name, vals:[p.contact, p.power, p.speed, p.fielding], ovr:p.ovr })), 4);
    side(Rt, 'PITCHERS', ['VEL', 'CTL', 'STA'], me.rot.concat(me.pen).slice(0, 10).map((p, i) => ({ pos:i < 5 ? 'SP' : i === 9 ? 'CP' : 'RP', posCol:'#54d67a', name:p.name, vals:[p.velocity, p.control, p.stamina], ovr:p.ovr })), 3);
    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');
  }
""" + s[b:]
a = s.index("  else if (menu === 'stand'){")
b = s.index("function drawOver(){")
s = s[:a] + """  else if (menu === 'stand'){
    R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');
    ptitle('STANDINGS', 10, 3, 9, '#ffffff', 'left');
    const list = G.teams.map((t, i) => ({ ...t, i })).sort((a, b) => (b.w - b.l) - (a.w - a.l));
    const colW = Math.floor((W - 24) / 2);
    const col = (items, x0) => items.forEach((t, i) => {
      const y = 25 + i * 12.5, mine = t.i === G.team;
      if (mine) R(x0 - 3, y - 2, colW, 12, UI.blueDD);
      textb(t.ab, x0, y, mine ? UI.yellow : '#ffffff', 7);
      textb(`${t.w}-${t.l}`, x0 + 34, y, mine ? UI.yellow : UI.ice, 7);
      textb(t.nick, x0 + 70, y, mine ? UI.yellow : '#ffffff', 6, 'left', colW - 76);
    });
    col(list.slice(0, 15), 12); col(list.slice(15), 12 + colW + 6);
    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');
  }
}
""" + s[b:]

# 3) the pick-your-team screen: as many tiles per row as fit
rep("    textb('PICK YOUR TEAM', W / 2, 8, '#ffd23f', 10, 'center');\n    TEAMS.forEach((t, i) => {\n      const x = 8 + (i % 6) * 70, y = 26 + Math.floor(i / 6) * 32;",
    "    ptitle('PICK YOUR TEAM', W / 2, 5, 10, '#ffffff');\n    const cols = Math.max(4, Math.floor((W - 8) / 70)), tx0 = (W - cols * 70 + 4) / 2;\n    TEAMS.forEach((t, i) => {\n      const x = tx0 + (i % cols) * 70, y = 26 + Math.floor(i / cols) * 31;")
rep("      textb(t.nick.slice(0, 9), x + 33, y + 19, '#ffffffaa', 6, 'center');", "      textb(t.nick, x + 33, y + 19, '#ffffffcc', 6, 'center', 60);")
open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
