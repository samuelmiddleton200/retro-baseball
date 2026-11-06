s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)
rep("  if (B.t >= P.t1){\n    const c = P.run.c, extra =",
"""  if (B.t >= P.t1){
    const c = P.run.c;
    // a FORCE play: the runner has to go and nobody who pushes him has been put out, so the out is made the moment the man on the bag has the ball. No waiting, and he can turn it
    const behind = Object.keys(RUNCTL).filter(k => k !== P.run.key && (k === 'runB' || RUNCTL[k].s0 < c.s0));
    if (isGPlay(B) && !c.back && !c.out && c.forced && P.run.nb === c.s0 + 90 && c.pos < P.run.nb - .05 && behind.every(k => !RUNCTL[k].out)){
      c.out = true; c.cap = c.pos; c.v = 0; c.outT = B.t; say('OUT!'); B.pass = { ph:'hold', x:P.to[0], y:P.to[1], t0:B.t + .45 }; return;
    }
    const extra =""")
s = s.replace("BUILD = '11-11l'", "BUILD = '11-11m'").replace("gl3d.js?v=11-11l", "gl3d.js?v=11-11m")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
