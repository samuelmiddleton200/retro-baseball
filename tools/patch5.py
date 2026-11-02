s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

# small cards (under 48 wide) get a compact layout: bigger face, one tidy row of the four ratings, no cramped list
rep("  const k = w / CARD_W, mini = w < 34;\n", "  const k = w / CARD_W, mini = w < 34, compact = w < 48;\n")
rep("const px = x + F, py = y + F, pw = w - F * 2, ph = Math.round(h * .52);", "const px = x + F, py = y + F, pw = w - F * 2, ph = Math.round(h * (compact ? .60 : .52));")
rep("    text(team.ab, px + 1 + bw / 2, py + 2 + Math.round(1 * k), lumB > .55 ? '#101010' : '#ffffff', Math.max(5, Math.round(5.5 * k)), 'center', bw - 3);",
    "    if (!compact) text(team.ab, px + 1 + bw / 2, py + 2 + Math.round(1 * k), lumB > .55 ? '#101010' : '#ffffff', Math.max(5, Math.round(5.5 * k)), 'center', bw - 3);")
rep("  const ny = py + ph + 1, nh = Math.round(11 * k);\n  R(px, ny, pw, nh, '#07090f'); R(px, ny + nh - 1, pw, 1, P.frame);",
    "  const ny = py + ph + 1, nh = Math.round((compact ? 9 : 11) * k);\n  R(px, ny, pw, nh, '#07090f'); R(px, ny + nh - 1, pw, 1, P.frame);")
rep("  text(nm, px + pw / 2, ny + Math.round(2.4 * k), '#ffffff', Math.max(5, Math.round(7 * k)), 'center', pw - 4);",
    "  text(compact ? parts[parts.length - 1].toUpperCase() : nm, px + pw / 2, ny + Math.round((compact ? 1.6 : 2.4) * k), '#ffffff', Math.max(5, Math.round(7 * k)), 'center', pw - 4);")
rep("  R(px, sy, pw, boxH, '#0a0d16');\n  const rowH = boxH / 4, fs = clamp(Math.round(rowH - 1.5), 5, 9);\n  statsOf(c).forEach(([lbl, key], i) => {",
    "  R(px, sy, pw, boxH, '#0a0d16');\n  if (compact){\n    statsOf(c).forEach(([lbl, key], i) => text(String(c[key]), px + pw * (i + .5) / 4, sy + Math.max(0, (boxH - 5) / 2), colOf(c[key]), 5, 'center'));\n    return;\n  }\n  const rowH = boxH / 4, fs = clamp(Math.round(rowH - 1.5), 5, 9);\n  statsOf(c).forEach(([lbl, key], i) => {")

# the trade screen's labels
rep("    text(TIER_LABEL[ti].slice(0, 7), x + 26, 38, on ? '#fff' : '#8e97a8', 6, 'center');\n    text(ti === 5 ? 'max' : `${n} spare`, x + 26, 45, ti === 5 ? '#5c6473' : n >= TRADE_N ? '#9af0ae' : '#6c7587', 6, 'center');",
    "    text(TIER_LABEL[ti], x + 26, 38, on ? '#fff' : UI.ice, 6, 'center', 48);\n    text(ti === 5 ? 'max' : `${n} spare`, x + 26, 45, ti === 5 ? '#8aa0d0' : n >= TRADE_N ? '#9af0ae' : '#ffffff', 6, 'center', 48);")
rep("text(`+${list.length - per * 2} more (lowest shown first)`, W / 2, H - 52, '#6c7587', 6, 'center');", "text(`+${list.length - per * 2} more (lowest shown first)`, W / 2, H - 52, UI.ice, 6, 'center');")
rep("textb('Red is the top colour: nothing to trade up to.', W / 2, 90, '#8e97a8', 8, 'center');", "textb('Red is the top colour: nothing to trade up to.', W / 2, 90, '#ffffff', 8, 'center');")
rep("textb('No spare cards of this colour (lineup cards cannot be traded).', W / 2, 90, '#8e97a8', 8, 'center');", "textb('No spare cards of this colour (lineup cards cannot be traded).', W / 2, 90, '#ffffff', 8, 'center', W - 20);")
open('index.html', 'w', encoding='utf-8').write(s)
print('patched')
