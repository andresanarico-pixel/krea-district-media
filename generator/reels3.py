import sys, math, subprocess
import numpy as np
from motion import C, F, mix, eo, eio, eb, prog, clamp, WHITE, GOLD, GRAY, BG, W, H, FPS, ROOT, DARK

class D(C):
    oy = 130
    _skip = False
    def text(self, txt, x, y, *a, **k): C.text(self, txt, x, y + self.oy, *a, **k)
    def line(self, p, q, col, th): C.line(self, (p[0], p[1] + self.oy), (q[0], q[1] + self.oy), col, th)
    def rect(self, x0, y0, x1, y1, col):
        o = 0 if self._skip else self.oy
        C.rect(self, x0, y0 + o, x1, y1 + o, col)
    def circle(self, cx, cy, r, col, th=-1):
        o = 0 if self._skip else self.oy
        C.circle(self, cx, cy + o, r, col, th)
    def rrect(self, x0, y0, x1, y1, r, col):
        self._skip = True
        C.rrect(self, x0, y0 + self.oy, x1, y1 + self.oy, r, col)
        self._skip = False
    def logo(self, cx, cy, width, a): C.logo(self, cx, cy + self.oy, width, a)
    def wipe(self, t, tb, dur=0.22):
        self._skip = True
        C.wipe(self, t, tb, dur)
        self._skip = False

def tw(txt, size, bold=True):
    return F(bold, size).getlength(txt)

def check(c, x, y, s, col=GOLD, th=9):
    c.line((x - 0.5 * s, y), (x - 0.12 * s, y + 0.4 * s), col, th)
    c.line((x - 0.12 * s, y + 0.4 * s), (x + 0.6 * s, y - 0.5 * s), col, th)

def cta_dm(c, t, t0):
    a = lambda d: eo(prog(t, t0 + d, t0 + d + 0.5))
    c.logo(540, 600, 820 * (0.92 + 0.08 * a(0)), a(0))
    c.text("Dal 20 gennaio 2027 · Cassano Magnago", 540, 980, 46, mix(GOLD, a(0.4)))
    k = 0.85 + 0.15 * eb((t - t0 - 0.6) / 0.4)
    c.text("Scrivici in DM", 540, 1140, 96 * k, mix(WHITE, a(0.6)))
    c.text("o chiamaci", 540, 1235, 44, mix(GRAY, a(0.9)), False)
    c.text("+39 375 113 9192", 540, 1325, 70, mix(GOLD, a(0.9)))
    c.text("info@kreadistrict.it", 540, 1410, 44, mix(GRAY, a(1.1)), False)
    c.text("Via Bruno Buozzi 6, 21012 Cassano Magnago (VA)", 540, 1490, 36, mix(GRAY, a(1.2)), False)

def pop(t, t0, d=0.4):
    return 0.75 + 0.25 * eb((t - t0) / d)

def pill(c, y, txt, a, hw=420, hh=68, size=50, col=GOLD):
    k = eb(a)
    if a <= 0: return
    c.rrect(540 - hw * k, y - hh * k, 540 + hw * k, y + hh * k, hh * k, col)
    c.rrect(540 - hw * k + 6, y - hh * k + 6, 540 + hw * k - 6, y + hh * k - 6, max(hh * k - 6, 1), BG)
    c.text(txt, 540, y, size * min(1, k), WHITE)

# ---------------------------------------------------------------- 7
def reel7(t):
    c = D()
    if t < 5.6:
        c.text("Un ufficio", 540, 230, 90, WHITE); c.text("tradizionale?", 540, 335, 90, WHITE)
        items = ["Contratto lungo", "Utenze a parte", "Internet da attivare", "Pulizie e arredi"]
        for i, it in enumerate(items):
            a = eo(prog(t, 0.5 + i * 0.5, 1.0 + i * 0.5))
            st = prog(t, 3.0 + i * 0.5, 3.35 + i * 0.5)
            y = 600 + i * 150
            col = mix(GRAY if st > 0 else WHITE, a)
            c.text(it, 170, y, 62, col, True, "lm")
            if st > 0:
                c.line((150, y), (150 + (tw(it, 62) + 40) * eo(st), y), GOLD, 8)
        c.wipe(t, 5.6)
    elif t < 10.4:
        tt = t - 5.6
        c.text("KREA District", 540, 230, 90, GOLD); c.text("è un'altra cosa.", 540, 335, 80, WHITE)
        items = ["Un solo canone", "Tutto incluso", "Nessun deposito cauzionale", "Accesso 24/7"]
        for i, it in enumerate(items):
            a = prog(tt, 0.6 + i * 0.6, 1.0 + i * 0.6)
            y = 600 + i * 150
            if a > 0:
                check(c, 170, y, 50 * eb(a))
                c.text(it, 250, y, 50, mix(WHITE, eo(a)), True, "lm")
        c.wipe(t, 5.6); c.wipe(t, 10.4)
    elif t < 12.8:
        tt = t - 10.4
        k = pop(tt, 0)
        c.text("Tu pensi solo", 540, 780, 104 * k, WHITE); c.text("al lavoro.", 540, 940, 130 * pop(tt, 0.3), GOLD)
        c.wipe(t, 10.4); c.wipe(t, 12.8)
    else:
        cta_dm(c, t, 12.8); c.wipe(t, 12.8)
    return c.finish()

# ---------------------------------------------------------------- 8
def reel8(t):
    c = D()
    if t < 2.4:
        c.text("Cliente", 540, 760, 150 * pop(t, 0), WHITE); c.text("alle 18:00.", 540, 930, 140 * pop(t, 0.2), GOLD)
        c.rect(190, 1070, 190 + 700 * eo((t - 0.5) / 0.8), 1080, GOLD)
        c.wipe(t, 2.4)
    elif t < 5.0:
        tt = t - 2.4
        c.text("Dove lo ricevi?", 540, 420, 90 * pop(tt, 0), WHITE)
        for i, it in enumerate(["A casa?", "Al bar?", "In studio, stretti?"]):
            a = eo(prog(tt, 0.3 + i * 0.4, 0.7 + i * 0.4)); st = prog(tt, 1.5 + i * 0.3, 1.8 + i * 0.3)
            y = 700 + i * 190
            c.text(it, 540, y, 78, mix(GRAY if st > 0 else WHITE, a))
            if st > 0:
                w = tw(it, 78) + 50
                c.line((540 - w / 2, y), (540 - w / 2 + w * eo(st), y), GOLD, 9)
        c.wipe(t, 2.4); c.wipe(t, 5.0)
    elif t < 9.6:
        tt = t - 5.0
        c.text("Prenoti la sala.", 540, 400, 96 * pop(tt, 0), GOLD)
        for i, it in enumerate(["1 ora", "2 ore", "Mezza giornata", "Una giornata", "Una sera"]):
            pill(c, 650 + i * 150, it, prog(tt, 0.5 + i * 0.55, 0.85 + i * 0.55), 380, 60, 48)
        c.wipe(t, 5.0); c.wipe(t, 9.6)
    elif t < 12.0:
        tt = t - 9.6
        c.text("Fino a 8 persone.", 540, 760, 100 * pop(tt, 0), WHITE)
        c.text("Spazio elegante.", 540, 905, 86 * pop(tt, 0.3), GOLD)
        c.text("Accesso 24/7.", 540, 1030, 60, mix(GRAY, eo(prog(tt, 0.9, 1.4))), False)
        c.wipe(t, 9.6); c.wipe(t, 12.0)
    else:
        cta_dm(c, t, 12.0); c.wipe(t, 12.0)
    return c.finish()

# ---------------------------------------------------------------- 9
def reel9(t):
    c = D()
    if t < 2.2:
        c.text("Sei un", 540, 780, 150 * pop(t, 0), WHITE); c.text("professionista?", 540, 940, 118 * pop(t, 0.2), GOLD)
        c.wipe(t, 2.2)
    elif t < 8.4:
        tt = t - 2.2
        c.text("KREA District è per te:", 540, 320, 62, GOLD)
        items = ["Libero professionista", "Agente immobiliare", "Amministratore di condominio", "Notaio o commercialista", "Piccola azienda"]
        for i, it in enumerate(items):
            pill(c, 540 + i * 165, it, prog(tt, 0.3 + i * 0.65, 0.65 + i * 0.65), 440, 66, 44 if len(it) > 24 else 50)
        c.wipe(t, 2.2); c.wipe(t, 8.4)
    elif t < 11.0:
        tt = t - 8.4
        c.text("Non ti serve", 540, 700, 98 * pop(tt, 0), WHITE); c.text("un ufficio enorme.", 540, 815, 98 * pop(tt, 0.15), WHITE)
        c.text("Ti serve il posto giusto.", 540, 1020, 70 * pop(tt, 1.0), GOLD if tt > 1.0 else BG)
        c.wipe(t, 8.4); c.wipe(t, 11.0)
    else:
        cta_dm(c, t, 11.0); c.wipe(t, 11.0)
    return c.finish()

# ---------------------------------------------------------------- 10
BEATS = [(["Hai bisogno di", "una scrivania?"], "Tutto incluso."), (["Di un ufficio", "privato?"], "Tutto incluso."),
         (["Di una sala", "riunioni?"], "Tutto incluso."), (["Di una sede", "legale?"], "Perfetto. Ci siamo.")]
def reel10(t):
    c = D()
    if t < 10.8:
        i = min(int(t // 2.7), 3); tt = t - i * 2.7
        q, ans = BEATS[i]
        c.text(q[0], 540, 640, 92 * pop(tt, 0), WHITE); c.text(q[1], 540, 760, 92 * pop(tt, 0.1), WHITE)
        a = prog(tt, 1.1, 1.6)
        if a > 0:
            y = 1080 + 80 * (1 - eo(a))
            c.circle(540, 960, 52 * eb(a), GOLD)
            check(c, 540, 962, 46 * eb(a), BG, 10)
            c.text(ans, 540, y + 60, (110 if i < 3 else 84) * pop(tt, 1.1), mix(GOLD, eo(a)))
        for k in range(1, 4):
            c.wipe(t, k * 2.7)
        c.wipe(t, 10.8)
    elif t < 13.2:
        tt = t - 10.8
        c.text("Noi ci siamo.", 540, 800, 128 * pop(tt, 0), WHITE)
        c.text("Cassano Magnago.", 540, 960, 70 * pop(tt, 0.4), GOLD if tt > 0.4 else BG)
        c.wipe(t, 10.8); c.wipe(t, 13.2)
    else:
        cta_dm(c, t, 13.2); c.wipe(t, 13.2)
    return c.finish()

BEATS2 = [(["Da casa", "ti distrai?"], "Scrivania vera."), (["Clienti da", "ricevere?"], "Sala da 8."),
          (["Un indirizzo", "per la società?"], "Sede legale."), (["Lavori fino", "a tardi?"], "Aperto 24/7.")]
def reel11(t):
    c = D()
    if t < 10.8:
        i = min(int(t // 2.7), 3); tt = t - i * 2.7
        q, ans = BEATS2[i]
        c.text(q[0], 540, 640, 92 * pop(tt, 0), WHITE); c.text(q[1], 540, 760, 92 * pop(tt, 0.1), WHITE)
        a = prog(tt, 1.1, 1.6)
        if a > 0:
            y = 1080 + 80 * (1 - eo(a))
            c.circle(540, 960, 52 * eb(a), GOLD)
            check(c, 540, 962, 46 * eb(a), BG, 10)
            c.text(ans, 540, y + 60, 100 * pop(tt, 1.1), mix(GOLD, eo(a)))
        for k in range(1, 4):
            c.wipe(t, k * 2.7)
        c.wipe(t, 10.8)
    elif t < 13.2:
        tt = t - 10.8
        c.text("Un problema,", 540, 780, 100 * pop(tt, 0), WHITE)
        c.text("una soluzione.", 540, 910, 100 * pop(tt, 0.3), GOLD if tt > 0.3 else BG)
        c.wipe(t, 10.8); c.wipe(t, 13.2)
    else:
        cta_dm(c, t, 13.2); c.wipe(t, 13.2)
    return c.finish()


# ---------------------------------------------------------------- 12-14 (factory)
def beat_reel(beats, closing):
    n = len(beats); T = n * 2.7
    def fn(t):
        c = D()
        if t < T:
            i = min(int(t // 2.7), n - 1); tt = t - i * 2.7
            q, ans = beats[i]
            c.text(q[0], 540, 640, 88 * pop(tt, 0), WHITE); c.text(q[1], 540, 760, 88 * pop(tt, 0.1), WHITE)
            a = prog(tt, 1.1, 1.6)
            if a > 0:
                y = 1080 + 80 * (1 - eo(a))
                c.circle(540, 960, 52 * eb(a), GOLD)
                check(c, 540, 962, 46 * eb(a), BG, 10)
                c.text(ans, 540, y + 60, 96 * pop(tt, 1.1), mix(GOLD, eo(a)))
            for k in range(1, n):
                c.wipe(t, k * 2.7)
            c.wipe(t, T)
        elif t < T + 2.4:
            tt = t - T
            c.text(closing[0], 540, 780, 100 * pop(tt, 0), WHITE)
            c.text(closing[1], 540, 910, 100 * pop(tt, 0.3), GOLD if tt > 0.3 else BG)
            c.wipe(t, T); c.wipe(t, T + 2.4)
        else:
            cta_dm(c, t, T + 2.4); c.wipe(t, T + 2.4)
        return c.finish()
    return fn, T + 2.4 + 3.6

BEATS3 = [(["Amministratore", "di condominio?"], "Assemblee in sala."), (["Agente", "immobiliare?"], "Clienti a casa tua."),
          (["Commercialista", "o notaio?"], "Studio, non affitto."), (["Libero", "professionista?"], "Scrivania vera.")]
BEATS4 = [(["Utenze", "a parte?"], "Tutto incluso."), (["Deposito", "cauzionale?"], "Nessuno."),
          (["Costi fissi", "da ufficio?"], "Un solo canone.")]
BEATS5 = [(["Società senza", "una sede?"], "Sede legale."), (["Domenica sera,", "scadenza lunedì?"], "Aperto 24/7."),
          (["Riunione", "a sorpresa?"], "Sala da 8.")]
_r12 = beat_reel(BEATS3, ("C'è un posto", "per te.")); _r13 = beat_reel(BEATS4, ("Meno pensieri,", "più lavoro.")); _r14 = beat_reel(BEATS5, ("Un problema,", "una soluzione."))
reel12, reel13, reel14 = _r12[0], _r13[0], _r14[0]

# ---------------------------------------------------------------- 15: postazione a ore / giornata / mesi
def reel15(t):
    c = D()
    if t < 2.4:
        c.text("Ti serve", 540, 770, 140 * pop(t, 0), WHITE); c.text("una scrivania?", 540, 930, 118 * pop(t, 0.2), GOLD)
        c.rect(190, 1060, 190 + 700 * eo((t - 0.5) / 0.8), 1070, GOLD)
        c.wipe(t, 2.4)
    elif t < 7.2:
        tt = t - 2.4
        c.text("Per quanto?", 540, 400, 100 * pop(tt, 0), WHITE)
        c.text("Scegli tu.", 540, 520, 64, mix(GOLD, eo(prog(tt, 0.3, 0.8))))
        for i, it in enumerate(["Qualche ora", "Una giornata", "Più mesi"]):
            pill(c, 760 + i * 190, it, prog(tt, 0.8 + i * 0.75, 1.2 + i * 0.75), 400, 72, 56)
        c.wipe(t, 2.4); c.wipe(t, 7.2)
    elif t < 11.0:
        tt = t - 7.2
        c.text("Postazione in open space.", 540, 420, 62, GOLD)
        for i, it in enumerate(["Canone tutto incluso", "Nessun deposito cauzionale", "Accesso 24/7"]):
            a = prog(tt, 0.4 + i * 0.6, 0.8 + i * 0.6); y = 660 + i * 170
            if a > 0:
                check(c, 150, y, 50 * eb(a)); c.text(it, 230, y, 54, mix(WHITE, eo(a)), True, "lm")
        c.wipe(t, 7.2); c.wipe(t, 11.0)
    elif t < 13.2:
        tt = t - 11.0
        c.text("Arrivi. Ti siedi.", 540, 790, 96 * pop(tt, 0), WHITE); c.text("Lavori.", 540, 940, 130 * pop(tt, 0.35), GOLD if tt > 0.35 else BG)
        c.wipe(t, 11.0); c.wipe(t, 13.2)
    else:
        cta_dm(c, t, 13.2); c.wipe(t, 13.2)
    return c.finish()

# ---------------------------------------------------------------- 16: a cosa serve la sala riunioni
def reel16(t):
    c = D()
    if t < 2.4:
        c.text("Sala riunioni.", 540, 770, 128 * pop(t, 0), WHITE); c.text("Fino a 8 persone.", 540, 930, 100 * pop(t, 0.2), GOLD)
        c.wipe(t, 2.4)
    elif t < 7.6:
        tt = t - 2.4
        c.text("Per cosa la usi?", 540, 380, 90 * pop(tt, 0), GOLD)
        for i, it in enumerate(["Assemblee di condominio", "Incontri con i clienti", "Consulenze", "Colloqui"]):
            a = prog(tt, 0.5 + i * 0.7, 0.9 + i * 0.7); y = 620 + i * 165
            if a > 0:
                check(c, 150, y, 50 * eb(a)); c.text(it, 230, y, 56, mix(WHITE, eo(a)), True, "lm")
        c.wipe(t, 2.4); c.wipe(t, 7.6)
    elif t < 11.8:
        tt = t - 7.6
        c.text("Per quanto tempo?", 540, 400, 84 * pop(tt, 0), WHITE)
        for i, it in enumerate(["A ore", "Mezza giornata", "Una giornata", "Anche di sera"]):
            pill(c, 640 + i * 165, it, prog(tt, 0.4 + i * 0.6, 0.75 + i * 0.6), 380, 64, 50)
        c.wipe(t, 7.6); c.wipe(t, 11.8)
    else:
        cta_dm(c, t, 11.8); c.wipe(t, 11.8)
    return c.finish()

REELS = {"7": (reel7, 16.4, "motion_7_perche_coworking"), "8": (reel8, 15.6, "motion_8_cliente_alle_18"),
         "9": (reel9, 14.6, "motion_9_per_chi_e"), "10": (reel10, 16.8, "motion_10_hai_bisogno_noi_ci_siamo"),
         "11": (reel11, 16.8, "motion_11_un_problema_una_soluzione"),
         "12": (reel12, _r12[1], "motion_12_per_chi_e_krea"), "13": (reel13, _r13[1], "motion_13_costi_fissi"),
         "14": (reel14, _r14[1], "motion_14_sede_domenica_sala"),
         "15": (reel15, 16.8, "motion_15_scrivania_quando_vuoi"), "16": (reel16, 15.4, "motion_16_sala_per_cosa")}

if __name__ == "__main__":
    fn, dur, name = REELS[sys.argv[1]]
    out = f"{ROOT}/out/reels/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("done", name)
