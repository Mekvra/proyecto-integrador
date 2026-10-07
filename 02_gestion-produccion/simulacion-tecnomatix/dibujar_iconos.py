# Iconos a color para el modelo de Plant Simulation (BMP con fondo blanco = transparente).
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iconos')
os.makedirs(OUT, exist_ok=True)
NAVY = (27, 42, 120)
COL = {
    'yogur': ((236, 112, 140), (252, 214, 223)),     # fresa
    'kefir': ((70, 140, 200), (210, 230, 247)),      # azul
    'queso': ((232, 180, 40), (252, 238, 190)),      # amarillo
    'comun': ((120, 130, 150), (225, 229, 237)),     # gris acero
}
S = 4  # sobremuestreo para bordes suaves


def canvas(w, h):
    im = Image.new('RGB', (w * S, h * S), (255, 255, 255))
    return im, ImageDraw.Draw(im)


def save(im, name, w, h):
    im = im.resize((w, h), Image.LANCZOS)
    # quitar blancos casi puros del antialias para que el fondo quede limpio
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 248 and g > 248 and b > 248:
                px[x, y] = (255, 255, 255)
    im.save(os.path.join(OUT, name + '.bmp'))


def s(*v):
    return [int(a * S) for a in v]


def tank(name, c, w=56, h=72, cone=False, agit=False, label=None):
    im, d = canvas(w, h)
    main, light = c
    top, bot = 8, h - (16 if cone else 8)
    d.rectangle(s(6, top + 4, w - 6, bot), fill=main, outline=NAVY, width=S * 2)
    d.ellipse(s(6, top - 2, w - 6, top + 10), fill=light, outline=NAVY, width=S * 2)
    if cone:
        d.polygon(s(6, bot, w - 6, bot, w / 2 + 6, h - 3, w / 2 - 6, h - 3), fill=main, outline=NAVY)
        d.line(s(6, bot, w / 2 - 6, h - 3), fill=NAVY, width=S * 2)
        d.line(s(w - 6, bot, w / 2 + 6, h - 3), fill=NAVY, width=S * 2)
    else:
        d.ellipse(s(6, bot - 6, w - 6, bot + 6), fill=main, outline=NAVY, width=S * 2)
        d.rectangle(s(8, bot - 6, w - 8, bot - 1), fill=main)
    d.rectangle(s(12, top + 12, 18, bot - 8), fill=light)   # brillo
    if agit:
        d.line(s(w / 2, 0, w / 2, bot - 10), fill=NAVY, width=S * 2)
        d.line(s(w / 2 - 10, bot - 10, w / 2 + 10, bot - 10), fill=NAVY, width=S * 3)
        d.ellipse(s(w / 2 - 5, 0, w / 2 + 5, 8), fill=(255, 210, 60), outline=NAVY, width=S)
    save(im, name, w, h)


def filler(name, c, w=72, h=60):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(4, 6, w - 4, h - 14), radius=6 * S, fill=light, outline=NAVY, width=S * 2)
    d.rectangle(s(4, h - 16, w - 4, h - 10), fill=NAVY)
    for i in range(4):
        x = 12 + i * 14
        d.rounded_rectangle(s(x, 22, x + 9, 42), radius=2 * S, fill=main, outline=NAVY, width=S)
        d.rectangle(s(x + 2, 18, x + 7, 22), fill=NAVY)
    d.rectangle(s(10, 8, w - 10, 14), fill=main)
    d.ellipse(s(w / 2 - 6, h - 12, w / 2 + 6, h), fill=(255, 255, 255), outline=NAVY, width=S)
    save(im, name, w, h)


def belt(name, c, w=96, h=36):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(3, 10, w - 3, h - 6), radius=10 * S, fill=light, outline=NAVY, width=S * 2)
    for x in (14, w - 14):
        d.ellipse(s(x - 7, h / 2 - 5, x + 7, h / 2 + 9), outline=NAVY, width=S * 2)
    for i in range(4):
        x = 26 + i * 12
        d.rounded_rectangle(s(x, 3, x + 9, 13), radius=2 * S, fill=main, outline=NAVY, width=S)
    save(im, name, w, h)


def vat(name, c, w=96, h=52):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(4, 14, w - 4, h - 4), radius=16 * S, fill=main, outline=NAVY, width=S * 2)
    d.rounded_rectangle(s(12, 18, w - 12, 26), radius=4 * S, fill=light)
    d.line(s(w / 2, 0, w / 2, 34), fill=NAVY, width=S * 2)
    for x in (w / 2 - 18, w / 2 + 18):
        d.line(s(x, 24, x, 40), fill=NAVY, width=S * 2)
    d.line(s(w / 2 - 18, 24, w / 2 + 18, 24), fill=NAVY, width=S * 2)
    d.ellipse(s(w / 2 - 5, 0, w / 2 + 5, 8), fill=(255, 210, 60), outline=NAVY, width=S)
    save(im, name, w, h)


def screw(name, c, w=80, h=44):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(4, 6, w - 4, h - 6), radius=8 * S, fill=light, outline=NAVY, width=S * 2)
    pts = []
    for i in range(9):
        pts += [8 + i * (w - 16) / 8, (12 if i % 2 == 0 else h - 12)]
    d.line(s(*pts), fill=main, width=S * 4)
    d.line(s(*pts), fill=NAVY, width=S)
    save(im, name, w, h)


def bath(name, c, w=60, h=44):
    im, d = canvas(w, h)
    main, light = c
    d.rectangle(s(4, 10, w - 4, h - 4), fill=(170, 210, 240), outline=NAVY, width=S * 2)
    for i in range(3):
        x = 10 + i * 15
        d.ellipse(s(x, 18, x + 12, 30), fill=main, outline=NAVY, width=S)
    d.line(s(4, 14, w - 4, 14), fill=(255, 255, 255), width=S * 2)
    save(im, name, w, h)


def machine(name, c, w=64, h=56, glyph='H'):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(4, 8, w - 4, h - 8), radius=6 * S, fill=light, outline=NAVY, width=S * 2)
    d.rectangle(s(4, h - 12, w - 4, h - 8), fill=NAVY)
    d.rounded_rectangle(s(12, 16, w - 12, h - 18), radius=4 * S, fill=main, outline=NAVY, width=S)
    if glyph == 'H':
        for i in range(4):
            x = 16 + i * 8
            d.line(s(x, 20, x, h - 22), fill=(255, 255, 255), width=S * 2)
    else:
        d.ellipse(s(w / 2 - 9, 19, w / 2 + 9, 37), outline=(255, 255, 255), width=S * 3)
    save(im, name, w, h)


def truck(name, c, w=72, h=44):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(2, 8, 48, 32), radius=10 * S, fill=main, outline=NAVY, width=S * 2)
    d.rounded_rectangle(s(50, 14, 70, 32), radius=3 * S, fill=light, outline=NAVY, width=S * 2)
    d.rectangle(s(55, 17, 66, 23), fill=(200, 225, 245))
    for x in (12, 36, 60):
        d.ellipse(s(x - 6, 28, x + 6, 40), fill=NAVY)
    save(im, name, w, h)


def store(name, c, w=64, h=60):
    im, d = canvas(w, h)
    main, light = c
    d.polygon(s(2, 22, w / 2, 4, w - 2, 22), fill=main, outline=NAVY)
    d.rectangle(s(8, 22, w - 8, h - 4), fill=light, outline=NAVY, width=S * 2)
    d.rectangle(s(22, 32, w - 22, h - 4), fill=(180, 215, 240), outline=NAVY, width=S)
    for y in (38, 46):
        d.line(s(24, y, w - 24, y), fill=NAVY, width=S)
    save(im, name, w, h)


def queue(name, c, w=56, h=36):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(2, 4, w - 2, h - 4), radius=6 * S, fill=light, outline=NAVY, width=S * 2)
    for i in range(3):
        x = 8 + i * 15
        d.rectangle(s(x, 12, x + 10, 24), fill=main, outline=NAVY, width=S)
    save(im, name, w, h)


if __name__ == '__main__':
    for ln in ('yogur', 'kefir', 'queso'):
        c = COL[ln]
        truck(f'pedidos_{ln}', c)
        queue(f'cola_{ln}', c)
        store(f'camara_{ln}', c)
        filler(f'llenadora_{ln}', c)
    tank('formulacion', COL['yogur'], agit=True)
    machine('u202', COL['comun'], glyph='H')
    tank('fermentador_yogur', COL['yogur'], cone=True, agit=True)
    tank('fermentador_kefir', COL['kefir'], cone=True, agit=True)
    tank('tanque_kefir', COL['kefir'], w=48, h=60)
    queue('pulmones', COL['yogur'])
    vat('tina', COL['queso'])
    belt('banda', COL['queso'])
    screw('hiladora', COL['queso'])
    bath('salmuera', COL['queso'])
    print(sorted(os.listdir(OUT)))
