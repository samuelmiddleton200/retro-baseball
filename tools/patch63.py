s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# who does what when it goes to the outfield: to the left the SS stands at the edge of the infield dirt for the short throw and 2B takes second; to the right the 2B is the cut-off man and the SS takes second
rep("const BAG_COVER = [", """const outfieldRoles = land => {
  const len = Math.hypot(land.d, land.lat) || 1, k = Math.min(len * .6, 138) / len, left = land.lat <= 0;
  return { cutPos: left ? 'SS' : '2B', bagPos: left ? '2B' : 'SS', cut:[land.d * k, land.lat * k] };      // 138 ft out is where the infield dirt meets the outfield grass
};
const BAG_COVER = [""")
rep("  const walk = (cur, rng, fps, tRel, legs, used, relays) => {", "  const roles = BALL && BALL.land && !live ? outfieldRoles(BALL.land) : null;\n  let loose = false;                                                      // first try only the real cut-off man where he stands; a long throw then goes through anyone along the line\n  const walk = (cur, rng, fps, tRel, legs, used, relays) => {")
rep("      if (!live) for (const fr of [.5, .65, .8, .9, .98]){", "      if (roles && m.pos === roles.cutPos && Math.hypot(tgt[0], tgt[1]) < 150 === false) spots.push(roles.cut);\n      if (!live && loose) for (const fr of [.5, .65, .8, .9, .98]){")
rep("  walk(from, throwRange(thrower.man.fielding), thrower.armFps, t0 + tr, [], [], []);\n  if (!best){", "  walk(from, throwRange(thrower.man.fielding), thrower.armFps, t0 + tr, [], [], []);\n  if (!best && !live){ loose = true; walk(from, throwRange(thrower.man.fielding), thrower.armFps, t0 + tr, [], [], []); }\n  if (!best){")
# planCover outfield branch
a = s.index("    const len = Math.hypot(land.d, land.lat) || 1, dir = { d:land.d / len, lat:land.lat / len };")
b = s.index("    send(byPos('1B'), STAND[1][0], STAND[1][1], 1);\n    send(byPos('3B'), STAND[3][0], STAND[3][1], 3);")
s = s[:a] + """    const rl = outfieldRoles(land), cutMan = byPos(rl.cutPos), bagMan = byPos(rl.bagPos);
    send(cutMan, rl.cut[0], rl.cut[1], 0);                                                        // the cut-off man at the edge of the infield dirt, lined up with the throw
    send(bagMan, STAND[2][0] - 2, STAND[2][1] + (bagMan === byPos('SS') ? 3 : -2), 2);            // the other takes second
""" + s[b:]
s = s.replace("BUILD = '11-11e'", "BUILD = '11-11f'").replace("gl3d.js?v=11-11e", "gl3d.js?v=11-11f")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
