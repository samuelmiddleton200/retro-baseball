s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# ── 1) the rule: home always wears its MAIN colour; away wears its main colour unless it is the same kind of colour as home's, then its SECOND ──
rep("const batTeam = () => M.top ? M.away : M.home;", '''// What a colour "is" for this rule: blue, navy and royal blue are all BLUE; red and maroon are RED, and so on. Two clubs may never wear the same family.
function colorFamily(hex){
  const [r, g, b] = hexRgb(hex).map(v => v / 255), mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
  if (d < .1) return l > .78 ? 'white' : l < .3 ? 'black' : 'grey';                       // white and silver are one family, black and charcoal another
  let h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h = (h * 60 + 360) % 360;
  if (h < 14 || h >= 346) return 'red';
  if (h < 42) return l < .24 ? 'brown' : 'orange';
  if (h < 70) return 'yellow';
  if (h < 170) return 'green';
  if (h < 200) return 'teal';
  if (h < 268) return 'blue';
  if (h < 330) return 'purple';
  return 'pink';
}
// home: main colour, always. away: main colour if it is a different kind of colour, else its second, else plain white or grey road colours.
function pickUniforms(home, away){
  const hf = colorFamily(home.c1);
  const opts = [[away.c1, away.c2], [away.c2, away.c1], ['#ffffff', away.c1], ['#c4ced4', away.c1], ['#27251f', away.c1]];
  const pick = opts.find(o => colorFamily(o[0]) !== hf) || opts[2];
  // the trim colour (cap brim, sleeves): home's second colour, kept different from its main one
  const trim = t => colorFamily(t.c2) !== colorFamily(t.c1) ? t.c2 : '#ffffff';
  return { home: home.c1, away: pick[0], homeTrim: trim(home), awayTrim: pick[0] === away.c1 ? trim(away) : away.c1 };
}
const uni = t => (M && M.uni) ? (t === M.home ? M.uni.home : M.uni.away) : t.c1;
const uni2 = t => (M && M.uni) ? (t === M.home ? M.uni.homeTrim : M.uni.awayTrim) : t.c2;
const batTeam = () => M.top ? M.away : M.home;''')

# the match is set up with it
rep("  M.pitcherHome.st.ip = M.pitcherHome.st.ip || 0;\n  phase = 'atbat'; setupAtBat();", "  M.uni = pickUniforms(M.home, M.away);                          // who wears what, once, for the whole game\n  M.pitcherHome.st.ip = M.pitcherHome.st.ip || 0;\n  phase = 'atbat'; setupAtBat();")

# ── 2) everywhere a figure is coloured: the match uniform, not the raw team colour ──
rep("const tasks = [], cols = [fldTeam().c1, batTeam().c1];", "const tasks = [], cols = [uni(fldTeam()), uni(batTeam())];")
rep("  const away = team === M.away, shirt = away ? '#cfd3dc' : team.c1;      // road grey, or the home team's own colour",
    "  const away = team === M.away, shirt = uni(team);                        // the club's colour for this match")
rep("ab:team.ab, cap:team.c1, cap2:team.c2, shirt, sleeve:team.c1,", "ab:team.ab, cap:uni(team), cap2:uni2(team), shirt, sleeve:uni(team),")
rep("parkCols: [ft.c1, bt.c1]", "parkCols: [uni(ft), uni(bt)]")
rep("GPF.img[f], 'FD' + f, fldTeam().c1,", "GPF.img[f], 'FD' + f, uni(fldTeam()),")
rep("k = pos - f0, c1 = fldTeam().c1;", "k = pos - f0, c1 = uni(fldTeam());")
s = s.replace("bt.c1", "uni(bt)")                                           # the batter (painted and 3D)
rep("{ glove:1, cap2:ft.c2, helm:ft.c1 });", "{ glove:1, cap2:uni2(ft), helm:uni(ft) });")
rep("'C' + lookKey(cm.look) + ft.c1 + ft.c2, oc,", "'C' + lookKey(cm.look) + uni(ft) + uni2(ft), oc,")
s = s.replace("BUILD = '11-03e'", "BUILD = '11-03f'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
