# Layout de detalle de la LÍNEA DE YOGURES (planta actual, paletizado manual) y sus diagramas de espagueti, actual y
# propuesto. Misma geometría que layout_planta.py (nave de 110 × 60 m). El espagueti dibuja las rutas que se repiten cada
# día (personas, montacargas e insumos) con su número de viajes, y suma los metros recorridos.
# Los viajes por día son estimaciones de diseño a partir de la producción simulada en Tecnomatix (≈ 57.600 L/día).
# Genera layout_linea_yogures_actual, espagueti_linea_yogures_actual y espagueti_linea_yogures_propuesto (.svg y .html).
import os, math

D = os.path.dirname(os.path.abspath(__file__))
PX, OX, OY = 13, 50 - 18 * 13, 180 - 12 * 13          # 1 m = 13 px; la nave empieza en x = 18 m
W, H = 2000, 1414
INK, MUTED, RULE, PAPER, BG = '#14202b', '#5b6876', '#c9d2dc', '#ffffff', '#f6f8fa'
ACC, ACC_S, PCC, OK = '#1f4e79', '#e4edf6', '#b4441b', '#2e7d4f'
FD = "Archivo, 'Arial Narrow', Arial, sans-serif"
FB = "'IBM Plex Sans', 'Segoe UI', Arial, sans-serif"
FM = "'IBM Plex Mono', Consolas, monospace"
Z = {'recepcion': ('#e8ecf4', '#5a6987'), 'prep': ('#e2f0ec', '#2d7d69'), 'ferm': ('#fcece1', '#c86928'),
     'acond': ('#eee8f8', '#7355a5'), 'envasado': ('#fce4ec', '#c33c64'), 'fin': ('#e4eef8', '#2d69a5'),
     'frio': ('#e1f1fb', '#2b7bb0'), 'serv': ('#eef0f2', '#6b7682'), 'pers': ('#f3eef6', '#7a5f8e'), 'otra': ('#f4f4f1', '#a3a39a')}


def X(m):
    return OX + m * PX


def Y(m):
    return OY + m * PX


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;')


class Hoja:
    def __init__(self):
        self.S = []

    def t(self, x, y, s, size=12, fill=INK, w=400, fam=FB, anchor='start', extra=''):
        self.S.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{fill}" '
                      f'text-anchor="{anchor}" {extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke, sw=1.0, rx=0, extra=''):
        self.S.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def zona(self, x, y, w, h, clave, nombre, sub=''):
        f, b = Z[clave]
        self.rect(X(x), Y(y), w * PX, h * PX, f, b, 1.2)
        self.t(X(x) + 8, Y(y) + 18, nombre, min(13, (w * PX - 12) / (0.66 * len(nombre))), b, 800, FD)
        if sub:
            self.t(X(x) + 8, Y(y) + 33, sub, 10, MUTED)

    def equipo(self, x, y, w, h, cod, color, size=10):
        self.rect(X(x), Y(y), w * PX, h * PX, '#ffffff', color, 1.2, 2)
        self.t(X(x + w / 2), Y(y + h / 2) + 3.5, cod, size, color, 600, FM, 'middle')

    def tanque(self, cx, cy, d, cod, color):
        self.S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{d / 2 * PX:.1f}" fill="#fff" stroke="{color}" stroke-width="1.3"/>')
        self.t(X(cx), Y(cy + d / 2) + 12, cod, 9.5, color, 600, FM, 'middle')

    def persona(self, cx, cy, color=INK):
        self.S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="5" fill="{color}"/>'
                      f'<path d="M{X(cx) - 7:.1f},{Y(cy) + 13:.1f} Q{X(cx):.1f},{Y(cy) + 2:.1f} {X(cx) + 7:.1f},{Y(cy) + 13:.1f}" fill="{color}"/>')

    def svg(self, nombre, titulo):
        defs = '<defs><marker id="f" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,1 L8,4.5 L0,8 z" fill="context-stroke"/></marker></defs>'
        s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(self.S) + '</svg>'
        open(os.path.join(D, nombre + '.svg'), 'w', encoding='utf-8').write(s)
        html = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
                f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:{BG}}}svg{{display:block}}</style></head><body>{s}</body></html>')
        open(os.path.join(D, nombre + '.html'), 'w', encoding='utf-8').write(html)


def base(h, kicker, titulo, sub, robot=False, ffs=False):
    h.S.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    h.rect(20, 20, W - 40, H - 40, PAPER, RULE, 1, 10)
    h.t(48, 64, kicker, 12, MUTED, 600, FM, extra='letter-spacing="1.5"')
    h.t(48, 98, titulo, 30, INK, 800, FD)
    h.t(48, 124, sub, 13, MUTED)
    h.t(W - 48, 64, 'Mekvra · APM 2026-2S · UNAL', 12, MUTED, 600, FM, 'end')
    # nave y zonas de la línea de yogures (las demás líneas en gris)
    h.rect(X(18), Y(14), 110 * PX, 60 * PX, PAPER, INK, 3)
    h.zona(18, 14, 26, 20, 'recepcion', '1 RECEPCIÓN', 'bahías · laboratorio de calidad')
    h.equipo(19.5, 20.5, 5, 4.5, 'U111', Z['recepcion'][1]); h.equipo(19.5, 26.5, 5, 4.5, 'U112', Z['recepcion'][1])
    h.equipo(27, 20.5, 8, 6, 'LAB.', Z['recepcion'][1])
    h.tanque(30.5, 30.5, 4.4, 'U113', Z['recepcion'][1]); h.tanque(37.5, 30.5, 4.4, 'U114', Z['recepcion'][1])
    h.zona(44, 14, 14, 20, 'recepcion', 'TRONCO COMÚN', 'pasteurización')
    h.equipo(45.5, 21, 4, 3, 'U121', Z['recepcion'][1]); h.equipo(50.5, 21, 6, 3, 'U122', Z['recepcion'][1])
    h.zona(18, 34, 40, 11, 'recepcion', 'SILOS', '')
    for i, c in enumerate(('U123A', 'U123B', 'U123C', 'U124', 'U125')):
        h.tanque(23 + i * 7.6, 40, 3.6, c, Z['recepcion'][1])
    h.zona(58, 14, 12, 20, 'prep', '2 PREPARACIÓN')
    h.tanque(62, 24, 2.8, 'U201', Z['prep'][1]); h.equipo(66, 20.5, 3, 2.5, 'tolva', Z['prep'][1], 8)
    h.equipo(59.5, 28.5, 9, 3, 'U202', Z['prep'][1])
    h.zona(70, 14, 14, 20, 'ferm', '3 FERMENTACIÓN')
    for i, c in enumerate(('U211', 'U212', 'U213', 'U218')):
        h.tanque(74 + (i % 2) * 6, 22.5 + (i // 2) * 6.5, 3.0, c, Z['ferm'][1])
    h.zona(84, 14, 13, 20, 'acond', '4 ACONDICIONAM.')
    h.equipo(85.5, 20.5, 3.5, 2.5, 'U215', Z['acond'][1]); h.equipo(85.5, 27, 3.5, 2.5, 'U216', Z['acond'][1])
    h.tanque(92, 21.5, 2.6, 'U214A', Z['acond'][1]); h.tanque(92, 27.5, 2.6, 'U214B', Z['acond'][1]); h.tanque(95.3, 24.5, 1.7, 'U217', Z['acond'][1])
    h.zona(97, 14, 16, 20, 'envasado', '5 ENVASADO', 'sala limpia')
    for i, (c, e) in enumerate((('U311 FFS' if ffs else 'U311', 'U321'), ('U312', 'U322'), ('U313', 'U323'))):
        h.equipo(98, 20.5 + i * 4.3, 7, 2.6, c, Z['envasado'][1], 9 if ffs and i == 0 else 10)
        h.equipo(106.5, 20.5 + i * 4.3, 5, 2.6, e, Z['envasado'][1], 9)
    h.zona(113, 14, 15, 20, 'fin', '6 PALETIZADO')
    h.equipo(114.5, 20.5, 5, 5, 'U341 robot' if robot else 'U341', Z['fin'][1], 9)
    h.equipo(121, 20.5, 5, 5, 'U342', Z['fin'][1])
    h.equipo(114.5, 28, 11.5, 3.5, 'estibas', Z['fin'][1], 9)
    if not robot:
        h.persona(116, 27); h.persona(118.5, 27)
    h.rect(X(58), Y(34), 70 * PX, 3.5 * PX, '#fff8e1', '#e0b400', 1)
    h.t(X(93), Y(36.4), 'PASILLO DE MONTACARGAS · 3,5 m', 10, '#8a6d00', 700, FM, 'middle')
    h.zona(113, 37.5, 15, 22.5, 'frio', 'CÁMARA 2–4 °C', 'U411')
    h.zona(85, 37.5, 28, 14, 'serv', 'BODEGA DE ENVASES Y FRUTA', 'bobinas de la FFS · botellas · fruta' if ffs else 'vasos · botellas · fruta (≤ 8 °C)')
    h.zona(58, 59, 14, 15, 'serv', 'BODEGA DE INSUMOS', 'polvos · azúcar')
    h.zona(72, 59, 13, 15, 'pers', 'ESCLUSA', 'sanitaria')
    h.zona(113, 60, 15, 14, 'serv', 'SALA DE CONTROL', 'MES y SCADA' if robot else 'registros en papel')
    h.zona(18, 45, 40, 29, 'otra', 'LÍNEA DE QUESOS', '(otra línea)')
    h.zona(58, 37.5, 27, 21.5, 'otra', 'LÍNEA DE LECHE UHT', '(otra línea)')
    h.zona(85, 51.5, 14, 22.5, 'otra', 'CIP CENTRAL')
    h.zona(99, 51.5, 14, 22.5, 'otra', 'MANTENIMIENTO')
    h.rect(X(83.6), Y(37.5), 1.2 * PX, 21.5 * PX, '#e6f4ea', '#3d8a52', 0.8)
    for i in range(3):                                                # muelles
        h.rect(X(128) - 3, Y(22 + i * 9), 6, 3.2 * PX, '#fff', ACC, 1)
    h.t(X(128) + 8, Y(19.5), 'MUELLES', 10, ACC, 700, FM)
    # escala y norte
    for i in range(3):
        h.rect(X(18) + i * 10 * PX, Y(76), 10 * PX, 7, INK if i % 2 == 0 else PAPER, INK, 1)
    for i, s in enumerate(('0', '10', '20', '30 m')):
        h.t(X(18) + i * 10 * PX, Y(76) + 22, s, 10, MUTED, 600, FM, 'middle')
    nx, ny = X(126), Y(77.5)
    h.S.append(f'<polygon points="{nx},{ny - 18} {nx - 8},{ny + 8} {nx},{ny + 2} {nx + 8},{ny + 8}" fill="{INK}"/>')
    h.t(nx, ny - 24, 'N', 13, INK, 800, FD, 'middle')


def largo(p):
    return sum(math.dist(a, b) for a, b in zip(p, p[1:]))


# rutas que se repiten cada día (coordenadas en m sobre la nave; pasillo de montacargas en y = 35,75)
P = 35.75
RUTAS = {
    'envases': ('Envases a las llenadoras', '#c33c64', [(99, 44), (99, P), (102, P), (102, 33.2)]),
    'insumos': ('Leche en polvo y azúcar a U201', '#2d7d69', [(65, 62), (65, 59.5), (84.2, 59.5), (84.2, P), (66.5, P), (66.5, 23.2)]),
    'fruta': ('Preparado de fruta al dosificador', '#b8325a', [(94, 44), (94, P), (96, P), (96, 23)]),
    'calidad': ('Analista: muestras de pH y llenado', '#7355a5', [(31, 26.5), (31, 33.4), (44, 33.4), (44, P), (77, P), (77, 26), (77, P), (101, P), (101, 33)]),
    'montacargas': ('Montacargas: estibas a la cámara', '#e0a800', [(117, 31.5), (117, P), (120, P), (120, 42)]),
    'despacho': ('Montacargas: cámara a los muelles', '#2d69a5', [(124, 46), (127, 46), (127, 31)]),
    'supervisor': ('Supervisor: rondas con registros', '#5b6876', [(116, 61), (112.3, 61), (112.3, P), (60, P), (60, 33.5)]),
}
# viajes de ida por día (estimación de diseño)
ACTUAL = {'envases': 50, 'insumos': 12, 'fruta': 4, 'calidad': 60, 'montacargas': 95, 'despacho': 95, 'supervisor': 9}
PROPUESTO = {'envases': 29, 'insumos': 12, 'fruta': 4, 'calidad': 12, 'montacargas': 95, 'despacho': 95, 'supervisor': 3}
NOTAS_VIAJES = {'envases': ('vasos, botellas y potes preformados', 'bobinas de la FFS, botellas y potes'),
                'insumos': ('≈ 2 estibas por lote', 'igual'),
                'fruta': ('canecas de 1.000 kg', 'igual'),
                'calidad': ('≈ 6 muestras por lote + revisión horaria', 'pH en línea en el MES; solo verificación'),
                'montacargas': ('≈ 95 estibas por día', 'igual'),
                'despacho': ('≈ 95 estibas por día', 'igual'),
                'supervisor': ('3 rondas por turno con planillas', '1 ronda por turno; datos en el MES')}
CAJAS = 11_600                                                       # cajas que los 2 operarios estiban a mano por día


def espagueti(h, viajes, propuesto):
    tot = 0
    filas = []
    for k, (nom, c, pts) in RUTAS.items():
        n = viajes[k]
        m_dia = largo(pts) * 2 * n
        tot += m_dia
        filas.append((nom, c, n, largo(pts), m_dia, NOTAS_VIAJES[k][1 if propuesto else 0]))
        capas = max(1, min(7, round(n / 12)))
        for j in range(capas):                                         # varias pasadas desplazadas = efecto espagueti
            d = (j - (capas - 1) / 2) * 0.28
            q = [(x + d, y + d) for x, y in pts]
            h.S.append('<polyline points="' + ' '.join(f'{X(a):.1f},{Y(b):.1f}' for a, b in q) +
                       f'" fill="none" stroke="{c}" stroke-width="1.6" stroke-opacity="0.75" stroke-linejoin="round"' +
                       (' marker-end="url(#f)"' if j == capas - 1 else '') + '/>')
    if not propuesto:                                                 # paletizado manual: lazos cortos de los 2 operarios
        for j in range(14):
            a = j * 0.9
            x0, y0 = 116.5 + 1.6 * math.cos(a), 26.6 + 1.0 * math.sin(a)
            h.S.append(f'<path d="M{X(115.5):.1f},{Y(25.8):.1f} Q{X(x0):.1f},{Y(y0 + 1.2):.1f} {X(117 + (j % 4) * 1.6):.1f},{Y(29.6):.1f}" '
                       f'fill="none" stroke="{PCC}" stroke-width="1.4" stroke-opacity="0.7"/>')
    return filas, tot


def tabla(h, filas, tot, x0, y0, propuesto, tot_ref=None):
    h.t(x0, y0, 'Recorridos que se repiten cada día', 15, ACC, 800, FD)
    cab = [('Ruta', 0), ('Viajes', 250), ('m/viaje', 330), ('m/día', 410)]
    for s, dx in cab:
        h.t(x0 + dx, y0 + 26, s, 10.5, MUTED, 600, FM, 'end' if dx else 'start')
    for i, (nom, c, n, l, md, nota) in enumerate(filas):
        y = y0 + 48 + i * 36
        h.S.append(f'<line x1="{x0}" y1="{y - 5}" x2="{x0 + 18}" y2="{y - 5}" stroke="{c}" stroke-width="3"/>')
        h.t(x0 + 24, y, nom, 11)
        h.t(x0 + 24, y + 14, nota, 9.5, MUTED)
        h.t(x0 + 250, y, f'{n}', 11, INK, 600, FM, 'end')
        h.t(x0 + 330, y, f'{l:.0f}', 11, INK, 600, FM, 'end')
        h.t(x0 + 410, y, f'{md:,.0f}'.replace(',', '.'), 11, INK, 600, FM, 'end')
    y = y0 + 48 + len(filas) * 36
    h.S.append(f'<line x1="{x0}" y1="{y - 12}" x2="{x0 + 410}" y2="{y - 12}" stroke="{INK}" stroke-width="1"/>')
    h.t(x0, y + 6, 'Total por día (ida y vuelta)', 12, INK, 700)
    h.t(x0 + 410, y + 6, f'{tot / 1000:.1f} km'.replace('.', ','), 14, INK, 800, FD, 'end')
    if tot_ref:
        h.t(x0, y + 30, f'≈ {(1 - tot / tot_ref) * 100:.0f} % menos que hoy'.replace('.', ','), 14, OK, 800, FD)
    if not propuesto:
        h.t(x0, y + 30, f'+ ≈ {CAJAS:,} cajas estibadas a mano'.replace(',', '.'), 13, PCC, 800, FD)
        h.t(x0, y + 48, '(2 operarios por turno, ≈ 6 m por caja)', 10.5, MUTED)
    return y + 60


# ---------------- 1 · layout de detalle de la línea ----------------
h = Hoja()
base(h, 'DISTRIBUCIÓN EN PLANTA · LÍNEA DE YOGURES · ESTADO ACTUAL', 'Línea de yogures · paletizado manual',
     'Planta de 150.000 L/día · la línea de yogures en color y las demás áreas en gris · 2 operarios estiban las cajas en U341 · medidas en m')
CX = 1545
h.t(CX, 200, 'Cómo está organizada', 15, ACC, 800, FD)
txt = ['El producto avanza de oeste a este en 6 secciones,', 'las mismas del modelo de Tecnomatix.', '',
       'Fin de línea manual: las encajonadoras', 'entregan cajas a una mesa y 2 operarios', 'por turno las estiban en U341.', '',
       'Los insumos llegan desde dos bodegas al sur:', 'cruzan la zona de leche UHT por el pasillo', 'peatonal y el de montacargas.', '',
       'El analista de calidad sale del laboratorio', 'de recepción hasta fermentación y envasado', 'para tomar muestras de pH.']
for i, s in enumerate(txt):
    h.t(CX, 228 + i * 18, s, 11.5)
h.t(CX, 520, 'Áreas de la línea', 15, ACC, 800, FD)
areas = [('Preparación', 12 * 20), ('Fermentación', 14 * 20), ('Acondicionamiento', 13 * 20), ('Envasado', 16 * 20), ('Paletizado', 15 * 20),
         ('Cámara 2–4 °C', 15 * 22.5), ('Bodega de envases y fruta', 28 * 14), ('Bodega de insumos', 14 * 15)]
for i, (n, a) in enumerate(areas):
    h.t(CX, 548 + i * 20, n, 11.5); h.t(CX + 330, 548 + i * 20, f'{a:,.0f} m²'.replace(',', '.'), 11.5, INK, 600, FM, 'end')
h.svg('layout_linea_yogures_actual', 'Layout línea de yogures')

# ---------------- 2 · espagueti actual ----------------
h = Hoja()
base(h, 'DIAGRAMA DE ESPAGUETI · ESTADO ACTUAL', 'Recorridos de la línea de yogures hoy',
     'Cada línea es una ruta que se repite durante el día: más líneas, más viajes. Viajes estimados para ≈ 57.600 L/día de leche a yogures.')
filas, tot_act = espagueti(h, ACTUAL, False)
tabla(h, filas, tot_act, 1545, 200, False)
h.svg('espagueti_linea_yogures_actual', 'Espagueti actual')

# ---------------- 3 · espagueti propuesto ----------------
h = Hoja()
base(h, 'DIAGRAMA DE ESPAGUETI · PROPUESTA DE AUTOMATIZACIÓN', 'Recorridos de la línea de yogures con la propuesta',
     'Celda robotizada en U341, llenadora FFS que forma el vaso desde bobina, pH en línea y registro en el MES. Mismas 6 secciones.', robot=True, ffs=True)
filas, tot_pro = espagueti(h, PROPUESTO, True)
y = tabla(h, filas, tot_pro, 1545, 200, True, tot_act)
h.t(1545, y + 20, 'Qué cambia', 15, ACC, 800, FD)
for i, s in enumerate(['Robot en U341: ya nadie estiba cajas a mano.', 'FFS: las bobinas reemplazan los vasos', 'preformados (menos viajes a la bodega).',
                       'pH en línea en el MES: el analista solo', 'verifica, no sale por cada muestra.', 'MES: el supervisor deja las planillas.']):
    h.t(1545, y + 46 + i * 18, s, 11.5)
yb = 1110                                                            # comparación hoy frente a la propuesta
h.t(50, yb, 'Metros recorridos por día', 15, ACC, 800, FD)
for i, (lab, v, c) in enumerate((('Hoy', tot_act, PCC), ('Con la propuesta', tot_pro, OK))):
    y = yb + 28 + i * 44
    h.t(50, y + 18, lab, 12.5, INK, 600)
    h.rect(230, y, 1200 * v / tot_act, 26, c, c, 0, 4, 'fill-opacity="0.85"')
    h.t(240 + 1200 * v / tot_act, y + 19, f'{v / 1000:.1f} km'.replace('.', ','), 14, c, 800, FD)
h.t(50, yb + 132, f'Además, los 2 operarios de paletizado dejan de estibar ≈ {CAJAS:,} cajas a mano por día: el robot U341 las toma de las bandas.'.replace(',', '.'), 12.5, INK)
h.svg('espagueti_linea_yogures_propuesto', 'Espagueti propuesto')
print('ok', round(tot_act), round(tot_pro))
