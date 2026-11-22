import sys, math, subprocess
import numpy as np, cv2
import scenes3d as S
from motion import C, cta, mix, eo, eio, eb, prog, clamp, WHITE, GOLD, GRAY, BG, W, H, FPS, ROOT
from r3d import YELLOW

def over(img):
    c = C(); c.a = img.copy(); return c

def foot(c):
    c.text("Render illustrativo", 540, 1860, 30, (190, 190, 190), False)

def head(c, t, t0, l1, l2, y=250):
    k = 0.75 + 0.25 * eb((t - t0) / 0.4)
    c.text(l1, 540, y, 84 * k, WHITE)
    if l2:
        c.text(l2, 540, y + 105, 66 * k, mix(GOLD, prog(t, t0 + 0.2, t0 + 0.6)) if False else GOLD)

def cta2(c, t, t0, l1, l2=None):
    a = eo(prog(t, t0, t0 + 0.5))
    c.text(l1, 540, 300, 76, mix(WHITE, a))
    if l2:
        c.text(l2, 540, 400, 60, mix(GOLD, a))
    cta(c, t, t0)

# ---------------------------------------------------------------- phone
def rr_out(c, x0, y0, x1, y1, r, outline, fill, th=3):
    c.rrect(x0, y0, x1, y1, r, outline); c.rrect(x0 + th, y0 + th, x1 - th, y1 - th, max(r - th, 1), fill)

def phone(t):
    c = C()
    k = 0.7 + 0.3 * eb(t / 0.5)
    c.text("Riunione stasera?", 540, 230, 88 * k, WHITE)
    c.text("Prenota la sala.", 540, 340, 88 * k, mix(GOLD, prog(t, 0.7, 1.1)))
    y0 = int(520 + 700 * (1 - eo(t / 0.8)) + 6 * math.sin(t * 2.2))
    c.rrect(270, y0, 810, y0 + 1060, 74, (86, 86, 90))
    SC = (250, 250, 250)
    c.rrect(282, y0 + 12, 798, y0 + 1048, 62, SC)
    c.text("Sala riunioni", 316, y0 + 110, 46, (25, 25, 27), True, "lm")
    c.text("Fino a 8 persone", 316, y0 + 165, 30, (120, 120, 124), False, "lm")
    for (a, b, lab, sel) in ((316, 436, "Oggi", True), (450, 600, "Domani", False), (614, 724, "Lun", False)):
        c.rrect(a, y0 + 220, b, y0 + 280, 30, (25, 25, 27) if sel else (232, 232, 234))
        c.text(lab, (a + b) / 2, y0 + 250, 30, WHITE if sel else (60, 60, 64))
    times = ["17:00 - 19:00", "18:00 - 20:00", "19:00 - 21:00", "20:00 - 22:00"]
    for i, tm in enumerate(times):
        yy = y0 + 330 + i * 108
        sel = (i == 1 and t > 1.9)
        if sel:
            c.rrect(316, yy, 764, yy + 88, 24, GOLD)
        else:
            rr_out(c, 316, yy, 764, yy + 88, 24, (222, 222, 225), SC, 3)
        c.text(tm, 350, yy + 44, 36, (25, 25, 27), True if sel else False, "lm")
    done = t > 3.1
    c.rrect(316, y0 + 800, 764, y0 + 900, 34, GOLD if done else (25, 25, 27))
    if done:
        c.text("Confermato", 560, y0 + 850, 40, (25, 25, 27))
        x, y = 392, y0 + 850
        c.line((x - 20, y), (x - 6, y + 16), (25, 25, 27), 8)
        c.line((x - 6, y + 16), (x + 22, y - 18), (25, 25, 27), 8)
    else:
        c.text("Prenota", 540, y0 + 850, 40, WHITE)
    # finger
    def fing(p):
        return (p[0], p[1])
    p0, p1, p2 = (720, y0 + 980), (540, y0 + 330 + 108 + 44), (540, y0 + 850)
    if t < 1.3:
        pos = None
    elif t < 1.9:
        pos = (p0[0] + (p1[0] - p0[0]) * eio((t - 1.3) / 0.6), p0[1] + (p1[1] - p0[1]) * eio((t - 1.3) / 0.6))
    elif t < 2.4:
        pos = p1
    elif t < 3.1:
        a = eio((t - 2.4) / 0.6); pos = (p1[0] + (p2[0] - p1[0]) * a, p1[1] + (p2[1] - p1[1]) * a)
    else:
        pos = p2
    if pos and t < 3.6:
        r = 34 - (8 if (1.85 < t < 2.0 or 3.0 < t < 3.15) else 0)
        c.circle(pos[0], pos[1], r, (150, 150, 156))
        c.circle(pos[0], pos[1], r, (235, 235, 238), 4)
        if 3.1 < t < 3.6:
            c.circle(pos[0], pos[1], 34 + 120 * (t - 3.1) / 0.5, mix((120, 120, 126), 1 - (t - 3.1) / 0.5), 4)
    return c.finish()

def reel_d(t):
    if t < 3.9:
        c = over(phone(t)); c.wipe(t, 3.9); return c.finish()
    if t < 8.3:
        tt = t - 3.9
        c = over(S.entrance(tt)); head(c, tt, 0.0, "Entri quando vuoi.", "24 ore su 24"); foot(c)
        c.wipe(t, 8.3); c.wipe(t, 3.9); return c.finish()
    if t < 13.3:
        tt = t - 8.3
        c = over(S.meeting(tt)); head(c, tt, 0.0, "Presenti con stile.", "Sala riunioni fino a 8 persone"); foot(c)
        c.wipe(t, 8.3); c.wipe(t, 13.3); return c.finish()
    c = C(); cta2(c, t, 13.3, "Lo spazio per le", "tue riunioni."); c.wipe(t, 13.3); return c.finish()

# ---------------------------------------------------------------- reel E
def reel_e(t):
    if t < 5.0:
        c = over(S.corridor(t)); head(c, t, 0.0, "Il tuo nuovo ufficio.", "Vetrato e luminoso"); foot(c); c.wipe(t, 5.0); return c.finish()
    if t < 10.0:
        tt = t - 5.0
        c = over(S.kitchen(tt)); head(c, tt, 0.0, "E per la pausa?", "Area cucina"); foot(c)
        c.wipe(t, 5.0); c.wipe(t, 10.0); return c.finish()
    c = C(); cta2(c, t, 10.0, "Il tuo spazio, a", "Cassano Magnago."); c.wipe(t, 10.0); return c.finish()

# ---------------------------------------------------------------- reel F
def dashed(c, p, q, col, th=4, seg=22):
    L = math.dist(p, q); n = int(L // seg)
    for i in range(0, n, 2):
        a = i / n; b = min((i + 1) / n, 1)
        c.line((p[0] + (q[0] - p[0]) * a, p[1] + (q[1] - p[1]) * a), (p[0] + (q[0] - p[0]) * b, p[1] + (q[1] - p[1]) * b), col, th)

def envelope(c, cx, cy, s, a=1.0):
    w, h = 260 * s, 180 * s
    col = mix(WHITE, a)
    c.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 16 * s, col)
    dk = mix((60, 60, 64), a)
    c.line((cx - w / 2 + 8, cy - h / 2 + 8), (cx, cy + 8 * s), dk, max(2, int(5 * s)))
    c.line((cx + w / 2 - 8, cy - h / 2 + 8), (cx, cy + 8 * s), dk, max(2, int(5 * s)))

def reel_f(t):
    c = C()
    if t < 1.9:
        k = 0.6 + 0.4 * eb(t / 0.45)
        c.text("Hai bisogno di una", 540, 780, 96 * k, WHITE)
        c.text("sede legale?", 540, 930, 140 * k, GOLD)
        c.rect(190, 1070, 190 + 700 * eo((t - 0.4) / 0.8), 1080, GOLD)
    elif t < 5.8:
        tt = t - 1.9
        c.text("Domicilia la tua", 540, 250, 80, WHITE)
        c.text("sede legale.", 540, 350, 80, GOLD)
        # card
        cy0 = 700
        c.rrect(110, cy0, 970, cy0 + 520, 40, (250, 250, 250))
        c.rect(110, cy0 + 120, 970, cy0 + 130, GOLD)
        c.text("SEDE LEGALE", 170, cy0 + 70, 40, (25, 25, 27), True, "lm")
        a = eo(prog(tt, 1.6, 2.2))
        c.text("Via Bruno Buozzi 6", 170, cy0 + 250, 62, mix((25, 25, 27), 1) if a > 0 else (250, 250, 250), True, "lm")
        c.text("21012 Cassano Magnago (VA)", 170, cy0 + 335, 46, (90, 90, 94) if a > 0 else (250, 250, 250), False, "lm")
        c.text("Ricevi la posta a un indirizzo professionale.", 170, cy0 + 440, 31, (120, 120, 124) if tt > 2.4 else (250, 250, 250), False, "lm")
        # envelope drops into card
        e = prog(tt, 0.3, 1.5)
        if e < 1:
            ey = 520 + (cy0 + 60 - 520) * eio(e)
            envelope(c, 540, ey, 1.0 - 0.45 * eio(e), 1 - 0.8 * prog(e, 0.7, 1))
        c.wipe(t, 5.8)
    elif t < 9.8:
        tt = t - 5.8
        for g in range(0, W, 120): c.line((g, 0), (g, H), (44, 42, 43), 2)
        for g in range(0, H, 120): c.line((0, g), (W, g), (44, 42, 43), 2)
        road = (72, 70, 72)
        for pts in (((0, 1500), (540, 1050), (1080, 600)), ((200, 1920), (540, 1050), (900, 0)), ((0, 800), (540, 1050), (1080, 1350))):
            for p, q in zip(pts[:-1], pts[1:]): c.line(p, q, road, 14)
        K = (540, 1050)
        pins = [("Malpensa", (330, 1380), 1.0), ("Milano", (840, 1560), 1.5), ("Varese", (470, 640), 2.0)]
        for name, pt, t0 in pins:
            a = eo(prog(tt, t0, t0 + 0.5))
            if a > 0:
                dashed(c, K, (K[0] + (pt[0] - K[0]) * a, K[1] + (pt[1] - K[1]) * a), (110, 108, 110))
                c.circle(pt[0], pt[1], 16, mix(WHITE, a))
                c.text(name, pt[0], pt[1] + (46 if pt[1] > K[1] else -46), 40, mix(GRAY, a), False)
        pul = (tt * 1.2) % 1
        c.circle(K[0], K[1], 30 + 70 * pul, mix(GOLD, 1 - pul), 4)
        c.circle(K[0], K[1], 28, GOLD); c.circle(K[0], K[1], 10, BG)
        c.text("KREA District", K[0], K[1] - 80, 52, WHITE)
        k = 0.8 + 0.2 * eb(tt / 0.4)
        c.text("Vicino a Malpensa.", 540, 250, 80 * k, WHITE)
        c.text("Facile da raggiungere.", 540, 350, 56 * k, GOLD)
        c.wipe(t, 5.8); c.wipe(t, 9.8)
    else:
        cta2(c, t, 9.8, "Sede legale a", "Cassano Magnago."); c.wipe(t, 9.8)
    return c.finish()

REELS = {"d": (reel_d, 16.8, "motion_4_prenota_entra_presenta"), "e": (reel_e, 13.5, "motion_5_uffici_vetrati_cucina"), "f": (reel_f, 13.3, "motion_6_sede_legale")}

if __name__ == "__main__":
    fn, dur, name = REELS[sys.argv[1]]
    out = f"{ROOT}/out/reels/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("done", name)
