import math
import numpy as np, cv2
from PIL import Image, ImageDraw
from r3d import *
from motion import C, F, cta, logo_img

LOGO = logo_tex()

def slide_tex(p):
    img = np.full((540, 960, 3), (246, 246, 246), np.uint8)
    cv2.rectangle(img, (0, 0), (960, 96), (32, 30, 31), -1)
    cv2.rectangle(img, (0, 90), (960, 96), GOLD, -1)
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil)
    d.text((48, 48), "Piano 2027", font=F(True, 44), fill=(255, 255, 255), anchor="lm")
    d.text((48, 150), "Risultati trimestrali", font=F(False, 30), fill=(110, 110, 112), anchor="lm")
    img = np.asarray(pil).copy()
    vals = [0.32, 0.46, 0.6, 0.78, 0.95]
    for i, v in enumerate(vals):
        h = int(300 * v * eo(prog(p, 0.1 + i * 0.12, 0.1 + i * 0.12 + 0.45)))
        x = 130 + i * 150
        cv2.rectangle(img, (x, 500 - h), (x + 96, 500), GOLD if i == 4 else (58, 58, 62), -1)
    cv2.line(img, (90, 502), (870, 502), (150, 150, 150), 3, cv2.LINE_AA)
    return img


def meeting(t, T=5.0):
    k = eio(t / T)
    cam = (0.3 * math.sin(t * 0.6), 1.5, -1.6 + 3.3 * k)
    r = R(cam, f=1000, cy=790, sky=(( 20, 20, 22), (20, 20, 22)), fog=(30, 30, 33), fog0=7, fogr=10, fogmax=0.35)
    X, Y, Z0, Z1 = 3.2, 2.9, -4.0, 7.5
    # shell
    floor_planks(r, -X, X, Z0, Z1, (170, 140, 106), 0.24)
    r.quad([(-X, Y, Z0), (X, Y, Z0), (X, Y, Z1), (-X, Y, Z1)], (196, 196, 198))
    r.quad([(-X, 0, Z0), (-X, 0, Z1), (-X, Y, Z1), (-X, Y, Z0)], (214, 214, 216), shade=0.95)
    r.quad([(X, 0, Z0), (X, 0, Z1), (X, Y, Z1), (X, Y, Z0)], (170, 170, 174), shade=0.9)
    # ceiling LED lines
    for lx in (-1.3, 1.3):
        r.quad([(lx - 0.05, Y - 0.01, Z0), (lx + 0.05, Y - 0.01, Z0), (lx + 0.05, Y - 0.01, Z1), (lx - 0.05, Y - 0.01, Z1)], (255, 252, 238), fogged=False)
    # slatted wall
    slats(r, -X, X, 0, Y, Z1)
    # TV
    tz = Z1 - 0.1
    r.quad([(-1.18, 0.88, tz), (1.18, 0.88, tz), (1.18, 2.22, tz), (-1.18, 2.22, tz)], (6, 6, 7), fogged=False)
    r.tex([(-1.1, 0.95, tz - 0.01), (1.1, 0.95, tz - 0.01), (1.1, 2.19, tz - 0.01), (-1.1, 2.19, tz - 0.01)], slide_tex(prog(t, 1.0, 4.2)))
    r.quad([(-1.0, 0.82, tz), (1.0, 0.82, tz), (1.0, 0.85, tz), (-1.0, 0.85, tz)], YELLOW, fogged=False)
    # table + chairs (depth sorted)
    def table():
        r.box(-0.62, -0.5, 0, 0.72, 3.5, 3.62, (30, 30, 33))
        r.box(0.5, 0.62, 0, 0.72, 3.5, 3.62, (30, 30, 33))
        r.box(-0.62, -0.5, 0, 0.72, 5.9, 6.02, (30, 30, 33))
        r.box(0.5, 0.62, 0, 0.72, 5.9, 6.02, (30, 30, 33))
        r.box(-0.9, 0.9, 0.72, 0.77, 3.0, 6.4, (222, 222, 224))
    r.add((0, 0.7, 4.7), table)
    for side in (-1, 1):
        for zc in (3.5, 4.3, 5.1, 5.9):
            def chair(side=side, zc=zc):
                cx = side * 1.3
                r.box(cx - 0.25, cx + 0.25, 0.42, 0.5, zc - 0.25, zc + 0.25, (44, 44, 48))
                r.box(cx - 0.2, cx + 0.2, 0, 0.42, zc - 0.03, zc + 0.03, (28, 28, 30))
                ox = cx + side * 0.25
                r.box(ox - 0.03, ox + 0.03, 0.5, 1.05, zc - 0.25, zc + 0.25, (40, 40, 44))
            r.add((side * 1.3, 0.5, zc), chair)
    r.flush()
    return post(r.img)


def entrance(t, T=4.4):
    k = eio(t / T)
    cam = (0.5 * (1 - k) - 0.2, 1.5, -6.5 + 8.0 * k)
    r = R(cam, f=1000, cy=800, sky=((10, 12, 22), (58, 62, 80)), fog=(40, 44, 60), fog0=8, fogr=18, fogmax=0.5)
    Z = 6.0
    r.quad([(-14, 0, -12), (14, 0, -12), (14, 0, Z), (-14, 0, Z)], (46, 46, 50))
    r.quad([(-1.4, 0, -12), (2.2, 0, -12), (2.2, 0, Z), (-1.4, 0, Z)], (92, 90, 92))
    open_ = eio(prog(t, 2.2, 3.3))
    # interior glow
    r.quad([(0.4, 0, Z + 0.01), (1.7, 0, Z + 0.01), (1.7, 2.2, Z + 0.01), (0.4, 2.2, Z + 0.01)], (255, 238, 196), fogged=False)
    r.quad([(0.4, 0, Z + 0.01), (1.7, 0, Z + 0.01), (1.7, 0.9, Z + 0.01), (0.4, 0.9, Z + 0.01)], (255, 214, 120), alpha=0.35, fogged=False)
    # wall (no base over door)
    r.quad([(-14, 0, Z), (0.4, 0, Z), (0.4, 3.4, Z), (-14, 3.4, Z)], (8, 8, 9))
    r.quad([(1.7, 0, Z), (14, 0, Z), (14, 3.4, Z), (1.7, 3.4, Z)], (8, 8, 9))
    r.quad([(0.4, 2.2, Z), (1.7, 2.2, Z), (1.7, 3.4, Z), (0.4, 3.4, Z)], (8, 8, 9))
    slats(r, -10, 10, 0, 3.4, Z - 0.01, base=None, skip=(0.4, 1.7, 0, 2.2))
    # logo sign
    r.tex([(-2.5, 1.0, Z - 0.03), (-1.0, 1.0, Z - 0.03), (-1.0, 2.06, Z - 0.03), (-2.5, 2.06, Z - 0.03)], LOGO)
    # light spill on ground
    r.quad([(0.2, 0.01, Z - 2.6), (1.9, 0.01, Z - 2.6), (1.9, 0.01, Z), (0.2, 0.01, Z)], (255, 226, 160), alpha=0.28 + 0.1 * open_, fogged=False)
    # sliding glass
    sh = 0.62 * open_
    for (a, b, d) in ((0.4, 1.05, -1), (1.05, 1.7, 1)):
        a2, b2 = a + d * sh, b + d * sh
        r.quad([(a2, 0, Z - 0.04), (b2, 0, Z - 0.04), (b2, 2.2, Z - 0.04), (a2, 2.2, Z - 0.04)], (200, 222, 235), alpha=0.22, fogged=False)
        for (p, q) in (((a2, 0, Z - 0.05), (a2, 2.2, Z - 0.05)), ((b2, 0, Z - 0.05), (b2, 2.2, Z - 0.05)), ((a2, 2.2, Z - 0.05), (b2, 2.2, Z - 0.05)), ((a2, 0.02, Z - 0.05), (b2, 0.02, Z - 0.05))):
            r.line3(p, q, (240, 240, 240))
    r.flush()
    return post(r.img, bloom=0.7)


def corridor(t, T=5.0):
    k = eio(t / T)
    cam = (0.0, 1.55, -2.0 + 6.0 * k)
    r = R(cam, f=1000, cy=800, sky=((24, 24, 26), (24, 24, 26)), fog=(30, 30, 33), fog0=6, fogr=10, fogmax=0.4)
    X, Y, Z0, Z1 = 1.4, 2.8, -4.0, 10.0
    OX = 4.4
    floor_planks(r, -OX, OX, Z0, Z1, (150, 148, 146), 0.6)
    r.quad([(-OX, Y, Z0), (OX, Y, Z0), (OX, Y, Z1), (-OX, Y, Z1)], (190, 190, 192))
    for lx in (-0.5, 0.5):
        r.quad([(lx - 0.05, Y - 0.01, Z0), (lx + 0.05, Y - 0.01, Z0), (lx + 0.05, Y - 0.01, Z1), (lx - 0.05, Y - 0.01, Z1)], (255, 252, 238), fogged=False)
    # end wall
    slats(r, -OX, OX, 0, Y, Z1)
    r.tex([(-0.75, 1.0, Z1 - 0.03), (0.75, 1.0, Z1 - 0.03), (0.75, 2.06, Z1 - 0.03), (-0.75, 2.06, Z1 - 0.03)], LOGO)
    zs = [(1.0, 3.5), (3.7, 6.2), (6.4, 8.9)]
    for side in (-1, 1):
        ox = side * OX
        gx = side * X
        # outer wall + dividers
        r.quad([(ox, 0, Z0), (ox, 0, Z1), (ox, Y, Z1), (ox, Y, Z0)], (205, 205, 207), shade=0.9)
        for (za, zb) in zs:
            for zz in (za, zb):
                lo, hi = sorted((ox, gx))
                r.add(((lo + hi) / 2, 1.2, zz), lambda lo=lo, hi=hi, zz=zz: r.box(lo, hi, 0, Y, zz - 0.03, zz + 0.03, (205, 205, 207)))
            def desk(za=za, zb=zb, side=side):
                zc = (za + zb) / 2
                dx = side * 3.6
                r.box(dx - 0.4, dx + 0.4, 0.7, 0.75, zc - 0.7, zc + 0.7, (245, 245, 245))
                r.box(dx - 0.35, dx - 0.3, 0, 0.7, zc - 0.65, zc - 0.6, (30, 30, 33))
                r.box(dx - 0.35, dx - 0.3, 0, 0.7, zc + 0.6, zc + 0.65, (30, 30, 33))
                r.box(dx - side * 0.8 - 0.25, dx - side * 0.8 + 0.25, 0.42, 0.5, zc - 0.25, zc + 0.25, (44, 44, 48))
                r.box(dx - side * 0.8 - 0.2, dx - side * 0.8 + 0.2, 0, 0.42, zc - 0.03, zc + 0.03, (28, 28, 30))
            r.add((side * 3.6, 0.7, (za + zb) / 2), desk)
            def glass(za=za, zb=zb, gx=gx):
                r.quad([(gx, 0, za), (gx, 0, zb), (gx, 2.6, zb), (gx, 2.6, za)], (196, 222, 236), alpha=0.16, fogged=False)
                for p, q in (((gx, 0.02, za), (gx, 0.02, zb)), ((gx, 2.6, za), (gx, 2.6, zb)), ((gx, 0, za), (gx, 2.6, za)), ((gx, 0, zb), (gx, 2.6, zb)), ((gx, 0, (za + zb) / 2), (gx, 2.6, (za + zb) / 2))):
                    r.line3(p, q, (250, 250, 250))
            r.add((gx, 1.3, (za + zb) / 2 - 0.01), glass)
    r.flush()
    return post(r.img)


def kitchen(t, T=5.0):
    k = eio(t / T)
    cam = (0.35 * math.sin(t * 0.5) , 1.55, -2.2 + 2.9 * k)
    r = R(cam, f=1000, cy=800, sky=((24, 24, 26), (24, 24, 26)), fog=(40, 36, 28), fog0=6, fogr=10, fogmax=0.3)
    X, Y, Z0, Z1 = 3.5, 2.9, -4.0, 6.5
    floor_planks(r, -X, X, Z0, Z1, (176, 146, 112), 0.24)
    r.quad([(-X, Y, Z0), (X, Y, Z0), (X, Y, Z1), (-X, Y, Z1)], (196, 196, 198))
    r.quad([(-X, 0, Z0), (-X, 0, Z1), (-X, Y, Z1), (-X, Y, Z0)], (214, 214, 216), shade=0.95)
    r.quad([(X, 0, Z0), (X, 0, Z1), (X, Y, Z1), (X, Y, Z0)], (172, 172, 176), shade=0.9)
    r.quad([(-X, 0, Z1), (X, 0, Z1), (X, Y, Z1), (-X, Y, Z1)], YELLOW)
    # shelves on yellow wall
    for sy in (1.45, 1.95):
        r.box(-2.6, 2.6, sy, sy + 0.05, Z1 - 0.3, Z1 - 0.02, (245, 245, 245))
    for i, bx in enumerate((-2.2, -1.6, -0.5, 0.9, 1.7, 2.2)):
        r.box(bx - 0.12, bx + 0.12, 1.5, 1.5 + 0.18 + 0.05 * (i % 3), Z1 - 0.26, Z1 - 0.06, (36, 36, 40) if i % 2 else (250, 250, 250))
    # back counter
    r.box(-3.0, 3.0, 0, 0.88, Z1 - 0.85, Z1 - 0.02, (30, 30, 33))
    r.box(-3.05, 3.05, 0.88, 0.93, Z1 - 0.9, Z1 - 0.02, (222, 222, 224))
    # island
    def island():
        r.box(-1.5, 1.5, 0, 0.9, 3.0, 4.0, (30, 30, 33))
        r.box(-1.58, 1.58, 0.9, 0.96, 2.92, 4.08, (226, 226, 228))
    r.add((0, 0.9, 3.5), island)
    for sx in (-1.0, -0.33, 0.33, 1.0):
        def stool(sx=sx):
            r.box(sx - 0.02, sx + 0.02, 0, 0.62, 2.35 - 0.02, 2.35 + 0.02, (28, 28, 30))
            r.box(sx - 0.2, sx + 0.2, 0.62, 0.69, 2.35 - 0.2, 2.35 + 0.2, (40, 40, 44))
        r.add((sx, 0.6, 2.35), stool)
    # pendants
    for px in (-1.0, 0.0, 1.0):
        def pend(px=px):
            r.line3((px, Y, 3.5), (px, 2.05, 3.5), (20, 20, 22), 2)
            r.box(px - 0.16, px + 0.16, 1.9, 2.05, 3.34, 3.66, (20, 20, 22))
            r.quad([(px - 0.14, 1.9, 3.36), (px + 0.14, 1.9, 3.36), (px + 0.14, 1.9, 3.64), (px - 0.14, 1.9, 3.64)], (255, 236, 190), fogged=False)
        r.add((px, 2.0, 3.5), pend)
    r.flush()
    return post(r.img, bloom=0.65)
