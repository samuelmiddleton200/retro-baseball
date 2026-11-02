s=open('index.html',encoding='utf-8').read()
old="function releasePt(){ const m = proj(60.5, 0); return { x: m.x + 7 * TU, y: m.y - 62 * TU }; }"
assert old in s
s=s.replace(old,'''function releasePt(){
  // the ball leaves the hand of the painted pitcher: sprite pixel (28, 59) of the release frame, so it never pops in somewhere else
  if (typeof GPP !== 'undefined' && GPP.ready && plateOK()){ const k = 80 * TU / (402 * .96); return { x: tx(412) - 160 * k + 28 * k, y: ty(232) - 402 * k + 59 * k }; }
  const m = proj(60.5, 0); return { x: m.x + 7 * TU, y: m.y - 62 * TU };
}''')
old2="    const k = clamp(P.caught / 260, 0, 1), end = mittPt(), from = ballAt(1);\n    const x = lerp(from.x, end.x, k), y = lerp(from.y, end.y, k);"
assert old2 in s
s=s.replace(old2,"    const k0 = clamp(P.caught / 260, 0, 1), k = k0 * k0 * (3 - 2 * k0), end = mittPt(), from = ballAt(1);\n    const x = lerp(from.x, end.x, k), y = lerp(from.y, end.y, k);")
# no frame without a ball between the end of the flight and the catch
old3="  else if (P && P.caught > 0 && P.state !== 'inplay'){            // into the catcher's mitt, with a little pop"
assert old3 in s
s=s.replace(old3,"  else if (P && P.thrown && P.t >= P.dur && !(P.caught > 0) && P.state !== 'inplay' && !P.result){ const e = ballAt(1); drawBall(e.x, e.y, e.r); }\n"+old3)
s=s.replace("BUILD = '11-01l'","BUILD = '11-02a'")
open('index.html','w',encoding='utf-8').write(s)
