# Reel: foto reale, nuvoletta che si scrive, occhiali che cadono sul naso, "Buon Natale!" + Jingle Bells sintetizzata (brano di pubblico dominio).
import os, math, subprocess, wave, numpy as np
from PIL import Image, ImageDraw
import pupazzo as pz
pz.PY0 = 150; pz.GLDX, pz.GLDY = 13, 55
import cv2
_o = pz.src.copy(); _m = np.zeros(_o.shape[:2], np.float32)
_m[pz.y0 + 62:pz.y0 + 128, pz.x0 + 138:pz.x0 + 280] = 1; _m = cv2.GaussianBlur(_m, (0, 0), 3)[:, :, None]   # solo sopra la testa: sfondo ricostruito (via gli occhiali)
_o = (_o * (1 - _m) + pz.bgfull * _m).astype(np.uint8)
pz.BG = cv2.resize(_o, (pz.W, pz.PH), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)   # pupazzo fermo: sfondo originale
W, H, FPS, DUR = 1080, 1920, 30, 10.5
F = pz.F; DARK = (31, 30, 32); YEL = (246, 215, 15); WHITE = (255, 255, 255)
LINES = [[("Ciao ragazzi!", WHITE, "Medium", 54)], [("Qui si ", WHITE, "Bold", 66), ("Krea", YEL, "Bold", 66), (" di tutto.", WHITE, "Bold", 66)], [("Pure me.", YEL, "Bold", 66)]]
T_POP, T_TYPE, CPS, T_GL, T_XMAS = 0.4, 0.8, 17.0, 4.3, 5.5
NCH = sum(len(t) for ln in LINES for t, *_ in ln)
BX0, BY0, BX1, BY1 = 250, 215, 1045, 520
TIP = (262, 150 + 548)
def bubble(t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = pz.bounce((t - T_POP) / 0.45) if t < T_XMAS else 0.9 + 0.1 * pz.bounce((t - T_XMAS) / 0.4)
    if t < T_POP: return np.zeros((H, W, 4), np.float32)
    cx, cy = (BX0 + BX1) / 2, (BY0 + BY1) / 2
    S = lambda x, y: (TIP[0] + (x - TIP[0]) * k, TIP[1] + (y - TIP[1]) * k) if t < T_XMAS else (cx + (x - cx) * k, cy + (y - cy) * k)
    x0, y0 = S(BX0, BY0); x1, y1 = S(BX1, BY1)
    ta, tb = S(BX0 + 70, BY1 - 6), S(BX0 + 180, BY1 - 6)
    d.rounded_rectangle((x0 - 6, y0 - 6, x1 + 6, y1 + 6), 66 * k, fill=YEL)
    d.polygon([(ta[0] - 10, ta[1]), (tb[0] + 10, tb[1]), (TIP[0] - 4, TIP[1] + 14)], fill=YEL)
    d.rounded_rectangle((x0, y0, x1, y1), 60 * k, fill=DARK); d.polygon([ta, tb, TIP], fill=DARK)
    if t < T_XMAS:
        n = int(max(0, (t - T_TYPE) * CPS)); y = BY0 + 38
        for ln in LINES:
            lw = sum(F(st, sz).getlength(tx) for tx, c, st, sz in ln); x = cx - lw / 2
            for tx, c, st, sz in ln:
                f = F(st, sz); show = tx[:max(0, n)]; n -= len(tx)
                d.text((x, y + (66 - sz) * 0.6), show, font=f, fill=c); x += f.getlength(tx)
            y += 84
    else:
        f = F("Bold", int(112 * k)); tx = "Buon Natale!"
        d.text((cx - f.getlength(tx) / 2, cy - 82 * k), tx, font=f, fill=YEL)
    return np.array(im).astype(np.float32)
def bottom():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for txt, y, f, col in [("KREA District · Coworking", 1640, F("Bold", 58), (216, 181, 86)), ("Dal 20 gennaio 2027 · Cassano Magnago (VA)", 1730, F("Medium", 38), WHITE),
                           ("Scrivici in DM · info@kreadistrict.it", 1790, F("Regular", 32), (190, 190, 190))]:
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=col)
    return np.array(im).astype(np.float32)
def state(t):
    s = dict(g=pz.bounce((t - T_GL) / 0.75), lights=1.0, noshadow=1.0)
    if t >= T_XMAS: s.update(snow=pz.cl((t - T_XMAS) / 0.8), lights=1.7)
    return s
# ---------- audio
SR = 44100
def audio(path):
    n = int(DUR * SR); a = np.zeros(n, np.float32); rng = np.random.default_rng(3)
    def bell(t0, f, dur, vol=0.22):
        m = int(min(dur * 2.2, 1.6) * SR); tt = np.arange(m) / SR
        w = (np.sin(2 * np.pi * f * tt) + 0.45 * np.sin(2 * np.pi * 2 * f * tt) + 0.22 * np.sin(2 * np.pi * 3.01 * f * tt) + 0.1 * np.sin(2 * np.pi * 4.2 * f * tt)) * np.exp(-tt * 4.2)
        i = int(t0 * SR); e = min(n, i + m); a[i:e] += (w[:e - i] * vol).astype(np.float32)
    def sleigh(t0, vol=0.05):
        m = int(0.12 * SR); tt = np.arange(m) / SR
        w = rng.normal(0, 1, m) * np.exp(-tt * 38); w = np.diff(w, prepend=0) ; w += 0.5 * np.sin(2 * np.pi * 5200 * tt) * np.exp(-tt * 30)
        i = int(t0 * SR); e = min(n, i + m); a[i:e] += (w[:e - i] * vol).astype(np.float32)
    N = dict(C=523.25, D=587.33, E=659.25, F=698.46, G=783.99)
    mel = [("E", 1), ("E", 1), ("E", 2), ("E", 1), ("E", 1), ("E", 2), ("E", 1), ("G", 1), ("C", 1.5), ("D", .5), ("E", 4),
           ("F", 1), ("F", 1), ("F", 1.5), ("F", .5), ("F", 1), ("E", 1), ("E", 1), ("E", .5), ("E", .5), ("G", 1), ("G", 1), ("F", 1), ("D", 1), ("C", 4)]
    beat = 60 / 196; t = 0.15
    for nm, b in mel:
        bell(t, N[nm], b * beat); bell(t, N[nm] / 2, b * beat, 0.08); t += b * beat
    for k in range(int((DUR - 0.3) / (beat / 2))):
        sleigh(0.15 + k * beat / 2, 0.06 if k % 2 == 0 else 0.03)
    # "boing" quando gli occhiali atterrano
    i = int((T_GL + 0.28) * SR); m = int(0.25 * SR); tt = np.arange(m) / SR
    a[i:i + m] += (np.sin(2 * np.pi * (420 + 500 * np.exp(-tt * 14)) * tt) * np.exp(-tt * 12) * 0.25).astype(np.float32)
    fade = np.minimum(1, (DUR - np.arange(n) / SR) / 0.8); a *= fade
    a = np.clip(a / max(1e-6, np.abs(a).max()) * 0.8, -1, 1)
    with wave.open(path, "wb") as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((a * 32767).astype(np.int16).tobytes())
if __name__ == "__main__":
    os.makedirs(f"{pz.ROOT}/out/reels", exist_ok=True)
    wavp = f"{pz.ROOT}/jingle.wav"; audio(wavp)
    out = f"{pz.ROOT}/out/reels/reel_pupazzo_nuvoletta.mp4"; bot = bottom()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wavp,
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        t = i / FPS
        p.stdin.write(pz.compose(t, state(t), [(bubble(t), 1.0)], bot).tobytes())
    p.stdin.close(); p.wait(); print("done", out)
