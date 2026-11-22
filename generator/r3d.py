import math
import numpy as np, cv2
from PIL import Image, ImageDraw
from motion import F, W, H, BG, WHITE, GOLD, GRAY, clamp, prog, eo, eio, eb, mix, _logo

YELLOW = (247, 206, 36)


def clip_near(pts, near=0.2):
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ia, ib = a[2] >= near, b[2] >= near
        if ia:
            out.append(a)
        if ia != ib:
            k = (near - a[2]) / (b[2] - a[2])
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, near))
    return out


def lerp(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


class R:
    def __init__(s, cam, f=1000, cy=800, sky=((14, 16, 26), (54, 58, 74)), fog=(40, 40, 44), fog0=6.0, fogr=16.0, fogmax=0.45):
        s.cam = cam
        s.f, s.cx, s.cy = f, 540, cy
        s.fog, s.fog0, s.fogr, s.fogmax = fog, fog0, fogr, fogmax
        s.img = np.empty((H, W, 3), np.uint8)
        top, bot = np.array(sky[0], np.float32), np.array(sky[1], np.float32)
        ys = np.clip(np.arange(H) / max(cy, 1), 0, 1)[:, None]
        grad = top[None, :] * (1 - ys) + bot[None, :] * ys
        s.img[:] = grad[:, None, :].astype(np.uint8)
        s.items = []

    # ---- low level
    def _cp(s, p):
        return (p[0] - s.cam[0], p[1] - s.cam[1], p[2] - s.cam[2])

    def _proj(s, cpts):
        return np.array([[s.cx + s.f * x / z, s.cy - s.f * y / z] for x, y, z in cpts])

    def col(s, c, d, shade=1.0):
        c = tuple(min(255, v * shade) for v in c)
        k = clamp((d - s.fog0) / s.fogr) * s.fogmax
        return tuple(int(c[i] + (s.fog[i] - c[i]) * k) for i in range(3))

    def poly(s, pts, color, alpha=1.0):
        cp = clip_near([s._cp(p) for p in pts])
        if len(cp) < 3:
            return
        sc = np.clip(s._proj(cp), -20000, 20000)
        pi = (sc * 16).astype(np.int32)
        color = tuple(int(v) for v in color)
        if alpha >= 1:
            cv2.fillPoly(s.img, [pi], color, cv2.LINE_AA, 4)
            return
        x0, y0 = np.floor(sc.min(0)).astype(int)
        x1, y1 = np.ceil(sc.max(0)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0:
            return
        roi = s.img[y0:y1, x0:x1]
        tmp = roi.copy()
        cv2.fillPoly(tmp, [pi - np.array([x0 * 16, y0 * 16], np.int32)], color, cv2.LINE_AA, 4)
        cv2.addWeighted(tmp, alpha, roi, 1 - alpha, 0, roi)

    def line3(s, p, q, color, th=None):
        a, b = s._cp(p), s._cp(q)
        if a[2] < 0.2 or b[2] < 0.2:
            return
        pa, pb = s._proj([a])[0], s._proj([b])[0]
        t = th if th is not None else max(1, int(0.035 * s.f / ((a[2] + b[2]) / 2)))
        cv2.line(s.img, (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])), tuple(int(v) for v in color), t, cv2.LINE_AA)

    # ---- shapes
    def quad(s, p4, color, alpha=1.0, shade=1.0, fogged=True):
        c = (p4[0][0] + p4[2][0]) / 2, (p4[0][1] + p4[2][1]) / 2, (p4[0][2] + p4[2][2]) / 2
        d = math.dist(c, s.cam)
        s.poly(p4, s.col(color, d, shade) if fogged else color, alpha)

    def box(s, x0, x1, y0, y1, z0, z1, color, shade_scale=1.0):
        cam = s.cam
        d = math.dist(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), cam)
        def c(sh):
            return s.col(color, d, sh * shade_scale)
        if cam[0] < x0:
            s.poly([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], c(0.82))
        if cam[0] > x1:
            s.poly([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], c(0.62))
        if cam[2] > z1:
            s.poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], c(0.7))
        if cam[2] < z0:
            s.poly([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], c(1.0))
        if cam[1] > y1:
            s.poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], c(1.15))

    def add(s, key_xyz, fn):
        s.items.append((math.dist(key_xyz, s.cam), fn))

    def flush(s):
        for _, fn in sorted(s.items, key=lambda i: -i[0]):
            fn()
        s.items = []

    def tex(s, p4, img):
        cp = [s._cp(p) for p in p4]
        if any(c[2] < 0.3 for c in cp):
            return
        dst = s._proj(cp).astype(np.float32)
        x0, y0 = np.floor(dst.min(0)).astype(int)
        x1, y1 = np.ceil(dst.max(0)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0:
            return
        h, w = img.shape[:2]
        src = np.float32([[0, h], [w, h], [w, 0], [0, 0]])
        M = cv2.getPerspectiveTransform(src, dst)
        T = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]], np.float64)
        warped = cv2.warpPerspective(img, T @ M, (x1 - x0, y1 - y0), flags=cv2.INTER_AREA)
        mask = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillPoly(mask, [(dst - np.array([x0, y0], np.float32)).astype(np.int32)], 255)
        roi = s.img[y0:y1, x0:x1]
        roi[mask > 0] = warped[mask > 0]


_vig = None
def post(img, bloom=0.38, top_shade=0.93, bot_shade=0.45):
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.46) / (H * 0.62)) ** 2)
        _vig = np.clip(1.12 - 0.5 * r ** 2, 0.55, 1.0)[:, :, None]
        ts = np.clip(1 - yy / 660, 0, 1) ** 1.2 * top_shade
        bs = np.clip((yy - (H - 520)) / 520, 0, 1) ** 1.6 * bot_shade
        _vig = (_vig, (1 - np.maximum(ts, bs))[:, :, None])
    v, sh = _vig
    f = img.astype(np.float32)
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.float32)
    bright = np.clip(small - 228, 0, 255) * 2.2
    glow = cv2.GaussianBlur(bright, (0, 0), 9)
    glow = cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR)
    out = (f + glow * bloom) * v * sh
    return np.clip(out, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ logo texture (unmodified logo image)
def logo_tex():
    return _logo


def slats(r, x0, x1, y0, y1, z, color=(34, 34, 37), pitch=0.09, w=0.06, base=(8, 8, 9), skip=None):
    if base is not None:
        r.quad([(x0, y0, z + 0.02), (x1, y0, z + 0.02), (x1, y1, z + 0.02), (x0, y1, z + 0.02)], base)
    x = x0
    while x + w <= x1 + 1e-6:
        if not (skip and skip[0] - w < x < skip[1]):
            r.quad([(x, y0, z), (x + w, y0, z), (x + w, y1, z), (x, y1, z)], color)
        elif skip and skip[0] - w < x < skip[1]:
            r.quad([(x, skip[3], z), (x + w, skip[3], z), (x + w, y1, z), (x, y1, z)], color)
        x += pitch


def floor_planks(r, x0, x1, z0, z1, color, plank=0.22, y=0.0):
    r.quad([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], color)
    dark = tuple(int(v * 0.9) for v in color)
    x = x0 + plank
    while x < x1:
        r.line3((x, y, z0), (x, y, z1), dark, 1)
        x += plank
