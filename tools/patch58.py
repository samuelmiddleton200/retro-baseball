import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:100]); s = s.replace(a, b)

# ── the three ballparks: each is a matched pair (pitch view + hit view) with its own measured fit of feet-on-the-field to picture pixels ──
a = s.index("// ── the painted hit view (ChatGPT's picture")
b = s.index("function gxSprites(list, B){")
new = """// ── the ballparks: every one is a matched pair of ChatGPT pictures, the batter's view and the high view, each with its own measured fit of feet on the field to picture pixels ──
const HITP = new Image(); HITP.src = 'assets/fields/hit_painted.png?b=11-10a';
const FPITCH = new Image(); FPITCH.src = 'assets/fields/fenway_pitch.png?b=11-10a';
const FHIT = new Image(); FHIT.src = 'assets/fields/fenway_hit.png?b=11-10a';
// PH: picture size, home plate's column, depth (ft) -> picture row as a measured table, sideways feet shrink with distance (kx / (depth + c)), height scale hs.
// shift: how far the pitcher stands from where the old picture's mound was (in target pixels across, in screen heights down)
const STADIUMS = [
  { id:'classic', name:'THE BALLPARK', pitch:() => PLATE, hit:() => HITP, shift:[0, 0],
    PH:{ IW:1697, IH:927, px:848, YD:[[-10, 855], [0, 808], [60.5, 521], [127.3, 375], [233.3, 238], [400, 185], [700, 168]], kx:1186, c:130.5, hs:.85 } },
  { id:'fenway', name:'BOSTON', pitch:() => FPITCH, hit:() => FHIT, shift:[8.9, 0],
    PH:{ IW:1697, IH:927, px:848, YD:[[-10, 870], [0, 824], [60.5, 548], [127.3, 406], [233.3, 268], [400, 241], [700, 225]], kx:1228, c:136.7, hs:.85 } },
  { id:'bay', name:'THE BAY', pitch:() => DPITCH, hit:() => DHIT, shift:[-21, .012],
    PH:{ IW:1873, IH:840, px:935, YD:[[-10, 872], [0, 805], [60.5, 563], [127.3, 446], [233.3, 358], [400, 295], [700, 248]], kx:1244, c:98, hs:.85 } },
];
const curStadium = () => STADIUMS[(M && M.stad) || 0] || STADIUMS[0];
const paintOn = () => ready(curStadium().hit()) && !window.__noPaint && !(M && M.derby);
function paintPt(d, lat, h){
  const PHs = curStadium().PH, T = PHs.YD; let y = T[T.length - 1][1];
  for (let i = 1; i < T.length; i++) if (d <= T[i][0]){ const a = T[i - 1], b = T[i]; y = lerp(a[1], b[1], (d - a[0]) / (b[0] - a[0])); break; }
  const s = PHs.kx / (Math.max(d, -40) + PHs.c), sc = H / PHs.IH, sx = Math.max(sc, W / PHs.IW), x0 = W / 2 - PHs.IW * sx / 2;      // a wider phone stretches the picture sideways to fill it; a narrower one crops it
  return { x: x0 + (PHs.px + lat * s) * sx, y: (y - h * s * PHs.hs) * sc, s: s * sc };
}
const toScr = (x, y, z, w, h) => paintOn() ? paintPt(-z, x, y) : GL3D.toScreen(x, y, z, w, h);
function drawPaintBG(){
  const st = curStadium(), PHs = st.PH, sc = H / PHs.IH, sx = Math.max(sc, W / PHs.IW), iw = PHs.IW * sx;
  g.fillStyle = '#05070b'; g.fillRect(0, 0, W, H); g.imageSmoothingEnabled = false;
  g.drawImage(st.hit(), W / 2 - iw / 2, 0, iw, H);
}
"""
s = s[:a] + new + s[b:]

# the batter's view picks the park's own picture
rep("g.drawImage(M && M.derby && ready(DPITCH) ? DPITCH : PLATE, W / 2 - 550 * s, 0, 1100 * s, H);", "g.drawImage(ready(curStadium().pitch()) ? curStadium().pitch() : PLATE, W / 2 - 550 * s, 0, 1100 * s, H);")
rep("const derbyMoundShift = () => M && M.derby ? { x:-21 * TU, y:H * .012 } : { x:0, y:0 };", "const derbyMoundShift = () => { const st = curStadium(); return { x:st.shift[0] * TU, y:st.shift[1] * H }; };      // each park's mound is a little off the old picture's")
# which park a game is played in: they rotate game by game; the derby is always in the bay
rep("  M.uni = pickUniforms(M.home, M.away);                          // who wears what, once, for the whole game",
    "  M.uni = pickUniforms(M.home, M.away);                          // who wears what, once, for the whole game\n  M.stad = (G.day || 0) % STADIUMS.length;                         // the three ballparks take turns")
rep("  M.uni = pickUniforms(M.home, M.away);\n  M.coins0 = G.coins; M.earn = {}; M.rep = {}; M.pitchSimmed = false;\n  M.batter = card;", "  M.uni = pickUniforms(M.home, M.away); M.stad = 2;                  // the derby is always played in the bay\n  M.coins0 = G.coins; M.earn = {}; M.rep = {}; M.pitchSimmed = false;\n  M.batter = card;")

s = s.replace("BUILD = '11-09h'", "BUILD = '11-10a'"); s = re.sub(r"gl3d\.js\?v=11-09h", "gl3d.js?v=11-10a", s)
open('index.html', 'w', encoding='utf-8').write(s)
d = open('tools/derby.js', encoding='utf-8').read()
x = "const derbyMoundShift = () => M && M.derby ? { x:-21 * TU, y:H * .012 } : { x:0, y:0 };"
assert d.count(x) == 1
d = d.replace(x, "const derbyMoundShift = () => { const st = curStadium(); return { x:st.shift[0] * TU, y:st.shift[1] * H }; };")
open('tools/derby.js', 'w', encoding='utf-8').write(d)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
