s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

# 1) six clearly different colours: grey, green, blue, PURPLE, GOLD, red  (orange read as bronze)
a = s.index("const TIERS = [")
b = s.index("];", a) + 2
s = s[:a] + """const TIERS = [
  { min:60,  col:'#9aa6bd', name:'Common'    },
  { min:70,  col:'#54d67a', name:'Uncommon'  },
  { min:80,  col:'#4aa3ff', name:'Rare'      },
  { min:90,  col:'#b26bff', name:'Epic'      },
  { min:100, col:'#ffd23f', name:'Legendary' },
  { min:110, col:'#ff4d4d', name:'Mythic'    },
];""" + s[b:]
rep("  { frame:'#ffd23f', lite:'#fff2b0', dark:'#7a5a10', top:'#c99a22', bot:'#3a2a0a' },\n  { frame:'#ff9330', lite:'#ffd2a0', dark:'#8a3f08', top:'#d9661a', bot:'#40190a' },\n",
    "  { frame:'#b26bff', lite:'#ead6ff', dark:'#4a1d85', top:'#8d48d9', bot:'#25103f' },\n  { frame:'#ffd23f', lite:'#fff2b0', dark:'#7a5a10', top:'#d6a526', bot:'#3a2a0a' },\n")
rep("const rgb = ti === 3 ? '255,210,63' : ti === 4 ? '255,147,48' : '255,77,77';", "const rgb = ti === 3 ? '178,107,255' : ti === 4 ? '255,210,63' : '255,77,77';")
rep("const rgb = sp.ti >= 5 ? '255,77,77' : sp.ti >= 4 ? '255,147,48' : sp.ti >= 3 ? '255,210,63' : '255,255,255';", "const rgb = sp.ti >= 5 ? '255,77,77' : sp.ti >= 4 ? '255,210,63' : sp.ti >= 3 ? '178,107,255' : '255,255,255';")
rep("each card is rated 60-120, the colour is its tier", "colour = rating: 60s grey, 70s green, 80s blue, 90s purple, 100s gold, 110+ red")

# 2) pack art
a = s.index("// a foil pack: a tall wrapper with a batter's silhouette behind the name")
b = s.index("function drawShop(){")
s = s[:a] + open('tools/pack_code.js', encoding='utf-8').read() + s[b:]

# 3) the card back: everything fits, and the flip is animated
a = s.index("function drawCardBackInner(x, y, c, w, h, t){")
b = s.index("// ── opening a pack ──")
s = s[:a] + """function drawCardBackInner(x, y, c, w, h, t){
  const ovr = ovrOf(c), ti = tierIdx(c), P = CARD_PAL[ti], k = w / CARD_W;
  const F = cardFrame(x, y, w, h, ti, t, k);
  const ix = x + F, iy = y + F, iw = w - F * 2, ih = h - F * 2;
  for (let i = 0; i < ih; i++) R(ix, iy + i, iw, 1, mix('#151d2e', '#0a0e17', i / ih));
  const fs = Math.max(5, Math.round(6.5 * k));
  textb(c.name.toUpperCase(), x + w / 2, iy + 3 * k, '#ffffff', Math.max(6, Math.round(7 * k)), 'center', iw - 4);
  text(`${TIER_LABEL[ti]} \\u00b7 ${c.pos}`, x + w / 2, iy + 12 * k, P.frame, Math.max(5, Math.round(5.5 * k)), 'center', iw - 4);
  R(ix + 3, iy + 20 * k, iw - 6, 1, P.dark);
  const s = c.st || newStat();
  const rows = isPitcher(c)
    ? [['IP', s.ip], ['K', s.ko], ['ER', s.er], ['W-L', `${s.w}-${s.l}`]]
    : [['AB', s.ab], ['H', s.h], ['HR', s.hr], ['RBI', s.rbi], ['AVG', (s.ab ? s.h / s.ab : 0).toFixed(3).replace('0.', '.')]];
  text('THIS SEASON', x + w / 2, iy + 23 * k, '#8fa0c8', Math.max(5, Math.round(5 * k)), 'center', iw - 4);
  const rh = 7.2 * k;
  rows.forEach((r, i) => {
    const ry = iy + 31 * k + i * rh;
    if (i % 2) R(ix + 2, ry - 1, iw - 4, rh, 'rgba(255,255,255,.05)');
    text(r[0], ix + 4 * k, ry, '#9fb0d8', fs); text(String(r[1]), ix + iw - 4 * k, ry, '#ffffff', fs, 'right');
  });
  const by = iy + 31 * k + 5 * rh + 2 * k;
  R(ix + 3, by, iw - 6, 1, P.dark);
  text(`OVERALL ${ovr}`, x + w / 2, by + 3 * k, P.lite, Math.max(5, Math.round(5.5 * k)), 'center', iw - 4);
  text(`UPGRADE ${c.lvl || 0}/10`, x + w / 2, by + 10 * k, '#9af0ae', Math.max(5, Math.round(5 * k)), 'center', iw - 4);
}

""" + s[b:]
rep("  if (cardFlip) drawCardBack(cx, cy, c, cw, chh); else drawCard(cx, cy, c, cw, chh, frame);",
    "  // the flip: the card turns edge-on, and the other side comes round\n  cardFlipA += clamp((cardFlip ? 1 : 0) - cardFlipA, -.085, .085);\n  const fsx = Math.max(.03, Math.abs(Math.cos(cardFlipA * Math.PI)));\n  g.save(); g.translate(cx + cw / 2, 0); g.scale(fsx, 1); g.translate(-(cx + cw / 2), 0);\n  if (cardFlipA > .5) drawCardBack(cx, cy, c, cw, chh, frame); else drawCard(cx, cy, c, cw, chh, frame);\n  g.restore();")
rep("let upStat = 0;\nfunction drawCardView(){", "let upStat = 0, cardFlipA = 0;\nfunction drawCardView(){")
# 4) trade grid clear of the chips
rep("const x = 8 + (i % per) * (cw + 4), y = 60 + Math.floor(i / per) * (ch + 6), sel = tradeSel.includes(c.id);", "const x = 8 + (i % per) * (cw + 4), y = 66 + Math.floor(i / per) * (ch + 6), sel = tradeSel.includes(c.id);")
open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
