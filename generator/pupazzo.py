# Reel natalizi dalla foto reale reali/pupazzo_natale.png (pupazzo ritagliato con reali/pupazzo_mask.png).
# Uso: python3 pupazzo.py 1|2|3   ->  out/reels/reel_pupazzo_<n>_*.mp4
import os, sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
ROOT = os.environ.get("KREA_ROOT", "/home/claude/social")
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BOX = (0, 480, 480, 1340); PY0 = 230
src = cv2.cvtColor(np.array(Image.open(f"{HERE}/../reali/pupazzo_natale.png").convert("RGB")), cv2.COLOR_RGB2BGR)
sc = W / src.shape[1]
mask = np.array(Image.open(f"{HERE}/../reali/pupazzo_mask.png").convert("L"))
x0, y0, x1, y1 = BOX
crop = src[y0:y1, x0:x1].copy(); CH, CW = crop.shape[:2]

def build_bg():
    """Ricostruisce lo sfondo dietro al pupazzo: pareti estese per righe/colonne, pavimento con inpaint."""
    hole = cv2.dilate((mask > 20).astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool)
    out = crop.copy()
    X, Y = np.meshgrid(np.arange(CW), np.arange(CH))
    floor = np.where(X < 150, 578, 528)       # base armadietti (sinistra) e base parete/pilastro
    wall = hole & (Y < floor)
    left = np.median(crop[:, 30:48], axis=1).astype(np.uint8)            # parete/armadietti a sinistra: uniformi in orizzontale
    top = np.median(crop[0:58, :], axis=0).astype(np.uint8)              # pilastro e doghe: uniformi in verticale
    a = wall & (X < 150); out[a] = left[Y[a]]
    b = wall & (X >= 150); out[b] = top[X[b]]
    fl = (hole & (Y >= floor)).astype(np.uint8)
    cv2.ellipse(fl, (215, 792), (205, 66), 0, 0, 360, 1, -1)             # anche l'ombra originale
    fl[Y < floor] = 0
    fm = fl.astype(bool)                                                  # pavimento: colore preso ai bordi del buco, riga per riga
    rc = np.full((CH, 3), np.nan, np.float32)
    wide = src[y0:y1, 0:700].astype(np.float32); wh = np.zeros(wide.shape[:2], bool); wh[:, :CW] = hole
    neutral = (wide.min(axis=2) > 165) & (wide.max(axis=2) - wide.min(axis=2) < 40) & ~wh
    for y in range(CH):
        if not fm[y].any(): continue
        p = wide[y][neutral[y]]
        if len(p) > 40: rc[y] = np.percentile(p, 75, axis=0)
    good = ~np.isnan(rc[:, 0]); idx = np.arange(CH)
    for k in range(3): rc[:, k] = np.interp(idx, idx[good], rc[good, k])
    rc = cv2.GaussianBlur(rc.reshape(CH, 1, 3), (1, 61), 0).reshape(CH, 3)
    tmp = out.copy(); nf = Y < floor
    tmp[nf] = rc[Y[nf]].astype(np.uint8)                                  # niente pareti scure che "colano" nel pavimento
    tmp[fm] = rc[Y[fm]].astype(np.uint8)
    ring = cv2.dilate(fl, np.ones((3, 3), np.uint8)) * 255
    tel = cv2.inpaint(tmp, ring, 12, cv2.INPAINT_TELEA).astype(np.float32)
    mix = 0.5 * tel + 0.5 * rc[Y].astype(np.float32)                      # gradiente dai bordi + tinta media del pavimento
    mix = cv2.GaussianBlur(mix, (0, 0), 4)
    out[fm] = mix[fm].astype(np.uint8)
    soft = cv2.GaussianBlur((hole | fm).astype(np.float32), (0, 0), 3)[:, :, None]
    return (crop * (1 - soft) + out * soft).astype(np.uint8)

bgc = build_bg()
bgfull = src.copy(); bgfull[y0:y1, x0:x1] = bgc
PH = round(src.shape[0] * sc)
BG = cv2.resize(bgfull, (W, PH), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)

# layer pupazzo (senza occhiali) + sprite occhiali
PAD = 160
gl = np.zeros((CH, CW), np.uint8)
gbox = (148, 74, 268, 114)
sub = crop[gbox[1]:gbox[3], gbox[0]:gbox[2]]
dark = (sub.max(axis=2) < 105) & (mask[gbox[1]:gbox[3], gbox[0]:gbox[2]] > 40)
gl[gbox[1]:gbox[3], gbox[0]:gbox[2]] = dark * 255
gl = cv2.dilate(gl, np.ones((5, 5), np.uint8))
noglass = cv2.inpaint(crop, cv2.dilate(gl, np.ones((11, 11), np.uint8)), 7, cv2.INPAINT_TELEA)
gsoft = cv2.GaussianBlur(gl, (3, 3), 0).astype(np.float32)
base = np.zeros((CH + PAD, CW + 2 * PAD, 4), np.float32)
alpha0 = cv2.GaussianBlur(mask, (3, 3), 0).astype(np.float32)
_yy, _xx = np.mgrid[0:CH, 0:CW]
_head = np.clip((77 - np.hypot(_xx - 210, _yy - 166)) / 2 + 0.5, 0, 1)      # profilo tondo della testa: via la sagoma degli occhiali che sporge
alpha0[:122] *= np.where(cv2.dilate(gl, np.ones((9, 9), np.uint8))[:122] > 0, _head[:122], 1)
base[PAD:, PAD:PAD + CW, :3] = noglass; base[PAD:, PAD:PAD + CW, 3] = alpha0
LH, LW = base.shape[:2]
piv = (PAD + 230, PAD + 800)
yy, xx = np.mgrid[0:LH, 0:LW].astype(np.float32)
hh = np.clip((piv[1] - yy) / 760, 0, 1.2)
GLDX, GLDY = 10, 46

def layer(g):
    L = base.copy()
    dx, dy = round(GLDX * g), round(GLDY * g)
    a = np.zeros((LH, LW), np.float32); c = np.zeros((LH, LW, 3), np.float32)
    a[PAD + dy:PAD + dy + CH - dy, PAD + dx:PAD + dx + CW - dx] = gsoft[:CH - dy, :CW - dx] / 255
    c[PAD + dy:PAD + dy + CH - dy, PAD + dx:PAD + dx + CW - dx] = crop[:CH - dy, :CW - dx]
    a = a[:, :, None]
    L[:, :, :3] = L[:, :, :3] * (1 - a) + c * a
    L[:, :, 3] = np.maximum(L[:, :, 3], a[:, :, 0] * 255)   # gli occhiali portano la propria sagoma
    return L

# luci albero
tx0, ty0, tx1, ty1 = [round(v * sc) for v in (700, 500, 1070, 1040)]
treg = BG[ty0:ty1, tx0:tx1]
lum = treg.mean(axis=2); warm = ((lum > 205) & (treg[:, :, 0] < treg[:, :, 2])).astype(np.float32)
glow = cv2.GaussianBlur(warm, (0, 0), 6) * 3
rng = np.random.default_rng(7)
phase = cv2.resize(rng.uniform(0, 6.28, (14, 10)).astype(np.float32), (tx1 - tx0, ty1 - ty0), interpolation=cv2.INTER_NEAREST)
N = 170
sx = rng.uniform(0, W, N); sy = rng.uniform(0, PH, N); sv = rng.uniform(70, 190, N); sr = rng.uniform(2, 6, N); sp = rng.uniform(0, 6.28, N)

P = "/usr/share/fonts/truetype/google-fonts/Poppins-"
F = lambda n, s: ImageFont.truetype(P + n + ".ttf", s)
GOLD = (216, 181, 86); WHITE = (255, 255, 255)
_tc = {}
def top_text(a, b, chip=None):
    k = (a, b, chip)
    if k not in _tc:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if chip:
            f = F("Bold", 50); w = f.getlength(chip)
            d.rounded_rectangle((60, 70, 60 + w + 56, 160), 45, fill=GOLD); d.text((88, 80), chip, font=f, fill=(31, 30, 32))
            d.text((60 + w + 86, 62), a, font=F("Medium", 44), fill=WHITE); d.text((60 + w + 86, 118), b, font=F("Bold", 44), fill=GOLD)
        else:
            f1 = F("Light", 54); f2 = F("Bold", 62 if len(b) < 24 else 50)
            d.text(((W - f1.getlength(a)) / 2, 44), a, font=f1, fill=WHITE); d.text(((W - f2.getlength(b)) / 2, 112), b, font=f2, fill=GOLD)
        _tc[k] = np.array(im).astype(np.float32)
    return _tc[k]
def bottom(l1):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for txt, y, f, col in [(l1, 1700, F("Bold", 54), GOLD), ("Dal 20 gennaio 2027 · Cassano Magnago (VA)", 1785, F("Medium", 36), WHITE),
                           ("Scrivici in DM · info@kreadistrict.it", 1842, F("Regular", 32), (190, 190, 190))]:
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)
    return np.array(im).astype(np.float32)
def over(fr, ov, a=1.0):
    if a <= 0: return
    al = ov[:, :, 3:4] / 255 * a
    fr[:] = fr * (1 - al) + ov[:, :, :3][:, :, ::-1] * al

def compose(t, s, texts, bot):
    """s: dict stato. X spostamento (px foto), bend, sq, hop, ang, g occhiali, frozen, dark, lights, snow, flash."""
    g = lambda k, d=0.0: s.get(k, d)
    ph = BG.copy()
    li = g("lights", 1.0)
    tw = 0.5 + 0.5 * np.sin(2 * math.pi * 1.3 * t + phase)
    ph[ty0:ty1, tx0:tx1] += (glow * tw * li)[:, :, None] * np.array([60, 150, 200], np.float32)
    dk = g("dark")
    if dk > 0:
        keep = np.zeros((PH, W), np.float32); keep[ty0:ty1, tx0:tx1] = np.clip(glow * (0.6 + 0.4 * tw), 0, 1)
        f = (1 - dk * 0.72) + keep * dk * 0.75
        ph = ph * f[:, :, None] * np.array([1 + 0.12 * dk, 1, 1 - 0.1 * dk], np.float32)
    # ombra + pupazzo
    X = g("X"); hop = g("hop")
    L = layer(g("g"))
    if g("bend"):
        L = cv2.remap(L, xx - g("bend") * hh ** 1.7, yy, cv2.INTER_LINEAR, borderValue=0)
    sq = 1 + g("sq")
    M = cv2.getRotationMatrix2D(piv, g("ang"), 1.0)
    S = np.array([[1 / sq, 0, piv[0] * (1 - 1 / sq)], [0, sq, piv[1] * (1 - sq) + hop], [0, 0, 1]], np.float32)
    M = (S @ np.vstack([M, [0, 0, 1]]))[:2]
    L = cv2.warpAffine(L, M, (LW, LH), flags=cv2.INTER_LINEAR, borderValue=0)
    fz = g("frozen")
    if fz > 0:
        gray = L[:, :, :3].mean(axis=2, keepdims=True)
        cold = gray * np.array([1.12, 1.0, 0.82], np.float32) + 18
        L[:, :, :3] = L[:, :, :3] * (1 - fz * 0.8) + cold * fz * 0.8
    if dk > 0:
        L[:, :, :3] *= (1 - dk * 0.6) * np.array([1.1, 1, 0.92], np.float32)
    shc = (int((x0 + 215 + X) * sc), int((y0 + 795) * sc))
    sh = np.zeros((PH, W), np.float32)
    k = 1 - min(1, abs(hop) / 60) * 0.35
    cv2.ellipse(sh, shc, (int(175 * k), int(40 * k)), 0, 0, 360, 0.42 * k * (1 - 0.5 * dk) * (1 - g("noshadow")), -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 22)[:, :, None]
    ph *= (1 - sh)
    Ls = cv2.resize(L, (round(LW * sc), round(LH * sc)), interpolation=cv2.INTER_AREA)
    ox, oy = round((x0 - PAD + X) * sc), round((y0 - PAD) * sc)
    hx0, hy0 = max(0, ox), max(0, oy); hx1, hy1 = min(W, ox + Ls.shape[1]), min(PH, oy + Ls.shape[0])
    if hx1 > hx0:
        sb = Ls[hy0 - oy:hy1 - oy, hx0 - ox:hx1 - ox]; al = sb[:, :, 3:4] / 255
        ph[hy0:hy1, hx0:hx1] = ph[hy0:hy1, hx0:hx1] * (1 - al) + sb[:, :, :3] * al
    if fz > 0:
        ph = ph * (1 - 0.35 * fz) + (ph.mean(axis=2, keepdims=True) * np.array([1.15, 1.0, 0.85], np.float32)) * 0.35 * fz
    sn_i = g("snow")
    if sn_i > 0:
        sn = np.zeros((PH, W), np.float32)
        for i in range(N):
            cy = (sy[i] + sv[i] * t) % PH; cx = (sx[i] + 18 * math.sin(t * 1.3 + sp[i])) % W
            cv2.circle(sn, (int(cx), int(cy)), int(sr[i]), 1.0, -1, cv2.LINE_AA)
        sn = cv2.GaussianBlur(sn, (0, 0), 1.6)[:, :, None] * 0.85 * sn_i
        ph = ph * (1 - sn) + 255 * sn
    fl = g("flash")
    if fl > 0: ph = ph * (1 - fl) + 255 * fl
    fade = g("fade", 1.0)
    fr = np.full((H, W, 3), (31, 30, 32), np.float32)
    fr[PY0:PY0 + PH] = np.clip(ph, 0, 255) * fade + np.array((31, 30, 32), np.float32) * (1 - fade)
    for ov, a in texts: over(fr, ov, a)
    over(fr, bot, min(1, max(0, (t - 0.3) / 0.5)))
    return cv2.cvtColor(np.clip(fr, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)

cl = lambda v: min(1.0, max(0.0, v))
eo = lambda v: 1 - (1 - cl(v)) ** 3
def bounce(v):
    v = cl(v)
    return 1 - abs(math.cos(v * math.pi * 2.5)) * (1 - v) ** 2
def walk(t, a, b, xa, xb):
    u = cl((t - a) / (b - a)); mv = 1 if 0 < u < 1 else 0
    return dict(X=xa + (xb - xa) * u, ang=5 * mv * math.sin(2 * math.pi * 2.6 * t), hop=-14 * mv * abs(math.sin(2 * math.pi * 2.6 * t)), sq=0.012 * mv * math.sin(2 * math.pi * 5.2 * t))
def dance(td, k=1.0, f=1.0):
    b = 2 * math.pi * f * td
    return dict(bend=55 * k * math.sin(b), sq=0.045 * k * math.sin(2 * b), hop=-26 * k * abs(math.sin(b)) ** 1.5, ang=3 * k * math.sin(b + 0.6))
def xf(t, cuts):  # dissolvenza tra testi: cuts = [(t_inizio, overlay)]
    out = []
    for i, (ts, ov) in enumerate(cuts):
        te = cuts[i + 1][0] if i + 1 < len(cuts) else 1e9
        a = cl((t - ts) / 0.3) * (1 - cl((t - te + 0.3) / 0.3))
        if a > 0: out.append((ov, a))
    return out

# ---- 1: il primo coworker è arrivato
def v1(t):
    s = walk(t, 0.2, 1.7, -560, 0)
    if 1.7 <= t < 3.0: s["sq"] = 0.006 * math.sin(2 * math.pi * 0.5 * t)
    s["g"] = bounce((t - 3.0) / 0.7)
    if 3.9 <= t < 7.6:   # lavora concentrato: piccoli cenni col capo
        s.update(bend=7 * math.sin(2 * math.pi * 1.6 * t), sq=0.008 * math.sin(2 * math.pi * 3.2 * t))
    if t >= 7.6:
        s.update(dance(t - 7.6, eo((t - 7.6) / 0.5), 1.1)); s["snow"] = cl((t - 7.6) / 0.8)
    tx = xf(t, [(0, top_text("Il primo coworker", "è arrivato.")), (2.8, top_text("Modalità:", "non disturbare.")),
                (5.4, top_text("Lui la scrivania", "l'ha già scelta.")), (7.6, top_text("E tu?", "Ti aspettiamo."))])
    return s, tx
# ---- 2: lo scongelamento
def v2(t):
    T = 3.6
    if t < T:
        s = dict(frozen=1.0, lights=0.0, sq=0.0)
        if t > 2.6: s["ang"] = 1.6 * math.sin(2 * math.pi * 9 * t) * cl((t - 2.6) / 1.0)   # trema prima di scongelarsi
    else:
        td = t - T
        s = dance(td, eo(td / 0.4), 1.15); s.update(frozen=max(0, 1 - td / 0.5), lights=1.6, snow=cl(td / 0.6), flash=max(0, 0.85 - td / 0.35), g=bounce((td - 0.6) / 0.7))
    tx = xf(t, [(0, top_text("30 novembre.", "Ancora congelato…")), (T - 0.05, top_text("1° dicembre.", "È ora."))])
    return s, tx
# ---- 3: una giornata da coworker
def v3(t):
    sc_ = [(0, 3.2), (3.2, 6.4), (6.4, 9.6), (9.6, 13.4)]
    i = max(k for k, (a, b) in enumerate(sc_) if t >= a); a, b = sc_[i]; u = t - a
    fade = cl(u / 0.2) * cl((b - t) / 0.2) if i < 3 else cl(u / 0.2)
    if i == 0:
        s = walk(u, 0.1, 1.6, -560, 0); tx = top_text("Primo ad arrivare.", "Ovviamente.", "08:00")
    elif i == 1:
        s = dict(bend=9 * math.sin(2 * math.pi * 1.4 * u), ang=1.2 * math.sin(2 * math.pi * 0.7 * u), sq=0.01 * math.sin(2 * math.pi * 2.8 * u))
        tx = top_text("Call col cliente.", "Serissimo.", "11:30")
    elif i == 2:
        s = dance(u, 0.8, 1.0); s.update(X=120, snow=1.0, lights=1.5, g=1.0); tx = top_text("Pausa.", "Meritata.", "16:00")
    else:
        s = walk(u, 1.2, 3.0, 0, -600); s.update(dark=1.0, lights=1.8, g=1.0); tx = top_text("Ultimo ad uscire.", "Aperto 24/7.", "23:00")
    s["fade"] = fade
    return s, [(tx, fade if i < 3 else cl(u / 0.2))]

VERS = {"1": (v1, 11.0, "reel_pupazzo_1_primo_coworker", "Buone feste da KREA District"),
        "2": (v2, 10.0, "reel_pupazzo_2_scongelamento", "Buone feste da KREA District"),
        "3": (v3, 13.4, "reel_pupazzo_3_giornata", "Una giornata in KREA District")}
if __name__ == "__main__":
    if sys.argv[1] == "bg":
        cv2.imwrite(f"{ROOT}/bgcheck.png", np.hstack([crop, bgc])); sys.exit()
    fn, dur, name, bl = VERS[sys.argv[1]]
    bot = bottom(bl)
    os.makedirs(f"{ROOT}/out/reels", exist_ok=True)
    out = f"{ROOT}/out/reels/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS; s, tx = fn(t)
        p.stdin.write(compose(t, s, tx, bot).tobytes())
    p.stdin.close(); p.wait(); print("done", out)
