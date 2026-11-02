"""Slice a ChatGPT portrait sheet (4 columns x 2 rows, plain white background, magenta caps and jerseys) into one
transparent PNG per player: assets/portraits/pNN.png.

usage: python tools/slice_portraits.py <sheet.png> <first index>
"""
import sys, os
from collections import deque
from PIL import Image
import numpy as np

sheet, first = sys.argv[1], int(sys.argv[2])
COLS, ROWS = 4, 2
OUT_W = 240                                  # each portrait is kept big: 240 x 320 = 76,800 pixels
im = Image.open(sheet).convert('RGB')
W, H = im.size
cw, ch = W // COLS, H // ROWS
os.makedirs('assets/portraits', exist_ok=True)

def cut_background(a):
    """Flood the near-white background in from the top, left and right edges (not the bottom: that is jersey)."""
    h, w, _ = a.shape
    white = (a[..., 0] > 232) & (a[..., 1] > 232) & (a[..., 2] > 232)
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        if white[0, x]: q.append((0, x)); seen[0, x] = True
    for y in range(h):
        for x in (0, w - 1):
            if white[y, x] and not seen[y, x]: q.append((y, x)); seen[y, x] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    return alpha

n = first
for r in range(ROWS):
    for c in range(COLS):
        x0, y0 = c * cw, r * ch
        cell = im.crop((x0 + 3, y0 + 3, x0 + cw - 3, y0 + ch - 3))           # a few pixels in, away from the seams
        a = np.array(cell)
        alpha = cut_background(a)
        # trim empty columns/rows so the head sits centred
        ys, xs = np.where(alpha > 0)
        rgba = np.dstack([a, alpha])
        out = Image.fromarray(rgba, 'RGBA').crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        scale = OUT_W / out.width
        out = out.resize((OUT_W, max(1, round(out.height * scale))), Image.LANCZOS)
        out.save(f'assets/portraits/p{n:02d}.png')
        print(f'p{n:02d}', out.size, out.size[0] * out.size[1], 'px')
        n += 1
