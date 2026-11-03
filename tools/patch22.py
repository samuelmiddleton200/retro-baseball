s=open('index.html',encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70]); s=s.replace(old,new)
a=s.index("const GPR = { img: [], ready: false, hx: [] };")
b=s.index("function gxSprites(list, B){")
new='''// the painted run cycles, one sheet per direction of travel (ChatGPT sheets, 8 frames each): side (faces right, mirrored for left), toward the camera, away from it
const GPR = { side:[], front:[], back:[], ready:false, hx:{} };
const RUN_SETS = { side:'run', front:'runf', back:'runb' };
RUN_SETS.front = 'runf'; RUN_SETS.back = 'runb';
for (const k of ['side', 'front', 'back']) for (let i = 0; i < 8; i++){
  const im = new Image(); im.onload = () => { im._ok = true; GPR.ready = ['side', 'front', 'back'].every(d => GPR[d].length === 8 && GPR[d].every(f => f._ok)); }; im.onerror = () => {};
  im.src = `assets/gp/${RUN_SETS[k]}${i}.png?b=2`; GPR[k].push(im);
}
function gpRunHead(dir, i){                              // x of the cap in each frame, so the body stays still while the legs swing
  const key = dir + i; if (GPR.hx[key] != null) return GPR.hx[key];
  const im = GPR[dir][i]; let hx = im.naturalWidth / 2;
  try {
    const cv = document.createElement('canvas'); cv.width = im.naturalWidth; cv.height = im.naturalHeight;
    const x = cv.getContext('2d'); x.drawImage(im, 0, 0); const d = x.getImageData(0, 0, cv.width, cv.height).data; let sx = 0, n = 0;
    for (let y = 0; y < cv.height * .4; y++) for (let xx = 0; xx < cv.width; xx++){ const q = (y * cv.width + xx) * 4; if (d[q + 3] > 60 && d[q] > 90 && d[q + 2] > 90 && d[q + 1] < d[q] * .6){ sx += xx; n++; } }
    if (n) hx = sx / n;
  } catch (e){}
  return GPR.hx[key] = hx;
}
// yaw: the way he is heading (atan2 of sideways, depth); the camera looks out from behind home, so negative depth = running away from us
function runCycle(yaw, ph){
  const sn = Math.sin(yaw), cs = Math.cos(yaw), right = sn > 0;
  if (GPR.ready){
    const dir = Math.abs(sn) >= .62 ? 'side' : cs < 0 ? 'back' : 'front';
    return { run:1, dir, i: Math.floor(ph * 8) % 8, flip: dir === 'side' && !right };
  }
  const a = Math.floor(ph * 2) % 2 === 0, hop = Math.abs(Math.sin(ph * Math.PI * 2));
  return right ? { f: a ? 2 : 3, flip: !a, bob: hop, lean: .07 } : { f: a ? 3 : 2, flip: !a, bob: hop, lean: -.07 };
}
'''
s=s[:a]+new+s[b:]
rep("    const runSp = (mv) => runCycle(Math.sin(mv.yaw) > 0, mv.ph);","    const runSp = (mv) => runCycle(mv.yaw, mv.ph);")
rep("runCycle(Math.sin(dirYaw) > 0, mv.ph)","runCycle(dirYaw, mv.ph)")
rep("      if (p.sp.run && GPR.ready){ const i = p.sp.i, dx = gpRunHead(i) - gpRunHead(0); gpStamp(GPR.img[i], 'RN' + i, p.cap, q.x, q.y, hPx / TU, !!p.sp.flip, .96, null, dx); return; }",
    "      if (p.sp.run && GPR.ready){ const i = p.sp.i, d = p.sp.dir, dx = gpRunHead(d, i) - gpRunHead(d, 0); gpStamp(GPR[d][i], 'RN' + d + i, p.cap, q.x, q.y, hPx / TU, !!p.sp.flip, .96, null, dx); return; }")
s=s.replace("BUILD = '11-02l'","BUILD = '11-02m'")
open('index.html','w',encoding='utf-8').write(s)
import re
m=re.findall(r'<script>(.*?)</script>',s,re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js','w',encoding='utf-8').write(max(m,key=len))
