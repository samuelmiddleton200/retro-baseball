s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# a man holding the ball ON a bag does not throw away from a runner who could turn round and get back: he holds it (anybody who comes back to the bag is tagged) until the runner is committed
rep("""function pickTarget(B, holder, px, py){
  let best = null;""", """function pickTarget(B, holder, px, py){
  let best = null;
  const sh = baseS(px, py);                                                                               // the base he stands on, if the ball is in his hands on a bag""")
rep("""    if (margin <= .05) continue;                                                                          // that throw cannot get him: they hold it instead
    if (!best || margin > best.margin) best = { key, c, nb, bi, back: dir < 0, margin, rt };""",
"""    if (margin <= .05) continue;                                                                          // that throw cannot get him: they hold it instead
    if (sh != null && nb !== sh){
      // a pickle: he is on a bag with the ball and the runner is between bases. If the runner could turn round, get back to the bag he left, and be there before the ball
      // has gone to the other base and come back, the throw is a gamble he does not take: he holds it, and anybody who comes back to the bag is tagged. He throws once the runner is committed.
      const bb = runBase(c, -dir), vmax = sprintFps(spdOf(c.man)), acc = vmax / CFG.RUNNER_ACCEL_T, dec = acc * 2, v0 = Math.abs(c.v || 0);
      const back = Math.abs(c.pos - bb) + v0 * v0 / (2 * dec), dA = vmax * vmax / (2 * acc);
      const tEscape = B.t + v0 / dec + (back <= dA ? Math.sqrt(2 * back / acc) : vmax / acc + (back - dA) / vmax);
      const tBall = rt.arr + 90 * CFG.GLOVE_PER_FT + 90 / (holder.armFps || 40);
      if (tEscape <= tBall + .1) continue;
    }
    if (!best || margin > best.margin) best = { key, c, nb, bi, back: dir < 0, margin, rt };""")
s = s.replace("BUILD = '11-12h'", "BUILD = '11-12i'").replace("gl3d.js?v=11-12h", "gl3d.js?v=11-12i")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
