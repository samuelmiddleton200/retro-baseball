"""PDF: the strike zone at true scale with the contact-reach rings (1, 2, 3.5, 5 and 6 inches outside it), a real baseball for scale, and the table."""
from PIL import Image, ImageDraw, ImageFont

ZW, ZH = 19.9, 26.4            # the game's strike zone: plate (17 in) plus a ball's width wide, 26.4 in tall
BALL = 2.9                     # a baseball's diameter
RINGS = [(1, '60 contact rule: 70-79', (255, 214, 64)), (2, '80-89', (120, 220, 120)), (3.5, '90-99', (80, 190, 255)), (5, '100-109', (190, 120, 255)), (6, '110-120', (255, 90, 90))]
PX = 30                        # pixels per inch
PW, PH = 2000, 2600

def font(sz, bold=False):
    for p in (r'C:\Windows\Fonts\arialbd.ttf' if bold else r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\segoeui.ttf'):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

pg = Image.new('RGB', (PW, PH), (248, 248, 250)); d = ImageDraw.Draw(pg)
d.text((80, 60), 'How far outside the strike zone a hitter can reach', fill=(20, 24, 40), font=font(58, True))
d.text((80, 135), 'Drawn at true size: 1 inch = %d px.  The zone is %.1f in wide (the 17 in plate plus a ball) and %.1f in tall.' % (PX, ZW, ZH), fill=(70, 76, 96), font=font(30))

cx, cy = PW // 2, 880
def box(inch, fill=None, outline=None, w=4):
    x0, x1 = cx - (ZW / 2 + inch) * PX, cx + (ZW / 2 + inch) * PX
    y0, y1 = cy - (ZH / 2 + inch) * PX, cy + (ZH / 2 + inch) * PX
    d.rounded_rectangle((x0, y0, x1, y1), radius=int(inch * PX), fill=fill, outline=outline, width=w)
for inch, lab, col in reversed(RINGS):
    box(inch, fill=tuple(int(c * .18 + 255 * .82) for c in col), outline=col, w=5)
box(0, fill=(255, 255, 255), outline=(30, 34, 50), w=7)
# the zone's 3 x 3 grid
for k in (1, 2):
    x = cx - ZW / 2 * PX + ZW * PX * k / 3; d.line((x, cy - ZH / 2 * PX, x, cy + ZH / 2 * PX), fill=(190, 194, 206), width=2)
    y = cy - ZH / 2 * PX + ZH * PX * k / 3; d.line((cx - ZW / 2 * PX, y, cx + ZW / 2 * PX, y), fill=(190, 194, 206), width=2)
d.text((cx, cy), 'STRIKE ZONE', fill=(30, 34, 50), font=font(44, True), anchor='mm')
d.text((cx, cy + 56), 'any strike can be hit', fill=(90, 96, 116), font=font(30), anchor='mm')
# label each ring under the figure: a drop line from the ring to its label
ybot = cy + (ZH / 2 + 6) * PX
for i, (inch, lab, col) in enumerate(RINGS):
    x = cx - 200 + i * 100; yb = cy + (ZH / 2 + inch) * PX
    d.line((x, yb, x, ybot + 40), fill=col, width=4)
    d.text((x, ybot + 62), '%g in' % inch, fill=tuple(int(c * .7) for c in col), font=font(36, True), anchor='mm')
# two baseballs: one just inside the 3.5 in ring, one at the 6 in ring edge, for scale
def ball(x, y):
    r = BALL / 2 * PX
    d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 248, 240), outline=(30, 34, 50), width=4)
    d.arc((x - r * 1.5, y - r, x - r * .1, y + r), -60, 60, fill=(214, 55, 44), width=4); d.arc((x + r * .1, y - r, x + r * 1.5, y + r), 120, 240, fill=(214, 55, 44), width=4)
ball(cx + (ZW / 2 + 2.5) * PX, cy + 6 * PX)
d.text((cx + (ZW / 2 + 2.5) * PX + 50, cy + 6 * PX), 'a baseball is 2.9 in', fill=(60, 66, 86), font=font(26), anchor='lm')
ball(cx - (ZW / 2 + 6) * PX, cy - 4 * PX)
d.text((cx - (ZW / 2 + 6) * PX - 70, cy - 4 * PX), 'two balls wide = about 6 in', fill=(60, 66, 86), font=font(26), anchor='rm')
# the table
ty = 1840
d.text((80, ty - 90), 'Contact rating and how far outside the zone he can still hit it', fill=(20, 24, 40), font=font(44, True))
rows = [('60 to 69', '0 in', 'only pitches inside the zone', None), ('70 to 79', '1 in', 'a ball just off the edge', RINGS[0][2]), ('80 to 89', '2 in', '', RINGS[1][2]),
        ('90 to 99', '3.5 in', 'about one ball past the edge', RINGS[2][2]), ('100 to 109', '5 in', '', RINGS[3][2]), ('110 to 120', '6 in', 'two balls past the edge', RINGS[4][2])]
d.text((120, ty + 0), 'CONTACT', fill=(110, 116, 136), font=font(26, True)); d.text((520, ty + 0), 'REACH', fill=(110, 116, 136), font=font(26, True)); d.text((820, ty + 0), 'MEANS', fill=(110, 116, 136), font=font(26, True))
for i, (a, b, c, col) in enumerate(rows):
    y = ty + 50 + i * 78
    d.rounded_rectangle((70, y - 6, 1930, y + 62), 14, fill=(255, 255, 255), outline=(220, 222, 232), width=2)
    d.rectangle((70, y - 6, 92, y + 62), fill=col or (200, 200, 205))
    d.text((120, y + 28), a, fill=(20, 24, 40), font=font(38, True), anchor='lm'); d.text((520, y + 28), b, fill=(20, 24, 40), font=font(38, True), anchor='lm'); d.text((820, y + 28), c, fill=(80, 86, 106), font=font(32), anchor='lm')
d.text((80, PH - 70), 'A swing at a pitch further out than his reach is a swing and a miss.  A pitch that touches the batter is a hit by pitch: first base.', fill=(70, 76, 96), font=font(28))
out = r'C:\Users\samue\OneDrive\Desktop\Contact reach.pdf'
pg.save(out, 'PDF', resolution=150.0)
pg.resize((PW // 2, PH // 2)).save(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/zone_pdf.png')
print('wrote', out)
