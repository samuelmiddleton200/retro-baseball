s=open('index.html',encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(s.count(a),a[:60]); s=s.replace(a,b)
i=s.index("<script>")
s=s[:i]+"<script>if (location.protocol === 'file:') document.write('<script src=\"embed.js\"><\/script>');</script>\n"+s[i:]
rep("im.src = `assets/gp/${RUN_SETS[k]}${i}.png?b=2`;","im.src = SRC(`assets/gp/${RUN_SETS[k]}${i}.png`);")
rep("im.src = `assets/gp/batter${i}.png`;","im.src = SRC(`assets/gp/batter${i}.png`);")
rep("im.src = `assets/gp/fielder${i}.png`;","im.src = SRC(`assets/gp/fielder${i}.png`);")
rep("im.src = `assets/gp/pitcher${i}.png`;","im.src = SRC(`assets/gp/pitcher${i}.png`);")
rep("im.src = `assets/portraits/p${String(i).padStart(2, '0')}.png`;","im.src = SRC(`assets/portraits/p${String(i).padStart(2, '0')}.png`);")
j=s.index("let G = null;")
s=s[:j]+"const SRC = p => (window.EMB && window.EMB[p]) || p;      // recolourable sprites come from embed.js when the page is opened as a file\n"+s[j:]
s=s.replace("BUILD = '11-03l'","BUILD = '11-03m'")
open('index.html','w',encoding='utf-8').write(s)
