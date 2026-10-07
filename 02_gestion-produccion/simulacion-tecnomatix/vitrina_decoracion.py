# Decoración 3D con primitivas pegada a objetos del modelo (coordenadas locales del objeto, en metros):
# punto de acopio (recepción de leche) y muelle de despacho. Uso: python vitrina_decoracion.py <zona> <salida>
import sys
from vitrina_vehiculos import Pieza, rgb, NEGRO, GRIS, ACERO, BLANCO, VIDRIO

AZUL, AZUL_OSC, AMARILLO, ASFALTO = (35, 100, 175), (25, 60, 120), (245, 195, 30), (62, 64, 70)

class Deco(Pieza):
    def __init__(self, obj, ocultar=300, dz=1.0):
        # dz: la estación se baja 1 m para que el camión quede a ras de piso; la decoración se sube lo mismo
        super().__init__(obj)
        self.ocultar, self.dz = ocultar, dz

    def codigo(self):
        cab = [f'var c: object := .Models.Model.{self.cls}', 'var g: any := c._3D.getGraphic("default")', 'var x: any']
        if self.ocultar:  # encoge la figura original del objeto
            cab += [f'for var i := 1 to {self.ocultar}', '\tx := c._3D.getGraphic("default", [i])',
                    '\tif x /= void', '\t\tx.Scale := [0.001, 0.001, 0.001]', '\tend', 'next']
        return '\n'.join(cab + self.L)

def techo(d, cx, cy, largo, ancho, alto, cols_x):
    for x in cols_x:
        for s in (-1, 1):
            d.caja((0.35, 0.35, alto), (x, cy + s * (ancho / 2 - 0.3), 0), AZUL_OSC)
    for s in (-1, 1):   # marco azul del techo (solo el borde, para que el techo translúcido deje ver)
        d.caja((largo + 0.2, 0.3, 0.45), (cx, cy + s * (ancho / 2 - 0.05), alto - 0.05), AZUL, 0.5)
        d.caja((0.3, ancho + 0.2, 0.45), (cx + s * (largo / 2 - 0.05), cy, alto - 0.05), AZUL, 0.5)
    d.caja((largo, ancho, 0.12), (cx, cy, alto + 0.4), (240, 243, 247), 0.3, transp=0.55)   # techo translúcido: deja ver el camión

def acopio():
    d = Deco('Recepcion_de_leche')
    cx, cy = 0.5, -0.5
    d.caja((32.0, 5.0, 0.04), (cx + 2.5, cy, 0), ASFALTO)                    # vía de camiones
    for i in range(14):                                                    # línea central discontinua
        d.caja((1.2, 0.15, 0.05), (cx - 13 + i * 2.3, cy, 0), BLANCO)
    d.caja((16.0, 7.0, 0.06), (cx, cy, 0), (120, 125, 135))                 # losa de descarga
    for s in (-1, 1):
        d.caja((16.0, 0.22, 0.07), (cx, cy + s * 3.4, 0), AMARILLO)         # demarcación
    techo(d, cx, cy, 16.5, 8.2, 5.6, (cx - 7.0, cx, cx + 7.0))
    d.caja((6.0, 0.25, 1.3), (cx, cy + 4.0, 5.6), BLANCO)                    # aviso
    d.caja((6.1, 0.2, 0.3), (cx, cy + 4.05, 5.6), AZUL)
    # bomba de descarga, filtro y manguera al camión
    d.caja((2.6, 1.4, 0.25), (cx + 0.6, cy - 5.0, 0), GRIS)
    d.cilindro(0.4, 0.9, (cx, cy - 5.0, 0.25), 'z', AZUL, brillo=0.7)
    d.cilindro(0.3, 1.3, (cx + 1.3, cy - 5.0, 0.25), 'z', ACERO, brillo=0.9)
    d.cilindro(0.09, 3.6, (cx, cy - 2.9, 0.9), 'y', NEGRO)                  # manguera
    # tubería de acero hacia los tanques de leche cruda (6,-15) y (11,-15) del mundo; recepción en (19,-3)
    d.cilindro(0.11, 1.4, (cx + 1.3, cy - 5.0, 1.55), 'z', ACERO)
    d.cilindro(0.11, 4.0, (cx + 1.3, cy - 7.0, 2.9), 'y', ACERO)
    d.cilindro(0.11, 14.0, (cx - 5.7, cy - 9.0, 2.9), 'x', ACERO)
    for tx in (-12.5, -7.5):
        d.cilindro(0.11, 2.0, (tx, cy - 10.0, 2.9), 'y', ACERO)
    # caseta de laboratorio (análisis de la leche al recibir)
    d.caja((3.4, 2.6, 2.7), (cx + 10.0, cy - 6.5, 0), BLANCO, 0.3)
    d.caja((3.8, 3.0, 0.25), (cx + 10.0, cy - 6.5, 2.7), AZUL)
    d.caja((1.4, 0.05, 0.9), (cx + 9.4, cy - 5.18, 1.2), VIDRIO, 0.9)
    d.caja((0.9, 0.05, 2.0), (cx + 11.0, cy - 5.18, 0), AZUL_OSC)
    for x in (cx - 9.5, cx + 9.5):                                         # bolardos
        for s in (-1, 1):
            d.cilindro(0.15, 1.0, (x, cy + s * 2.9, 0), 'z', AMARILLO)
    return d.codigo()

def muelle():
    d = Deco('Muelle_de_despacho')
    cx, cy = 0.5, -0.5
    d.caja((22.0, 5.0, 0.04), (cx + 1.5, cy, 0), ASFALTO)
    for i in range(9):
        d.caja((1.2, 0.15, 0.05), (cx - 9 + i * 2.3, cy, 0), BLANCO)
    d.caja((12.0, 3.5, 1.2), (cx, cy + 4.3, 0), (150, 155, 165))            # andén de carga
    d.caja((12.0, 0.25, 0.08), (cx, cy + 2.55, 1.2), AMARILLO)
    techo(d, cx, cy + 2.0, 12.5, 10.0, 6.0, (cx - 5.5, cx + 5.5))
    for i, col in enumerate(((236, 112, 140), (70, 140, 200), (232, 180, 40))):  # estibas de yogur, kéfir y queso
        d.caja((1.2, 1.0, 0.15), (cx - 3.5 + i * 3.5, cy + 4.5, 1.2), (160, 110, 60))
        d.caja((1.1, 0.9, 1.0), (cx - 3.5 + i * 3.5, cy + 4.5, 1.35), col, 0.4)
    for x in (cx - 7.5, cx + 7.5):
        for s in (-1, 1):
            d.cilindro(0.15, 1.0, (x, cy + s * 2.9 - 0.5, 0), 'z', AMARILLO)
    return d.codigo()

GEN = {'acopio': acopio, 'muelle': muelle}

if __name__ == '__main__':
    open(sys.argv[2], 'w', encoding='utf-8').write('simtalk\n' + GEN[sys.argv[1]]() + '\n')
