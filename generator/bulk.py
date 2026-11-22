import sys, subprocess
sys.argv=[sys.argv[0]]
import reels3 as R
from reels3 import *
from motion import ROOT, W, H, FPS
import reels3

SETS = {
 "12": ("agenti_immobiliari", [(["Visite fuori", "orario?"], "Aperto 24/7."), (["Clienti da", "ricevere?"], "Sala da 8."), (["Un indirizzo", "professionale?"], "Cassano Magnago."), (["Costi fissi", "da gestire?"], "Un solo canone.")], ["Per agenti", "immobiliari."]),
 "13": ("notai_commercialisti", [(["Incontri con", "i clienti?"], "Sala da 8."), (["Lavori fuori", "orario?"], "Aperto 24/7."), (["Serve una", "sede legale?"], "Ce l'abbiamo."), (["Spazio", "professionale?"], "Tutto incluso.")], ["Per notai e", "commercialisti."]),
 "14": ("freelance", [(["A casa ti", "distrai?"], "Scrivania vera."), (["Lavori da", "solo?"], "Community."), (["Serve una", "sala riunioni?"], "Da 8 persone."), (["Orari rigidi?", ""], "Aperto 24/7.")], ["Per freelance e", "professionisti."]),
 "15": ("amministratori_condominio", [(["Assemblee da", "organizzare?"], "Sala da 8."), (["Un indirizzo", "per lo studio?"], "Sede legale."), (["Incontri con", "i condomini?"], "Sala riunioni."), (["Studio da", "gestire?"], "Tutto incluso.")], ["Per amministratori", "di condominio."]),
 "16": ("tra_milano_malpensa", [(["Cerchi un ufficio", "in zona?"], "Cassano Magnago."), (["Vicino a", "Malpensa?"], "Ci siamo."), (["Tra Milano", "e Varese?"], "Ci siamo."), (["Parcheggio e", "comodità?"], "Via Buozzi 6.")], ["Il coworking", "tra Milano e Malpensa."]),
 "17": ("sala_riunioni_ore", [(["Una riunione", "importante?"], "Sala da 8."), (["Cliente in", "arrivo?"], "Sala da 8."), (["Presentazione", "al team?"], "Sala da 8."), (["Solo per", "qualche ora?"], "Si prenota.")], ["La sala riunioni", "di KREA District."]),
 "18": ("sede_legale_soluzione", [(["Hai una", "società?"], "Sede legale."), (["Non serve un", "ufficio intero?"], "Solo l'indirizzo."), (["Vuoi una sede", "in Lombardia?"], "Cassano Magnago."), (["Vuoi anche", "uno spazio?"], "Postazione.")], ["La sede legale", "a Cassano Magnago."]),
 "19": ("costi_ufficio", [(["Affitto da", "pagare?"], "Un solo canone."), (["Utenze da", "gestire?"], "Tutto incluso."), (["Arredi da", "comprare?"], "Già pronto."), (["Internet da", "attivare?"], "Già pronto.")], ["Un ufficio senza", "pensieri."]),
 "20": ("lavoro_da_casa", [(["Divano e", "distrazioni?"], "Scrivania vera."), (["Videocall con", "il cane?"], "Sala riunioni."), (["Silenzio per", "concentrarti?"], "Spazio tuo."), (["Orari sempre", "uguali?"], "Aperto 24/7.")], ["Esci di casa,", "entra in KREA."]),
 "21": ("lavoro_di_sera", [(["Lavori fino", "a tardi?"], "Aperto 24/7."), (["Sveglia", "presto?"], "Aperto 24/7."), (["Weekend di", "lavoro?"], "Aperto 24/7."), (["Orari tuoi?", ""], "Su prenotazione.")], ["Il tuo ufficio,", "quando vuoi."]),
 "22": ("networking", [(["Lavori in", "solitudine?"], "Community."), (["Cerchi nuovi", "contatti?"], "Network."), (["Vuoi confrontarti", "con altri?"], "Community."), (["Un posto", "dove crescere?"], "KREA District.")], ["Coworking, network,", "community."]),
 "23": ("nuovo_anno", [(["Nuovo anno?", ""], "Nuovo ufficio."), (["Nuovi obiettivi?", ""], "Nuovo spazio."), (["Nuovi clienti?", ""], "Nuova sala."), (["Nuovo inizio?", ""], "20 gennaio.")], ["Il 20 gennaio", "apre KREA District."]),
}

def make(key):
    name, beats, closing = SETS[key]
    def fn(t):
        c = D()
        if t < 10.8:
            i = min(int(t // 2.7), 3); tt = t - i * 2.7
            q, ans = beats[i]
            c.text(q[0], 540, 640, 92 * pop(tt, 0), WHITE)
            if q[1]: c.text(q[1], 540, 760, 92 * pop(tt, 0.1), WHITE)
            a = prog(tt, 1.1, 1.6)
            if a > 0:
                y = 1080 + 80 * (1 - eo(a))
                c.circle(540, 960, 52 * eb(a), GOLD)
                check(c, 540, 962, 46 * eb(a), BG, 10)
                c.text(ans, 540, y + 60, 96 * pop(tt, 1.1), mix(GOLD, eo(a)))
            for k in range(1, 4): c.wipe(t, k * 2.7)
            c.wipe(t, 10.8)
        elif t < 13.2:
            tt = t - 10.8
            c.text(closing[0], 540, 780, 88 * pop(tt, 0), WHITE)
            c.text(closing[1], 540, 910, 88 * pop(tt, 0.3), GOLD if tt > 0.3 else BG)
            c.wipe(t, 10.8); c.wipe(t, 13.2)
        else:
            cta_dm(c, t, 13.2); c.wipe(t, 13.2)
        return c.finish()
    out = f"{ROOT}/out/reels/motion_{key}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",out], stdin=subprocess.PIPE)
    for i in range(int(16.8 * FPS)): p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("done", out)

if __name__ == "__main__":
    import os
    make(os.environ["K"])
