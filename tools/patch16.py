s=open('index.html',encoding='utf-8').read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(s.count(old),old[:80]); s=s.replace(old,new)

# pitcher + catcher
rep("S.people.push(gxPerson('pit', 'pitch', pit, ft, 0, -60.5, face(0, -60.5), GL3D.poseReady(t), { y:.9, glove:1 }));",
    "S.people.push(gxPerson('pit', 'pitch', pit, ft, 0, -60.5, face(0, -60.5), GL3D.poseReady(t), { y:.9, glove:1, sp:{ f:0 } }));")
rep("S.people.push(gxPerson('cat', 'catch', ft.lineup[7] || ft.lineup[0], ft, 0, 3.4, Math.PI, GL3D.poseCatcher(0, 2.4, t), { glove:1, cap2:ft.c1 }));",
    "S.people.push(gxPerson('cat', 'catch', ft.lineup[7] || ft.lineup[0], ft, 0, 3.4, Math.PI, GL3D.poseCatcher(0, 2.4, t), { glove:1, cap2:ft.c1, sp:{ bat:1 } }));")
# fielders
rep("    let pose, yaw = face(X, Z);\n    if (f.go && !f.chasing){","    let pose, yaw = face(X, Z), sp = { f: ((frame + f.i * 41) % 170) < 100 ? 0 : 1 };\n    const runSp = (mv) => ({ f: Math.sin(mv.yaw) > 0 ? 2 : 3, bob: Math.sin(mv.ph * 6.28) });      // frame 2 runs toward screen-right, 3 toward screen-left\n    if (f.go && !f.chasing){")
rep("      if (f.moving){ yaw = mv.moved > .02 ? mv.yaw : yaw; pose = GL3D.poseRun(mv.ph, f.speed); }","      if (f.moving){ yaw = mv.moved > .02 ? mv.yaw : yaw; pose = GL3D.poseRun(mv.ph, f.speed); sp = runSp(mv); }")
rep("        pose = f.go.bag && B.thr ? GL3D.poseCatch(.55) : GL3D.poseReady(t + f.i * .7);    // on the bag the glove goes up for the throw\n      }\n      S.people.push(gxPerson(key, 'field', f.man, ft, X, Z, yaw, pose, { glove:1 }));",
    "        pose = f.go.bag && B.thr ? GL3D.poseCatch(.55) : GL3D.poseReady(t + f.i * .7);    // on the bag the glove goes up for the throw\n        if (f.go.bag && B.thr) sp = { f:5 };\n      }\n      S.people.push(gxPerson(key, 'field', f.man, ft, X, Z, yaw, pose, { glove:1, sp }));")
rep("        pose = B.grounder && dist < 11 ? GL3D.poseGrab(1 - dist / 11) : near ? GL3D.poseCatch(1 - dist / 14) : GL3D.poseRun(mv.ph, f.speed);",
    "        pose = B.grounder && dist < 11 ? GL3D.poseGrab(1 - dist / 11) : near ? GL3D.poseCatch(1 - dist / 14) : GL3D.poseRun(mv.ph, f.speed);\n        sp = B.grounder && dist < 11 ? { f:6 } : near ? { f: B.h > 5 ? 4 : 5 } : runSp(mv);")
rep("        if (B.thr){ const th = B.thr.to; yaw = Math.atan2(th[1] - X, -th[0] - Z); }\n      }\n    } else pose = GL3D.poseReady(t + f.i * .7);\n    S.people.push(gxPerson(key, 'field', f.man, ft, X, Z, yaw, pose, { glove:1 }));",
    "        if (B.thr){ const th = B.thr.to; yaw = Math.atan2(th[1] - X, -th[0] - Z); }\n        sp = B.isCatch ? { f:5 } : B.foul ? sp : { f:7, flip: B.thr ? B.thr.to[1] < X : false };\n      }\n    } else pose = GL3D.poseReady(t + f.i * .7);\n    S.people.push(gxPerson(key, 'field', f.man, ft, X, Z, yaw, pose, { glove:1, sp }));")
# runners
rep("      S.people.push(gxPerson(key, 'run', man, bt, X, Z, dirYaw, B.t < dly ? GL3D.poseBatter(1, t) : (held ? GL3D.poseReady(t) : GL3D.poseRun(mv.ph, man.speed)), {}));",
    "      S.people.push(gxPerson(key, 'run', man, bt, X, Z, dirYaw, B.t < dly ? GL3D.poseBatter(1, t) : (held ? GL3D.poseReady(t) : GL3D.poseRun(mv.ph, man.speed)), { sp: B.t < dly || held ? { f:0 } : { f: Math.sin(dirYaw) > 0 ? 2 : 3, bob: Math.sin(mv.ph * 6.28) } }));")
# drawing
rep("    const prev = GX.sp[p.key]; GX.sp[p.key] = [p.x, p.z];\n",
"""    const prev = GX.sp[p.key]; GX.sp[p.key] = [p.x, p.z];
    if (p.sp && GPF.ready && GP.ready){                        // the painted figures: the same sprites as the at-bat view, sized by perspective
      const head = GL3D.toScreen(p.x, 6.2, p.z, W, H), hPx = Math.max(10, (q.y - head.y) * 1.05);
      const bob = (p.sp.bob || 0) * hPx * .03;
      if (p.sp.bat) gpStamp(GP.batter[0], 'B0', p.cap, q.x, q.y, hPx / TU, false, .96);
      else gpStamp(GPF.img[p.sp.f], 'FD' + p.sp.f, p.cap, q.x, q.y - bob, hPx / TU, !!p.sp.flip, .96);
      return;
    }
""")
s=s.replace("BUILD = '11-02b'","BUILD = '11-02c'")
open('index.html','w',encoding='utf-8').write(s)
print('ok')
