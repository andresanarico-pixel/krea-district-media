from PIL import Image, ImageDraw, ImageFont
BG=(32,30,31); GOLD=(216,181,86); W=(255,255,255); G=(170,170,170)
FB="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"; FM="/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
lg=Image.open('assets/logo.jpg').convert('RGB'); lg=lg.crop((12,12,lg.width-12,lg.height-12))
lg=lg.resize((560,int(lg.height*560/lg.width)),Image.LANCZOS)
POSTS=[
("SALA RIUNIONI","Una sala da 8 persone.","Per riunioni, presentazioni e incontri con i clienti. Si prenota a ore."),
("SEDE LEGALE","La sede legale della tua società.","A Cassano Magnago, tra Milano e Malpensa."),
("ACCESSO 24/7","Il tuo spazio, sempre aperto.","Accesso autonomo, 24 ore su 24, su prenotazione."),
("PER CHI È","Per professionisti e piccole realtà.","Amministratori di condominio, agenti immobiliari, notai, commercialisti, freelance."),
("TUTTO INCLUSO","Un solo canone.","Meno pensieri, più tempo per il tuo lavoro."),
("LAVORI DA CASA?","Esci di casa, entra in KREA.","Una scrivania vera, in uno spazio pensato per concentrarti."),
("COMMUNITY","Non lavori più da solo.","Coworking, network e community a Cassano Magnago."),
("A CASSANO MAGNAGO","Un ufficio vicino a te.","Via Bruno Buozzi 6, tra Milano e Malpensa."),
("POSTAZIONI","Una scrivania ti basta?","Postazioni open space per lavorare quando vuoi."),
("PER AGENTI IMMOBILIARI","Ricevi i clienti con stile.","Sala riunioni da 8 persone e un indirizzo professionale."),
("PER NOTAI E COMMERCIALISTI","Spazi per incontri riservati.","Sala riunioni e accesso 24/7 su prenotazione."),
("COUNTDOWN","Mancano poche settimane.","KREA District apre il 20 gennaio 2027."),
("SCRIVICI","Vuoi sapere di più?","Scrivici in DM o a info@kreadistrict.it. +39 375 113 9192"),
("IL 20 GENNAIO","Si apre.","KREA District, coworking a Cassano Magnago. Ti aspettiamo."),
]
def wrap(d,t,f,mw):
    ws=t.split(); ln=[]; cur=""
    for w in ws:
        x=(cur+" "+w).strip()
        if d.textlength(x,font=f)<=mw: cur=x
        else: ln.append(cur); cur=w
    ln.append(cur); return ln
for i,(k,h,b) in enumerate(POSTS,3):
    im=Image.new('RGB',(1080,1350),BG); d=ImageDraw.Draw(im)
    im.paste(lg,(260,120))
    d.text((90,620),k,font=ImageFont.truetype(FM,44),fill=GOLD)
    y=700
    for l in wrap(d,h,ImageFont.truetype(FB,84),900): d.text((90,y),l,font=ImageFont.truetype(FB,84),fill=W); y+=100
    y+=30
    for l in wrap(d,b,ImageFont.truetype(FM,44),900): d.text((90,y),l,font=ImageFont.truetype(FM,44),fill=W); y+=60
    d.text((90,1240),"Via Bruno Buozzi 6, Cassano Magnago (VA)",font=ImageFont.truetype(FM,36),fill=G)
    im.save(f'out/posts/post_{i}.png')
print(len(POSTS))
