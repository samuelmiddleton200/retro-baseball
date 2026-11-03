s=open('index.html',encoding='utf-8').read()
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:70]); s=s.replace(old,new)
rep("function runCycle(right, ph){","""// the painted side-view run cycle (assets/gp/run0-7, from ChatGPT; faces right, mirrored to run left)
const GPR = { img: [], ready: false, hx: [] };
for (let i = 0; i < 8; i++){ const im = new Image(); im.onload = () => { im._ok = true; GPR.ready = GPR.img.every(f => f._ok); }; im.onerror = () => {}; im.src = `assets/gp/run${i}.png?b=1`; GPR.img.push(im); }
function gpRunHead(i){                                   // x of the cap in each frame, so the body stays still while the legs swing
  if (GPR.hx[i] != null) return GPR.hx[i];
  const im = GPR.img[i]; let hx = im.naturalWidth / 2;
  try {
    const cv = document.createElement('canvas'); cv.width = im.naturalWidth; cv.height = im.naturalHeight;
    const x = cv.getContext('2d'); x.drawImage(im, 0, 0); const d = x.getImageData(0, 0, cv.width, cv.height).data; let sx = 0, n = 0;
    for (let y = 0; y < cv.height * .4; y++) for (let xx = 0; xx < cv.width; xx++){ const q = (y * cv.width + xx) * 4; if (d[q + 3] > 60 && d[q] > 90 && d[q + 2] > 90 && d[q + 1] < d[q] * .6){ sx += xx; n++; } }
    if (n) hx = sx / n;
  } catch (e){}
  return GPR.hx[i] = hx;
}
function runCycle(right, ph){
  if (GPR.ready) return { run:1, i: Math.floor(ph * 8) % 8, flip: !right };""")
rep("      if (p.sp.bat) gpStamp(GP.batter[0], 'B0', p.cap, q.x, q.y, hPx / TU, false, .96);",
    "      if (p.sp.run && GPR.ready){ const i = p.sp.i, dx = gpRunHead(i) - gpRunHead(0); gpStamp(GPR.img[i], 'RN' + i, p.cap, q.x, q.y, hPx / TU, !!p.sp.flip, .96, null, dx); return; }\n      if (p.sp.bat) gpStamp(GP.batter[0], 'B0', p.cap, q.x, q.y, hPx / TU, false, .96);")
s=s.replace("BUILD = '11-02k'","BUILD = '11-02l'")
open('index.html','w',encoding='utf-8').write(s)
import re
m=re.findall(r'<script>(.*?)</script>',s,re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js','w',encoding='utf-8').write(max(m,key=len))
