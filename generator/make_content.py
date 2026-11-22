import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/claude/social"
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


CONTACT = ["Via Bruno Buozzi 6, Cassano Magnago (VA)", "+39 375 113 9192  ·  info@kreadistrict.it"]
W, H = 1080, 1920

# ---- stories ----
stories = [
    dict(kicker="NUOVA APERTURA", headline=[("Dal 20 gennaio 2027.", WHITE), ("Cassano Magnago.", GOLD)],
         sub="Il tuo ufficio. Tutto incluso.", footer=CONTACT[:1], y0=860),
    dict(kicker="COWORKING", headline=[("Uno spazio di lavoro condiviso.", WHITE)],
         bullets=["Canone tutto incluso", "Nessun deposito cauzionale", "Accesso 24/7"], footer=CONTACT[:1], y0=820),
    dict(kicker="SALA RIUNIONI", headline=[("Fino a 8 persone.", WHITE), ("A ore.", GOLD), ("Di giorno e di sera.", WHITE)],
         sub="Assemblee, clienti, consulenze.", footer=CONTACT[:1], y0=800, ),
    dict(kicker="ACCESSO 24/7", headline=[("Entri quando vuoi.", WHITE)],
         sub="24 ore su 24, 7 giorni su 7. Accesso autonomo, su prenotazione.", footer=CONTACT[:1], y0=860),
    dict(kicker="SEDE LEGALE", headline=[("A Cassano Magnago,", WHITE), ("a prezzi vantaggiosi.", GOLD)],
         sub="Scrivici per scoprire i pacchetti.", footer=CONTACT, y0=840),
]
for i, s in enumerate(stories, 1):
    hs = 74 if i == 5 else 90
    im = scene(W, H, 760, 110, hsize=hs, **s)
    im.save(f"{OUT}/stories/story_{i}.png")

# ---- posts 1080x1350 ----
PW, PH = 1080, 1350
posts = [
    dict(kicker="NUOVA APERTURA", headline=[("Apre il 20 gennaio 2027.", WHITE)],
         sub="Uffici, postazioni e sala riunioni a Cassano Magnago. Accesso 24/7.",
         footer=CONTACT[:1], y0=560, hsize=84),
    dict(kicker="PER CHI È", headline=[("Il tuo studio, senza costi fissi.", WHITE)],
         bullets=["Amministratori di condominio", "Agenti immobiliari", "Notai e commercialisti", "Professionisti e partite IVA"],
         footer=CONTACT[:1], y0=560, hsize=70),
]
for i, s in enumerate(posts, 1):
    im = scene(PW, PH, 600, 50, **s)
    im.save(f"{OUT}/posts/post_{i}.png")

# ---- profile picture ----
pp = Image.new("RGB", (1080, 1080), BG)
lg = logo(840)
pp.paste(lg, (120, (1080 - lg.height) // 2))
pp.save(f"{OUT}/profile_picture.png")

# ---- reels ----
reels = {
    "reel_1_cose_il_coworking": [
        (3, dict(kicker="", headline=[("Coworking:", WHITE), ("cos'è?", GOLD)], y0=860, hsize=130)),
        (4, dict(kicker="COWORKING", headline=[("Uno spazio di lavoro condiviso.", WHITE)], y0=860)),
        (5, dict(kicker="SCEGLI QUELLO CHE TI SERVE", headline=[("Scrivania.", WHITE), ("Sala riunioni.", WHITE), ("Ufficio privato.", GOLD)], y0=800)),
        (4, dict(kicker="", headline=[("Canone tutto incluso.", WHITE), ("Nessun deposito cauzionale.", GOLD)], y0=860)),
        (4, dict(kicker="DAL 20 GENNAIO", headline=[("KREA District,", WHITE), ("Cassano Magnago.", GOLD)], footer=CONTACT[:1], y0=860)),
    ],
    "reel_2_sala_riunioni": [
        (3, dict(kicker="", headline=[("Ti serve una sala riunioni", WHITE), ("per 2 ore?", GOLD)], y0=820, hsize=96)),
        (5, dict(kicker="SALA RIUNIONI", headline=[("Fino a 8 persone.", WHITE), ("Di giorno e di sera.", GOLD)], y0=840)),
        (5, dict(kicker="PER", headline=[("Assemblee, clienti, consulenze.", WHITE)], sub="Amministratori, agenti, notai, commercialisti.", y0=800)),
        (4, dict(kicker="ACCESSO 24/7", headline=[("Entri in autonomia, su prenotazione.", WHITE)], footer=CONTACT[:1], y0=860)),
    ],
    "reel_3_cosa_trovi": [
        (3, dict(kicker="", headline=[("Dal 20 gennaio,", WHITE), ("a Cassano Magnago.", GOLD)], y0=860, hsize=100)),
        (6, dict(kicker="COSA TROVI", headline=[("Postazioni.", WHITE), ("Uffici privati.", WHITE), ("Sala riunioni.", WHITE), ("Sede legale.", GOLD)], y0=760, hsize=96)),
        (4, dict(kicker="", headline=[("Entri quando vuoi.", WHITE), ("24/7.", GOLD)], y0=860, hsize=110)),
        (4, dict(kicker="VISITE SU APPUNTAMENTO", headline=[("Chiamaci:", WHITE), ("+39 375 113 9192", GOLD)], footer=CONTACT[:1], y0=840, hsize=84)),
    ],
}
FADE = 0.4
for name, scenes in reels.items():
    paths, durs = [], []
    for j, (dur, s) in enumerate(scenes):
        p = f"{ROOT}/frames/{name}_{j}.png"
        scene(W, H, 620, 100, hsize=s.pop("hsize", 92), **s).save(p)
        paths.append(p)
        durs.append(dur)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, d in zip(paths, durs):
        cmd += ["-loop", "1", "-framerate", "30", "-t", str(d + FADE), "-i", p]
    flt, last, off = "", "[0:v]", 0.0
    for k in range(1, len(paths)):
        off += durs[k - 1]
        flt += f"{last}[{k}:v]xfade=transition=fade:duration={FADE}:offset={off:.2f}[v{k}];"
        last = f"[v{k}]"
    flt = flt.rstrip(";")
    cmd += ["-filter_complex", flt, "-map", last, "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", f"{OUT}/reels/{name}.mp4"]
    subprocess.run(cmd, check=True)
    print("ok", name, sum(durs))
