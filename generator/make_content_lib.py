import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.environ.get("KREA_ROOT", "/home/claude/social")
OUT = f"{ROOT}/out"
os.makedirs(f"{OUT}/stories", exist_ok=True)
os.makedirs(f"{OUT}/posts", exist_ok=True)
os.makedirs(f"{OUT}/reels", exist_ok=True)
os.makedirs(f"{ROOT}/frames", exist_ok=True)

BG = (32, 30, 31)
WHITE = (255, 255, 255)
# gold sampled from the supplied logo's A
logo_src = Image.open(f"{ROOT}/assets/logo.jpg").convert("RGB")
_w,_h=logo_src.size
logo_src = logo_src.crop((12,12,_w-12,_h-12))  # trim scan-edge hairline only; logo untouched
GOLD = (216, 181, 86)
for x in range(2000, 2300, 5):
    p = logo_src.getpixel((x, 880))
    if p[0] > 180 and p[2] < 130:
        GOLD = p
        break
print("gold", GOLD)

FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
if not os.path.exists(FM):
    FM = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def logo(width):
    h = round(logo_src.height * width / logo_src.width)
    return logo_src.resize((width, h), Image.LANCZOS)


def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def canvas(w, h, logo_w, logo_y):
    im = Image.new("RGB", (w, h), BG)
    lg = logo(logo_w)
    im.paste(lg, ((w - logo_w) // 2, logo_y))
    return im, logo_y + lg.height


def scene(w, h, logo_w, logo_y, kicker, headline, sub=None, bullets=None, footer=None, hsize=92, y0=None):
    im, y = canvas(w, h, logo_w, logo_y)
    d = ImageDraw.Draw(im)
    M = 90
    maxw = w - 2 * M
    y = (y + 80) if y0 is None else y0
    if kicker:
        d.text((M, y), kicker, font=font(FM, 38), fill=GOLD)
        y += 80
    fh = font(FB, hsize)
    for part, col in headline:
        for ln in wrap(d, part, fh, maxw):
            d.text((M, y), ln, font=fh, fill=col)
            y += int(hsize * 1.18)
    y += 30
    if sub:
        fs = font(FM, 46)
        for ln in wrap(d, sub, fs, maxw):
            d.text((M, y), ln, font=fs, fill=WHITE)
            y += 66
        y += 20
    if bullets:
        fb = font(FM, 50)
        for b in bullets:
            d.rectangle((M, y + 20, M + 18, y + 38), fill=GOLD)
            d.text((M + 48, y), b, font=fb, fill=WHITE)
            y += 84
    if footer:
        ff = font(FM, 36)
        yy = h - 150
        for ln in footer:
            d.text((M, yy), ln, font=ff, fill=(200, 200, 200))
            yy += 52
    return im


