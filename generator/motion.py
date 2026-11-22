import sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (32, 30, 31)
WHITE = (255, 255, 255)
GOLD = (216, 181, 86)
GRAY = (150, 148, 149)
DARK = (62, 60, 61)
ROOT = "/home/claude/social"
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"

_fc = {}
def F(bold, size):
    k = (bold, max(8, int(size)))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FB if bold else FM, k[1])
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def eb(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def mix(c, a):
    a = clamp(a)
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))

_logo = Image.open(f"{ROOT}/assets/logo.jpg").convert("RGB")
_lw, _lh = _logo.size
_logo = np.asarray(_logo.crop((12, 12, _lw - 12, _lh - 12)))
_lcache = {}
def logo_img(width):
    width = int(width)
    if width not in _lcache:
        h = round(_logo.shape[0] * width / _logo.shape[1])
        _lcache[width] = cv2.resize(_logo, (width, h), interpolation=cv2.INTER_AREA)
    return _lcache[width]


class C:
    def __init__(s):
        s.a = np.empty((H, W, 3), np.uint8)
        s.a[:] = BG
        s.t = []

    def circle(s, cx, cy, r, col, th=-1):
        if r > 0:
            cv2.circle(s.a, (int(cx), int(cy)), int(r), col, th, cv2.LINE_AA)

    def arc(s, cx, cy, r, deg, col, th):
        if deg > 0:
            cv2.ellipse(s.a, (int(cx), int(cy)), (int(r), int(r)), 0, -90, -90 + deg, col, th, cv2.LINE_AA)

    def line(s, p, q, col, th):
        cv2.line(s.a, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), col, th, cv2.LINE_AA)

    def rect(s, x0, y0, x1, y1, col):
        x0, x1 = int(clamp(x0, 0, W)), int(clamp(x1, 0, W))
        y0, y1 = int(clamp(y0, 0, H)), int(clamp(y1, 0, H))
        if x1 > x0 and y1 > y0:
            s.a[y0:y1, x0:x1] = col

    def rrect(s, x0, y0, x1, y1, r, col):
        r = int(min(r, (x1 - x0) / 2, (y1 - y0) / 2))
        s.rect(x0 + r, y0, x1 - r, y1, col)
        s.rect(x0, y0 + r, x1, y1 - r, col)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
            s.circle(cx, cy, r, col)

    def rrect_outline(s, x0, y0, x1, y1, r, col, th):
        s.rrect(x0, y0, x1, y1, r, col)
        s.rrect(x0 + th, y0 + th, x1 - th, y1 - th, max(r - th, 1), BG)

    def text(s, txt, x, y, size, col, bold=True, anchor="mm"):
        s.t.append((txt, x, y, size, col, bold, anchor))

    def multi(s, segs, cx, cy, size, bold=True):
        f = F(bold, size)
        widths = [f.getlength(t) for t, _ in segs]
        x = cx - sum(widths) / 2
        for (t, col), w in zip(segs, widths):
            s.text(t, x, cy, size, col, bold, "lm")
            x += w

    def logo(s, cx, cy, width, a):
        if a <= 0:
            return
        L = logo_img(width)
        h, w = L.shape[:2]
        x0, y0 = int(cx - w / 2), int(cy - h / 2)
        roi = s.a[y0:y0 + h, x0:x0 + w].astype(np.float32)
        s.a[y0:y0 + h, x0:x0 + w] = (roi * (1 - a) + L.astype(np.float32) * a).astype(np.uint8)

    def wipe(s, t, tb, dur=0.22):
        if tb - dur <= t < tb:
            s.rect(0, 0, W * eio((t - (tb - dur)) / dur), H, GOLD)
        elif tb <= t < tb + dur:
            s.rect(W * eio((t - tb) / dur), 0, W, H, GOLD)

    def finish(s):
        img = Image.fromarray(s.a)
        d = ImageDraw.Draw(img)
        for txt, x, y, size, col, bold, anc in s.t:
            d.text((x, y), txt, font=F(bold, size), fill=col, anchor=anc)
        return np.asarray(img)


def cta(c, t, t0):
    a = eo(prog(t, t0, t0 + 0.6))
    c.logo(540, 700, 860 * (0.92 + 0.08 * a), a)
    c.text("Dal 20 gennaio 2027", 540, 1090, 66, mix(GOLD, eo(prog(t, t0 + 0.5, t0 + 1.0))))
    c.text("Cassano Magnago (VA)", 540, 1180, 52, mix(WHITE, eo(prog(t, t0 + 0.7, t0 + 1.2))))
    c.text("Via Bruno Buozzi 6", 540, 1250, 42, mix(GRAY, eo(prog(t, t0 + 0.8, t0 + 1.3))), False)
    c.text("+39 375 113 9192", 540, 1390, 62, mix(WHITE, eo(prog(t, t0 + 1.0, t0 + 1.5))))
    c.text("info@kreadistrict.it", 540, 1470, 42, mix(GRAY, eo(prog(t, t0 + 1.1, t0 + 1.6))), False)


# ------------------------------------------------------------------ Reel A: 24/7
def reel_a(t):
    c = C()
    cx, cy, R = 540, 830, 400
    if t < 9.0:
        sweep = 360 * eo(t / 1.5)
        c.circle(cx, cy, R, DARK, 4)
        c.arc(cx, cy, R, sweep, GOLD, 14)
        if t >= 3.0:
            al = prog(t, 3.0, 3.6)
            for i in range(24):
                ang = math.radians(i * 15)
                r0, r1 = R + 24, R + (56 if i % 6 == 0 else 40)
                c.line((cx + r0 * math.sin(ang), cy - r0 * math.cos(ang)),
                       (cx + r1 * math.sin(ang), cy - r1 * math.cos(ang)),
                       mix(WHITE if i % 6 == 0 else GRAY, al), 4)
        c.text("ENTRI QUANDO VUOI", 540, 240, 56, GOLD)
    if t < 1.7:
        n = int(round(24 * eo(t / 1.4)))
        c.text(str(n), cx, cy, 420, WHITE)
        c.text("ORE", cx, cy + 270, 64, GRAY)
    elif t < 3.4:
        k = 0.7 + 0.3 * eb((t - 1.7) / 0.45)
        c.multi([("24", WHITE), ("/", GOLD), ("7", WHITE)], cx, cy, 300 * k)
        c.text("Accesso autonomo.", 540, 1330, 66, mix(WHITE, eo(prog(t, 2.2, 2.7))))
    elif t < 9.0:
        slots = [(3.4, "06:30", "Prima del caffè.", 6.5), (4.9, "22:00", "A studio chiuso.", 22.0),
                 (6.4, "03:15", "Anche di notte.", 3.25), (7.8, "10:00", "Anche la domenica.", 10.0)]
        i = max(k for k, s in enumerate(slots) if t >= s[0])
        st, tm, cap, hrs = slots[i]
        tt = t - st
        k = 0.8 + 0.2 * eb(tt / 0.35)
        c.text(tm, cx, cy, 210 * k, WHITE)
        if i == 3:
            c.text("DOMENICA", cx, cy - 170, 52, GOLD)
        c.text(cap, 540, 1380, 70 * (0.9 + 0.1 * eb(tt / 0.35)), mix(WHITE, eo(prog(tt, 0, 0.25))))
        cur = hrs / 24 * 360
        if i == 0:
            ang = cur
        else:
            prev = slots[i - 1][3] / 24 * 360
            ang = prev + ((cur - prev) % 360) * eio(tt / 0.6)
        r = math.radians(ang)
        px, py = cx + R * math.sin(r), cy - R * math.cos(r)
        c.circle(px, py, 40, BG)
        c.circle(px, py, 30, GOLD)
        c.circle(px, py, 12, WHITE)
    elif t < 11.4:
        tt = t - 9.0
        off1 = -400 * (1 - eo(tt / 0.5))
        off2 = -400 * (1 - eo((tt - 0.2) / 0.5))
        c.text("Accesso autonomo.", 540 + off1, 760, 84, WHITE)
        c.text("Su prenotazione.", 540 + off2, 890, 84, GOLD)
        c.rect(190, 1000, 190 + 700 * eo((tt - 0.3) / 0.6), 1010, GOLD)
        c.text("24 ore su 24, 7 giorni su 7.", 540, 1120, 54, mix(GRAY, eo(prog(tt, 0.9, 1.4))), False)
    else:
        cta(c, t, 11.4)
    for tb in (3.4, 9.0, 11.4):
        c.wipe(t, tb)
    return c.finish()


# ------------------------------------------------------------------ Reel B: sala riunioni
def reel_b(t):
    c = C()
    if t < 1.8:
        k = 0.6 + 0.4 * eb(t / 0.45)
        c.text("Riunione", 540, 760, 170 * k, WHITE)
        c.text("tra un'ora?", 540, 960, 150 * k, GOLD)
        c.rect(190, 1110, 190 + 700 * eo((t - 0.4) / 0.8), 1120, GOLD)
    elif t < 6.2:
        tt = t - 1.8
        c.text("SALA RIUNIONI", 540, 300, 58, GOLD)
        tx, ty = 540, 900
        c.rrect_outline(tx - 270, ty - 150, tx + 270, ty + 150, 40, GOLD, 8)
        seats = [(-170, -235), (0, -235), (170, -235), (-170, 235), (0, 235), (170, 235), (-365, 0), (365, 0)]
        n = 0
        for i, (dx, dy) in enumerate(seats):
            a = prog(tt, 0.3 + i * 0.42, 0.3 + i * 0.42 + 0.35)
            if a > 0:
                n += 1
                c.circle(tx + dx, ty + dy, 56 * eb(a), WHITE)
        label = "1 persona" if n == 1 else f"{n} persone"
        if n == 0:
            label = ""
        c.text(label, 540, 1330, 110, GOLD if n == 8 else WHITE)
        c.text("A ore. Di giorno e di sera.", 540, 1480, 50, mix(GRAY, eo(prog(tt, 3.6, 4.1))), False)
    elif t < 10.0:
        tt = t - 6.2
        c.text("Prenoti solo", 540, 520, 84, WHITE)
        c.text("le ore che ti servono.", 540, 630, 84, GOLD)
        x0, x1, y0, y1 = 90, 990, 880, 990
        c.rrect(x0, y0, x1, y1, 24, DARK)
        pxh = (x1 - x0) / 16
        blocks = [(9, 11, "2 ore"), (14, 15, "1 ora"), (20, 22, "2 ore")]
        for i, (a, b, lab) in enumerate(blocks):
            g = eo(prog(tt, 0.5 + i * 0.7, 0.5 + i * 0.7 + 0.5))
            bx0 = x0 + (a - 8) * pxh
            bx1 = bx0 + (b - a) * pxh * g
            c.rrect(bx0, y0 + 10, bx1, y1 - 10, 14, GOLD)
            c.text(lab, (bx0 + (b - a) * pxh / 2), y0 - 50, 44, mix(WHITE, g))
        for h in (8, 12, 16, 20, 24):
            c.text(f"{h:02d}", x0 + (h - 8) * pxh, 1060, 38, GRAY, False)
        c.text("08:00 - 24:00", 540, 1250, 56, mix(WHITE, eo(prog(tt, 2.4, 2.9))))
    elif t < 12.8:
        tt = t - 10.0
        c.text("Perfetta per", 540, 420, 76, GOLD)
        items = ["Amministratori", "Agenti immobiliari", "Notai", "Commercialisti"]
        for i, it in enumerate(items):
            a = prog(tt, 0.2 + i * 0.5, 0.2 + i * 0.5 + 0.35)
            if a > 0:
                k = eb(a)
                y = 640 + i * 190
                hw, hh = 400 * k, 70 * k
                c.rrect_outline(540 - hw, y - hh, 540 + hw, y + hh, 70, GOLD, 6)
                c.text(it, 540, y, 56 * min(1, k), WHITE)
    else:
        cta(c, t, 12.8)
    for tb in (1.8, 6.2, 10.0, 12.8):
        c.wipe(t, tb)
    return c.finish()


# ------------------------------------------------------------------ Reel C: 20 gennaio
def reel_c(t):
    c = C()
    if t < 4.6:
        c.text("Segna la data.", 540, 250, 104, WHITE)
        c.text("GENNAIO 2027", 540, 450, 80, GOLD)
        for i, wd in enumerate("LMMGVSD"):
            c.text(wd, 157.5 + i * 135, 570, 44, GRAY, False)
        hl = t >= 2.4
        for d in range(1, 32):
            col, row = (4 + d - 1) % 7, (4 + d - 1) // 7
            x, y = 157.5 + col * 135, 690 + row * 150
            a = prog(t, 0.3 + 0.03 * d, 0.3 + 0.03 * d + 0.2)
            if d == 20 and hl:
                continue
            c.text(str(d), x, y, 56, mix(WHITE, a * (0.28 if hl else 1)), False)
        if hl:
            col, row = (4 + 19) % 7, (4 + 19) // 7
            x, y = 157.5 + col * 135, 690 + row * 150
            k = eb((t - 2.4) / 0.5)
            c.circle(x, y, 70 * k, GOLD)
            c.text("20", x, y, 64, BG)
            c.multi([("Apre ", WHITE), ("KREA District", GOLD)], 540, 1500, 70 * (0.85 + 0.15 * eb((t - 2.9) / 0.4)))
            c.text("Cassano Magnago (VA)", 540, 1590, 50, mix(GRAY, eo(prog(t, 3.2, 3.7))), False)
    elif t < 8.8:
        tt = t - 4.6
        c.text("COSA TROVI", 540, 330, 60, GOLD)
        items = ["Postazioni", "Uffici privati", "Sala riunioni", "Sede legale"]
        for i, it in enumerate(items):
            a = eo(prog(tt, 0.3 + i * 0.75, 0.3 + i * 0.75 + 0.45))
            if a > 0:
                y = 560 + i * 190
                c.rect(110, y - 12, 134, y + 12, GOLD)
                c.text(it, 170 - 300 * (1 - a), y, 96, mix(GOLD if i == 3 else WHITE, a), True, "lm")
        c.text("Accesso 24/7.", 540, 1450, 66, mix(GOLD, eo(prog(tt, 3.4, 3.9))))
    elif t < 10.6:
        tt = t - 8.8
        k = 0.7 + 0.3 * eb(tt / 0.4)
        c.text("Vieni a vederlo", 540, 780, 98 * k, WHITE)
        c.text("prima dell'apertura.", 540, 920, 84 * k, GOLD)
        c.text("Visite su appuntamento.", 540, 1080, 54, mix(GRAY, eo(prog(tt, 0.6, 1.1))), False)
    else:
        cta(c, t, 10.6)
    for tb in (4.6, 8.8, 10.6):
        c.wipe(t, tb)
    return c.finish()


REELS = {"a": (reel_a, 14.5, "motion_1_24_7"), "b": (reel_b, 15.0, "motion_2_sala_riunioni"), "c": (reel_c, 13.4, "motion_3_20_gennaio")}

if __name__ == "__main__":
    fn, dur, name = REELS[sys.argv[1]]
    out = f"{ROOT}/out/reels/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    print("done", name)
