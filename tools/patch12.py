s=open('index.html',encoding='utf-8').read()
old="  return bakeStamp('p', 'P' + lookKey(p.look) + '|' + step, o, GL3D.posePitcher(step / 16), -.2, tx(412), ty(232), 74, false, 5.9);\n"
assert old in s
new='''  // the 17 windup poses are baked on first use (about 100 ms each): bake one extra per frame, unseen, so no pitch ever hitches
  const wk = lookKey(p.look); PWARM.k !== wk && (PWARM.k = wk, PWARM.n = 0);
  if (PWARM.n <= 16 && PWARM.n !== step){ const w = PWARM.n++; g.save(); g.globalAlpha = 0; bakeStamp('p', 'P' + wk + '|' + w, o, GL3D.posePitcher(w / 16), -.2, tx(412), ty(232), 74, false, 5.9); g.restore(); }
  return bakeStamp('p', 'P' + wk + '|' + step, o, GL3D.posePitcher(step / 16), -.2, tx(412), ty(232), 74, false, 5.9);
'''
s=s.replace(old,new)
s=s.replace("function drawPitcherAt(xL, yL, u){","const PWARM = { k:'', n:0 };\nfunction drawPitcherAt(xL, yL, u){",1)
open('index.html','w',encoding='utf-8').write(s)
