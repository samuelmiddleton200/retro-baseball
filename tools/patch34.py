s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:70]); s = s.replace(a, b)

# the celebration lasts longer
rep("B.tJudge = Math.min(B.T, 3.2); B.tEnd = B.tJudge + 2.0; B.runN = 4; return; }", "B.tJudge = Math.min(B.T, 3.2); B.tEnd = B.tJudge + 3.6; B.runN = 4; return; }", 2)

# the ball's path turns gold on a homer
rep("S.trail = GX.trail.slice(); S.trailMode = 'line';", "S.trail = GX.trail.slice(); S.trailMode = 'line'; S.hr = !!B.hr;")
rep("    g.strokeStyle = 'rgba(255,255,255,.55)'; g.lineWidth = .9; g.beginPath();\n    S.trail.forEach",
    "    g.strokeStyle = S.hr ? 'rgba(255,214,64,.9)' : 'rgba(255,255,255,.55)'; g.lineWidth = S.hr ? 1.6 : .9; g.beginPath();\n    S.trail.forEach")

# the show
rep("function gxPlayHud(B){\n", '''// ── a home run: gold ball trail, a flash as it clears the wall, fireworks over the stands, confetti, a big bouncing banner ──
const FW_COLS = ['#ffd23f', '#ff4d4d', '#4aa3ff', '#54d67a', '#ff9330', '#ffffff', '#b26bff'];
function homerShow(B){
  const T = B.t - B.tJudge, now = performance.now();
  if (GX.fxB !== B){ GX.fxB = B; GX.fx = []; GX.fxBursts = 0; GX.fxLast = now; GX.fxConf = 0; }
  const dt = clamp((now - GX.fxLast) / 1000, 0, .05); GX.fxLast = now;
  const fx = GX.fx;
  // new fireworks every 0.3 s for the first 2.4 s: a ring of sparks, then a few fat ones
  while (T >= 0 && T < 2.4 && GX.fxBursts * .3 <= T){
    GX.fxBursts++;
    const bx = W * (.12 + Math.random() * .76), by = H * (.12 + Math.random() * .32), col = FW_COLS[(Math.random() * FW_COLS.length) | 0], col2 = FW_COLS[(Math.random() * FW_COLS.length) | 0];
    for (let i = 0; i < 34; i++){ const a = i / 34 * Math.PI * 2, v = 30 + Math.random() * 52; fx.push({ x:bx, y:by, vx:Math.cos(a) * v, vy:Math.sin(a) * v, life:1.1 + Math.random() * .5, age:0, c: i % 3 ? col : col2, s:2, g:55 }); }
  }
  // confetti rains down the whole time
  GX.fxConf += dt * 60;
  while (T >= 0 && T < 3.2 && GX.fxConf >= 1){ GX.fxConf--; fx.push({ x:Math.random() * W, y:-4, vx:(Math.random() - .5) * 18, vy:26 + Math.random() * 36, life:3.5, age:0, c:FW_COLS[(Math.random() * FW_COLS.length) | 0], s:1.5, w:true, g:0 }); }
  for (let i = fx.length - 1; i >= 0; i--){
    const p = fx[i]; p.age += dt; if (p.age > p.life){ fx.splice(i, 1); continue; }
    p.vy += p.g * dt; p.x += p.vx * dt + (p.w ? Math.sin(p.age * 6 + p.x) * .3 : 0); p.y += p.vy * dt;
    const a = clamp(1 - p.age / p.life, 0, 1); g.globalAlpha = p.w ? clamp(a * 2, 0, 1) : a;
    R(Math.round(p.x), Math.round(p.y), p.s, p.w ? 1 : p.s, p.c);
  }
  g.globalAlpha = 1;
  // a white flash the moment the ball clears the fence, and a gold glow behind the banner
  if (T >= 0 && T < .3){ g.fillStyle = `rgba(255,255,255,${.7 * (1 - T / .3)})`; g.fillRect(0, 0, W, H); }
  if (T >= 0){
    const e = clamp(T / .4, 0, 1), over = 1 + 2.2 * Math.pow(e - 1, 3) + 1.2 * Math.pow(e - 1, 2), sz = (22 + 30 * over * e) * (1 + .04 * Math.sin(T * 9)), flick = T < 1.4 && Math.floor(T / .11) % 2;
    g.fillStyle = `rgba(255,200,40,${.18 * clamp(1 - Math.max(0, T - 2.4) / .8, 0, 1) * e})`; g.fillRect(0, ty(102), W, ty(78) - ty(0));
    tt('HOME RUN!', W / 2, ty(108), sz, flick ? '#ffffff' : '#ffd23f', 'center');
    if (T > .35){ g.globalAlpha = clamp((T - .35) / .3, 0, 1);
      tt(`${Math.round(B.carry || ballDist())} FT   ${Math.round(B.ev)} MPH`, W / 2, ty(172), 22, '#ffffff', 'center');
      if (M.msg && /SLAM/.test(M.msg)) tt('GRAND SLAM!', W / 2, ty(206), 20, '#ff9330', 'center');
      g.globalAlpha = 1; }
  }
}
function gxPlayHud(B){
''')
rep("  tt(`${Math.round(B.ev)} MPH   ${Math.round(ballDist())} FT`, W / 2, ty(150), 20, '#ffffff', 'center');\n  if (CFG.DEBUG)",
    "  const hrShow = B.hr && B.judged;\n  if (!hrShow) tt(`${Math.round(B.ev)} MPH   ${Math.round(ballDist())} FT`, W / 2, ty(150), 20, '#ffffff', 'center');\n  if (hrShow) homerShow(B);\n  if (CFG.DEBUG)")
rep("    if (B.play === 'hr') tt('GONE!', W / 2, ty(150), 48, '#ffd23f', 'center');\n    else if (M.msg)", "    if (B.play === 'hr'){ /* the show above */ }\n    else if (M.msg)")
s = s.replace("BUILD = '11-03t'", "BUILD = '11-03u'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
