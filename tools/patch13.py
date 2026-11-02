s=open('index.html',encoding='utf-8').read()
old="const PWARM = { k:'', n:0 };\nfunction drawPitcherAt(xL, yL, u){\n  if (!plateOK()) return drawPitcherAtOld(xL, yL, u);\n"
assert old in s
new='''const PWARM = { k:'', n:0 };
// painted pitcher (assets/gp/pitcher0-7): 0-1 set, 2 leg lift, 3-4 arm cocked, 5 release, 6 follow-through, 7 finish; same club colour as the fielders
const GPP = { img: [], ready: false };
for (let i = 0; i < 8; i++){ const im = new Image(); im.onload = () => { im._ok = true; GPP.ready = GPP.img.every(f => f._ok); }; im.onerror = () => {}; im.src = `assets/gp/pitcher${i}.png`; GPP.img.push(im); }
function drawPitcherAt(xL, yL, u){
  if (!plateOK()) return drawPitcherAtOld(xL, yL, u);
  if (GPP.ready){
    const pos = u < .70 ? (u / .70) * 5 : 5 + clamp((u - .70) / .16, 0, 1) * 2, f0 = Math.min(7, Math.floor(pos)), f1 = Math.min(7, f0 + 1), k = pos - f0, c1 = fldTeam().c1;
    const X = tx(412), Y = ty(232);
    gpStamp(GPP.img[f0], 'PT' + f0, c1, X, Y, 80, false, .96);
    if (k > .03 && f1 !== f0) gpStamp(GPP.img[f1], 'PT' + f1, c1, X, Y, 80, false, .96, k);
    return;
  }
'''
s=s.replace(old,new)
s=s.replace("BUILD = '11-01j'","BUILD = '11-01k'")
open('index.html','w',encoding='utf-8').write(s)
