s=open('index.html',encoding='utf-8').read()
old="function drawFielderSprite(xL, yL, pos, grab, hOver){\n  if (!plateOK()) return drawFielderSpriteOld(xL, yL, pos, grab);\n"
assert old in s
new='''// painted fielders (assets/gp/fielder0-7, from ChatGPT): 0-1 ready, 2-3 run, 4 reach, 5 catch, 6 scoop, 7 throw
const GPF = { img: [], ready: false };
for (let i = 0; i < 8; i++){ const im = new Image(); im.onload = () => { im._ok = true; GPF.ready = GPF.img.every(f => f._ok); }; im.onerror = () => {}; im.src = `assets/gp/fielder${i}.png`; GPF.img.push(im); }
function drawFielderSprite(xL, yL, pos, grab, hOver){
  if (!plateOK()) return drawFielderSpriteOld(xL, yL, pos, grab);
  if (GPF.ready){
    const i = Math.max(0, FIELDERS.findIndex(f => f[2] === pos)), f = ((frame + i * 37) % 150) < 90 ? 0 : 1;      // he shifts his weight every couple of seconds
    return gpStamp(GPF.img[f], 'FD' + f, fldTeam().c1, xL, yL, (hOver || figH(yL / TU)) * 1.55, pos === '1B' || pos === '2B' || pos === 'RF', .96);
  }
'''
s=s.replace(old,new)
open('index.html','w',encoding='utf-8').write(s)
