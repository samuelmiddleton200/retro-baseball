"""Repaint the smeared left batter's box / bottom-left corner of plate_clean.png by mirroring the clean right side."""
import numpy as np
from PIL import Image
src = Image.open('assets/fields/plate_clean_v1.png').convert('RGB'); a = np.array(src); H, W, _ = a.shape
b = a.copy(); CX2 = 775                                    # mirror axis: x' = 775 - x
# A: the left box and the dirt around it, from the right side
for y in range(380, H):
    for x in range(125, 300):
        b[y, x] = a[y, CX2 - x]
# B: far-left corner: plain foul-ground dirt below the foul-grass edge (which runs on down-right as a straight line), feathered into A
patch = a[405:440, 330:440]
tex = lambda y, x: patch[(y * 7 + x * 3) % patch.shape[0], (x * 5 + y) % patch.shape[1]]
for y in range(300, H):
    for x in range(0, 160):
        if y > 322 + x * .56 - 3:
            t = tex(y, x)
            if x < 125: b[y, x] = t
            elif y >= 380: k = (x - 125) / 35; b[y, x] = (t * (1 - k) + b[y, x] * k).astype(np.uint8)
# fix the seam: blur 2px band at x=125 and x=300 horizontally
for x0 in (299,):
    for x in range(x0 - 2, x0 + 3):
        b[380:, x] = (b[380:, x - 1].astype(int) + b[380:, x + 1].astype(int)) // 2
Image.fromarray(b).save('assets/fields/plate_clean.png'); print('ok')
