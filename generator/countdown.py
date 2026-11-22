import sys
sys.path.insert(0, "/home/claude/social")
from datetime import date, timedelta
from PIL import Image, ImageDraw
import make_content_lib as L

OPEN = date(2027, 1, 20)
W, H = 1080, 1920
d = date(2026, 11, 22)
n = 0
while d < OPEN:
    left = (OPEN - d).days
    im, y = L.canvas(W, H, 760, 110)
    dr = ImageDraw.Draw(im)
    M = 90
    if left == 1:
        big, small, sub = "DOMANI", "apre KREA District", "20 gennaio 2027"
    else:
        big, small, sub = str(left), "giorni all'apertura" , "20 gennaio 2027"
    dr.text((M, 880), "CONTO ALLA ROVESCIA", font=L.font(L.FM, 38), fill=L.GOLD)
    fs = 330 if left > 1 else 210
    dr.text((M - 6, 930), big, font=L.font(L.FB, fs), fill=L.GOLD)
    yy = 930 + int(fs * 1.25)
    dr.text((M, yy), small, font=L.font(L.FB, 70), fill=L.WHITE)
    dr.text((M, yy + 95), sub, font=L.font(L.FM, 48), fill=L.WHITE)
    dr.text((M, H - 150), "Via Bruno Buozzi 6, Cassano Magnago (VA)", font=L.font(L.FM, 36), fill=(200, 200, 200))
    im.save(f"/home/claude/social/out/countdown/story_{d.isoformat()}_{left:02d}.png")
    n += 1
    d += timedelta(days=1)
print(n)
