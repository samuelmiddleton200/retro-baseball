s=open('index.html',encoding='utf-8').read()
a=s.index("    let top = -1;"); b=s.index("    if (n) hx = sx / n;")
s=s[:a]+"""    let sx = 0, n = 0;       // the helmet: magenta pixels in the upper half (the bat tip can poke above the head)
    for (let y = 0; y < cv.height * .5; y++) for (let xx = 0; xx < cv.width; xx++){ const q = (y * cv.width + xx) * 4; if (d[q + 3] > 60 && d[q] > 90 && d[q + 2] > 90 && d[q + 1] < d[q] * .6){ sx += xx; n++; } }
"""+s[b:]
s=s.replace("BUILD = '11-01c'","BUILD = '11-01d'")
open('index.html','w',encoding='utf-8').write(s)
