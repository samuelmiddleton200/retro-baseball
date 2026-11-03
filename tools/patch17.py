s=open('index.html',encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70]); s=s.replace(old,new)
rep("  DRAG_K: 0.0022,               // a = -k |v| v   (with the lift below: 105 mph at 28 deg goes ~395 ft and hangs ~5.2 s; 95 mph ~350 ft)\n  LIFT_K: 0.0012,",
    "  DRAG_K: 0.0018,               // a = -k |v| v   (tuned against Statcast-style numbers: 100 mph at 10 deg ~2 s, 20 deg ~3.4 s, 28 deg ~4.3 s and ~370 ft, 45 deg ~5.8 s)\n  LIFT_K: 0.00055,")
rep("  CQ_MIN: 0.5, CQ_MAX: 1.0,     // exit velo = power * contact quality",
    "  CQ_MIN: 0.72, CQ_MAX: 1.12,   // exit velo = power * contact quality: an 84-power hitter averages ~88 mph, the league average")
rep("  swing.dErr = dErr; swing.tN = tN; swing.sN = sN;","  swing.dErr = dErr; swing.tN = tN; swing.sN = sN; swing.plane = plane;")
rep("  // a pitch up in the zone gets lifted, a pitch down gets beaten into the ground\n  const la = clamp(lerp(-10, 40, bell()) + qual * 9 - P.ty * 11, -22, 56);",
    """  // Launch angle comes from where the barrel meets the ball: under it lifts it (fly ball, pop-up), on top of it beats it into the
  // ground, square puts it on a line. A well-centred swing is more consistent. The average works out near 12 degrees, like the league.
  const under = clamp(swing && swing.plane != null ? swing.plane - P.ty : 0, -.9, .9);          // + = the barrel was below the ball's height
  const la = clamp(12 + under * 42 + (bell() - .5) * 34 * lerp(1.15, .5, qual), -25, 64);""")
s=s.replace("BUILD = '11-02d'","BUILD = '11-02e'")
open('index.html','w',encoding='utf-8').write(s)
print('ok')
