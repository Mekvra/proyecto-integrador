# Distribución en planta (layout) de Lácteos Altos de Teusacá, planta actual de 150.000 L/día (acta 9-oct-2026).
# La línea de yogures va en detalle (mismos códigos ISA-88 y mismas 6 secciones del modelo de Tecnomatix);
# quesos y leche UHT van como zonas. Medidas propuestas por Mekvra (no hay plano del terreno): terreno 150 × 95 m,
# nave de 110 × 60 m, pasillo de montacargas de 3,5 m y pasillos peatonales de 1,2 m.
# Genera layout_planta_actual.svg y .html (exportar a PNG/PDF con ../vsm/exportar.mjs, tamaño A3 apaisado).
import os

D = os.path.dirname(os.path.abspath(__file__))
PX = 10                                   # px por metro
OX, OY = 40, 150                          # origen del terreno en el lienzo
W, H = 2000, 1414                         # A3 apaisado (√2)
INK, MUTED, RULE, PAPER, BG = '#14202b', '#5b6876', '#c9d2dc', '#ffffff', '#f6f8fa'
ACC, ACC_S = '#1f4e79', '#e4edf6'
FD = "Archivo, 'Arial Narrow', Arial, sans-serif"
FB = "'IBM Plex Sans', 'Segoe UI', Arial, sans-serif"
FM = "'IBM Plex Mono', Consolas, monospace"
# colores por zona (los mismos tonos de las secciones del modelo de Tecnomatix)
Z = {'recepcion': ('#e8ecf4', '#5a6987'), 'prep': ('#e2f0ec', '#2d7d69'), 'ferm': ('#fcece1', '#c86928'),
     'acond': ('#eee8f8', '#7355a5'), 'envasado': ('#fce4ec', '#c33c64'), 'fin': ('#e4eef8', '#2d69a5'),
     'quesos': ('#fbf3dc', '#a37c12'), 'uht': ('#e3f2e6', '#3d8a52'), 'servicios': ('#eef0f2', '#6b7682'),
     'personal': ('#f3eef6', '#7a5f8e'), 'exterior': ('#f1f1ee', '#9a9a90'), 'frio': ('#e1f1fb', '#2b7bb0')}
S = []


def X(m):
    return OX + m * PX


def Y(m):
    return OY + m * PX


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;')


def t(x, y, s, size=12, fill=INK, w=400, fam=FB, anchor='start', extra=''):
    S.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{fill}" '
             f'text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def rect(x, y, w, h, fill, stroke, sw=1.0, rx=0, extra=''):
    S.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
             f'stroke-width="{sw}" {extra}/>')


AREAS = []


def zona(x, y, w, h, clave, nombre, sub='', num=None, area=True, etiqueta='arriba'):
    fondo, borde = Z[clave]
    rect(X(x), Y(y), w * PX, h * PX, fondo, borde, 1.2)
    if etiqueta == 'arriba':
        tx, ty = X(x) + 8, Y(y) + 18
        if num:
            S.append(f'<circle cx="{tx + 9}" cy="{ty - 5}" r="9" fill="{borde}"/>')
            t(tx + 9, ty - 1, num, 11, '#fff', 700, FD, 'middle')
            tx += 24
        size = min(12.5, (X(x + w) - tx - 6) / (0.66 * len(nombre)))
        t(tx, ty, nombre, size, borde, 800, FD)
        if sub:
            t(X(x) + 8, ty + 15, sub, 10, MUTED)
    if area:
        AREAS.append((nombre, w * h, clave))


def equipo(x, y, w, h, cod, color=INK, fill='#ffffff', size=9.5):
    rect(X(x), Y(y), w * PX, h * PX, fill, color, 1.1, 2)
    t(X(x + w / 2), Y(y + h / 2) + 3.5, cod, size, color, 600, FM, 'middle')


def tanque(cx, cy, d, cod, color=INK, size=9):
    S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{d / 2 * PX:.1f}" fill="#ffffff" stroke="{color}" stroke-width="1.3"/>')
    S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{d / 2 * PX * 0.25:.1f}" fill="none" stroke="{color}" stroke-width="0.8"/>')
    t(X(cx), Y(cy + d / 2) + 11, cod, size, color, 600, FM, 'middle')


def cota_h(x1, x2, y, s, arriba=True):
    yy = Y(y)
    S.append(f'<line x1="{X(x1)}" y1="{yy}" x2="{X(x2)}" y2="{yy}" stroke="{MUTED}" stroke-width="0.9" marker-start="url(#c)" marker-end="url(#c)"/>')
    for xx in (x1, x2):
        S.append(f'<line x1="{X(xx)}" y1="{yy - 6}" x2="{X(xx)}" y2="{yy + 6}" stroke="{MUTED}" stroke-width="0.9"/>')
    t((X(x1) + X(x2)) / 2, yy - 5 if arriba else yy + 14, s, 10.5, MUTED, 600, FM, 'middle')


def cota_v(x, y1, y2, s):
    xx = X(x)
    S.append(f'<line x1="{xx}" y1="{Y(y1)}" x2="{xx}" y2="{Y(y2)}" stroke="{MUTED}" stroke-width="0.9" marker-start="url(#c)" marker-end="url(#c)"/>')
    for yy in (y1, y2):
        S.append(f'<line x1="{xx - 6}" y1="{Y(yy)}" x2="{xx + 6}" y2="{Y(yy)}" stroke="{MUTED}" stroke-width="0.9"/>')
    t(xx - 6, (Y(y1) + Y(y2)) / 2, s, 10.5, MUTED, 600, FM, 'middle',
      f'transform="rotate(-90 {xx - 6} {(Y(y1) + Y(y2)) / 2})"')


def flujo(pts, color=ACC, w=2.2):
    S.append('<polyline points="' + ' '.join(f'{X(a):.1f},{Y(b):.1f}' for a, b in pts) +
             f'" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="8 5" marker-end="url(#f)" opacity="0.85"/>')


def puerta(x, y, ancho, vertical=False, rapida=False):
    """Vano en el muro (se pinta del color del piso) con su símbolo."""
    if vertical:
        rect(X(x) - 3, Y(y), 6, ancho * PX, PAPER, PAPER, 0)
        S.append(f'<line x1="{X(x)}" y1="{Y(y)}" x2="{X(x)}" y2="{Y(y + ancho)}" stroke="{ACC}" stroke-width="1" stroke-dasharray="3 2"/>')
    else:
        rect(X(x), Y(y) - 3, ancho * PX, 6, PAPER, PAPER, 0)
        S.append(f'<line x1="{X(x)}" y1="{Y(y)}" x2="{X(x + ancho)}" y2="{Y(y)}" stroke="{ACC}" stroke-width="1" stroke-dasharray="3 2"/>')


# ---------------- lienzo, título ----------------
S.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
rect(20, 20, W - 40, H - 40, PAPER, RULE, 1, 10)
t(48, 64, 'DISTRIBUCIÓN EN PLANTA · ESTADO ACTUAL', 12, MUTED, 600, FM, extra='letter-spacing="1.5"')
t(48, 98, 'Lácteos Altos de Teusacá · planta de 150.000 L/día', 30, INK, 800, FD)
t(48, 124, 'Yogures ≈ 57.000 L/día (detalle) · quesos 50.000 L/día · leche UHT 43.000 L/día · flujo de oeste (recepción) a este (despacho)', 13, MUTED)

# ---------------- terreno y exteriores ----------------
rect(X(0), Y(0), 150 * PX, 95 * PX, '#fbfbf8', '#9a9a90', 1.2, 0, 'stroke-dasharray="10 6"')
zona(0.5, 14, 15.5, 46, 'exterior', 'PATIO DE CISTERNAS', 'maniobra · 2 bahías', area=True)
for i in range(3):
    rect(X(2.5), Y(26 + i * 9), 12 * PX, 3 * PX, '#ffffff', '#9a9a90', 0.9, 3)          # cisternas estacionadas
    t(X(8.5), Y(27.9 + i * 9), 'cisterna 20 m³', 9, MUTED, 500, FM, 'middle')
zona(128.5, 14, 21, 46, 'exterior', 'PATIO DE DESPACHO', 'camiones refrigerados')
for i in range(3):
    rect(X(132), Y(23 + i * 9), 15 * PX, 3 * PX, '#ffffff', '#9a9a90', 0.9, 3)
    t(X(139.5), Y(24.9 + i * 9), 'camión 2–4 °C', 9, MUTED, 500, FM, 'middle')
zona(1, 1, 148, 11.5, 'servicios', 'SERVICIOS INDUSTRIALES', '', area=False)
srv = [(4, 'Subestación y planta eléctrica'), (30, 'Caldera de vapor'), (52, 'Sala de frío (NH₃) y agua helada'),
       (82, 'Compresores de aire'), (100, 'Tratamiento de agua'), (120, 'PTAR · suero y efluentes')]
for i, (x, s) in enumerate(srv):
    w = (srv[i + 1][0] if i + 1 < len(srv) else 148) - x - 2
    equipo(x, 4.5, w, 6, '', Z['servicios'][1], '#f9fafb')
    t(X(x + w / 2), Y(8.2), s, 10, Z['servicios'][1], 600, FB, 'middle')
    AREAS.append((s, w * 6, 'servicios'))
zona(18, 77, 40, 16, 'personal', 'OFICINAS Y ATENCIÓN', 'administración · ventas · sala de juntas')
zona(60, 77, 22, 16, 'personal', 'VESTIERES Y BAÑOS', 'hombres · mujeres · lavado de botas')
zona(84, 77, 16, 16, 'personal', 'COMEDOR', '')
zona(102, 77, 46, 16, 'exterior', 'PARQUEADERO', 'visitantes y personal')
rect(X(0.5), Y(77), 16 * PX, 16 * PX, '#fbfbf8', '#9a9a90', 0.9)
t(X(8.5), Y(85.5), 'PORTERÍA', 11, MUTED, 700, FD, 'middle')

# ---------------- nave de producción (110 × 60 m) ----------------
NX, NY, NW, NH = 18, 14, 110, 60
rect(X(NX), Y(NY), NW * PX, NH * PX, PAPER, INK, 3.2)

# 1 · recepción y tronco común
zona(18, 14, 26, 20, 'recepcion', 'RECEPCIÓN', 'bahías · laboratorio', num='1')
equipo(19.5, 20.5, 5, 4.5, 'U111', Z['recepcion'][1])
equipo(19.5, 26.5, 5, 4.5, 'U112', Z['recepcion'][1])
equipo(27, 20.5, 8, 6, 'LAB. CALIDAD', Z['recepcion'][1], '#ffffff', 9)
equipo(36.5, 20.5, 6, 4, 'CIP-R', Z['recepcion'][1])
tanque(30.5, 30.5, 4.4, 'U113', Z['recepcion'][1])
tanque(37.5, 30.5, 4.4, 'U114', Z['recepcion'][1])
zona(44, 14, 14, 20, 'recepcion', 'TRONCO COMÚN', 'pasteurización 20 m³/h', area=True)
equipo(45.5, 21, 4, 3, 'U121', Z['recepcion'][1])
equipo(50.5, 21, 6, 3, 'U122 HTST', Z['recepcion'][1])
equipo(45.5, 26, 4, 3, 'U126', Z['recepcion'][1])
equipo(50.5, 26, 6, 3, 'CIP-C', Z['recepcion'][1])
zona(18, 34, 40, 11, 'recepcion', 'SILOS DE LECHE PASTEURIZADA', '', area=True)
for i, (cod, d) in enumerate((('U123A', 3.6), ('U123B', 3.6), ('U123C', 3.0), ('U124', 4.0), ('U125', 3.8))):
    tanque(23 + i * 7.6, 40, d, cod, Z['recepcion'][1])

# línea de yogures: secciones 2 a 6
zona(58, 14, 12, 20, 'prep', 'PREPARACIÓN', '', num='2')
tanque(62, 24, 2.8, 'U201', Z['prep'][1])
equipo(66, 20.5, 3, 2.5, 'tolva', Z['prep'][1], size=8)
equipo(59.5, 28.5, 9, 3, 'U202 92 °C', Z['prep'][1])
zona(70, 14, 14, 20, 'ferm', 'FERMENTACIÓN', '4 × 12 m³', num='3')
for i, cod in enumerate(('U211', 'U212', 'U213', 'U218')):
    tanque(74 + (i % 2) * 6, 22.5 + (i // 2) * 6.5, 3.0, cod, Z['ferm'][1])
zona(84, 14, 13, 20, 'acond', 'ACONDICIONAM.', '', num='4')
equipo(85.5, 20.5, 3.5, 2.5, 'U215', Z['acond'][1])
equipo(85.5, 27, 3.5, 2.5, 'U216', Z['acond'][1])
tanque(92, 21.5, 2.6, 'U214A', Z['acond'][1], 8)
tanque(92, 27.5, 2.6, 'U214B', Z['acond'][1], 8)
tanque(95.3, 24.5, 1.7, 'U217', Z['acond'][1], 8)
zona(97, 14, 16, 20, 'envasado', 'ENVASADO', 'sala limpia', num='5')
for i, (cod, enc) in enumerate((('U311', 'U321'), ('U312', 'U322'), ('U313', 'U323'))):
    yy = 20.5 + i * 4.3
    equipo(98, yy, 7, 2.6, cod, Z['envasado'][1])
    equipo(106.5, yy, 5, 2.6, enc, Z['envasado'][1], size=8.5)
zona(113, 14, 15, 20, 'fin', 'PALETIZADO', '', num='6')
equipo(114.5, 20.5, 5, 5, 'U341', Z['fin'][1])
equipo(121, 20.5, 5, 5, 'U342', Z['fin'][1])
equipo(114.5, 28, 11.5, 3.5, 'zona de estibas', Z['fin'][1], '#ffffff', 8.5)

# pasillo de montacargas y peatonal
rect(X(58), Y(34), 70 * PX, 3.5 * PX, '#fff8e1', '#e0b400', 1, 0)
t(X(93), Y(36.4), 'PASILLO DE MONTACARGAS · 3,5 m', 10, '#8a6d00', 700, FM, 'middle')
AREAS.append(('Pasillos de circulación', 70 * 3.5 + 1.2 * 60, 'servicios'))

# cámara de producto terminado y muelle
zona(113, 37.5, 15, 22.5, 'frio', 'CÁMARA 2–4 °C', 'U411 · reposo ≥ 12 h', num='6')
for i in range(4):
    rect(X(114.5), Y(43 + i * 4), 12 * PX, 2.2 * PX, '#ffffff', Z['frio'][1], 0.8)
for i in range(3):
    puerta(128, 22 + i * 9, 3.2, vertical=True)
t(X(128) + 8, Y(61.5), '3 MUELLES', 9.5, ACC, 700, FM)

# quesos, leche UHT, bodegas y CIP central
zona(18, 45, 40, 29, 'quesos', 'LÍNEA DE QUESOS', '50.000 L/día · tinas, hilado, prensado, salmuera')
for i in range(3):
    equipo(21 + i * 11, 56, 9, 4, 'tina', Z['quesos'][1], '#ffffff', 8.5)
equipo(21, 63, 14, 4, 'hiladora · moldeo', Z['quesos'][1], '#ffffff', 8.5)
equipo(38, 63, 16, 8, 'salmuera · cámara quesos', Z['quesos'][1], '#ffffff', 8.5)
zona(58, 37.5, 27, 21.5, 'uht', 'LÍNEA DE LECHE UHT', '43.000 L/día · entera, descremada, chocolate')
equipo(60, 48, 9, 4, 'UHT', Z['uht'][1])
equipo(71, 48, 12, 4, 'envasadora aséptica', Z['uht'][1], '#ffffff', 8.5)
equipo(60, 53.5, 23, 3.5, 'encajonado y estiba', Z['uht'][1], '#ffffff', 8.5)
zona(58, 59, 14, 15, 'servicios', 'BODEGA DE INSUMOS', 'polvos · azúcar · cultivos')
zona(72, 59, 13, 15, 'personal', 'ESCLUSA SANITARIA', 'manos · botas · cofia')
zona(85, 37.5, 28, 14, 'servicios', 'BODEGA DE ENVASES Y FRUTA', 'vasos · botellas · preparado de fresa (≤ 8 °C)')
zona(85, 51.5, 14, 22.5, 'servicios', 'CIP CENTRAL', 'U901 · químicos')
zona(99, 51.5, 14, 22.5, 'servicios', 'MANTENIMIENTO', 'taller · repuestos')
zona(113, 60, 15, 14, 'servicios', 'SALA DE CONTROL', 'oficina de producción')

# muros interiores clave y puertas
for x1, y1, x2, y2 in ((58, 14, 58, 34), (113, 14, 113, 74), (18, 45, 58, 45), (58, 37.5, 113, 37.5)):
    S.append(f'<line x1="{X(x1)}" y1="{Y(y1)}" x2="{X(x2)}" y2="{Y(y2)}" stroke="{INK}" stroke-width="1.8"/>')
puerta(18, 20, 4, vertical=True)
puerta(18, 26, 4, vertical=True)
puerta(118, 74, 3)

# pasillo peatonal (1,2 m) de la esclusa al envasado, y puertas de la esclusa
rect(X(83.6), Y(37.5), 1.2 * PX, 21.5 * PX, '#e6f4ea', '#3d8a52', 0.8)
rect(X(83.6), Y(34), 1.2 * PX, 3.5 * PX, '#e6f4ea', '#3d8a52', 0.8)
t(X(83.2), Y(48), 'PEATONAL 1,2 m', 8.5, '#3d8a52', 700, FM, 'middle', f'transform="rotate(-90 {X(83.2)} {Y(48)})"')
puerta(74, 74, 3)
for i in range(13):                                                   # puestos de parqueo
    S.append(f'<line x1="{X(104 + i * 3.4)}" y1="{Y(84)}" x2="{X(104 + i * 3.4)}" y2="{Y(92)}" stroke="#9a9a90" stroke-width="0.8"/>')

# ---------------- flujos ----------------
flujo([(14.5, 28.5), (24.5, 28.5), (27, 33), (45, 33), (45, 25)], ACC)                      # cruda: bahías → tanques → pasteurizador
flujo([(57, 25), (57, 36), (25, 36)], ACC)                                                    # pasteurizada → silos
flujo([(26, 39), (58.5, 33), (112, 33), (120.5, 33), (120.5, 38.5)], '#c33c64', 2.6)             # yogur: silos → línea → cámara
flujo([(127, 44), (131, 44)], '#c33c64', 2.6)                                                 # cámara → muelles
flujo([(46.8, 42.5), (40, 52)], Z['quesos'][1], 2)
flujo([(54.4, 42.5), (61, 47)], Z['uht'][1], 2)

# ---------------- cotas, norte y escala ----------------
cota_h(NX, NX + NW, 75.6, '110,0 m')
cota_v(17, NY, NY + NH, '60,0 m')
cota_h(0, 150, 96.8, '150,0 m (terreno)', arriba=False)
cota_h(97, 113, 13.2, '16 m')
cota_h(70, 84, 13.2, '14 m')
nx, ny = X(146), Y(-6)
S.append(f'<polygon points="{nx},{ny - 18} {nx - 8},{ny + 8} {nx},{ny + 2} {nx + 8},{ny + 8}" fill="{INK}"/>')
t(nx, ny - 24, 'N', 13, INK, 800, FD, 'middle')
for i in range(3):
    rect(X(0) + i * 100, Y(99.5), 100, 7, INK if i % 2 == 0 else PAPER, INK, 1)
for i, s in enumerate(('0', '10', '20', '30 m')):
    t(X(0) + i * 100, Y(99.5) + 22, s, 10, MUTED, 600, FM, 'middle')

# ---------------- columna derecha: leyenda, áreas y rótulo ----------------
CX = 1575
t(CX, 175, 'Convenciones', 15, ACC, 800, FD)
ley = [('#c33c64', 'Flujo del yogur (de la leche cruda al despacho)', True), (ACC, 'Flujo de leche cruda y pasteurizada', True),
       (Z['quesos'][1], 'Leche hacia quesos', True), (Z['uht'][1], 'Leche hacia leche UHT', True)]
for i, (c, s, _) in enumerate(ley):
    y = 200 + i * 22
    S.append(f'<line x1="{CX}" y1="{y}" x2="{CX + 34}" y2="{y}" stroke="{c}" stroke-width="2.4" stroke-dasharray="8 5"/>')
    t(CX + 44, y + 4, s, 11)
y = 200 + 4 * 22
S.append(f'<circle cx="{CX + 17}" cy="{y}" r="8" fill="#fff" stroke="{INK}"/>')
t(CX + 44, y + 4, 'Tanque o silo (código ISA-88)', 11)
rect(CX + 5, y + 14, 24, 12, '#fff', INK, 1, 2)
t(CX + 44, y + 24, 'Equipo de proceso', 11)
rect(CX + 5, y + 36, 24, 10, '#fff8e1', '#e0b400', 1)
t(CX + 44, y + 45, 'Pasillo de montacargas', 11)
S.append(f'<circle cx="{CX + 17}" cy="{y + 64}" r="9" fill="{Z["ferm"][1]}"/>')
t(CX + 17, y + 68, '3', 11, '#fff', 700, FD, 'middle')
t(CX + 44, y + 68, 'Sección de la línea (igual que en Tecnomatix)', 11)

y0 = y + 104
t(CX, y0, 'Cuadro de áreas', 15, ACC, 800, FD)
grupos = {}
for nombre, a, clave in AREAS:
    g = {'recepcion': 'Recepción, tronco común y silos', 'prep': 'Línea de yogures', 'ferm': 'Línea de yogures',
         'acond': 'Línea de yogures', 'envasado': 'Línea de yogures', 'fin': 'Línea de yogures', 'frio': 'Cámara de producto terminado',
         'quesos': 'Línea de quesos', 'uht': 'Línea de leche UHT', 'servicios': 'Bodegas, CIP, mantenimiento y servicios',
         'personal': 'Personal, oficinas y esclusa', 'exterior': 'Patios, parqueadero y maniobra'}[clave]
    grupos[g] = grupos.get(g, 0) + a
orden = ['Recepción, tronco común y silos', 'Línea de yogures', 'Línea de quesos', 'Línea de leche UHT', 'Cámara de producto terminado',
         'Bodegas, CIP, mantenimiento y servicios', 'Personal, oficinas y esclusa', 'Patios, parqueadero y maniobra']
for i, g in enumerate(orden):
    yy = y0 + 26 + i * 21
    t(CX, yy, g, 11)
    t(CX + 370, yy, f'{grupos[g]:,.0f} m²'.replace(',', '.'), 11, INK, 600, FM, 'end')
    S.append(f'<line x1="{CX}" y1="{yy + 7}" x2="{CX + 370}" y2="{yy + 7}" stroke="{RULE}" stroke-width="0.8"/>')
yy = y0 + 26 + len(orden) * 21 + 6
t(CX, yy, 'Nave de producción', 11.5, INK, 700)
t(CX + 370, yy, f'{NW * NH:,.0f} m²'.replace(',', '.'), 11.5, INK, 700, FM, 'end')
t(CX, yy + 21, 'Terreno', 11.5, INK, 700)
t(CX + 370, yy + 21, f'{150 * 95:,.0f} m²'.replace(',', '.'), 11.5, INK, 700, FM, 'end')

yN = yy + 56
t(CX, yN, 'Criterios', 15, ACC, 800, FD)
crit = ['Flujo en línea de oeste a este: lo crudo y lo', 'terminado no se cruzan (BPM, Res. 2674/2013).',
        'Envasado en sala limpia, con acceso solo por', 'la esclusa sanitaria.',
        'Fermentación junto a envasado para acortar', 'tuberías de producto.',
        'Cámara junto a los muelles: el despacho no', 'atraviesa producción.',
        'Servicios al norte, fuera de la nave.',
        'Medidas propuestas por Mekvra: se ajustan', 'cuando haya plano del terreno.']
for i, s in enumerate(crit):
    t(CX, yN + 22 + i * 17, s, 11, INK if not s.startswith('Medidas') and i < 9 else MUTED)

rect(CX - 10, 1200, 395, 172, BG, RULE, 1, 6)
t(CX + 6, 1226, 'PROYECTO', 10, MUTED, 600, FM)
t(CX + 6, 1246, 'Proyecto integrador APM 2026-2S · UNAL', 12.5, INK, 700)
t(CX + 6, 1272, 'PLANO', 10, MUTED, 600, FM)
t(CX + 6, 1292, 'Distribución en planta · estado actual', 12.5, INK, 700)
t(CX + 6, 1318, 'ESCALA', 10, MUTED, 600, FM)
t(CX + 6, 1338, '1:500 en A3 · metros', 12.5, INK, 700)
t(CX + 230, 1318, 'FECHA', 10, MUTED, 600, FM)
t(CX + 230, 1338, '10-oct-2026', 12.5, INK, 700)
t(CX + 6, 1362, 'Mekvra · líder de instrumentación y software', 10.5, MUTED)

defs = ('<defs><marker id="f" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
        '<path d="M0,1 L9,5 L0,9 z" fill="context-stroke"/></marker>'
        f'<marker id="c" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M1,1 L7,7" stroke="{MUTED}" stroke-width="1.2"/></marker></defs>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(S) + '</svg>'
open(os.path.join(D, 'layout_planta_actual.svg'), 'w', encoding='utf-8').write(svg)
html = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Layout planta</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
        f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:{BG}}}svg{{display:block}}</style></head><body>{svg}</body></html>')
open(os.path.join(D, 'layout_planta_actual.html'), 'w', encoding='utf-8').write(html)
print('ok', {g: round(v) for g, v in grupos.items()})
