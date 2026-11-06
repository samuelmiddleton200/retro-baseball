s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

fn = r"""// ── the playoff picture: the top 6 of each league, as the standings have it today. 4 v 5 and 3 v 6 play a wild-card game; the winners play the 1 and 2 seeds; then the league series and the World Series ──
function playoffSeeds(lg){
  const pctOf = t => (t.w + t.l) ? t.w / (t.w + t.l) : 0;
  return G.teams.map((t, i) => ({ t, i })).filter(o => o.t.lg === lg).sort((a, b) => pctOf(b.t) - pctOf(a.t) || b.t.w - a.t.w || a.i - b.i);
}
function drawPlayoffs(){
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('PLAYOFFS', 10, 3, 9, '#ffffff', 'left');
  textb('IF THE SEASON ENDED TODAY', W - 8, 5, UI.ice, 6, 'right');
  const bh = 16, cx = W / 2, wsW = 56, avail = cx - wsW / 2 - 6, gap = 5, cw = Math.floor((avail - 2 * gap - 4) / 3), top = 36;
  const lum = c => { const n = parseInt(c.slice(1), 16); return ((n >> 16) * .3 + ((n >> 8) & 255) * .59 + (n & 255) * .11); };
  const mine = G.team;
  const tile = (x, y, o, seed, lbl) => {                               // a team: its colours, its letters and (for the first round) its seed
    const t = o && o.t;
    R(x, y, cw, bh, o && o.i === mine ? UI.yellow : '#ffffff');
    R(x + 1, y + 1, cw - 2, bh - 2, t ? t.c1 : '#1c2a5e');
    if (t){ textb(t.ab, x + cw / 2 + (seed ? 4 : 0), y + 5, lum(t.c1) > 150 ? '#101010' : '#ffffff', 7, 'center'); }
    else textb(lbl || 'TBD', x + cw / 2, y + 5, '#8fa0c8', 6, 'center');
    if (seed){ R(x + 1, y + 1, 9, bh - 2, UI.yellow); textb(String(seed), x + 5.5, y + 5, UI.navy, 7, 'center'); }
  };
  const line = (x1, y1, x2, y2) => { const c = '#9fb8ff'; R(Math.min(x1, x2), y1, Math.abs(x2 - x1) + 1, 1, c); R(x2, Math.min(y1, y2), 1, Math.abs(y2 - y1) + 1, c); };
  const pill = (x, w, label) => { R(x, 24, w, 9, UI.blueD); R(x, 24, w, 1, 'rgba(255,255,255,.4)'); textb(label, x + w / 2, 26, '#ffffff', 6, 'center'); };
  const mirrorY = y => 2 * top + (210 - top) - y - bh - top + top;           // the bottom half is the top half turned over
  ['AL', 'NL'].forEach((lg, side) => {
    const L = playoffSeeds(lg).slice(0, 6), sd = k => L[k - 1] || null, dir = side === 0 ? 1 : -1;
    // x of each column, outer to inner (the NL is the AL turned round)
    const col = n => side === 0 ? 4 + n * (cw + gap) : W - 4 - cw - n * (cw + gap);
    const edgeOut = n => side === 0 ? col(n) + cw : col(n), edgeIn = n => side === 0 ? col(n) : col(n) + cw;
    const yWC = [top, top + bh + 2], yDS = [top + 8, top + 8 + bh + 4], ymid = top + 8 + bh + 2;
    const yB = y => mirrorY(y);
    pill(col(0), cw, lg + ' WILD CARDS'); pill(col(1), cw, lg + 'DS'); pill(col(2), cw, lg + 'CS');
    // wild-card round: 4 v 5 on top, 3 v 6 at the bottom
    tile(col(0), yWC[0], sd(4), 4); tile(col(0), yWC[1], sd(5), 5);
    tile(col(0), yB(yWC[1]), sd(3), 3); tile(col(0), yB(yWC[0]), sd(6), 6);
    // division series: the 1 seed and the 4/5 winner; the 2 seed and the 3/6 winner
    tile(col(1), yDS[0], null, 0, 'WC WINNER'); tile(col(1), yDS[1], sd(1), 1);
    tile(col(1), yB(yDS[1]), sd(2), 2); tile(col(1), yB(yDS[0]), null, 0, 'WC WINNER');
    // league series
    const yL = [ymid + 2, yB(ymid + 2)];
    tile(col(2), yL[0], null, 0, 'TBD'); tile(col(2), yL[1], null, 0, 'TBD');
    // the lines: wild card pair -> its winner box; the winner box and the 1 seed -> the league series
    const m1 = yWC[0] + bh / 2, m2 = yWC[1] + bh / 2;
    line(edgeIn(0), m1, edgeIn(0) + dir * 3 * -1 * -1, m1);
    [[yWC[0], yWC[1], yDS[0]], [yB(yWC[1]), yB(yWC[0]), yB(yDS[0])]].forEach(([a, b, d]) => {
      const x0 = edgeOut(0) + dir * 3, ya = a + bh / 2, yb = b + bh / 2, yd = d + bh / 2;
      R(Math.min(edgeOut(0), x0), ya, 4, 1, '#9fb8ff'); R(Math.min(edgeOut(0), x0), yb, 4, 1, '#9fb8ff');
      R(x0, Math.min(ya, yb), 1, Math.abs(yb - ya) + 1, '#9fb8ff');
      R(Math.min(x0, edgeIn(1)), (ya + yb) / 2, Math.abs(edgeIn(1) - x0) + 1, 1, '#9fb8ff');
    });
    [[yDS[0], yDS[1]], [yB(yDS[1]), yB(yDS[0])]].forEach(([a, b], k) => {
      const x0 = edgeOut(1) + dir * 3, ya = a + bh / 2, yb = b + bh / 2;
      R(Math.min(edgeOut(1), x0), ya, 4, 1, '#9fb8ff'); R(Math.min(edgeOut(1), x0), yb, 4, 1, '#9fb8ff');
      R(x0, Math.min(ya, yb), 1, Math.abs(yb - ya) + 1, '#9fb8ff');
      R(Math.min(x0, edgeIn(2)), yL[k] + bh / 2, Math.abs(edgeIn(2) - x0) + 1, 1, '#9fb8ff');
    });
    // league series -> World Series
    const xs = edgeOut(2) + dir * 3, yc = (yL[0] + yL[1] + bh) / 2;
    R(Math.min(edgeOut(2), xs), yL[0] + bh / 2, 4, 1, '#9fb8ff'); R(Math.min(edgeOut(2), xs), yL[1] + bh / 2, 4, 1, '#9fb8ff');
    R(xs, yL[0] + bh / 2, 1, yL[1] - yL[0] + 1, '#9fb8ff');
    R(Math.min(xs, side === 0 ? cx - wsW / 2 : cx + wsW / 2), yc, Math.abs((side === 0 ? cx - wsW / 2 : cx + wsW / 2) - xs) + 1, 1, '#9fb8ff');
    // your place in this league
    if (G.team >= 0 && G.teams[G.team].lg === lg){
      const all = playoffSeeds(lg), rank = all.findIndex(o => o.i === G.team) + 1, six = all[5].t, me = G.teams[G.team];
      const gb = ((six.w - me.w) + (me.l - six.l)) / 2;
      G._poNote = rank <= 6 ? `YOU ARE THE ${lg} #${rank} SEED` : `${rank}TH IN THE ${lg}: ${gb.toFixed(1)} GB OF THE LAST SPOT`;
    }
  });
  // the middle: the league names and the World Series
  const cyMid = (top + 8 + bh + 2 + 2 + (mirrorY(top + 8 + bh + 2 + 2))) / 2 + bh / 2;
  textb('AMERICAN LEAGUE', 6, cyMid - 3, '#ffffff', 8, 'left'); textb('NATIONAL LEAGUE', W - 6, cyMid - 3, '#ffffff', 8, 'right');
  R(cx - wsW / 2, cyMid - 9, wsW, 18, '#ffffff'); R(cx - wsW / 2 + 1, cyMid - 8, wsW - 2, 16, UI.blueDD);
  textb('WORLD', cx, cyMid - 7, UI.yellow, 6, 'center'); textb('SERIES', cx, cyMid + 1, UI.yellow, 6, 'center');
  textb(G._poNote || '', 8, H - 17, UI.yellow, 6, 'left', W - 76);
  button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'stand');
}
"""
rep("// ── league leaders: batters or pitchers,", fn + "// ── league leaders: batters or pitchers,")
rep("  else if (menu === 'stats'){ drawStats(); return; }", "  else if (menu === 'stats'){ drawStats(); return; }\n  else if (menu === 'playoffs'){ drawPlayoffs(); return; }")
rep("    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');\n  }\n}\n" + fn[:0] + "// ── the playoff picture", "    button(8, H - 20, 62, 16, 'PLAYOFFS', () => menu = 'playoffs', '#2f6fe0', '#fff', 7);\n    button(W - 58, H - 20, 50, 16, 'BACK', () => menu = 'title');\n  }\n}\n// ── the playoff picture")
s = s.replace("BUILD = '11-11k'", "BUILD = '11-11l'").replace("gl3d.js?v=11-11k", "gl3d.js?v=11-11l")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
