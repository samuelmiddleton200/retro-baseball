s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

a = s.index("// yaw: the way he is heading (atan2 of sideways, depth)")
b = s.index("function gxSprites(list, B){")
new = '''// yaw: the way he is heading (atan2 of sideways, depth); the camera looks out from behind home, so negative depth = running away from us.
// A runner's path bends, so the raw direction wobbles from frame to frame: he only changes sheet after the new direction has held for 10 frames,
// and the stride advances with distance run (one 8-frame cycle every 15 ft, about 15 frames a second at full speed).
const RUNDIR = {};
function runCycle(yaw, ph, key){
  const sn = Math.sin(yaw), cs = Math.cos(yaw);
  if (GPR.ready){
    const cand = Math.abs(sn) >= .62 ? (sn > 0 ? 'right' : 'left') : cs < 0 ? 'back' : 'front';
    let st = RUNDIR[key]; if (!st) st = RUNDIR[key] = { cur:cand, cand, n:0 };
    if (cand === st.cur) st.n = 0; else if (cand === st.cand){ if (++st.n >= 10){ st.cur = cand; st.n = 0; } } else { st.cand = cand; st.n = 1; }
    const side = st.cur === 'left' || st.cur === 'right';
    return { run:1, dir: side ? 'side' : st.cur, i: Math.floor(ph * 4) % 8, flip: st.cur === 'left' };
  }
  const right = sn > 0, a = Math.floor(ph * 2) % 2 === 0, hop = Math.abs(Math.sin(ph * Math.PI * 2));
  return right ? { f: a ? 2 : 3, flip: !a, bob: hop, lean: .07 } : { f: a ? 3 : 2, flip: !a, bob: hop, lean: -.07 };
}
'''
s = s[:a] + new + s[b:]
rep("    const runSp = (mv) => runCycle(mv.yaw, mv.ph);", "    const runSp = (mv) => runCycle(mv.yaw, mv.ph, key);")
rep("runCycle(dirYaw, mv.ph)", "runCycle(dirYaw, mv.ph, key)")
s = s.replace("BUILD = '11-02r'", "BUILD = '11-02s'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
