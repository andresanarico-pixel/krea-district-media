# Caroselli 1080x1350 (usa make_content_lib; ROOT in make_content_lib punta alla cartella di sessione)
import os
from make_content_lib import scene, WHITE, GOLD, OUT
CONTACT = ["Via Bruno Buozzi 6, Cassano Magnago (VA)", "+39 375 113 9192  ·  info@kreadistrict.it"]
CARS = {
 "car_5_motivi": [
  dict(kicker="COWORKING", headline=[("5 motivi per lasciare il tavolo in cucina.", WHITE)], sub="Scorri di lato", y0=560, hsize=78),
  dict(kicker="1 / 5", headline=[("A casa ti distrai.", WHITE)], sub="Una scrivania vera, in un luogo fatto per lavorare.", y0=560, hsize=84),
  dict(kicker="2 / 5", headline=[("Hai clienti da ricevere.", WHITE)], sub="Sala riunioni fino a 8 persone.", y0=560, hsize=84),
  dict(kicker="3 / 5", headline=[("Ti serve un indirizzo per la società.", WHITE)], sub="Sede legale a Cassano Magnago.", y0=560, hsize=78),
  dict(kicker="4 / 5", headline=[("Lavori fino a tardi.", WHITE)], sub="Accesso 24/7, in autonomia e su prenotazione.", y0=560, hsize=84),
  dict(kicker="5 / 5", headline=[("Non vuoi i costi fissi di un ufficio.", WHITE)], sub="Canone tutto incluso, nessun deposito cauzionale.", y0=560, hsize=78),
  dict(kicker="DAL 20 GENNAIO 2027", headline=[("Scrivici in DM.", GOLD)], sub="info@kreadistrict.it", footer=CONTACT, y0=600, hsize=96),
 ],
 "car_sala_8": [
  dict(kicker="SALA RIUNIONI", headline=[("Fino a 8 persone.", WHITE), ("A cosa serve?", GOLD)], sub="Scorri di lato", y0=560, hsize=84),
  dict(kicker="1 / 4", headline=[("Assemblee di condominio.", WHITE)], sub="Per gli amministratori che cercano un luogo adatto.", y0=560, hsize=82),
  dict(kicker="2 / 4", headline=[("Incontri con i clienti.", WHITE)], sub="Agenti immobiliari, consulenti, professionisti.", y0=560, hsize=84),
  dict(kicker="3 / 4", headline=[("Consulenze e colloqui.", WHITE)], sub="Un ambiente elegante, quando serve.", y0=560, hsize=84),
  dict(kicker="4 / 4", headline=[("Di giorno e di sera.", WHITE)], sub="Con accesso 24/7, su prenotazione.", y0=560, hsize=84),
  dict(kicker="DAL 20 GENNAIO 2027", headline=[("Scrivici in DM.", GOLD)], sub="info@kreadistrict.it", footer=CONTACT, y0=600, hsize=96),
 ],
}
for name, slides in CARS.items():
    os.makedirs(f"{OUT}/posts", exist_ok=True)
    for i, s in enumerate(slides, 1):
        scene(1080, 1350, 600, 50, **s).save(f"{OUT}/posts/{name}_{i}.png")
print("ok")
