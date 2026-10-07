# Estructura tipo VSM para la vitrina 3D (planta_lactea_3d.spp): carteles 3D por zona y por proceso, envasadoras
# con sus presentaciones a la vista y celda de paletizado U341. Todo va en el grupo gráfico "Deco" del Frame,
# así que no cuenta para el límite de 80 objetos. Coordenadas: 3D (m) = 2D (px) / 20, con el eje y invertido.
import math

Y, Q, K, G = (236, 112, 140), (232, 180, 40), (70, 140, 200), (120, 130, 150)
ACERO, BLANCO, OSCURO = (205, 210, 218), (246, 247, 249), (25, 30, 45)
NAVY = (35, 60, 120)


def rgb(c):
    return f'makeRGBValue({c[0]}, {c[1]}, {c[2]})'


class Deco:
    def __init__(self):
        self.L = []

    def _mat(self, c, brillo=None, transp=None):
        self.L += ['x.MaterialActive := true', f'x.MaterialDiffuseColor := {rgb(c)}']
        if brillo is not None:
            self.L.append(f'x.MaterialShininess := {brillo}')
        if transp is not None:
            self.L.append(f'x.MaterialTransparency := {transp}')

    def caja(self, cx, cy, z, l, w, h, c, brillo=None, transp=None):
        self.L += [f'x := g.createCuboid([{round(l, 3)}, {round(w, 3)}, {round(h, 3)}])', f'x.Position := [{round(cx, 3)}, {round(cy, 3)}, {round(z, 3)}]']
        self._mat(c, brillo, transp)

    def cil(self, cx, cy, z, r, h, c, r2=None, eje='z', brillo=None):
        self.L.append(f'x := g.createConeFrustum({r}, {r if r2 is None else r2}, {round(h, 3)})')
        if eje == 'x':
            self.L.append('x.Rotation := [90.0, 0.0, 1.0, 0.0]'); cx -= h / 2
        elif eje == 'y':
            self.L.append('x.Rotation := [90.0, 1.0, 0.0, 0.0]'); cy += h / 2
        self.L.append(f'x.Position := [{round(cx, 3)}, {round(cy, 3)}, {round(z, 3)}]')
        self._mat(c, brillo)

    def texto(self, x0, y0, z, s, esc, c):
        s = s.replace('"', "'")
        self.L += [f'x := g.createText("{s}")', 'x.Rotation := [90.0, 1.0, 0.0, 0.0]',
                   f'x.Scale := [{esc}, {esc}, {esc}]', f'x.Position := [{round(x0, 3)}, {round(y0, 3)}, {round(z, 3)}]']
        self._mat(c)

    def ordenes(self, n=400):
        cab = ['var m: object := .Models.Model', 'var g: any := m._3D.getGraphic("Deco")', 'var x: any']
        out, cur = [], []
        for ln in self.L:                       # se corta solo donde empieza una figura nueva
            if ln.startswith('x := ') and len(cur) >= n:
                out.append('\n'.join(cab + cur)); cur = []
            cur.append(ln)
        if cur:
            out.append('\n'.join(cab + cur))
        return out


d = Deco()


def W(x, y):
    return x / 20, -y / 20


def tablero(cx, cy, s, c_tablero, esc, alto, poste=(90, 95, 105), grueso=0.06):
    """Cartel de pie mirando al sur: postes, tablero del color de la línea y texto blanco centrado.
    El texto 3D se dibuja como un bloque blanco con las letras caladas, que dejan ver el tablero."""
    ancho = 0.62 * len(s) * esc + 0.8
    hb = 1.25 * esc + 0.5
    for sx in (-1, 1):
        d.cil(cx + sx * (ancho / 2 - 0.25), cy, 0, grueso, alto + hb, poste)
    d.caja(cx, cy, alto, ancho, 0.12, hb, c_tablero, 0.4)
    d.caja(cx, cy, alto + hb, ancho + 0.1, 0.16, 0.14, NAVY)
    s = s.replace('"', "'")
    t = round(esc * 3.4, 3)          # el texto 3D mide ~0,18 m por carácter a escala 1 y se ancla en su centro
    d.L += [f'x := g.createText("{s}")', 'x.Rotation := [90.0, 1.0, 0.0, 0.0]', f'x.Scale := [{t}, {t}, {t}]',
            f'x.Position := [{round(cx, 3)}, {round(cy - 0.08, 3)}, {round(alto + hb / 2, 3)}]']
    d._mat((255, 255, 255))


def cartel(cx, cy, s, c, esc=0.5, alto=2.2):
    tablero(cx, cy, s, c, esc, alto)


def gran_cartel(x0, y0, s, c, esc=1.6):
    ancho = 0.62 * len(s) * esc + 0.8
    tablero(x0 + ancho / 2, y0 - 0.6, s, c, esc, 3.6, poste=NAVY, grueso=0.18)


def productos(cx, cy, z, n, forma, c, tam=1.0, paso=0.42):
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * paso
        if forma == 'vaso':
            d.cil(x, cy, z, 0.09 * tam, 0.16 * tam, c, r2=0.12 * tam)
            d.cil(x, cy, z + 0.16 * tam, 0.125 * tam, 0.02, (230, 230, 235))
        elif forma == 'botella':
            d.cil(x, cy, z, 0.1 * tam, 0.32 * tam, BLANCO)
            d.cil(x, cy, z + 0.32 * tam, 0.1 * tam, 0.08 * tam, BLANCO, r2=0.04 * tam)
            d.cil(x, cy, z + 0.4 * tam, 0.045 * tam, 0.05, c)
        elif forma == 'bloque':
            d.caja(x, cy, z, 0.26 * tam, 0.16 * tam, 0.1 * tam, c, 0.8)
        elif forma == 'tarrina':
            d.cil(x, cy, z, 0.15, 0.12, BLANCO)
            d.cil(x, cy, z + 0.12, 0.155, 0.02, c)


def llenadora(x2, y2, c, forma, tams, titulo):
    cx, cy = W(x2, y2)
    d.caja(cx, cy, 0, 3.0, 1.5, 1.2, (232, 235, 240), 0.4)               # cuerpo
    d.caja(cx, cy, 1.2, 3.04, 1.54, 0.12, c)                               # franja del color de la línea
    d.caja(cx - 1.15, cy - 0.78, 0.8, 0.45, 0.05, 0.4, (40, 70, 110), 0.9)  # panel HMI
    d.caja(cx, cy, 1.32, 3.0, 0.5, 0.06, (60, 62, 70))                     # banda superior
    for i, t in enumerate(tams):                                            # una fila por presentación
        dy = (i - (len(tams) - 1) / 2) * 0.35
        productos(cx, cy + dy * 0.6, 1.38, 6, forma, c, t, paso=0.45)
    cartel(cx, cy + 1.5, titulo, c, esc=0.5, alto=2.5)


def paletizado(x2, y2):
    cx, cy = W(x2, y2)
    d.caja(cx - 2.6, cy, 0, 3.4, 1.0, 0.8, (60, 62, 70))                   # banda de cajas
    for i, c in enumerate((Y, K, Q)):
        d.caja(cx - 3.6 + i * 1.0, cy, 0.8, 0.5, 0.5, 0.35, c)
    d.caja(cx, cy, 0, 1.0, 1.0, 0.6, (245, 170, 20))                       # robot
    d.cil(cx, cy, 0.6, 0.28, 1.9, (245, 170, 20))
    d.cil(cx + 0.9, cy, 2.4, 0.16, 1.8, (245, 170, 20), eje='x')
    d.caja(cx + 1.8, cy, 1.6, 0.25, 0.25, 0.8, (60, 62, 70))
    d.caja(cx + 2.3, cy, 0, 1.2, 1.0, 0.14, (160, 110, 60))               # estiba
    for k in range(2):
        for i, c in enumerate((Y, K, Q)):
            d.caja(cx + 1.95 + i * 0.36, cy, 0.14 + k * 0.42, 0.34, 0.9, 0.4, c)
    for sx in (-1, 1):                                                      # reja de seguridad
        d.caja(cx + 0.3, cy + sx * 1.6, 0, 4.4, 0.05, 1.8, (245, 200, 40), transp=0.4)
    cartel(cx, cy + 2.2, 'U341 PALETIZADO (común)', G, esc=0.5, alto=2.8)


def construir(DX=360, DY=160):
    def S(x, y):          # posición 2D de la lógica (desplazada)
        return x + DX, y + DY
    # carteles grandes por zona (borde norte de cada piso)
    gran_cartel(2.5, -10.6, 'RECEPCIÓN Y SILOS', G, esc=1.3)
    gran_cartel(20.5, -7.8, 'LÍNEA 1 · YOGUR CON TROZOS DE FRESA', (200, 70, 105))
    gran_cartel(20.5, -25.3, 'LÍNEA 3 · KÉFIR NATURAL', (50, 110, 175))
    gran_cartel(20.5, -50.3, 'LÍNEA 2 · QUESO MOZZARELLA', (190, 140, 20))
    gran_cartel(78.0, -7.9, 'BODEGA DE PRODUCTO TERMINADO', G, esc=1.3)
    # tronco común
    for (x, y), s in ((W(120, 300), 'U113/U114 LECHE CRUDA'), (W(120, 520), 'S1 YOGUR'), (W(220, 520), 'S2 QUESO'), (W(320, 520), 'S3 KÉFIR')):
        cartel(x + (2.5 if s.startswith('U113') else 0), y + 2.6, s, G, esc=0.5)
    # línea 1 · yogur
    for (x2, y2), s, dy in ((S(320, 170), 'U201 FORMULACIÓN', 2.4), (S(448, 170), 'U202 HOMOG.+PAST.', 2.0),
                             (S(608, 75), 'FERMENTADORES U211-U213', 2.2), (S(736, 170), 'PULMÓN U215', 2.0), (S(832, 170), 'U214 PULMÓN Y FRUTA', 2.0)):
        x, y = W(x2, y2); cartel(x, y + dy, s, Y, esc=0.5)
    llenadora(*S(920, 120), Y, 'vaso', [1.0], 'U311 · VASOS 150 g · 12.000/h')
    llenadora(*S(920, 220), Y, 'botella', [1.0, 1.35], 'U312 · BOTELLAS 1000 g Y 1750 g')
    # línea 3 · kéfir
    for (x2, y2), s, dy in ((S(448, 520), 'U202 KÉFIR (compartida)', 2.0), (S(608, 380), 'FERMENTADORES KÉFIR', 2.2),
                             (S(768, 470), 'U234 PULMONES', 2.0)):
        x, y = W(x2, y2); cartel(x, y + dy, s, K, esc=0.5)
    llenadora(*S(870, 520), K, 'botella', [0.8, 1.0, 1.3], 'U331 · BOTELLAS 240, 500 Y 1000 g')
    # línea 2 · mozzarella
    for (x2, y2), s, dy in ((S(320, 1080), 'U221 TINA QUESERA', 2.2), (S(448, 1080), 'U222 ACIDIFICACIÓN', 2.0),
                             (S(576, 1080), 'U223 HILADORA', 2.0), (S(704, 940), 'U224 SALMUERA', 2.0),
                             (S(840, 1080), 'REPARTO A EMPAQUE', 2.0)):
        x, y = W(x2, y2); cartel(x, y + dy, s, Q, esc=0.5)
    llenadora(*S(920, 1030), Q, 'bloque', [1.0, 1.5], 'U321 · AL VACÍO 400 g Y 1000 g')
    llenadora(*S(920, 1130), Q, 'tarrina', [1.0], 'U322 · TARRINA 250 g')
    # fin de línea
    paletizado(1240, 960)
    for (x2, y2), s, c in (((1420, 330), 'CÁMARA YOGUR', Y), ((1420, 680), 'CÁMARA KÉFIR', K), ((1420, 1240), 'CÁMARA QUESO', Q)):
        x, y = W(x2, y2); cartel(x, y + 3.2, s, c, esc=0.5, alto=4.2)
    return d.ordenes()


OCULTAR = ['U311', 'U312', 'U321', 'U322', 'U331', 'U341_Paletizado']   # sus cajas por defecto se reemplazan por la decoración
