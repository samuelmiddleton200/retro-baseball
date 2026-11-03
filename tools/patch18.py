s=open('index.html',encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70]); s=s.replace(old,new)
# smaller ball: true scale (a 2.9 in ball next to a 6 ft batter drawn 196 px tall is ~8 px wide at the plate; it was 9 px, and 3 px at the mound where true size is 2)
rep("r: lerp(1.6, 4.6, e) };","r: lerp(1.15, 3.5, e) };")
# the end of the flight: the ball stops where the pitch ended and stays put (with a soft ring) instead of sliding into the mitt
a=s.index("  else if (P && P.thrown && P.t >= P.dur && !(P.caught > 0) && P.state !== 'inplay' && !P.result){")
b=s.index("  drawBehindPlate();\n  // the strike zone, a faint box over the plate")
new='''  else if (P && P.thrown && P.t >= P.dur && P.state !== 'inplay' && P.state !== 'flight'){
    // the pitch is over: the ball stops dead where it ended and stays for the whole call (about 1.4 s), so you can see where it landed
    const e = ballAt(1), tn = P.state === 'catch' ? (P.caught || 0) : CATCH_TIME + (P.hold || 0);
    if (tn < 700){ const k = tn / 700; g.strokeStyle = `rgba(255,255,255,${(1 - k) * .75})`; g.lineWidth = 1; g.beginPath(); g.arc(e.x, e.y, e.r + 2 + k * 9, 0, 7); g.stroke(); }
    drawBall(e.x, e.y, e.r);
  }

'''
s=s[:a]+new+s[b:]
s=s.replace("BUILD = '11-02e'","BUILD = '11-02f'")
open('index.html','w',encoding='utf-8').write(s)
print('ok')
