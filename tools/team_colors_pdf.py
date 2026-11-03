"""PDF of all 30 clubs' main and secondary colour on the batter sprite (60 sprites), recoloured exactly the way the game does it."""
import re, numpy as np
from PIL import Image, ImageDraw, ImageFont
s = open('index.html', encoding='utf-8').read()
teams = re.findall(r"\['([A-Z]+)','([^']+)','([^']+)','(#[0-9a-f]{6})','(#[0-9a-f]{6})'", s)
assert len(teams) == 30, len(teams)

base = Image.open('assets/gp/batter0.png').convert('RGBA')
def tint(img, hexc):
    a = np.array(img).astype(float); br, bg, bb = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    m = (al >= 8) & (r > 70) & (b > 70) & (g < r * .66) & (g < b * .66) & (abs(r - b) < r * .42)
    lum = .3 * r + .59 * g + .11 * b; t = np.clip((lum - 34) / 90, 0, 1)
    dk = (.3 * br + .59 * bg + .11 * bb) < 80
    f = (.34 + .95 * t) * (1.3 if dk else 1); hi = np.where(t > .85, 30, 0) + (16 + 34 * t if dk else 0)
    for i, c in enumerate((br, bg, bb)):
        a[..., i] = np.where(m, np.clip(c * f + hi, 0, 255), a[..., i])
    return Image.fromarray(a.astype(np.uint8))

def font(sz, bold=False):
    for p in (r'C:\Windows\Fonts\arialbd.ttf' if bold else r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\segoeui.ttf'):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()
F1, F2, F3 = font(32, True), font(24), font(21)

PW, PH = 2200, 1700; COLS, ROWS = 3, 5; CW, CH = PW // COLS, (PH - 150) // ROWS; SH = 190          # sprite height on the page
pages = []
per = COLS * ROWS
for p0 in range(0, 30, per):
    pg = Image.new('RGB', (PW, PH), (245, 245, 248)); d = ImageDraw.Draw(pg)
    d.text((40, 36), 'Retro Baseball - club colours on the batter sprite (main | secondary)', fill=(20, 24, 40), font=font(44, True))
    for i, (ab, city, nick, c1, c2) in enumerate(teams[p0:p0 + per]):
        cx, cy = (i % COLS) * CW, 150 + (i // COLS) * CH
        d.rounded_rectangle((cx + 20, cy + 8, cx + CW - 20, cy + CH - 8), 18, fill=(255, 255, 255), outline=(205, 208, 220), width=3)
        d.text((cx + 44, cy + 24), f'{ab}  {city} {nick}', fill=(20, 24, 40), font=F1)
        for j, (lab, col) in enumerate((('MAIN', c1), ('SECOND', c2))):
            sp = tint(base, col); sc = SH / sp.height; sp = sp.resize((int(sp.width * sc), SH), Image.LANCZOS)
            bx = cx + 36 + j * (CW // 2 - 14)
            pg.paste(sp, (bx + 40, cy + 68), sp)
            d.rectangle((bx + 4, cy + 68 + SH + 10, bx + 40, cy + 68 + SH + 36), fill=col, outline=(40, 40, 50))
            d.text((bx + 48, cy + 68 + SH + 10), f'{lab} {col.upper()}', fill=(50, 54, 70), font=F3)
    pages.append(pg)
out = r'C:\Users\samue\OneDrive\Desktop\MLB team colors.pdf'
pages[0].save(out, 'PDF', resolution=150.0, save_all=True, append_images=pages[1:])
[p.save(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/colors_p%d.png' % (i + 1)) for i, p in enumerate(pages)]
print('wrote', out, len(pages), 'pages')
