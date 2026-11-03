s=open('index.html',encoding='utf-8').read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(s.count(old),old[:80]); s=s.replace(old,new)

# 1) a real run cycle for everybody: two leg positions alternated with the stride (frame 2 and the mirror of frame 3 when going right, and the reverse going left),
#    plus a hop and a lean into the direction of travel
rep("    const runSp = (mv) => ({ f: Math.sin(mv.yaw) > 0 ? 2 : 3, bob: Math.sin(mv.ph * 6.28) });      // frame 2 runs toward screen-right, 3 toward screen-left",
    "    const runSp = (mv) => runCycle(Math.sin(mv.yaw) > 0, mv.ph);")
rep("      S.people.push(gxPerson(key, 'run', man, bt, X, Z, dirYaw, B.t < dly ? GL3D.poseBatter(1, t) : (held ? GL3D.poseReady(t) : GL3D.poseRun(mv.ph, man.speed)), { sp: B.t < dly || held ? { f:0 } : { f: Math.sin(dirYaw) > 0 ? 2 : 3, bob: Math.sin(mv.ph * 6.28) } }));",
    "      S.people.push(gxPerson(key, 'run', man, bt, X, Z, dirYaw, B.t < dly ? GL3D.poseBatter(1, t) : (held ? GL3D.poseReady(t) : GL3D.poseRun(mv.ph, man.speed)), { sp: B.t < dly || held ? { f:0 } : runCycle(Math.sin(dirYaw) > 0, mv.ph) }));")
rep("function gxSprites(list, B){","""// the run cycle, the same for the first baseman and the centre fielder: frame 2 runs toward screen-right and frame 3 toward screen-left; their mirrors
// give the other leg forward, so the legs swap every half stride
function runCycle(right, ph){
  const a = Math.floor(ph * 2) % 2 === 0, hop = Math.abs(Math.sin(ph * Math.PI * 2));
  return right ? { f: a ? 2 : 3, flip: !a, bob: hop, lean: .07 } : { f: a ? 3 : 2, flip: !a, bob: hop, lean: -.07 };
}
function gxSprites(list, B){""")
rep("""      const bob = (p.sp.bob || 0) * hPx * .03;
      if (p.sp.bat) gpStamp(GP.batter[0], 'B0', p.cap, q.x, q.y, hPx / TU, false, .96);
      else gpStamp(GPF.img[p.sp.f], 'FD' + p.sp.f, p.cap, q.x, q.y - bob, hPx / TU, !!p.sp.flip, .96);
      return;""","""      const bob = (p.sp.bob || 0) * hPx * .07;
      if (p.sp.bat) gpStamp(GP.batter[0], 'B0', p.cap, q.x, q.y, hPx / TU, false, .96);
      else if (p.sp.lean){ g.save(); g.translate(q.x, q.y - bob); g.rotate(p.sp.lean); gpStamp(GPF.img[p.sp.f], 'FD' + p.sp.f, p.cap, 0, 0, hPx / TU, !!p.sp.flip, .96); g.restore(); }
      else gpStamp(GPF.img[p.sp.f], 'FD' + p.sp.f, p.cap, q.x, q.y - bob, hPx / TU, !!p.sp.flip, .96);
      return;""")

# 2) the swing button is always the game's own (the picture of it is gone from the background)
a_ = s.index("  if (PLATE_ON){ if (armed)")
b_ = s.index(chr(10), a_) + 1
s = s[:a_] + s[b_:]

# 3) no shadow under the batter
rep("function gpStamp(img, key, c1, xL, yL, hT, flip, figFrac, alpha, dxSrc){","function gpStamp(img, key, c1, xL, yL, hT, flip, figFrac, alpha, dxSrc, noShadow){")
rep("  if (alpha == null || alpha >= 1){ g.fillStyle = 'rgba(20,14,6,.30)';","  if (!noShadow && (alpha == null || alpha >= 1)){ g.fillStyle = 'rgba(20,14,6,.30)';")
s=s.replace("gpStamp(GP.batter[f], 'B' + f, bt.c1, xL, yL, 196, lefty, null, null, gpHead(f) - GP.batter[f].naturalWidth / 2 - (gpHead(0) - GP.batter[0].naturalWidth / 2)); }",
            "gpStamp(GP.batter[f], 'B' + f, bt.c1, xL, yL, 196, lefty, null, null, gpHead(f) - GP.batter[f].naturalWidth / 2 - (gpHead(0) - GP.batter[0].naturalWidth / 2), true); }")
rep("    gpStamp(GP.batter[f0], 'B' + f0, bt.c1, xL, yL, 196, lefty, null, null, dx(f0));","    gpStamp(GP.batter[f0], 'B' + f0, bt.c1, xL, yL, 196, lefty, null, null, dx(f0), true);")
rep("    if (u > .02 && f1 !== f0) gpStamp(GP.batter[f1], 'B' + f1, bt.c1, xL, yL, 196, lefty, null, u, dx(f1));","    if (u > .02 && f1 !== f0) gpStamp(GP.batter[f1], 'B' + f1, bt.c1, xL, yL, 196, lefty, null, u, dx(f1), true);")
s=s.replace("BUILD = '11-02f'","BUILD = '11-02g'")
open('index.html','w',encoding='utf-8').write(s)
print('ok')
