# Decoración 3D del modelo de la línea de yogures (linea_yogures_actual.spp), aplicada DESPUÉS de crear la escena
# con «Open 2D/3D». Pisos de color por sección, carteles de pie, tanques, tuberías de colores por producto (cada
# producto con su propio pulmón), bandas con cajas, robot KUKA de la biblioteca de Plant Simulation, operarios,
# laboratorio de calidad, cámara fría con estanterías y camiones de recepción y despacho.
# Todo va en el grupo gráfico "Deco" del Frame (no cuenta para el límite de 80 objetos).
# Coordenadas: 3D (m) = 2D (px) / 20, con el eje y invertido. Uso: python decorar_3d.py <carpeta de órdenes>
import os, sys, json

D = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(D, 'coords_yogures.json'), encoding='utf-8'))
MANUAL = os.environ.get('PALETIZADO') == 'manual'      # variante con paletizado por personas (sin robot)
COORD, SECC, Y0 = C['coord'], C['secciones'], C['Y0']
LIB = r'C:\Program Files\Siemens\Tecnomatix Plant Simulation 2404\3D\jt-graphics' + '\\'
FRESA, NATURAL, GRIEGO = (236, 112, 140), (95, 150, 215), (215, 175, 70)
LECHE, BASE, YOGUR = (200, 206, 214), (238, 226, 196), (246, 240, 226)
ACERO, BLANCO, OSCURO, NAVY = (205, 210, 218), (246, 247, 249), (40, 44, 55), (35, 60, 120)
GOMA, AMARILLO = (25, 25, 28), (245, 190, 30)


def rgb(c):
    return f'makeRGBValue({c[0]}, {c[1]}, {c[2]})'


L = []


def mat(c, brillo=None, transp=None):
    L.extend(['x.MaterialActive := true', f'x.MaterialDiffuseColor := {rgb(c)}'])
    if brillo is not None:
        L.append(f'x.MaterialShininess := {brillo}')
    if transp is not None:
        L.append(f'x.MaterialTransparency := {transp}')


def caja(cx, cy, z, l, w, h, c, brillo=None, transp=None):
    L.extend([f'x := g.createCuboid([{l:.3f}, {w:.3f}, {h:.3f}])', f'x.Position := [{cx:.3f}, {cy:.3f}, {z:.3f}]'])
    mat(c, brillo, transp)


def cil(cx, cy, z, r, h, c, r2=None, brillo=None, transp=None, rot=None):
    L.extend([f'x := g.createConeFrustum({r:.3f}, {(r if r2 is None else r2):.3f}, {h:.3f})', f'x.Position := [{cx:.3f}, {cy:.3f}, {z:.3f}]'])
    if rot:
        L.append(f'x.Rotation := [{rot[0]:.1f}, {rot[1]:.1f}, {rot[2]:.1f}, {rot[3]:.1f}]')
    mat(c, brillo, transp)


def W(x, y):
    return x / 20, -y / 20


# ---------------- piezas ----------------
def tubo_x(x0, x1, y, z, c, r=0.09):
    """Tubo horizontal a lo largo de x (el cilindro girado 90° sobre y crece hacia +x)."""
    a, b = min(x0, x1), max(x0, x1)
    if b - a > 0.01:
        cil(a, y, z, r, b - a, c, brillo=0.9, rot=(90, 0, 1, 0))


def tubo_y(x, y0, y1, z, c, r=0.09):
    """Tubo horizontal a lo largo de y (girado 90° sobre x crece hacia −y)."""
    a, b = min(y0, y1), max(y0, y1)
    if b - a > 0.01:
        cil(x, b, z, r, b - a, c, brillo=0.9, rot=(90, 1, 0, 0))


def tuberia(puntos, c, z=0.35, r=0.09):
    """Tubería ortogonal entre puntos del plano 2D (px), con codos."""
    P = [W(*p) for p in puntos]
    for (xa, ya), (xb, yb) in zip(P, P[1:]):
        if abs(ya - yb) < 1e-6:
            tubo_x(xa, xb, ya, z, c, r)
        else:
            tubo_y(xa, ya, yb, z, c, r)
    for xa, ya in P[1:-1]:                                            # codo
        cil(xa, ya, z - r * 1.3, r * 1.35, r * 2.6, c, brillo=0.9)


ANCHO_LETRA = 0.8
LETRA_EQUIPO = 0.62                                           # en letra pequeña el texto ocupa ≈ 0,62 m por letra a escala 1
CARTEL_MAX = 4.0                                              # ancho máximo de un cartel de equipo (m)


def tablero(cx, cy, s, color, esc, alto, poste=(90, 95, 105), grueso=0.06, ancho_max=None, letra=ANCHO_LETRA, postes=True):
    """Cartel de pie mirando al sur: dos postes, tablero del color de la sección, borde azul y texto blanco."""
    if ancho_max:                                             # la letra se achica para no invadir el cartel vecino
        esc = min(esc, (ancho_max - 0.6) / (letra * len(s)))
    ancho = letra * len(s) * esc + (1.2 if letra == ANCHO_LETRA else 0.6)                 # el texto real mide ≈ 0,8 m por letra a escala 1
    hb = 1.25 * esc + 0.5
    for sx in (-1, 1) if postes else ():
        cil(cx + sx * (ancho / 2 - 0.25), cy + 0.06 + grueso + 0.02, 0, grueso, alto + hb, poste)   # postes detrás del tablero
    caja(cx, cy, alto, ancho, 0.12, hb, color, 0.4)
    caja(cx, cy, alto + hb, ancho + 0.1, 0.16, 0.14, NAVY)
    t = round(esc * 3.4, 3)
    L.extend([f'x := g.createText("{s}")', 'x.Rotation := [90.0, 1.0, 0.0, 0.0]', f'x.Scale := [{t}, {t}, {t}]',
              f'x.Position := [{cx:.3f}, {cy - 0.08:.3f}, {alto + hb / 2:.3f}]'])
    mat((255, 255, 255))


def cartel(nombre, s, color, dy=2.2, esc=0.42, alto=2.0, dx=0.0, postes=True):
    x, y = W(*COORD[nombre])
    tablero(x + dx, y + dy, s, color, esc, alto, ancho_max=CARTEL_MAX, letra=LETRA_EQUIPO, postes=postes)


def tanque(nombre, r, h, color, n=1, paso=0.0, tapa=ACERO, dy=0.0):
    x0, y0 = W(*COORD[nombre])
    y0 += dy
    for i in range(n):
        x = x0 + (i - (n - 1) / 2) * paso
        for sx in (-1, 1):                                   # patas
            for sy in (-1, 1):
                cil(x + sx * r * 0.6, y0 + sy * r * 0.6, 0, 0.07, 0.8, OSCURO)
        cil(x, y0, 0.35, 0.08, 0.5, ACERO, brillo=0.9)       # salida inferior hacia la tubería
        cil(x, y0, 0.8, 0.25, 0.6, ACERO, r2=r, brillo=0.8)  # fondo cónico
        cil(x, y0, 1.4, r, h, ACERO, brillo=0.85)
        cil(x, y0, 1.4 + h * 0.62, r + 0.03, 0.35, color)    # franja del color del producto o de la sección
        cil(x, y0, 1.4 + h, r, 0.45, tapa, r2=r * 0.3, brillo=0.8)


def rueda(x, y, r=0.45, ancho=0.3):
    cil(x, y + ancho / 2, r, r, ancho, GOMA, rot=(90, 1, 0, 0))
    cil(x, y + ancho / 2 + 0.01, r, r * 0.5, 0.02, (180, 184, 190), rot=(90, 1, 0, 0))


def camion(x_cola, y, largo, cab, carga='caja', hacia=-1):
    """Camión a lo largo de x. x_cola = extremo trasero; hacia = +1 si la cabina queda al este, −1 al oeste."""
    s = hacia
    xc = x_cola + s * largo / 2
    caja(xc, y, 0.0, largo + 0.4, 2.2, 0.35, (55, 58, 66))                     # chasis bajo
    if carga == 'caja':
        caja(xc, y, 1.1, largo, 2.5, 2.7, (244, 246, 250), 0.4)                 # furgón refrigerado
        caja(xc, y - 1.26, 2.0, largo - 0.6, 0.02, 0.5, NAVY)                   # franja azul
        caja(x_cola + s * 0.6, y, 3.8, 1.0, 1.6, 0.4, (150, 155, 165))          # equipo de frío
    else:
        caja(xc, y, 0.35, largo - 0.4, 1.0, 0.6, (70, 74, 82))                  # cuna
        x_ini = min(x_cola, x_cola + s * largo) + 0.3
        cil(x_ini, y, 1.85, 1.15, largo - 0.6, ACERO, brillo=0.95, rot=(90, 0, 1, 0))   # tanque acostado
        for k in (0.25, 0.5, 0.75):
            cil(x_cola + s * largo * k - 0.06, y, 1.85, 1.2, 0.12, (170, 176, 186), rot=(90, 0, 1, 0))
    xk = x_cola + s * (largo + 1.2)
    caja(xk, y, 0.35, 2.2, 2.4, 2.4, cab, 0.6)                                  # cabina
    caja(xk + s * 1.11, y, 1.6, 0.02, 2.0, 0.9, (40, 60, 85), 0.95)             # parabrisas
    for xr in (x_cola + s * 1.0, x_cola + s * 2.2, x_cola + s * (largo - 0.8), xk + s * 0.5):
        rueda(xr, y + 1.05)
        rueda(xr, y - 1.35)


def operario(cx, cy, giro=0):
    L.extend([f'x := g.importGraphics("{LIB}OperatorWorking.jt", false, false)', f'x.Position := [{cx:.3f}, {cy:.3f}, 0.0]'])
    if giro:
        L.append(f'x.Rotation := [{giro:.1f}, 0.0, 0.0, 1.0]')


def modelo(archivo, cx, cy, z=0.0, giro=0):
    L.extend([f'x := g.importGraphics("{LIB}{archivo}", false, false)', f'x.Position := [{cx:.3f}, {cy:.3f}, {z:.3f}]'])
    if giro:
        L.append(f'x.Rotation := [{giro:.1f}, 0.0, 0.0, 1.0]')


def productos(cx, cy, z, n, forma, c, tam=1.0, paso=0.42):
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * paso
        if forma == 'vaso':
            cil(x, cy, z, 0.09 * tam, 0.16 * tam, c, r2=0.12 * tam)
            cil(x, cy, z + 0.16 * tam, 0.125 * tam, 0.02, (230, 230, 235))
        elif forma == 'botella':
            cil(x, cy, z, 0.1 * tam, 0.32 * tam, BLANCO)
            cil(x, cy, z + 0.32 * tam, 0.1 * tam, 0.08 * tam, BLANCO, r2=0.04 * tam)
            cil(x, cy, z + 0.4 * tam, 0.045 * tam, 0.05, c)
        elif forma == 'pote':
            cil(x, cy, z, 0.15 * tam, 0.13 * tam, BLANCO)
            cil(x, cy, z + 0.13 * tam, 0.155 * tam, 0.025, c)


def llenadora(nombre, filas, titulo, color):
    cx, cy = W(*COORD[nombre])
    caja(cx, cy, 0, 3.2, 1.6, 1.2, (232, 235, 240), 0.4)
    caja(cx, cy, 1.2, 3.24, 1.64, 0.12, color)
    caja(cx, cy, 1.32, 3.2, 1.2, 1.1, (215, 235, 245), transp=0.6)             # guarda de policarbonato
    caja(cx - 1.2, cy - 0.83, 0.8, 0.45, 0.05, 0.4, (40, 70, 110), 0.9)        # pantalla HMI
    caja(cx, cy, 1.32, 3.2, 0.55, 0.06, (60, 62, 70))                          # banda
    for i, (forma, c, tam) in enumerate(filas):
        dy = (i - (len(filas) - 1) / 2) * 0.32
        productos(cx, cy + dy, 1.38, 6, forma, c, tam, paso=0.45)
    tablero(cx, cy + 1.6, titulo, color, 0.4, 2.3, ancho_max=3.4, letra=LETRA_EQUIPO)
    operario(cx - 1.2, cy - 1.5)


def estiba(cx, cy, colores, niveles=3):
    caja(cx, cy, 0, 1.2, 1.0, 0.14, (176, 128, 74))
    for k in range(niveles):
        for i in range(3):
            for j in range(2):
                caja(cx - 0.4 + i * 0.4, cy - 0.25 + j * 0.5, 0.14 + k * 0.36, 0.38, 0.48, 0.34, colores[(i + j + k) % len(colores)])
    caja(cx, cy, 0.14, 1.22, 1.02, niveles * 0.36 + 0.02, (235, 240, 245), transp=0.7)   # film


def montacargas():
    """Montacargas de contrapeso a escala real (≈ 2,4 m sin horquillas, guarda a 2,15 m), dibujado sobre la clase
    .MUs.Montacargas; coordenadas locales: avanza hacia +x. Lleva una estiba envuelta en las horquillas y su operario."""
    NAR, GRIS, NEG = (240, 150, 20), (70, 74, 82), (30, 31, 35)
    caja(-0.15, 0, 0.18, 1.9, 1.12, 0.62, NAR, 0.6)                             # chasis
    caja(-0.95, 0, 0.18, 0.5, 1.12, 0.95, GRIS, 0.5)                            # contrapeso trasero
    cil(-1.2, 0, 0.18, 0.56, 0.95, GRIS, brillo=0.5)                            # contrapeso redondeado
    caja(0.55, 0, 0.8, 0.35, 1.0, 0.45, NAR, 0.6)                               # tablero delantero
    caja(-0.45, 0, 0.8, 0.5, 0.55, 0.12, NEG)                                   # asiento
    caja(-0.68, 0, 0.92, 0.1, 0.55, 0.55, NEG)                                  # respaldo
    cil(0.35, 0, 1.25, 0.03, 0.25, NEG)                                         # columna de dirección
    cil(0.35, 0, 1.47, 0.17, 0.04, NEG)                                         # volante
    for sx, sy in ((-0.8, 0.5), (-0.8, -0.5), (0.62, 0.5), (0.62, -0.5)):       # postes de la guarda
        caja(sx, sy, 0.8, 0.06, 0.06, 1.35, NEG)
    caja(-0.09, 0, 2.15, 1.5, 1.08, 0.06, NEG)                                  # techo (guarda)
    for k in range(4):
        caja(-0.64 + k * 0.37, 0, 2.21, 0.05, 1.08, 0.04, GRIS)                 # barras del techo
    cil(-0.6, 0.4, 2.21, 0.06, 0.1, (255, 120, 0), brillo=0.9)                  # baliza
    for sy in (-0.42, 0.42):                                                    # mástil de dos rieles
        caja(0.82, sy, 0.1, 0.1, 0.12, 2.25, GRIS, 0.7)
    caja(0.82, 0, 2.2, 0.1, 0.96, 0.1, GRIS)
    caja(0.92, 0, 0.12, 0.08, 0.95, 0.75, NEG)                                  # tablero portahorquillas
    for sy in (-0.3, 0.3):
        caja(1.5, sy, 0.12, 1.1, 0.12, 0.05, NEG)                               # horquillas
    caja(1.55, 0, 0.17, 1.2, 1.0, 0.14, (176, 128, 74))                         # estiba que lleva
    for k in range(3):
        for i in range(3):
            for j in range(2):
                caja(1.15 + i * 0.4, -0.25 + j * 0.5, 0.31 + k * 0.34, 0.38, 0.48, 0.32,
                     (FRESA, NATURAL, GRIEGO)[(i + j + k) % 3])
    caja(1.55, 0, 0.31, 1.22, 1.02, 1.04, (235, 240, 245), transp=0.7)          # film
    for xr, r in ((0.45, 0.33), (-0.85, 0.27)):
        rueda(xr, 0.42, r=r, ancho=0.22)
        rueda(xr, -0.64, r=r, ancho=0.22)
    L.extend([f'x := g.importGraphics("{LIB}OperatorWorking.jt", false, false)', 'x.Position := [-0.35, 0.0, 0.18]',
              'x.Rotation := [-90.0, 0.0, 0.0, 1.0]'])                          # operario de pie en la cabina


def caja_mu(color):
    """Gráfico de cada caja (MU de presentación): bulto de 4 cajas de cartón con franja del sabor."""
    for i in (-1, 1):
        for j in (-1, 1):
            caja(i * 0.24, j * 0.2, 0.0, 0.46, 0.38, 0.32, (196, 160, 112), 0.3)
            caja(i * 0.24, j * 0.2, 0.12, 0.47, 0.39, 0.07, color)
    caja(0, 0, 0.32, 0.96, 0.8, 0.01, (215, 190, 140))                          # cinta superior


def encajonadora(nombre, llenadora, titulo, color, forma, c_prod, tam):
    """Encajonadora: forma la caja con el cartón plano del almacén, mete los envases que llegan por la banda y la cierra."""
    xe, ye = W(*COORD[nombre])
    xl = W(*COORD[llenadora])[0] + 1.6                                          # salida de la llenadora
    caja((xl + xe - 1.2) / 2, ye, 0, xe - 1.2 - xl, 0.5, 0.8, (70, 74, 84))      # banda de envases
    caja((xl + xe - 1.2) / 2, ye, 0.8, xe - 1.2 - xl, 0.4, 0.03, (35, 37, 42))
    productos((xl + xe - 1.2) / 2, ye, 0.83, int((xe - 1.2 - xl) / 0.45), forma, c_prod, tam, paso=0.45)
    caja(xe, ye, 0, 2.4, 1.6, 1.0, (225, 229, 236), 0.4)                        # cuerpo
    caja(xe, ye, 1.0, 2.44, 1.64, 0.1, color)
    caja(xe, ye, 1.1, 2.4, 1.6, 1.0, (215, 235, 245), transp=0.6)               # guarda
    caja(xe - 0.3, ye, 1.1, 0.5, 0.42, 0.34, (196, 160, 112))                   # caja abierta recibiendo envases
    caja(xe + 0.6, ye, 1.1, 0.5, 0.42, 0.34, (196, 160, 112))                   # caja cerrada
    caja(xe + 0.6, ye, 1.44, 0.52, 0.06, 0.01, (200, 180, 120))                 # cinta de cierre
    caja(xe - 0.2, ye - 1.3, 0, 1.2, 0.9, 0.14, (176, 128, 74))                 # estiba de cartón plano
    caja(xe - 0.2, ye - 1.3, 0.14, 1.1, 0.8, 0.7, (205, 170, 120))
    caja(xe + 0.9, ye - 0.83, 0.8, 0.4, 0.05, 0.35, (40, 70, 110), 0.9)         # pantalla HMI
    tablero(xe, ye + 1.6, titulo, color, 0.36, 2.3, ancho_max=3.0, letra=LETRA_EQUIPO)


ORD = []


def cortar(n=380):
    cab = ['var m: object := .Models.Model', 'var g: any := m._3D.getGraphic("Deco")', 'var x: any']
    out, cur = [], []
    for ln in L:
        if ln.startswith('x := ') and len(cur) >= n:
            out.append('\n'.join(cab + cur)); cur = []
        cur.append(ln)
    if cur:
        out.append('\n'.join(cab + cur))
    return out


# ---------------- pisos, franjas de seguridad y carteles de sección ----------------
YT, YB = 150, 620
XMAX = max(s[4] for s in SECC)
caja(XMAX / 40, -(YT + YB) / 2 / 20, -0.12, XMAX / 20 + 4, (YB - YT) / 20 + 6, 0.1, (185, 190, 198))      # losa general
caja(XMAX / 20 + 6, -(YT + YB) / 2 / 20, -0.12, 8, (YB - YT) / 20 + 6, 0.1, (95, 98, 104))              # patio de camiones
PISO = {'1': (120, 138, 178), '2': (80, 168, 140), '3': (232, 150, 95), '4': (150, 125, 200), '5': (222, 110, 150), '6': (95, 150, 210)}
CORTO = {'1': 'RECEPCIÓN Y TRONCO COMÚN', '2': 'PREPARACIÓN', '3': 'FERMENTACIÓN', '4': 'ACONDICIONAMIENTO', '5': 'ENVASADO Y ENCAJONADO', '6': 'PALETIZADO, CÁMARA Y DESPACHO'}
for num, tit, sub, x0, x1, fondo, borde in SECC:
    cx, cy = (x0 + x1) / 2 / 20, -(YT + YB) / 2 / 20
    caja(cx, cy, -0.02, (x1 - x0) / 20 - 0.3, (YB - YT) / 20, 0.04, PISO[num], 0.2)                  # piso de la sección
    caja(cx, -YT / 20 - 0.15, 0.02, (x1 - x0) / 20 - 0.3, 0.3, 0.02, borde)                         # franja de color al norte
    for xe in (x0 / 20 + 0.1, x1 / 20 - 0.1):                                                       # bordes amarillos
        caja(xe, cy, 0.02, 0.12, (YB - YT) / 20, 0.02, AMARILLO)
    s = f'{num} · {CORTO[num]}'
    ancho_max = (x1 - x0) / 20 - 1.0
    esc = max(0.35, min(1.3, (ancho_max - 1.2) / (ANCHO_LETRA * len(s))))
    tablero(cx, -YT / 20 + 1.2, s, borde, esc, 3.4, poste=NAVY, grueso=0.14)
SEC = {s[0]: s[6] for s in SECC}

# ---------------- tuberías (px del plano 2D) ----------------
tuberia([(150, Y0), (380, Y0)], LECHE)                                               # cisterna → recepción → leche cruda → HTST
tuberia([(380, Y0), (430, Y0), (430, Y0 - 70), (506, Y0 - 70)], LECHE)               # HTST → silos
tuberia([(430, Y0), (430, Y0 + 70), (480, Y0 + 70)], LECHE)
tuberia([(506, Y0 - 70), (560, Y0 - 70), (560, Y0 + 70), (480, Y0 + 70)], LECHE)    # silos → formulación
tuberia([(560, Y0), (640, Y0)], LECHE)
tuberia([(640, Y0), (790, Y0)], BASE)                                                # base → U202
cil(790 / 20, -Y0 / 20, 0.35, 0.09, 6.05, BASE, brillo=0.9)                          # subida a la tubería aérea
tuberia([(790, Y0), (830, Y0)], BASE, z=6.4, r=0.12)
tuberia([(830, Y0 - 60), (830, Y0 + 60)], BASE, z=6.4, r=0.12)
for yy in (Y0 - 60, Y0 + 60):                                                        # los fermentadores se llenan por arriba
    tuberia([(830, yy), (1010, yy)], BASE, z=6.4, r=0.12)
    cil(830 / 20, -yy / 20, 0, 0.08, 6.4, (120, 125, 135))                           # columna de soporte
for f in C['ferm']:
    x, y = W(*COORD[f])
    cil(x, y, 6.0, 0.07, 0.4, BASE, brillo=0.9)
tuberia([(900, Y0 - 60), (1080, Y0 - 60)], YOGUR)                                    # salida de los fermentadores (abajo)
tuberia([(900, Y0 + 60), (1080, Y0 + 60)], YOGUR)
tuberia([(1080, Y0 - 70), (1080, Y0 + 90)], YOGUR)
tuberia([(1080, Y0 - 70), (1225, Y0 - 70)], YOGUR)                                   # → U215 enfriamiento
tuberia([(1225, Y0 - 70), (1225, Y0 - 120), (1280, Y0 - 120)], FRESA)                # U215 → pulmón FRESA
tuberia([(1225, Y0 - 70), (1225, Y0 - 20), (1280, Y0 - 20)], NATURAL)                # U215 → pulmón NATURAL
tuberia([(1080, Y0 + 90), (1298, Y0 + 90)], GRIEGO)                                  # → separador → pulmones griego
tuberia([(1280, Y0 - 120), (1488, Y0 - 120)], FRESA)                                 # pulmón fresa → fruta → U311
tuberia([(1470, Y0 - 120), (1470, Y0 - 26), (1488, Y0 - 26)], FRESA)                 # ... → U312 botellas
tuberia([(1280, Y0 - 20), (1488, Y0 - 20)], NATURAL, z=0.35)                         # pulmón natural → U312
cil(1450 / 20, -(Y0 - 20) / 20, 0.35, 0.08, 0.75, NATURAL, brillo=0.9)               # puente sobre la línea de fresa
tuberia([(1450, Y0 - 20), (1450, Y0 - 114), (1488, Y0 - 114)], NATURAL, z=1.1)       # pulmón natural → U311 vasos
tuberia([(1298, Y0 + 90), (1488, Y0 + 90)], GRIEGO)                                  # pulmón griego → U313

# ---------------- sección 1 · recepción y tronco común ----------------
x, y = W(*COORD['U111_Recepcion'])
camion(x - 1.2, y, 5.6, (200, 40, 40), carga='tanque', hacia=-1)  # cisterna de leche cruda en la bahía
caja(x - 3.6, y, 0, 8.6, 3.4, 0.08, (120, 125, 135))              # bahía de descargue
for sx in (-1, 1):
    for xx in (x - 7.4, x + 0.6):
        cil(xx, y + sx * 1.8, 0, 0.08, 4.4, (120, 125, 135))
caja(x - 3.4, y, 4.4, 8.6, 4.0, 0.15, (150, 155, 165), transp=0.35)   # techo
caja(x + 0.6, y - 0.9, 0, 0.6, 0.5, 1.4, ACERO, 0.8)              # bomba y caudalímetro
cartel('U111_Recepcion', 'U111/U112 RECEPCIÓN', SEC['1'], dy=2.6)
operario(x + 0.3, y - 2.0)
tanque('U113_Leche_cruda', 1.1, 4.5, SEC['1'], n=2, paso=2.6)
cartel('U113_Leche_cruda', 'U113-U114 LECHE CRUDA', SEC['1'], dy=2.4)
x, y = W(*COORD['U121_Pasteurizador'])
caja(x - 0.8, y, 0, 1.2, 1.0, 1.8, ACERO, 0.8)                    # separadora
caja(x + 0.8, y, 0, 1.6, 0.8, 1.6, (180, 186, 196), 0.8)          # placas HTST
cil(x + 0.8, y - 0.8, 0.3, 0.12, 1.2, (200, 70, 60))              # tubo de retención
modelo('Cabinet.jt', x - 0.4, y - 1.6)
cartel('U121_Pasteurizador', 'U121/U122 HTST 75 °C', SEC['1'])
tanque('U123AB_Silo_entera', 1.1, 5.5, NATURAL, n=2, paso=2.6)
cartel('U123AB_Silo_entera', 'SILOS LECHE ENTERA', SEC['1'], dy=2.5)
tanque('U123C_Silo_descremada', 1.0, 5.0, GRIEGO)
cartel('U123C_Silo_descremada', 'SILO DESCREMADA', SEC['1'], dy=2.2)
# silos de las otras dos líneas de la planta (acta 9-oct): la leche sale hacia su línea, fuera de este modelo
QUESO, UHT = (240, 200, 90), (110, 170, 120)
tuberia([(430, Y0 + 70), (430, Y0 + 225), (480, Y0 + 225)], LECHE)
tuberia([(430, Y0 + 150), (480, Y0 + 150)], LECHE)
for nm, txt, c in (('Hacia_quesos', 'U124 A QUESOS 50.000 L/día', QUESO), ('Hacia_leche_UHT', 'U125 A LECHE UHT 43.000 L/día', UHT)):
    tanque(nm, 1.0, 4.6, c)
    x, y = W(*COORD[nm])
    tubo_x(x, x + 2.6, y, 0.35, c, r=0.1)                                       # sale hacia su línea, al sur de la planta
    tubo_y(x + 2.6, y, -YB / 20 - 1.5, 0.35, c, r=0.1)
    cil(x + 2.6, y, 0.25, 0.2, 0.2, c, brillo=0.9)                              # codo
    cartel(nm, txt, c, dx=0.6, dy=-1.8, esc=0.36)
# laboratorio de calidad (andén de recepción): vidrio, escritorio, mesa y analista
lx, ly = 13.0, -27.0
caja(lx, ly, 0, 9.0, 4.4, 0.06, (236, 238, 242))
caja(lx, ly, 0.06, 9.0, 4.4, 2.8, (200, 225, 240), transp=0.75)
modelo('Desk.jt', lx - 2.0, ly + 0.6)
operario(lx - 2.0, ly - 0.25)                                         # analista en el escritorio
modelo('Table2x1x1.jt', lx + 2.2, ly + 0.8)
modelo('Cabinet.jt', lx + 3.8, ly - 1.2)
operario(lx + 2.2, ly - 0.4)
tablero(lx, ly + 2.6, 'LABORATORIO DE CALIDAD', SEC['1'], 0.45, 2.8, ancho_max=8.5, letra=LETRA_EQUIPO)

# ---------------- sección 2 · preparación de la base ----------------
tanque('U201_Formulacion', 1.2, 2.6, SEC['2'])
x, y = W(*COORD['U201_Formulacion'])
caja(x - 1.8, y, 0, 0.9, 0.9, 1.4, (230, 232, 236))               # tolva de polvos
caja(x - 1.8, y - 1.0, 0, 1.2, 1.0, 0.14, (176, 128, 74))         # estiba de leche en polvo y azúcar
for i in range(2):
    caja(x - 1.8, y - 1.0, 0.14 + i * 0.3, 1.1, 0.9, 0.28, (240, 236, 222))
operario(x - 2.9, y - 0.4)
cartel('U201_Formulacion', 'U201 FORMULACIÓN', SEC['2'], dy=2.2)
x, y = W(*COORD['U202_Tratamiento'])
caja(x - 0.9, y, 0, 1.4, 1.0, 1.3, (60, 90, 140), 0.6)             # homogeneizador
caja(x + 0.8, y, 0, 1.6, 0.8, 1.7, (180, 186, 196), 0.8)          # placas
cil(x + 0.8, y - 0.9, 0.3, 0.14, 1.3, (200, 70, 60))              # retención 5 min
modelo('Cabinet.jt', x - 0.9, y - 1.5)
cartel('U202_Tratamiento', 'U202 92 °C x 5 min', SEC['2'])

# ---------------- sección 3 · fermentación ----------------
for f in C['ferm']:
    tanque(f, 1.15, 4.2, SEC['3'])
    cartel(f, f.split('_')[0], SEC['3'], dy=1.9, esc=0.4)
x, y = W(*COORD[C['ferm'][0]])
operario(x + 2.75, y - 3.0)

# ---------------- sección 4 · acondicionamiento ----------------
x, y = W(*COORD['U215_Enfriamiento'])
caja(x, y, 0, 1.8, 0.9, 1.7, (180, 186, 196), 0.8)
cartel('U215_Enfriamiento', 'U215 ENFRIAMIENTO 20 °C', SEC['4'], dy=1.8)
x, y = W(*COORD['U216_Separador_griego'])
caja(x, y, 0, 1.4, 1.4, 0.9, (60, 90, 140), 0.6)                   # base
cil(x, y, 0.9, 0.6, 0.9, ACERO, r2=0.35, brillo=0.9)               # tambor del separador
cartel('U216_Separador_griego', 'U216 SEPARADOR GRIEGO', GRIEGO, dy=1.9)
tanque('U214A_Pulmon_fresa', 1.0, 3.6, FRESA)
cartel('U214A_Pulmon_fresa', 'U214A PULMÓN FRESA', FRESA, dy=-1.1, esc=0.36, alto=2.4, postes=False)   # placa en la cara del tanque
tanque('U214B_Pulmon_natural', 1.0, 3.6, NATURAL)
cartel('U214B_Pulmon_natural', 'U214B PULMÓN NATURAL', NATURAL, dy=-1.9, esc=0.36)
tanque('U217_Pulmones_griego', 0.75, 2.6, GRIEGO, n=2, paso=1.8)
cartel('U217_Pulmones_griego', 'U217 PULMONES GRIEGO', GRIEGO, dy=-1.9, esc=0.36)
x, y = W(*COORD['Reparto_fresa'])                                   # dosificación de fruta en línea
tanque('Reparto_fresa', 0.45, 1.4, FRESA, dy=-1.4)
caja(x, y, 0, 0.9, 0.7, 0.9, (225, 228, 234), 0.6)                  # dosificador
cartel('Reparto_fresa', 'FRUTA EN LÍNEA', FRESA, dy=1.5, esc=0.32, alto=1.6)
for nm, s, c in (('Reparto_natural', 'VÁLVULAS NATURAL', NATURAL), ('Reparto_griego', 'VÁLVULAS GRIEGO', GRIEGO)):
    x, y = W(*COORD[nm])
    caja(x, y, 0, 0.9, 0.7, 0.9, (225, 228, 234), 0.6)
    caja(x, y, 0.9, 0.92, 0.72, 0.1, c)
    cartel(nm, s, c, dy=1.5, esc=0.32, alto=1.6)

# ---------------- sección 5 · envasado ----------------
llenadora('U311_Vasos', [('vaso', FRESA, 1.0), ('vaso', NATURAL, 1.15)], 'U311 VASOS · 12.000/h', SEC['5'])
llenadora('U312_Botellas', [('botella', FRESA, 1.0), ('botella', NATURAL, 1.0)], 'U312 BOTELLAS', SEC['5'])
llenadora('U313_Griego', [('vaso', GRIEGO, 1.0), ('pote', GRIEGO, 1.0)], 'U313 GRIEGO', GRIEGO)
encajonadora('U321_Encajonadora_vasos', 'U311_Vasos', 'U321 ENCAJONADORA', SEC['5'], 'vaso', NATURAL, 1.0)
encajonadora('U322_Encajonadora_botellas', 'U312_Botellas', 'U322 ENCAJONADORA', SEC['5'], 'botella', FRESA, 1.0)
encajonadora('U323_Encajonadora_griego', 'U313_Griego', 'U323 ENCAJONADORA', GRIEGO, 'pote', GRIEGO, 1.0)
xp, yp = W(*COORD['U341_Paletizado'])
# las bandas de cajas son objetos Conveyor reales del modelo: las cajas (MU) viajan por ellas hasta el robot

# ---------------- sección 6 · fin de línea y cámara ----------------
if not MANUAL:
    # el robot es el objeto PickAndPlace del modelo (se mueve de verdad); aquí solo van estibas y reja
    estiba(xp + 2.1, yp, (FRESA, NATURAL, GRIEGO))
    estiba(xp + 2.1, yp + 2.0, (NATURAL, FRESA), niveles=2)
    for sy in (-1, 1):                                              # reja de seguridad
        caja(xp + 0.6, yp + sy * 2.0 + (1.0 if sy > 0 else 0), 0, 5.0, 0.05, 1.8, AMARILLO, transp=0.45)
    caja(xp + 3.15, yp + 0.5, 0, 0.05, 5.0, 1.8, AMARILLO, transp=0.45)
    cartel('U341_Paletizado', 'U341 PALETIZADO', SEC['6'], dy=3.6)
    operario(xp - 1.5, yp - 2.4)
else:
    # paletizado manual: mesa de llegada al final de las bandas, dos operarios y estibas armándose en el piso
    caja(xp - 0.2, yp, 0, 1.4, 1.2, 0.8, (150, 155, 165), 0.5)     # mesa de rodillos donde llegan las cajas
    caja(xp - 0.2, yp, 0.8, 1.42, 1.22, 0.04, (60, 62, 70))
    estiba(xp + 1.6, yp - 0.9, (FRESA, NATURAL, GRIEGO), niveles=2)  # estibas en formación
    estiba(xp + 1.6, yp + 0.9, (NATURAL, GRIEGO), niveles=1)
    estiba(xp + 3.0, yp, (FRESA, NATURAL, GRIEGO))                 # estiba completa esperando la envolvedora
    operario(xp + 0.7, yp - 0.9, giro=180)                          # dos operarios por turno
    operario(xp + 0.7, yp + 0.9, giro=180)
    caja(xp + 1.0, yp - 2.3, 0, 1.0, 0.6, 0.9, (200, 70, 60), 0.5)  # carro de cartón y esquineros
    cartel('U341_Paletizado', 'U341 PALETIZADO MANUAL', SEC['6'], dy=3.6)
x, y = W(*COORD['U342_Envolvedora'])                               # envolvedora de film stretch
cil(x, y, 0, 0.95, 0.15, (70, 74, 84))                              # mesa giratoria
estiba(x, y + 0.0, (NATURAL, GRIEGO, FRESA))
caja(x + 1.25, y, 0, 0.25, 0.25, 2.6, (60, 90, 140))                # mástil
cil(x + 1.0, y, 0.6, 0.11, 0.55, (235, 240, 245), brillo=0.6)       # rollo de film
caja(x + 1.25, y, 2.6, 0.6, 0.6, 0.15, (60, 90, 140))
cartel('U342_Envolvedora', 'U342 ENVOLVEDORA', SEC['6'], dy=2.4)
y1, y2 = W(1935, Y0 + 60)[1], W(1935, Y0 + 80)[1]                    # carril del montacargas pintado en el piso
caja(W(1980, 0)[0], (y1 + y2) / 2, 0.02, 6.0, 2.6, 0.01, (230, 200, 60), 0.2)
caja(W(1980, 0)[0], (y1 + y2) / 2, 0.03, 5.8, 2.4, 0.01, PISO["6"], 0.2)
x, y = W(*COORD['U411_Camara'])
caja(x, y, 0, 5.0, 7.5, 3.8, (210, 230, 245), transp=0.62)          # cámara fría
caja(x, y, 3.8, 5.1, 7.6, 0.08, (225, 238, 250), transp=0.7)         # techo de vidrio
for i in range(3):                                                  # estanterías con estibas
    yy = y - 2.6 + i * 2.6
    for xx in (x - 1.4, x + 1.4):
        caja(xx, yy, 0, 1.3, 1.1, 0.06, (90, 110, 140))
        for nivel in range(3):
            caja(xx, yy, 0.06 + nivel * 1.2, 1.3, 1.1, 0.05, (230, 120, 30))
            caja(xx, yy, 0.12 + nivel * 1.2, 1.1, 0.9, 0.7, (FRESA, NATURAL, GRIEGO)[(i + nivel) % 3], 0.3)
        for sx in (-0.62, 0.62):
            for sy in (-0.52, 0.52):
                cil(xx + sx, yy + sy, 0, 0.04, 3.6, (60, 90, 140))
cartel('U411_Camara', 'CÁMARA 2-4 °C', SEC['6'], dy=4.6, alto=3.0)
# muelle y camión de despacho
xs = [W(*COORD[f'Despacho_{c}']) for c in C['desp']]
xd = xs[0][0]
caja(xd + 1.6, y, 0, 1.2, 3.4, 1.2, (150, 155, 165))                 # muelle
caja(xd + 0.2, y, 0, 0.3, 3.6, 3.6, (90, 95, 105))                   # marco de la puerta
camion(xd + 2.3, y, 8.0, (40, 90, 160), carga='caja', hacia=1)
estiba(xd - 0.6, y + 2.6, (FRESA, NATURAL, GRIEGO), niveles=2)
tablero(xd + 1.0, y + 4.6, 'DESPACHO', SEC['6'], 0.5, 2.6)

ORD.extend(cortar())
L.clear()
montacargas()
ORD.append('\n'.join(['var g: any := .MUs.Montacargas._3D.getGraphic("default")', 'var x: any'] + L))
for ref in C['desp']:                                                   # gráfico de las cajas en cada clase de MU
    L.clear()
    caja_mu({'YF': FRESA, 'YN': NATURAL, 'YG': GRIEGO}[ref[:2]])
    ORD.append('\n'.join([f'var g: any := .MUs.{ref}._3D.getGraphic("default")', 'var x: any'] + L))
# sin esto Plant Simulation encoge el gráfico de cada MU al tamaño de su ícono 2D
ORD.append('\n'.join(f'.MUs.{c}._3D.ScaleAutomatically := false' for c in ['Montacargas'] + C['desp']))
OCULTAR = ['U113_Leche_cruda', 'U123AB_Silo_entera', 'U123C_Silo_descremada', 'U201_Formulacion', 'U202_Tratamiento',
           'U121_Pasteurizador', 'U215_Enfriamiento', 'U216_Separador_griego', 'U214A_Pulmon_fresa', 'U214B_Pulmon_natural',
           'U217_Pulmones_griego', 'U311_Vasos', 'U312_Botellas', 'U313_Griego', 'U411_Camara',
           'U321_Encajonadora_vasos', 'U322_Encajonadora_botellas', 'U323_Encajonadora_griego', 'U342_Envolvedora',
           'U111_Recepcion', 'Cisternas', 'Reparto_fresa', 'Reparto_natural', 'Reparto_griego', 'Registro_de_lotes',
           'Programa_semanal', 'Hacia_quesos', 'Hacia_leche_UHT'] + C['ferm'] + [f'Despacho_{c}' for c in C['desp']]
ORD.append('\n'.join(['var m: object := .Models.Model'] + [f'm.{n}._3D.Scale := [0.02, 0.02, 0.02]' for n in OCULTAR]))
ORD.append('var m: object := .Models.Model\nm.Analizador_cuellos._3D.Scale := [0.02, 0.02, 0.02]')
ORD.append('var m: object := .Models.Model\nm.EventController._3D.Scale := [0.02, 0.02, 0.02]')
ORD.append('var mt: object := str_to_obj(".Models.Model.Init")\nmt._3D.Scale := [0.02, 0.02, 0.02]')   # m.Init ejecutaría el método
# los tanques y la cámara muestran nivel de llenado en vez de apilar MUs; los repartos (lotes partidos en fragmentos
# esperando la llenadora) no muestran su contenido para que su cola no se vea como una torre
ORD.append('\n'.join(['var m: object := .Models.Model'] + [f'm.{b}._3D.ShowContentsAs := "Fill level"' for b in (
    'U113_Leche_cruda', 'U123AB_Silo_entera', 'U123C_Silo_descremada', 'U214A_Pulmon_fresa', 'U214B_Pulmon_natural',
    'U217_Pulmones_griego', 'U411_Camara')] + ['m.' + r + '._3D.ShowContent := false'
                                               for r in ('Reparto_fresa', 'Reparto_natural', 'Reparto_griego')]))

if __name__ == '__main__':
    dst = sys.argv[1] if len(sys.argv) > 1 else D
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(dst):
        if f.startswith('deco_'):
            os.remove(os.path.join(dst, f))
    for i, o in enumerate(ORD, 1):
        open(os.path.join(dst, f'deco_{i:02d}.txt'), 'w', encoding='utf-8').write('simtalk\n' + o + '\n')
    print(len(ORD), 'órdenes', sum(o.count('x := ') for o in ORD), 'figuras')
