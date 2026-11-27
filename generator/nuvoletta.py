# Post 1080x1350 dalla foto reale con nuvoletta del pupazzo. Uso: python3 nuvoletta.py
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("KREA_ROOT", "/home/claude/social")
P = "/usr/share/fonts/truetype/google-fonts/Poppins-"
F = lambda n, s: ImageFont.truetype(P + n + ".ttf", s)
DARK = (31, 30, 32); YEL = (246, 215, 15); WHITE = (255, 255, 255)
# ogni riga: lista di (testo, colore, stile)
VARS = {
 "a": [[("Ciao ragazzi!", WHITE, "Medium")], [("Qui si ", WHITE, "Bold"), ("Krea", YEL, "Bold"), (" di tutto.", WHITE, "Bold")], [("Pure me.", YEL, "Bold")]],
 "b": [[("Fuori si gela.", WHITE, "Medium")], [("Io lavoro da ", WHITE, "Bold"), ("qui.", YEL, "Bold")], [("(Ma niente riscaldamento, grazie.)", WHITE, "Light")]],
 "c": [[("Ho chiesto una postazione", WHITE, "Medium")], [("al ", WHITE, "Bold"), ("fresco.", YEL, "Bold")], [("Mi hanno dato la migliore.", WHITE, "Bold")]],
}
SIZE = {"Medium": 50, "Bold": 62, "Light": 34}
def make(key):
    im = Image.open(f"{HERE}/../reali/pupazzo_natale.png").convert("RGB")
    w, h = im.size; nh = round(w * 5 / 4)
    im = im.crop((0, 60, w, 60 + nh)).resize((1080, 1350), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")
    lines = VARS[key]
    widths = [sum(F(st, SIZE[st]).getlength(t) for t, c, st in ln) for ln in lines]
    heights = [max(SIZE[st] for t, c, st in ln) * 1.28 for ln in lines]
    bw = max(widths) + 110; bh = sum(heights) + 80
    bx0 = 270; by0 = 150; bx1 = bx0 + bw; by1 = by0 + bh
    if bx1 > 1040: bx0 -= bx1 - 1040; bx1 = 1040
    tail = [(bx0 + 70, by1 - 6), (bx0 + 170, by1 - 6), (262, 462)]
    for off, col in ((5, YEL), (0, DARK)):
        d.rounded_rectangle((bx0 - off, by0 - off, bx1 + off, by1 + off), 54 + off, fill=col)
        if off: d.polygon([(tail[0][0] - 9, tail[0][1]), (tail[1][0] + 9, tail[1][1]), (tail[2][0] - 3, tail[2][1] + 12)], fill=col)
        else: d.polygon(tail, fill=col)
    y = by0 + 40
    for ln, lw, lh in zip(lines, widths, heights):
        x = (bx0 + bx1) / 2 - lw / 2
        for t, c, st in ln:
            f = F(st, SIZE[st]); d.text((x, y + (lh - SIZE[st] * 1.28) ), t, font=f, fill=c); x += f.getlength(t)
        y += lh
    # fascia in basso
    for i in range(170):
        d.line((0, 1350 - 170 + i, 1080, 1350 - 170 + i), fill=(20, 20, 22, int(215 * (i / 170) ** 1.3)))
    f1 = F("Bold", 34); f2 = F("Regular", 28)
    t1 = "KREA District · Coworking a Cassano Magnago"; t2 = "Dal 20 gennaio 2027 · Scrivici in DM"
    d.text(((1080 - f1.getlength(t1)) / 2, 1252), t1, font=f1, fill=WHITE); d.text(((1080 - f2.getlength(t2)) / 2, 1300), t2, font=f2, fill=(225, 225, 225))
    os.makedirs(f"{ROOT}/out/posts", exist_ok=True)
    out = f"{ROOT}/out/posts/post_pupazzo_nuvoletta_{key}.jpg"; im.save(out, quality=93); return out
if __name__ == "__main__":
    for k in VARS: print(make(k))
