# Reel natalizio: anima il pupazzo di neve della foto reale (reali/pupazzo_natale.png).
# Maschera del pupazzo (ritaglio rembg del riquadro BOX): reali/pupazzo_mask.png
import os, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
ROOT = os.environ.get("KREA_ROOT", "/home/claude/social")
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 10.0
BOX = (0, 480, 480, 1340); PY0 = 230  # y della foto nel canvas
src = cv2.cvtColor(np.array(Image.open(f"{HERE}/../reali/pupazzo_natale.png").convert("RGB")), cv2.COLOR_RGB2BGR)
sc = W / src.shape[1]
mask = np.array(Image.open(f"{HERE}/../reali/pupazzo_mask.png").convert("L"))
x0, y0, x1, y1 = BOX
crop = src[y0:y1, x0:x1].copy()
# sfondo senza pupazzo
hole = cv2.dilate((mask > 20).astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
bgc = cv2.inpaint(crop, hole, 7, cv2.INPAINT_TELEA)
bg = src.copy(); bg[y0:y1, x0:x1] = bgc
PH = round(src.shape[0] * sc)
bg = cv2.resize(bg, (W, PH), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
# layer pupazzo su tela larga
PAD = 160
lay = np.zeros((y1 - y0 + PAD, x1 - x0 + 2 * PAD, 4), np.float32)
lay[PAD:, PAD:PAD + x1 - x0, :3] = crop; lay[PAD:, PAD:PAD + x1 - x0, 3] = cv2.GaussianBlur(mask, (3, 3), 0)
LH, LW = lay.shape[:2]
piv = (PAD + 230, PAD + 800)
yy, xx = np.mgrid[0:LH, 0:LW].astype(np.float32)
hh = np.clip((piv[1] - yy) / 760, 0, 1.2)
# luci albero
tx0, ty0, tx1, ty1 = [round(v * sc) for v in (700, 500, 1070, 1040)]
treg = bg[ty0:ty1, tx0:tx1]
lum = treg.mean(axis=2); warm = ((lum > 205) & (treg[:, :, 0] < treg[:, :, 2])).astype(np.float32)
glow = cv2.GaussianBlur(warm, (0, 0), 6) * 3
rng = np.random.default_rng(7)
phase = cv2.resize(rng.uniform(0, 6.28, (14, 10)).astype(np.float32), (tx1 - tx0, ty1 - ty0), interpolation=cv2.INTER_NEAREST)
# neve
N = 150
sx = rng.uniform(0, W, N); sy = rng.uniform(0, PH, N); sv = rng.uniform(70, 190, N); sr = rng.uniform(2, 6, N); sp = rng.uniform(0, 6.28, N)
# testi
P = "/usr/share/fonts/truetype/google-fonts/Poppins-"
F = lambda n, s: ImageFont.truetype(P + n + ".ttf", s)
GOLD = (216, 181, 86)
def band(lines):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for txt, y, f, col in lines:
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)
    return np.array(im).astype(np.float32)
T1 = band([("Quando scopri che", 48, F("Light", 54), (255, 255, 255)), ("a Cassano Magnago apre un coworking…", 122, F("Medium", 46), (255, 255, 255))])
T2 = band([("…e la scrivania", 48, F("Light", 54), (255, 255, 255)), ("l'hai già scelta.", 112, F("Bold", 66), GOLD)])
BOT = band([("Buone feste da KREA District", 1705, F("Bold", 56), GOLD), ("Dal 20 gennaio 2027 · Cassano Magnago (VA)", 1790, F("Medium", 36), (255, 255, 255)),
            ("Scrivici in DM · info@kreadistrict.it", 1845, F("Regular", 32), (190, 190, 190))])
def over(fr, ov, a=1.0):
    al = ov[:, :, 3:4] / 255 * a
    fr[:] = fr * (1 - al) + ov[:, :, :3][:, :, ::-1] * al
T0 = 2.4
def frame(t):
    ph = bg.copy()
    # luci
    tw = 0.5 + 0.5 * np.sin(2 * math.pi * 1.3 * t + phase)
    ph[ty0:ty1, tx0:tx1] += (glow * tw)[:, :, None] * np.array([60, 150, 200], np.float32)
    # pupazzo
    k = min(1, max(0, (t - T0) / 0.5)); td = max(0, t - T0)
    beat = 2 * math.pi * 1.0 * td
    bend = 55 * k * math.sin(beat)
    mapx = xx - bend * hh ** 1.7; mapy = yy
    L = cv2.remap(lay, mapx, mapy, cv2.INTER_LINEAR, borderValue=0)
    s = 1 + (0.045 * k * math.sin(2 * beat) if k else 0.006 * math.sin(2 * math.pi * 0.4 * t))
    hop = -26 * k * abs(math.sin(beat)) ** 1.5
    ang = 3.0 * k * math.sin(beat + 0.6)
    M = cv2.getRotationMatrix2D(piv, ang, 1.0)
    S = np.array([[1 / s, 0, piv[0] * (1 - 1 / s)], [0, s, piv[1] * (1 - s) + hop], [0, 0, 1]], np.float32)
    M = (S @ np.vstack([M, [0, 0, 1]]))[:2]
    L = cv2.warpAffine(L, M, (LW, LH), flags=cv2.INTER_LINEAR, borderValue=0)
    Ls = cv2.resize(L, (round(LW * sc), round(LH * sc)), interpolation=cv2.INTER_AREA)
    ox, oy = round((x0 - PAD) * sc), round((y0 - PAD) * sc)
    hx0, hy0 = max(0, ox), max(0, oy); hx1, hy1 = min(W, ox + Ls.shape[1]), min(PH, oy + Ls.shape[0])
    sub = Ls[hy0 - oy:hy1 - oy, hx0 - ox:hx1 - ox]; al = sub[:, :, 3:4] / 255
    ph[hy0:hy1, hx0:hx1] = ph[hy0:hy1, hx0:hx1] * (1 - al) + sub[:, :, :3] * al
    # neve
    sn = np.zeros((PH, W), np.float32)
    for i in range(N):
        cy = (sy[i] + sv[i] * t) % PH; cx = (sx[i] + 18 * math.sin(t * 1.3 + sp[i])) % W
        cv2.circle(sn, (int(cx), int(cy)), int(sr[i]), 1.0, -1, cv2.LINE_AA)
    sn = cv2.GaussianBlur(sn, (0, 0), 1.6)[:, :, None] * 0.85
    ph = ph * (1 - sn) + 255 * sn
    fr = np.full((H, W, 3), (31, 30, 32), np.float32)
    fr[PY0:PY0 + PH] = np.clip(ph, 0, 255)
    a2 = min(1, max(0, (t - T0 + 0.15) / 0.3))
    over(fr, T1, (1 - a2) * min(1, t / 0.4)); over(fr, T2, a2); over(fr, BOT, min(1, max(0, (t - 0.3) / 0.5)))
    return cv2.cvtColor(np.clip(fr, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)
if __name__ == "__main__":
    os.makedirs(f"{ROOT}/out/reels", exist_ok=True)
    out = f"{ROOT}/out/reels/reel_natale_pupazzo.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("done", out)
