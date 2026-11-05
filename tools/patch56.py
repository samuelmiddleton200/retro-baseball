import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:100]); s = s.replace(a, b)

# ── the engine: a derby pitch, no fielders, its own result ──
rep("""      if (P.clock > SET_TIME){
        P.windup = clamp((P.clock - SET_TIME) / WINDUP_TIME, 0, 1);
        if (P.windup >= 1){ const a = aiPitch(); throwPitch(a.type, a.ax, a.ay); }
      }""",
"""      const setT = M.derby ? 500 : SET_TIME;
      if (P.clock > setT){
        P.windup = clamp((P.clock - setT) / WINDUP_TIME, 0, 1);
        if (P.windup >= 1){ if (M.derby) derbyThrow(); else { const a = aiPitch(); throwPitch(a.type, a.ax, a.args || a.ay); } }
      }""".replace("a.args || a.ay", "a.ay"))
rep("""  if (P.state === 'inplay'){
    P.playT += dt;
    if (swing) swing.t += dt;
    const ds = dt * CFG.TIME_SCALE;""",
"""  if (P.state === 'inplay'){
    if (M.derby) return derbyStepPlay(dt);
    P.playT += dt;
    if (swing) swing.t += dt;
    const ds = dt * CFG.TIME_SCALE;""")
rep("    if (P.hold > RESULT_HOLD) afterPitch();", "    if (P.hold > (M.derby ? 450 : RESULT_HOLD)) afterPitch();")
rep("function afterPitch(){\n  snapMatch();", "function afterPitch(){\n  if (M.derby) return derbyAfter();\n  snapMatch();")
rep("  launchBall(ev, la, sa, qual);\n  P.state = 'inplay'; P.playT = 0;\n  planFielders();", "  launchBall(ev, la, sa, qual);\n  P.state = 'inplay'; P.playT = 0;\n  if (!M.derby) planFielders();")
rep("  BALL.foul = true; BALL.tJudge = Math.min(BALL.T, 2.5); BALL.tEnd = BALL.tJudge + .6;\n  P.state = 'inplay'; P.playT = 0;\n  planFielders();", "  BALL.foul = true; BALL.tJudge = Math.min(BALL.T, 2.5); BALL.tEnd = BALL.tJudge + .6;\n  P.state = 'inplay'; P.playT = 0;\n  if (!M.derby) planFielders();")
rep("if (!M || M.over || !G || phase === 'menu' || phase === 'over') return;\n    const bt = batTeam()", "if (!M || M.over || M.derby || !G || phase === 'menu' || phase === 'over') return;\n    const bt = batTeam()")

# ── drawing: the derby stadium, no fielders, its own scoreboard, its own hit view ──
rep("  const PM = plateOK();\n  drawFielders(ft);", "  const PM = plateOK();\n  if (!M.derby) drawFielders(ft);")
rep("    g.stroke();\n  }\n\n  drawHUD();\n  if (M.msg) tt(M.msg, W / 2, ty(150), 34, M.msg.includes('!') ? '#ffd23f' : '#ffffff', 'center');\n}",
    "    g.stroke();\n  }\n\n  if (M.derby){ derbyHUD(); drawPitchSpeed(); } else drawHUD();\n  if (M.msg) tt(M.msg, W / 2, ty(150), 34, M.msg.includes('!') ? '#ffd23f' : '#ffffff', 'center');\n}")
rep("  g.drawImage(PLATE, W / 2 - 550 * s, 0, 1100 * s, H);          // the field with NO people in it",
    "  g.drawImage(M && M.derby && ready(DPITCH) ? DPITCH : PLATE, W / 2 - 550 * s, 0, 1100 * s, H);          // the field with NO people in it")
rep("  if (!B){ drawBatterView(16); return; }\n  if (gxOK())", "  if (!B){ drawBatterView(16); return; }\n  if (M.derby){ drawDerbyHit(B); return; }\n  if (gxOK())")
rep("function drawOver(){\n  btns = [];", "function drawOver(){\n  if (M.derby) return drawDerbyOver();\n  btns = [];")
rep("function drawGameMenu(){\n  btns = [];", "function drawGameMenu(){\n  if (M.derby) return drawDerbyPause();\n  btns = [];")

# ── the menus ──
rep("      button(W / 2 - 34, 164, 68, 18, 'ROSTER', () => menu = 'roster');", "      button(W / 2 - 34, 164, 68, 18, 'MINIGAMES', () => menu = 'minigames');")
rep("  else if (menu === 'shop'){ drawShop(); return; }", "  else if (menu === 'minigames'){ drawMinigames(); return; }\n  else if (menu === 'derbypick'){ drawDerbyPick(); return; }\n  else if (menu === 'shop'){ drawShop(); return; }")

# ── splice the derby module in before the input section, and hook it up for tests ──
mod = open('tools/derby.js', encoding='utf-8').read()
marker = "// ───────────────────────────────────────────────────────────────────────────\n//  INPUT\n"
assert s.count(marker) == 1
s = s.replace(marker, mod + "\n" + marker)
rep("  tap: (x, y) => { for (const b of btns)", "  derbyStart, derbyEnd, derbyPt, DHIT, DPITCH, derbyDist, DH,\n  tap: (x, y) => { for (const b of btns)")

s = s.replace("BUILD = '11-08b'", "BUILD = '11-09a'"); s = re.sub(r"gl3d\.js\?v=11-08b", "gl3d.js?v=11-09a", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
