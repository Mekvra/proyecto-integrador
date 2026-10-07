# Iconos del modelo VSM: tronco común, silos, pulmón, envasadoras por presentación, paletizado, cámara y despacho.
# Reutiliza las funciones de dibujar_iconos.py (BMP con fondo blanco = transparente en Plant Simulation).
import os
from PIL import ImageFont
from dibujar_iconos import COL, NAVY, canvas, save, s, tank, truck, store, machine, S

GRIS = COL['comun']


def fuente(px):
    for f in ('arialbd.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts', f), px * S)
        except OSError:
            pass
    return ImageFont.load_default()


def texto(d, cx, cy, t, px, color=NAVY):
    f = fuente(px)
    b = d.textbbox((0, 0), t, font=f)
    d.text((cx * S - (b[2] - b[0]) / 2, cy * S - (b[3] - b[1]) / 2 - b[1]), t, font=f, fill=color)


def cisterna(name, w=80, h=46):
    im, d = canvas(w, h)
    d.rounded_rectangle(s(2, 8, 54, 32), radius=11 * S, fill=(205, 212, 222), outline=NAVY, width=S * 2)
    d.rectangle(s(10, 16, 46, 22), fill=(255, 255, 255))
    texto(d, 28, 19, 'LECHE', 7)
    d.rounded_rectangle(s(56, 13, 78, 32), radius=3 * S, fill=(200, 30, 40), outline=NAVY, width=S * 2)
    d.rectangle(s(61, 16, 74, 22), fill=(200, 225, 245))
    for x in (12, 40, 67):
        d.ellipse(s(x - 6, 29, x + 6, 41), fill=NAVY)
    save(im, name, w, h)


def htst(name, w=72, h=56):
    im, d = canvas(w, h)
    d.rounded_rectangle(s(4, 6, w - 4, h - 8), radius=5 * S, fill=GRIS[1], outline=NAVY, width=S * 2)
    for i in range(9):
        x = 12 + i * 6
        d.rectangle(s(x, 12, x + 3, h - 16), fill=(120, 170, 220) if i % 2 else (230, 120, 90))
    d.rectangle(s(4, h - 12, w - 4, h - 8), fill=NAVY)
    save(im, name, w, h)


def bahia(name, w=72, h=50):
    im, d = canvas(w, h)
    d.polygon(s(2, 16, w / 2, 3, w - 2, 16), fill=(35, 100, 175), outline=NAVY)
    d.rectangle(s(8, 16, w - 8, h - 6), fill=GRIS[1], outline=NAVY, width=S * 2)
    d.rectangle(s(16, 24, w - 16, h - 6), fill=(70, 72, 78))
    d.line(s(w / 2, 24, w / 2, h - 6), fill=(245, 195, 30), width=S * 2)
    save(im, name, w, h)


def silo(name, c, rotulo, w=46, h=80):
    im, d = canvas(w, h)
    main, light = c
    d.rectangle(s(6, 12, w - 6, h - 18), fill=main, outline=NAVY, width=S * 2)
    d.ellipse(s(6, 4, w - 6, 18), fill=light, outline=NAVY, width=S * 2)
    d.polygon(s(6, h - 18, w - 6, h - 18, w / 2 + 5, h - 6, w / 2 - 5, h - 6), fill=main, outline=NAVY)
    for x in (9, w - 9):
        d.line(s(x, h - 18, x, h - 1), fill=NAVY, width=S * 2)
    d.rectangle(s(10, 26, w - 10, 40), fill=(255, 255, 255))
    texto(d, w / 2, 33, rotulo, 9)
    save(im, name, w, h)


def llenadora(name, c, rotulo, envase, w=88, h=66):
    im, d = canvas(w, h)
    main, light = c
    d.rounded_rectangle(s(3, 4, w - 3, h - 16), radius=6 * S, fill=light, outline=NAVY, width=S * 2)
    d.rectangle(s(3, h - 18, w - 3, h - 13), fill=NAVY)
    n = 4
    for i in range(n):
        x = 10 + i * (w - 20) / n
        if envase == 'vaso':
            d.polygon(s(x, 14, x + 12, 14, x + 10, 30, x + 2, 30), fill=main, outline=NAVY)
        elif envase == 'bloque':
            d.rounded_rectangle(s(x, 16, x + 13, 30), radius=2 * S, fill=main, outline=NAVY, width=S)
        elif envase == 'tarrina':
            d.ellipse(s(x, 16, x + 13, 30), fill=main, outline=NAVY, width=S)
        else:  # botella
            d.rounded_rectangle(s(x + 2, 14, x + 11, 31), radius=3 * S, fill=main, outline=NAVY, width=S)
            d.rectangle(s(x + 4, 10, x + 9, 14), fill=NAVY)
    d.rounded_rectangle(s(8, h - 15, w - 8, h - 1), radius=3 * S, fill=(255, 255, 255), outline=NAVY, width=S)
    texto(d, w / 2, h - 8, rotulo, 9)
    save(im, name, w, h)


def reparto(name, c, w=56, h=56):
    im, d = canvas(w, h)
    main, light = c
    d.ellipse(s(4, 4, w - 4, h - 4), fill=light, outline=NAVY, width=S * 2)
    d.line(s(12, h / 2, w / 2, h / 2), fill=NAVY, width=S * 3)
    for y in (14, h / 2, h - 14):
        d.line(s(w / 2, h / 2, w - 12, y), fill=main, width=S * 3)
        d.ellipse(s(w - 16, y - 4, w - 8, y + 4), fill=main, outline=NAVY, width=S)
    save(im, name, w, h)


def paletizado(name, w=80, h=64):
    im, d = canvas(w, h)
    d.rectangle(s(30, h - 14, w - 4, h - 8), fill=(160, 110, 60), outline=NAVY, width=S)
    for i, col in enumerate(((236, 112, 140), (232, 180, 40), (70, 140, 200))):
        d.rectangle(s(34 + i * 14, h - 28, 46 + i * 14, h - 14), fill=col, outline=NAVY, width=S)
    d.rectangle(s(6, h - 12, 22, h - 4), fill=(245, 170, 20), outline=NAVY, width=S)
    d.line(s(14, h - 12, 14, 20, 38, 10, 52, 22), fill=(245, 170, 20), width=S * 5)
    d.line(s(14, h - 12, 14, 20, 38, 10, 52, 22), fill=NAVY, width=S)
    d.rectangle(s(48, 20, 58, 28), fill=NAVY)
    save(im, name, w, h)


if __name__ == '__main__':
    Y, Q, K = COL['yogur'], COL['queso'], COL['kefir']
    cisterna('vsm_cisterna')
    bahia('vsm_recepcion')
    tank('vsm_crudo', GRIS, w=56, h=70)
    htst('vsm_htst')
    silo('vsm_silo1', Y, 'S1')
    silo('vsm_silo2', Q, 'S2')
    silo('vsm_silo3', K, 'S3')
    tank('vsm_pulmon', Y, w=52, h=66, agit=True)
    llenadora('vsm_u311', Y, '150 g', 'vaso')
    llenadora('vsm_u312', Y, '1000 · 1750 g', 'botella')
    llenadora('vsm_u321', Q, '400 · 1000 g', 'bloque')
    llenadora('vsm_u322', Q, '250 g', 'tarrina')
    llenadora('vsm_u331', K, '240·500·1000 g', 'botella')
    reparto('vsm_reparto_y', Y)
    reparto('vsm_reparto_q', Q)
    paletizado('vsm_paletizado')
    store('vsm_camara', GRIS)
    truck('vsm_despacho_y', Y)
    truck('vsm_despacho_q', Q)
    truck('vsm_despacho_k', K)
    print('ok')
