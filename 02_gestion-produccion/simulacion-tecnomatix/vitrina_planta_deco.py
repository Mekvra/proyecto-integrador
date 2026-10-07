# Decoración general de la planta (nave, pisos por línea, pasillos, bodega con estanterías, cámaras frías, árboles)
# pegada al drenaje Salida_cisternas. Las medidas se dan en coordenadas 3D del mundo (m) y se pasan a locales.
# Uso: python vitrina_planta_deco.py <salida>
import sys
from vitrina_decoracion import Deco, AZUL, AZUL_OSC, AMARILLO, ASFALTO
from vitrina_vehiculos import BLANCO, VIDRIO, GRIS, NEGRO

HOST, HX, HY = 'Salida_cisternas', 37.0, -3.0
ROSA, CELESTE, CREMA = (238, 160, 190), (150, 195, 240), (245, 215, 120)
VERDE, MURO, PASTO = (70, 160, 90), (196, 204, 216), (90, 150, 70)

class Mundo(Deco):
    def __init__(self):
        super().__init__(HOST, ocultar=400, dz=0.0)

    def caja_w(self, x0, y0, x1, y1, z0, alto, color, brillo=None):
        """Caja entre las esquinas (x0, y0)-(x1, y1) del mundo, desde z0 con la altura dada."""
        cx, cy = (x0 + x1) / 2 - HX, (y0 + y1) / 2 - HY
        self.caja((round(abs(x1 - x0), 3), round(abs(y1 - y0), 3), alto), (round(cx, 3), round(cy, 3), z0), color, brillo)

    def cil_w(self, x, y, r, alto, z0, color, r2=None):
        self.cilindro(r, alto, (round(x - HX, 3), round(y - HY, 3), z0), 'z', color, r2=r2)

def muros(d, x0, y0, x1, y1, alto, color, banda, huecos=()):
    """Muros perimetrales con franja superior; huecos = [(lado, desde, hasta)] para puertas."""
    t = 0.3
    lados = {'n': (x0, y0, x1, y0), 's': (x0, y1, x1, y1), 'o': (x0, y0, x0, y1), 'e': (x1, y0, x1, y1)}
    for lado, (ax, ay, bx, by) in lados.items():
        tramos = [(0.0, 1.0)]
        for l, a, b in huecos:
            if l == lado:
                nuevos = []
                for p, q in tramos:
                    nuevos += [(p, min(q, a)), (max(p, b), q)]
                tramos = [(p, q) for p, q in nuevos if q - p > 0.01]
        for p, q in tramos:
            if ay == by:   # horizontal
                xa, xb = ax + (bx - ax) * p, ax + (bx - ax) * q
                d.caja_w(xa, ay - t / 2, xb, ay + t / 2, 0, alto, color, 0.2)
                d.caja_w(xa, ay - t / 2 - 0.02, xb, ay + t / 2 + 0.02, alto - 0.6, 0.6, banda, 0.4)
            else:
                ya, yb = ay + (by - ay) * p, ay + (by - ay) * q
                d.caja_w(ax - t / 2, ya, ax + t / 2, yb, 0, alto, color, 0.2)
                d.caja_w(ax - t / 2 - 0.02, ya, ax + t / 2 + 0.02, yb, alto - 0.6, 0.6, banda, 0.4)

def estanteria(d, x, y, colores):
    """Rack de 3 niveles (3,6 m x 1,2 m) con estibas de colores."""
    for dx in (0, 3.5):
        for dy in (0, 1.1):
            d.caja_w(x + dx, y + dy, x + dx + 0.1, y + dy + 0.1, 0, 4.2, (240, 120, 30))
    for k, z in enumerate((0.15, 1.5, 2.85)):
        d.caja_w(x, y, x + 3.6, y + 1.2, z, 0.08, (40, 70, 140))
        for j in range(2):
            c = colores[(k + j) % len(colores)]
            d.caja_w(x + 0.25 + j * 1.7, y + 0.15, x + 1.45 + j * 1.7, y + 1.05, z + 0.08, 0.12, (160, 110, 60))
            d.caja_w(x + 0.3 + j * 1.7, y + 0.2, x + 1.4 + j * 1.7, y + 1.0, z + 0.2, 0.9, c, 0.4)

def arbol(d, x, y, h=6.0):
    d.cil_w(x, y, 0.25, h * 0.35, 0, (110, 75, 45))
    d.cil_w(x, y, 1.8, h * 0.45, h * 0.3, (50, 130, 60), r2=0.9)
    d.cil_w(x, y, 1.3, h * 0.35, h * 0.6, (60, 150, 70), r2=0.1)

def planta():
    d = Mundo()
    # pasto alrededor y andenes de concreto bajo la nave y la bodega
    d.caja_w(-12.0, 8.0, 136.0, -92.0, 0, 0.01, PASTO)
    d.caja_w(15.5, -5.0, 77.0, -74.0, 0, 0.02, (200, 202, 206))
    d.caja_w(75.0, -6.0, 125.0, -24.0, 0, 0.02, (200, 202, 206))
    d.caja_w(0.0, 1.0, 40.0, -33.0, 0, 0.02, (200, 202, 206))
    # pisos por línea dentro de la nave y pasillos peatonales verdes
    d.caja_w(18.5, -7.5, 74.0, -23.0, 0, 0.03, ROSA)
    d.caja_w(18.5, -25.0, 74.0, -48.0, 0, 0.03, CELESTE)
    d.caja_w(18.5, -50.0, 74.0, -71.5, 0, 0.03, CREMA)
    for y in (-24.0, -49.0):
        d.caja_w(18.5, y - 0.6, 74.0, y + 0.6, 0, 0.04, VERDE)
    d.caja_w(18.5, -7.5, 19.7, -71.5, 0, 0.04, VERDE)
    # nave de producción (muros a media altura para ver adentro)
    muros(d, 17.5, -6.5, 75.0, -72.5, 3.2, MURO, AZUL, huecos=[('n', 0.62, 0.70), ('s', 0.10, 0.18), ('e', 0.02, 0.24), ('e', 0.25, 0.55), ('e', 0.86, 0.98)])
    # zona de silos y tanques de leche cruda
    d.caja_w(2.0, -11.0, 17.0, -31.0, 0, 0.03, (215, 220, 228))
    for x0, x1 in ((2.0, 17.0),):
        d.caja_w(x0, -11.2, x1, -10.8, 0, 0.9, AMARILLO)
    # bodega de producto terminado: piso, muros, estanterías a ambos lados del pasillo del montacargas
    d.caja_w(77.0, -8.0, 123.0, -22.0, 0, 0.03, (225, 232, 240))
    d.caja_w(78.0, -14.3, 122.0, -15.7, 0, 0.04, AMARILLO)
    muros(d, 76.5, -7.5, 123.5, -22.5, 4.5, (235, 240, 246), AZUL_OSC, huecos=[('o', 0.3, 0.7)])
    cols = [(236, 112, 140), (70, 140, 200), (232, 180, 40), (250, 250, 250)]
    for i in range(10):
        x = 80.0 + i * 4.2
        estanteria(d, x, -10.2, cols[i % 4:] + cols[:i % 4])
        estanteria(d, x, -21.0, cols[(i + 2) % 4:] + cols[:(i + 2) % 4])
    # cámaras frías junto a cada línea (en los drenajes Camara_*)
    for y, c in ((-16.5, (236, 112, 140)), (-34.0, (70, 140, 200)), (-62.0, (232, 180, 40))):
        d.caja_w(68.5, y - 2.6, 74.0, y + 2.6, 0, 3.6, (245, 248, 252), 0.6)
        d.caja_w(68.4, y - 2.7, 74.1, y + 2.7, 3.6, 0.35, c, 0.5)
        d.caja_w(68.3, y - 1.0, 68.45, y + 1.0, 0, 2.6, (120, 170, 220), 0.8)
    # vía y patio de despacho
    d.caja_w(73.0, -71.5, 110.0, -76.5, 0, 0.03, ASFALTO)
    # árboles alrededor de la planta
    for x in range(-6, 130, 12):
        arbol(d, x, -86.0, 6.5)
    for y in range(-10, -84, -12):
        arbol(d, -6.0, y, 6.0)
        arbol(d, 130.0, y, 6.0)
    for x in range(48, 130, 14):
        arbol(d, x, 4.0, 5.5)
    return d.codigo()

if __name__ == '__main__':
    open(sys.argv[1], 'w', encoding='utf-8').write('simtalk\n' + planta() + '\n')
