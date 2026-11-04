s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── 1) the wide picture: the old field with real field added at both sides, the same size and place in the middle ──
rep("PLATE.src = 'assets/fields/plate_clean.png?b=11-03c';", "PLATE.src = 'assets/fields/plate_wide.png?b=11-05e';       // 1100 x 492 target pixels (stored at 2x): the old picture is the middle 756, new field fills both sides")
rep("""  const s = TU, x0 = W / 2 - 380 * s, pw = 760 * s;
  g.imageSmoothingEnabled = false;
  g.fillStyle = '#05070b'; g.fillRect(0, 0, W, H);
  // wide phones: the picture keeps its own shape at full screen height and the sides are plain black (no stretching, no blur)
  g.drawImage(PLATE, 2, 0, 756, 492, x0 + 2 * s, 0, 756 * s, H);   // the field with NO people in it: every figure is drawn live, so idle and moving look the same""",
"""  const s = TU;
  g.imageSmoothingEnabled = false;
  g.fillStyle = '#05070b'; g.fillRect(0, 0, W, H);
  // the picture is 1100 target pixels wide with the old 756-wide picture in the middle, so every position stays where it was.
  // A phone narrower than that crops the same amount off both sides; one wider (rare) shows a sliver of black at the edges.
  g.drawImage(PLATE, W / 2 - 550 * s, 0, 1100 * s, H);          // the field with NO people in it: every figure is drawn live""")
rep("""  const [x0, y0, x1, y1] = IDLE_BOX[k], s = TU, ox = W / 2 - 380 * s;
  g.imageSmoothingEnabled = false; g.drawImage(PLATE, x0, y0, x1 - x0, y1 - y0, ox + x0 * s, y0 * s, (x1 - x0) * s, (y1 - y0) * s);""",
"""  const [x0, y0, x1, y1] = IDLE_BOX[k], s = TU, ox = W / 2 - 380 * s;
  g.imageSmoothingEnabled = false; g.drawImage(PLATE, (x0 + 170) * 2, y0 * 2, (x1 - x0) * 2, (y1 - y0) * 2, ox + x0 * s, y0 * s, (x1 - x0) * s, (y1 - y0) * s);""")

# ── 2) the aim pad: the strike zone drawn 2x, with room around it for pitches off the plate ──
rep("// ── a ball in play, on the same field you are looking at", """// ── the aim pad ───────────────────────────────────────────────────────────
// The strike zone on the field is small, so while you aim a big copy of it sits to the side of the plate (away from the batter).
// The box is the strike zone at 2x; the pad goes 0.6 of a zone further on every side so you can throw off the plate too.
// You tap on the pad and the ball goes to that exact spot in the real zone.
const PAD_RNG = 1.6;                                              // zone units from the middle to the edge of the pad (1 = the edge of the strike zone)
function padGeom(){
  const lefty = !!(M && M.batter && M.batter.bats === 'L'), ux = ZONE.w, uy = ZONE.h;      // pad pixels per zone unit: 2x the zone on the field
  return { cx: W / 2 + (lefty ? -64 : 64), cy: 76, ux, uy, w: 2 * PAD_RNG * ux, h: 2 * PAD_RNG * uy };
}
function padHit(p){
  const G = padGeom(); return p.x >= G.cx - G.w / 2 - 4 && p.x <= G.cx + G.w / 2 + 4 && p.y >= G.cy - G.h / 2 - 4 && p.y <= G.cy + G.h / 2 + 4;
}
function padAim(p){                                              // where a tap on the pad lands, in zone units
  const G = padGeom(); return { x: clamp((p.x - G.cx) / G.ux, -PAD_RNG, PAD_RNG), y: clamp((p.y - G.cy) / G.uy, -PAD_RNG, PAD_RNG) };
}
function drawAimPad(ax, ay, dIn){
  const G = padGeom(), x0 = G.cx - G.w / 2, y0 = G.cy - G.h / 2;
  g.fillStyle = 'rgba(8,18,40,.66)'; rrect(x0 - 4, y0 - 12, G.w + 8, G.h + 16, 4); g.fill();
  g.strokeStyle = 'rgba(190,215,255,.9)'; g.lineWidth = 1; rrect(x0 - 4, y0 - 12, G.w + 8, G.h + 16, 4); g.stroke();
  tt('AIM', x0 + 1, y0 - 6, 13, '#ffffff', 'left');
  g.fillStyle = 'rgba(80,84,96,.38)'; g.fillRect(x0, y0, G.w, G.h);                                        // off the plate: a ball
  g.fillStyle = 'rgba(48,128,70,.55)'; g.fillRect(G.cx - G.ux, G.cy - G.uy, 2 * G.ux, 2 * G.uy);           // the strike zone
  g.strokeStyle = 'rgba(235,245,235,.5)'; g.lineWidth = .6; g.beginPath();
  for (const k of [-1 / 3, 1 / 3]){ g.moveTo(G.cx + k * G.ux, G.cy - G.uy); g.lineTo(G.cx + k * G.ux, G.cy + G.uy); g.moveTo(G.cx - G.ux, G.cy + k * G.uy); g.lineTo(G.cx + G.ux, G.cy + k * G.uy); }
  g.stroke();
  g.strokeStyle = '#ffffff'; g.lineWidth = 1; g.strokeRect(G.cx - G.ux, G.cy - G.uy, 2 * G.ux, 2 * G.uy);
  const mx = G.cx + ax * G.ux, my = G.cy + ay * G.uy, rx = dIn / 2 / IN_X * G.ux, ry = dIn / 2 / IN_Y * G.uy;   // the circle at real size, in the same inches as the real zone
  g.strokeStyle = '#ff6b5a'; g.lineWidth = 1.2; g.beginPath(); g.ellipse(mx, my, rx, ry, 0, 0, 7); g.stroke();
  R(mx - .6, my - .6, 1.6, 1.6, '#ffffff');
}

// ── a ball in play, on the same field you are looking at""")
rep("  drawAimCircle(aim.x, aim.y, circleIn(p));\n}", "  drawAimCircle(aim.x, aim.y, circleIn(p));\n  drawAimPad(aim.x, aim.y, circleIn(p));\n}")
rep("    else if (P && P.aim) drawAimCircle(P.aim.ax, P.aim.ay, circleIn(curPitcher()));\n    else if (P && P.circ && P.thrown && P.t < P.dur && P.state === 'flight') drawAimCircle(P.circ.ax, P.circ.ay, P.circ.d);\n",
    "    else if (P && P.aim){ drawAimCircle(P.aim.ax, P.aim.ay, circleIn(curPitcher())); drawAimPad(P.aim.ax, P.aim.ay, circleIn(curPitcher())); }\n    else if (P && P.circ && P.thrown && P.t < P.dur && P.state === 'flight'){ drawAimCircle(P.circ.ax, P.circ.ay, P.circ.d); drawAimPad(P.circ.ax, P.circ.ay, P.circ.d); }\n")
# tapping: the pad first, then the field as before
rep("  if (phase === 'pitching'){\n    // tap inside the zone area to aim and throw\n    if (p.y > 40 && p.y < H - 4){",
    "  if (phase === 'pitching' && P && !P.aim && !P.thrown && padHit(p)){\n    const a = padAim(p); aim.x = a.x; aim.y = a.y;\n    P.aim = { ax:aim.x, ay:aim.y, type:pitchSel }; P.clock = 0; phase = 'atbat'; touch.used = true; return;\n  }\n  if (phase === 'pitching'){\n    // tap inside the zone area to aim and throw\n    if (p.y > 40 && p.y < H - 4){")
rep("l2 = 'TAP THE ZONE'; }", "l2 = 'TAP THE PAD'; }")
rep("runToggle, runBack, drawPlay, circleIn,", "runToggle, runBack, drawPlay, circleIn, padGeom, padAim, get W(){ return W; }, get SC(){ return SC; }, get OX(){ return OX; },")
s = s.replace("BUILD = '11-05d'", "BUILD = '11-05e'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
