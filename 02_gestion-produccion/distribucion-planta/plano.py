# Planos de distribución en planta de Lácteos Altos de Teusacá (planta de 150.000 L/día, acta del 9-oct-2026) en estilo de
# plano arquitectónico: solo el edificio de producción (nave de 110 × 60 m), muros con espesor, puertas y portones, ejes,
# cotas, equipos a escala sobre piso blanco (lo blanco es espacio libre), pasillos marcados y un cuadro de áreas libres.
# Las medidas son una propuesta de Mekvra: no hay plano del terreno.
#
# Genera (svg + html; PNG y PDF con ../vsm/exportar.mjs, 2000 × 1414):
#   layout_planta_3_lineas            · planta con las tres líneas en color
#   layout_linea_yogures_actual       · la línea de yogures en color y lo demás en gris (paletizado manual)
#   espagueti_linea_yogures_actual    · recorridos diarios sobre el plano, hoy
#   espagueti_linea_yogures_propuesto · recorridos con la propuesta de automatización
import os, math

D = os.path.dirname(os.path.abspath(__file__))
W, H = 2000, 1414
PX, OX, OY = 12.6, 118, 262                       # 1 m = 13,4 px · origen de la nave en el lienzo
NW, NH = 110, 60
INK, MUTED, RULE, PAPER, BG = '#14202b', '#5b6876', '#c9d2dc', '#ffffff', '#f6f8fa'
ACC, PCC, OK, AMAR = '#1f4e79', '#b4441b', '#2e7d4f', '#d9a400'
FD = "Archivo, 'Arial Narrow', Arial, sans-serif"
FB = "'IBM Plex Sans', 'Segoe UI', Arial, sans-serif"
FM = "'IBM Plex Mono', Consolas, monospace"
LINEA = {'tronco': '#5a6987', 'yogur': '#c33c64', 'queso': '#a37c12', 'uht': '#3d8a52', 'serv': '#6b7682', 'frio': '#2b7bb0'}
GRIS = '#9aa3ad'


def X(m):
    return OX + m * PX


def Y(m):
    return OY + m * PX


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;')


def tinte(hexc, a=0.13):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % tuple(round(255 - (255 - c) * a) for c in (r, g, b))


# ---------------- geometría (metros, origen en la esquina noroeste de la nave) ----------------
# recintos: nombre, x0, y0, x1, y1, posición de la etiqueta (x, y)
RECINTOS = [
    ('RECEPCIÓN', 0, 0, 26, 20, (8, 2.4)), ('TRONCO COMÚN', 26, 0, 40, 20, (33, 2.4)),
    ('SILOS', 0, 20, 40, 31, (36.5, 22.4)),
    ('PREPARACIÓN', 40, 0, 52, 20, (46, 2.4)), ('FERMENTACIÓN', 52, 0, 66, 20, (59, 2.4)),
    ('ACONDICIONAMIENTO', 66, 0, 79, 20, (72.5, 2.4)), ('ENVASADO · SALA LIMPIA', 79, 0, 95, 20, (87, 2.4)),
    ('PALETIZADO', 95, 0, 110, 20, (102.5, 2.4)),
    ('LÍNEA DE QUESOS', 0, 31, 40, 52.5, (20, 33.4)), ('CÁMARA DE QUESOS', 0, 52.5, 40, 60, (32, 54.6)),
    ('LÍNEA DE LECHE UHT', 40, 23.5, 67, 45, (53.5, 25.9)),
    ('BODEGA DE ENVASES Y FRUTA', 67, 23.5, 95, 37.5, (81, 25.9)), ('CÁMARA 2–4 °C', 95, 23.5, 110, 46, (102.5, 25.9)),
    ('BODEGA DE INSUMOS', 40, 45, 54, 60, (47, 47.4)), ('ESCLUSA SANITARIA', 54, 45, 67, 60, (60.5, 47.4)),
    ('CIP CENTRAL', 67, 37.5, 81, 60, (74, 39.9)), ('MANTENIMIENTO', 81, 37.5, 95, 60, (88, 39.9)),
    ('SALA DE CONTROL', 95, 46, 110, 60, (102.5, 48.4)),
]
PASILLO = (40, 20, 110, 23.5)                       # pasillo de montacargas, 3,5 m
PEATONAL = (65.6, 23.5, 66.8, 45)                   # pasillo peatonal de 1,2 m desde la esclusa

# equipos: (código, línea, forma, datos) · rect: x, y, w, h · circ: cx, cy, diámetro · rack: x, y, w, h (estantería)
EQ = [
    ('U111', 'tronco', 'rect', (1.5, 6.5, 5, 4.5)), ('U112', 'tronco', 'rect', (1.5, 12.5, 5, 4.5)),
    ('LAB', 'tronco', 'rect', (9, 6.5, 8, 6)), ('CIP-R', 'tronco', 'rect', (18.5, 6.5, 6, 4)),
    ('U113', 'tronco', 'circ', (12.5, 16.3, 4.4)), ('U114', 'tronco', 'circ', (19.5, 16.3, 4.4)),
    ('U121', 'tronco', 'rect', (27.5, 7, 4, 3)), ('U122', 'tronco', 'rect', (32.5, 7, 6, 3)),
    ('U126', 'tronco', 'rect', (27.5, 12, 4, 3)), ('CIP-C', 'tronco', 'rect', (32.5, 12, 6, 3)),
    ('U123A', 'yogur', 'circ', (5, 26, 3.6)), ('U123B', 'yogur', 'circ', (12.6, 26, 3.6)), ('U123C', 'yogur', 'circ', (20.2, 26, 3.0)),
    ('U124', 'queso', 'circ', (27.8, 26, 4.0)), ('U125', 'uht', 'circ', (35.4, 26, 3.8)),
    ('U201', 'yogur', 'circ', (44, 10, 2.8)), ('tolva', 'yogur', 'rect', (48, 6.5, 3, 2.5)), ('U202', 'yogur', 'rect', (41.5, 14.5, 9, 3)),
    ('U211', 'yogur', 'circ', (56, 8.5, 3.0)), ('U212', 'yogur', 'circ', (62, 8.5, 3.0)),
    ('U213', 'yogur', 'circ', (56, 15, 3.0)), ('U218', 'yogur', 'circ', (62, 15, 3.0)),
    ('U215', 'yogur', 'rect', (67.5, 6.5, 3.5, 2.5)), ('U216', 'yogur', 'rect', (67.5, 13, 3.5, 2.5)),
    ('U214A', 'yogur', 'circ', (74, 7.5, 2.6)), ('U214B', 'yogur', 'circ', (74, 13.5, 2.6)), ('U217', 'yogur', 'circ', (77.2, 10.5, 1.7)),
    ('U311', 'yogur', 'rect', (80, 6.5, 7, 2.6)), ('U321', 'yogur', 'rect', (88.5, 6.5, 5, 2.6)),
    ('U312', 'yogur', 'rect', (80, 10.8, 7, 2.6)), ('U322', 'yogur', 'rect', (88.5, 10.8, 5, 2.6)),
    ('U313', 'yogur', 'rect', (80, 15.1, 7, 2.6)), ('U323', 'yogur', 'rect', (88.5, 15.1, 5, 2.6)),
    ('U341', 'yogur', 'rect', (96.5, 6.5, 5, 5)), ('U342', 'yogur', 'rect', (103, 6.5, 5, 5)),
    ('estibas', 'yogur', 'rect', (96.5, 14, 11.5, 3.5)),
    ('Q201', 'queso', 'rect', (2, 37.5, 6.5, 3.2)), ('Q202', 'queso', 'rect', (9.5, 37.5, 6.5, 3.2)), ('Q203', 'queso', 'rect', (17, 37.5, 6.5, 3.2)),
    ('Q301', 'queso', 'rect', (26, 37.5, 6, 3.2)), ('Q311', 'queso', 'rect', (33.5, 37.5, 5, 3.2)),
    ('Q302 salmuera', 'queso', 'rect', (2, 44.5, 22, 5)), ('Q341', 'queso', 'rect', (26, 44.5, 6, 4)),
    ('L201', 'uht', 'circ', (43.5, 31.5, 2.6)), ('L202 UHT', 'uht', 'rect', (47, 30, 6, 3)), ('L203', 'uht', 'circ', (56, 31.5, 2.6)),
    ('L311', 'uht', 'rect', (58.5, 30, 6, 3)), ('L341', 'uht', 'rect', (58.5, 36, 6, 2.5)),
]
RACKS = [  # estanterías de almacenamiento (se dibujan rayadas)
    ('frio', (97, 29, 12, 2.2)), ('frio', (97, 33.2, 12, 2.2)), ('frio', (97, 37.4, 12, 2.2)), ('frio', (97, 41.6, 12, 2.2)),
    ('queso', (2, 55.5, 26, 1.6)), ('queso', (2, 58, 26, 1.4)),
    ('uht', (41.5, 39.5, 16, 1.6)), ('uht', (41.5, 42.4, 16, 1.6)),
    ('serv', (69, 29.5, 24, 1.6)), ('serv', (69, 33, 24, 1.6)),
    ('serv', (41.5, 50, 11, 1.4)), ('serv', (41.5, 53.6, 11, 1.4)), ('serv', (41.5, 57.2, 11, 1.4)),
]
CIP_TANQUES = [(70, 44, 2.6), (74, 44, 2.6), (78, 44, 2.6)]
MANT = [(83, 42, 10, 2), (83, 50, 4, 6)]
# muros interiores (x1, y1, x2, y2) y vanos en ellos [(desde, hasta)] medidos a lo largo del muro
# vano: (desde, hasta) = puerta de personas con su giro · (desde, hasta, 'p') = portón o paso de banda, sin hoja
MUROS = [
    # solo hay muros donde la función los exige (sala limpia, frío, bodegas, esclusa, CIP, mantenimiento, sala de control);
    # recepción, tronco común, silos, preparación, fermentación, acondicionamiento, quesos y leche UHT son nave abierta
    ((40, 45, 40, 60), []), ((79, 0, 79, 20), []), ((95, 0, 95, 20), [(6.6, 8.4, 'p'), (10.9, 12.7, 'p'), (15.2, 17, 'p')]),
    ((79, 20, 95, 20), [(6, 7.5)]), ((67, 23.5, 110, 23.5), [(13, 16.5, 'p'), (34, 37.5, 'p')]),
    ((67, 23.5, 67, 45), []), ((67, 37.5, 95, 37.5), [(6, 7.5), (20, 21.5)]), ((81, 37.5, 81, 60), []),
    ((95, 23.5, 95, 60), [(25, 26.5)]), ((95, 46, 110, 46), [(3, 4.5)]), ((40, 45, 67, 45), [(8, 9.5), (24, 25.2)]),
    ((54, 45, 54, 60), [(4, 5.5)]), ((0, 52.5, 40, 52.5), [(35, 38.5, 'p')]),
]
# vanos en los muros exteriores: (lado, desde, hasta, tipo) · tipo: portón (vehículos) o puerta (personas)
VANOS = [('O', 6, 10, 'portón'), ('O', 12, 16, 'portón'), ('E', 26.5, 29.7, 'portón'), ('E', 32.5, 35.7, 'portón'),
         ('E', 38.5, 41.7, 'portón'), ('S', 56, 59, 'puerta'), ('S', 100, 101.5, 'puerta'), ('S', 30, 33.5, 'portón')]


class Hoja:
    def __init__(self):
        self.S = []

    def t(self, x, y, s, size=12, fill=INK, w=400, fam=FB, anchor='start', extra=''):
        self.S.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{fill}" '
                      f'text-anchor="{anchor}" {extra}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke, sw=1.0, rx=0, extra=''):
        self.S.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def line(self, x1, y1, x2, y2, c, sw=1.0, extra=''):
        self.S.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{sw}" {extra}/>')

    def svg(self, nombre, titulo):
        defs = (f'<defs><pattern id="muro" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<rect width="5" height="5" fill="#2a3440"/><line x1="0" y1="0" x2="0" y2="5" stroke="#55606c" stroke-width="1.6"/></pattern>'
                f'<pattern id="rack" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="6" stroke="#9aa3ad" stroke-width="1"/></pattern>'
                f'<pattern id="pasillo" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<line x1="0" y1="0" x2="0" y2="10" stroke="#f2d27a" stroke-width="2"/></pattern>'
                '<marker id="f" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,1 L8,4.5 L0,8 z" fill="context-stroke"/></marker>'
                f'<marker id="tic" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M1,7 L7,1" stroke="{MUTED}" stroke-width="1.2"/></marker></defs>')
        s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(self.S) + '</svg>'
        open(os.path.join(D, nombre + '.svg'), 'w', encoding='utf-8').write(s)
        html = (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>'
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
                f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:{BG}}}svg{{display:block}}</style></head><body>{s}</body></html>')
        open(os.path.join(D, nombre + '.html'), 'w', encoding='utf-8').write(html)


def area_equipo(forma, d):
    return d[2] * d[3] if forma == 'rect' else math.pi * (d[2] / 2) ** 2


def centro(forma, d):
    return (d[0] + d[2] / 2, d[1] + d[3] / 2) if forma == 'rect' else (d[0], d[1])


def cuadro_areas():
    """Área de cada recinto, área ocupada por equipos y estanterías, y porcentaje libre."""
    filas = []
    for nom, x0, y0, x1, y1, _ in RECINTOS:
        dentro = lambda c: x0 <= c[0] <= x1 and y0 <= c[1] <= y1
        occ = sum(area_equipo(f, d) for _, _, f, d in EQ if dentro(centro(f, d)))
        occ += sum(d[2] * d[3] for _, d in RACKS if dentro((d[0] + d[2] / 2, d[1] + d[3] / 2)))
        occ += sum(math.pi * (r / 2) ** 2 for cx, cy, r in CIP_TANQUES if dentro((cx, cy)))
        occ += sum(w * h for x, y, w, h in MANT if dentro((x + w / 2, y + h / 2)))
        a = (x1 - x0) * (y1 - y0)
        filas.append((nom, a, occ, 1 - occ / a))
    return filas


def plano(h, enfoque=None, kicker='', titulo='', sub='', etiquetas_equipo=True):
    """Dibuja el plano. enfoque = None (todas las líneas en color) o 'yogur' (solo la línea de yogures en color)."""
    h.S.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    h.rect(20, 20, W - 40, H - 40, PAPER, RULE, 1, 10)
    h.t(48, 62, kicker, 12, MUTED, 600, FM, extra='letter-spacing="1.5"')
    h.t(48, 96, titulo, 30, INK, 800, FD)
    h.t(48, 122, sub, 13, MUTED)
    h.t(W - 48, 62, 'Mekvra · APM 2026-2S · UNAL', 12, MUTED, 600, FM, 'end')
    # ejes del edificio cada 10 m (números arriba, letras a la izquierda)
    for i in range(0, NW + 1, 10):
        h.line(X(i), Y(-3.2), X(i), Y(NH + 1), '#d5dbe2', 0.8, 'stroke-dasharray="10 4 2 4"')
        h.S.append(f'<circle cx="{X(i):.1f}" cy="{Y(-4.4):.1f}" r="10" fill="#fff" stroke="{MUTED}" stroke-width="1"/>')
        h.t(X(i), Y(-4.4) + 4, str(i // 10 + 1), 10.5, MUTED, 600, FM, 'middle')
    for k, j in enumerate(range(0, NH + 1, 10)):
        h.line(X(-3.2), Y(j), X(NW + 1), Y(j), '#d5dbe2', 0.8, 'stroke-dasharray="10 4 2 4"')
        h.S.append(f'<circle cx="{X(-4.4):.1f}" cy="{Y(j):.1f}" r="10" fill="#fff" stroke="{MUTED}" stroke-width="1"/>')
        h.t(X(-4.4), Y(j) + 4, 'ABCDEFG'[k], 10.5, MUTED, 600, FM, 'middle')
    # piso blanco = espacio libre
    h.rect(X(0), Y(0), NW * PX, NH * PX, '#ffffff', 'none', 0)
    # pasillos
    x0, y0, x1, y1 = PASILLO
    h.rect(X(x0), Y(y0), (x1 - x0) * PX, (y1 - y0) * PX, 'url(#pasillo)', 'none', 0)
    for yy in (y0, y1):
        h.line(X(x0), Y(yy) + (1.5 if yy == y0 else -1.5), X(x1), Y(yy) + (1.5 if yy == y0 else -1.5), AMAR, 1.6, 'stroke-dasharray="9 5"')
    h.t(X(86), Y(21.95), 'PASILLO DE MONTACARGAS · 3,5 m', 10, '#8a6d00', 700, FM, 'middle')
    x0, y0, x1, y1 = PEATONAL
    h.rect(X(x0), Y(y0), (x1 - x0) * PX, (y1 - y0) * PX, '#e9f5ec', 'none', 0)
    for xx in (x0, x1):
        h.line(X(xx), Y(y0), X(xx), Y(y1), '#3d8a52', 1.2, 'stroke-dasharray="6 4"')
    # límites de área sin muro (línea fina discontinua)
    for nom, x0_, y0_, x1_, y1_, _ in RECINTOS:
        h.rect(X(x0_), Y(y0_), (x1_ - x0_) * PX, (y1_ - y0_) * PX, 'none', '#aab3bd', 0.9, 0, 'stroke-dasharray="2 4"')
    # equipos
    color_de = lambda l: LINEA[l] if (enfoque is None or l == enfoque or l == 'tronco') else GRIS
    for kind, (x, y, w, hh) in RACKS:
        c = LINEA[kind] if enfoque is None or kind in ('frio', 'serv') else (LINEA[kind] if kind == enfoque else GRIS)
        h.rect(X(x), Y(y), w * PX, hh * PX, 'url(#rack)', c, 1)
    for cx, cy, r in CIP_TANQUES:
        h.S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{r / 2 * PX:.1f}" fill="{tinte(LINEA["serv"])}" stroke="{LINEA["serv"]}" stroke-width="1.1"/>')
    for x, y, w, hh in MANT:
        h.rect(X(x), Y(y), w * PX, hh * PX, tinte(LINEA['serv']), LINEA['serv'], 1)
    for cod, lin, forma, d in EQ:
        c = color_de(lin)
        if forma == 'rect':
            x, y, w, hh = d
            h.rect(X(x), Y(y), w * PX, hh * PX, tinte(c, 0.16), c, 1.2, 1.5)
            if etiquetas_equipo:
                h.t(X(x + w / 2), Y(y + hh / 2) + 3.5, cod, 9 if len(cod) < 9 else 8, c, 600, FM, 'middle')
        else:
            cx, cy, dd = d
            h.S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{dd / 2 * PX:.1f}" fill="{tinte(c, 0.16)}" stroke="{c}" stroke-width="1.2"/>')
            h.S.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="2" fill="{c}"/>')
            if etiquetas_equipo:
                h.t(X(cx), Y(cy + dd / 2) + 11, cod, 8.5, c, 600, FM, 'middle')
    # muros interiores con vanos
    for (x1, y1, x2, y2), vanos in MUROS:
        largo = abs(x2 - x1) + abs(y2 - y1)
        cortes = [0] + [v for par in vanos for v in par[:2]] + [largo]
        for a, b in zip(cortes[::2], cortes[1::2]):
            if x1 == x2:
                h.rect(X(x1) - 2, Y(min(y1, y2) + a), 4, (b - a) * PX, '#2a3440', 'none', 0)
            else:
                h.rect(X(min(x1, x2) + a), Y(y1) - 2, (b - a) * PX, 4, '#2a3440', 'none', 0)
        for vano in vanos:                                            # hoja de puerta con su arco de giro
            a, b = vano[:2]
            if len(vano) == 3:                                        # portón o paso: línea discontinua, sin hoja
                if x1 == x2:
                    h.line(X(x1), Y(min(y1, y2) + a), X(x1), Y(min(y1, y2) + b), ACC, 1.6, 'stroke-dasharray="4 3"')
                else:
                    h.line(X(min(x1, x2) + a), Y(y1), X(min(x1, x2) + b), Y(y1), ACC, 1.6, 'stroke-dasharray="4 3"')
                continue
            if x1 == x2:
                px_, py_ = X(x1), Y(min(y1, y2) + a)
                r = (b - a) * PX
                h.S.append(f'<path d="M{px_:.1f},{py_:.1f} L{px_ + r:.1f},{py_:.1f} A{r:.1f},{r:.1f} 0 0,1 {px_:.1f},{py_ + r:.1f}" fill="none" stroke="{MUTED}" stroke-width="0.8"/>')
            else:
                px_, py_ = X(min(x1, x2) + a), Y(y1)
                r = (b - a) * PX
                h.S.append(f'<path d="M{px_:.1f},{py_:.1f} L{px_:.1f},{py_ + r:.1f} A{r:.1f},{r:.1f} 0 0,0 {px_ + r:.1f},{py_:.1f}" fill="none" stroke="{MUTED}" stroke-width="0.8"/>')
    # muros exteriores (30 cm, rayados) con portones y puertas
    t_ = 0.35 * PX
    lados = {'N': (0, NW), 'S': (0, NW), 'O': (0, NH), 'E': (0, NH)}
    for lado, (a0, a1) in lados.items():
        vs = sorted((a, b, tp) for l, a, b, tp in VANOS if l == lado)
        cortes = [a0] + [v for a, b, _ in vs for v in (a, b)] + [a1]
        for a, b in zip(cortes[::2], cortes[1::2]):
            if lado in 'NS':
                yy = Y(0) - t_ if lado == 'N' else Y(NH)
                h.rect(X(a) - (t_ if a == 0 else 0), yy, (b - a) * PX + (t_ if a == 0 else 0) + (t_ if b == NW else 0), t_, 'url(#muro)', '#2a3440', 0.8)
            else:
                xx = X(0) - t_ if lado == 'O' else X(NW)
                h.rect(xx, Y(a), t_, (b - a) * PX, 'url(#muro)', '#2a3440', 0.8)
        for a, b, tp in vs:
            if tp == 'portón':                                        # portón seccional: línea discontinua
                if lado in 'NS':
                    yy = Y(NH) + t_ / 2
                    h.line(X(a), yy, X(b), yy, ACC, 2, 'stroke-dasharray="5 3"')
                else:
                    xx = X(0) - t_ / 2 if lado == 'O' else X(NW) + t_ / 2
                    h.line(xx, Y(a), xx, Y(b), ACC, 2, 'stroke-dasharray="5 3"')
            else:
                r = (b - a) * PX
                xx, yy = X(a), Y(NH)
                h.S.append(f'<path d="M{xx:.1f},{yy:.1f} L{xx:.1f},{yy - r:.1f} A{r:.1f},{r:.1f} 0 0,1 {xx + r:.1f},{yy:.1f}" fill="none" stroke="{MUTED}" stroke-width="0.8"/>')
    # accesos exteriores
    h.t(X(-1.6), Y(11) + 4, 'cisternas →', 10, ACC, 700, FM, 'end')
    h.t(X(NW) + 12, Y(34.2), '→ despacho', 10, ACC, 700, FM)
    h.t(X(31.75), Y(NH) + 26, 'despacho de quesos', 9.5, ACC, 600, FM, 'middle')
    h.t(X(57.5), Y(NH) + 26, 'ingreso de personal', 9.5, ACC, 600, FM, 'middle')
    # etiquetas de recintos con su área
    for nom, x0, y0, x1, y1, (lx, ly) in RECINTOS:
        a = (x1 - x0) * (y1 - y0)
        h.t(X(lx), Y(ly), nom, 10.5 if len(nom) < 20 else 9.5, INK, 700, FD, 'middle', 'letter-spacing="0.4"')
        h.t(X(lx), Y(ly) + 13, f'{a:,.0f} m²'.replace(',', '.'), 9.5, MUTED, 500, FM, 'middle')
    # cotas
    def cota_h(xs, y, arriba=True):
        yy = Y(y)
        h.line(X(xs[0]), yy, X(xs[-1]), yy, MUTED, 0.8)
        for x in xs:
            h.line(X(x), yy - 5, X(x), yy + 5, MUTED, 0.8)
            h.line(X(x) - 3, yy + 3, X(x) + 3, yy - 3, MUTED, 1.2)
        for a, b in zip(xs, xs[1:]):
            h.t((X(a) + X(b)) / 2, yy - 4 if arriba else yy + 13, f'{b - a:g}'.replace('.', ','), 9.5, MUTED, 600, FM, 'middle')

    def cota_v(ys, x):
        xx = X(x)
        h.line(xx, Y(ys[0]), xx, Y(ys[-1]), MUTED, 0.8)
        for y in ys:
            h.line(xx - 5, Y(y), xx + 5, Y(y), MUTED, 0.8)
            h.line(xx - 3, Y(y) + 3, xx + 3, Y(y) - 3, MUTED, 1.2)
        for a, b in zip(ys, ys[1:]):
            cy = (Y(a) + Y(b)) / 2
            h.t(xx + 4, cy, f'{b - a:g}'.replace('.', ','), 9.5, MUTED, 600, FM, 'middle', f'transform="rotate(-90 {xx + 4:.1f} {cy:.1f})"')
    cota_h([0, 26, 40, 52, 66, 79, 95, 110], -1.6)
    cota_h([0, 110], NH + 3.4, False)
    cota_v([0, 20, 23.5, 46, 60], NW + 2.4)
    # escala gráfica y norte
    for i in range(4):
        h.rect(X(0) + i * 5 * PX, Y(NH + 6.2), 5 * PX, 6, INK if i % 2 == 0 else PAPER, INK, 0.8)
    for i, s in enumerate(('0', '5', '10', '15', '20 m')):
        h.t(X(0) + i * 5 * PX, Y(NH + 6.2) + 20, s, 9.5, MUTED, 600, FM, 'middle')
    nx, ny = X(NW) - 10, Y(NH + 6.8)
    h.S.append(f'<polygon points="{nx},{ny - 16} {nx - 7},{ny + 7} {nx},{ny + 2} {nx + 7},{ny + 7}" fill="{INK}"/>')
    h.t(nx, ny - 21, 'N', 12, INK, 800, FD, 'middle')


def leyenda(h, x, y, enfoque=None):
    h.t(x, y, 'Convenciones', 15, ACC, 800, FD)
    items = [('muro', 'Muro exterior (30 cm)'), ('int', 'Muro interior y puerta con su giro'), ('porton', 'Portón, o paso de banda en un muro'), ('limite', 'Límite de área sin muro (nave abierta)'),
             ('pasillo', 'Pasillo de montacargas (3,5 m)'), ('peatonal', 'Pasillo peatonal (1,2 m)'), ('libre', 'Piso libre')]
    for i, (k, s) in enumerate(items):
        yy = y + 24 + i * 22
        if k == 'muro':
            h.rect(x, yy - 9, 30, 9, 'url(#muro)', '#2a3440', 0.8)
        elif k == 'int':
            h.rect(x, yy - 6, 30, 3.5, '#2a3440', 'none', 0)
        elif k == 'limite':
            h.line(x, yy - 4, x + 30, yy - 4, '#aab3bd', 1, 'stroke-dasharray="2 4"')
        elif k == 'porton':
            h.line(x, yy - 4, x + 30, yy - 4, ACC, 2, 'stroke-dasharray="5 3"')
        elif k == 'pasillo':
            h.rect(x, yy - 11, 30, 12, 'url(#pasillo)', AMAR, 1)
        elif k == 'peatonal':
            h.rect(x, yy - 11, 30, 12, '#e9f5ec', '#3d8a52', 1)
        else:
            h.rect(x, yy - 11, 30, 12, '#ffffff', RULE, 1)
        h.t(x + 42, yy, s, 11.5)
    y2 = y + 24 + len(items) * 22 + 6
    lins = [('tronco', 'Tronco común'), ('yogur', 'Línea de yogures'), ('queso', 'Línea de quesos'), ('uht', 'Línea de leche UHT'),
            ('serv', 'Servicios y almacén')]
    for i, (k, s) in enumerate(lins):
        yy = y2 + i * 22
        c = LINEA[k] if enfoque is None or k in (enfoque, 'tronco', 'serv') else GRIS
        h.rect(x, yy - 11, 30, 12, tinte(c, 0.16), c, 1.2, 1.5)
        h.t(x + 42, yy, s + ('' if c != GRIS else ' (otra línea)'), 11.5)
    yy = y2 + len(lins) * 22
    h.rect(x, yy - 11, 30, 12, 'url(#rack)', GRIS, 1)
    h.t(x + 42, yy, 'Estanterías', 11.5)
    return yy + 30


def tabla_areas(h, x, y, solo=None):
    h.t(x, y, 'Áreas y espacio libre', 15, ACC, 800, FD)
    for s, dx in (('Recinto', 0), ('m²', 250), ('libre', 330)):
        h.t(x + dx, y + 24, s, 10, MUTED, 600, FM, 'end' if dx else 'start')
    filas = [f for f in cuadro_areas() if solo is None or f[0] in solo]
    for i, (nom, a, occ, lib) in enumerate(filas):
        yy = y + 44 + i * 19
        h.t(x, yy, nom.capitalize().replace('uht', 'UHT').replace('°c', '°C').replace('Cip', 'CIP'), 10.5)
        h.t(x + 250, yy, f'{a:,.0f}'.replace(',', '.'), 10.5, INK, 600, FM, 'end')
        h.rect(x + 262, yy - 9, 40, 9, '#eef1f4', 'none', 0)
        h.rect(x + 262, yy - 9, 40 * lib, 9, '#9fd0b0', 'none', 0)
        h.t(x + 330, yy, f'{lib * 100:.0f} %', 10.5, OK, 700, FM, 'end')
    yy = y + 44 + len(filas) * 19 + 6
    tot = sum(a for _, a, _, _ in filas)
    libre = sum(a * l for _, a, _, l in filas)
    h.line(x, yy - 10, x + 330, yy - 10, INK, 0.8)
    h.t(x, yy + 4, 'Total', 11, INK, 700)
    h.t(x + 250, yy + 4, f'{tot:,.0f}'.replace(',', '.'), 11, INK, 700, FM, 'end')
    h.t(x + 330, yy + 4, f'{libre / tot * 100:.0f} %', 11, OK, 800, FM, 'end')
    h.t(x, yy + 24, 'Libre = área del recinto sin equipos ni estanterías;', 9.5, MUTED)
    h.t(x, yy + 37, 'incluye las zonas de operación y mantenimiento.', 9.5, MUTED)
    return yy + 60


def rotulo(h, plano_txt, y=1236):
    x = 1585
    h.rect(x - 10, y, 385, 150, BG, RULE, 1, 6)
    h.t(x + 6, y + 24, 'PROYECTO', 9.5, MUTED, 600, FM)
    h.t(x + 6, y + 42, 'Proyecto integrador APM 2026-2S · UNAL', 12, INK, 700)
    h.t(x + 6, y + 66, 'PLANO', 9.5, MUTED, 600, FM)
    h.t(x + 6, y + 84, plano_txt, 12, INK, 700)
    h.t(x + 6, y + 108, 'ESCALA', 9.5, MUTED, 600, FM)
    h.t(x + 6, y + 126, '1:750 en A3 · cotas en m', 12, INK, 700)
    h.t(x + 220, y + 108, 'FECHA', 9.5, MUTED, 600, FM)
    h.t(x + 220, y + 126, '10-oct-2026', 12, INK, 700)
    h.t(x + 6, y + 144, 'Mekvra · medidas propuestas, sin plano del terreno', 9.5, MUTED)


# ---------------- espagueti: rutas que se repiten cada día (m sobre la nave) ----------------
P = 21.75
RUTAS = {
    'envases': ('Envases a las llenadoras', '#c33c64', [(81, 30), (81, P), (84, P), (84, 19.2)]),
    'insumos': ('Leche en polvo y azúcar a U201', '#2d7d69', [(47, 48), (47, 45.5), (66.2, 45.5), (66.2, P), (48.5, P), (48.5, 9.2)]),
    'fruta': ('Preparado de fruta al dosificador', '#b8325a', [(76, 30), (76, P), (78, P), (78, 9)]),
    'calidad': ('Analista: muestras de pH y llenado', '#7355a5', [(13, 12.5), (13, 18.5), (23.7, 18.5), (23.7, 20.5), (40, 20.5), (40, P), (59, P), (59, 12), (59, P), (83, P), (83, 18.5)]),
    'montacargas': ('Montacargas: estibas a la cámara', '#d9a400', [(99, 17.5), (99, P), (102, P), (102, 28)]),
    'despacho': ('Montacargas: cámara a los muelles', '#2d69a5', [(106, 30), (109, 30), (109, 34)]),
    'supervisor': ('Supervisor: rondas con registros', '#5b6876', [(98, 47), (95.5, 48.7), (94, 48.7), (94, 39), (88, 39), (88, P), (42, P), (42, 19.5)]),
}
ACTUAL = {'envases': 50, 'insumos': 12, 'fruta': 4, 'calidad': 60, 'montacargas': 95, 'despacho': 95, 'supervisor': 9}
PROPUESTO = {'envases': 29, 'insumos': 12, 'fruta': 4, 'calidad': 12, 'montacargas': 95, 'despacho': 95, 'supervisor': 3}
NOTAS = {'envases': ('vasos, botellas y potes preformados', 'bobinas de la FFS, botellas y potes'), 'insumos': ('≈ 2 estibas por lote', 'igual'),
         'fruta': ('canecas de 1.000 kg', 'igual'), 'calidad': ('≈ 6 muestras por lote + revisión horaria', 'pH en línea en el MES; solo verificación'),
         'montacargas': ('≈ 95 estibas por día', 'igual'), 'despacho': ('≈ 95 estibas por día', 'igual'),
         'supervisor': ('3 rondas por turno con planillas', '1 ronda por turno; datos en el MES')}
CAJAS = 11_600


def largo(p):
    return sum(math.dist(a, b) for a, b in zip(p, p[1:]))


def espagueti(h, viajes, propuesto):
    tot, filas = 0, []
    for k, (nom, c, pts) in RUTAS.items():
        n = viajes[k]
        md = largo(pts) * 2 * n
        tot += md
        filas.append((nom, c, n, largo(pts), md, NOTAS[k][1 if propuesto else 0]))
        capas = max(1, min(7, round(n / 12)))
        for j in range(capas):
            d = (j - (capas - 1) / 2) * 0.28
            h.S.append('<polyline points="' + ' '.join(f'{X(a + d):.1f},{Y(b + d):.1f}' for a, b in pts) +
                       f'" fill="none" stroke="{c}" stroke-width="1.8" stroke-opacity="0.8" stroke-linejoin="round"' +
                       (' marker-end="url(#f)"' if j == capas - 1 else '') + '/>')
    if not propuesto:
        for j in range(14):
            a = j * 0.9
            h.S.append(f'<path d="M{X(97.5):.1f},{Y(11.8):.1f} Q{X(98.5 + 1.6 * math.cos(a)):.1f},{Y(13.8 + math.sin(a)):.1f} {X(99 + (j % 4) * 2.4):.1f},{Y(15.6):.1f}" '
                       f'fill="none" stroke="{PCC}" stroke-width="1.4" stroke-opacity="0.75"/>')
    return filas, tot


def tabla_rutas(h, filas, tot, x, y, propuesto, tot_ref=None):
    h.t(x, y, 'Recorridos que se repiten cada día', 15, ACC, 800, FD)
    for s, dx in (('Ruta', 0), ('Viajes', 235), ('m/viaje', 300), ('m/día', 370)):
        h.t(x + dx, y + 24, s, 10, MUTED, 600, FM, 'end' if dx else 'start')
    for i, (nom, c, n, l, md, nota) in enumerate(filas):
        yy = y + 46 + i * 34
        h.line(x, yy - 4, x + 16, yy - 4, c, 3)
        h.t(x + 22, yy, nom, 10.5)
        h.t(x + 22, yy + 13, nota, 9, MUTED)
        h.t(x + 235, yy, f'{n}', 10.5, INK, 600, FM, 'end')
        h.t(x + 300, yy, f'{l:.0f}', 10.5, INK, 600, FM, 'end')
        h.t(x + 370, yy, f'{md:,.0f}'.replace(',', '.'), 10.5, INK, 600, FM, 'end')
    yy = y + 46 + len(filas) * 34
    h.line(x, yy - 12, x + 370, yy - 12, INK, 0.8)
    h.t(x, yy + 4, 'Total por día (ida y vuelta)', 11.5, INK, 700)
    h.t(x + 370, yy + 4, f'{tot / 1000:.1f} km'.replace('.', ','), 14, INK, 800, FD, 'end')
    if tot_ref:
        h.t(x, yy + 28, f'≈ {(1 - tot / tot_ref) * 100:.0f} % menos que hoy', 14, OK, 800, FD)
    else:
        h.t(x, yy + 28, f'+ ≈ {CAJAS:,} cajas estibadas a mano'.replace(',', '.'), 13, PCC, 800, FD)
        h.t(x, yy + 45, '(2 operarios por turno en U341, ≈ 6 m por caja)', 10, MUTED)
    return yy + 70


if __name__ == '__main__':
    # 1 · planta con las tres líneas
    h = Hoja()
    plano(h, None, 'PLANO DE DISTRIBUCIÓN · PLANTA CON TRES LÍNEAS · ESTADO ACTUAL', 'Lácteos Altos de Teusacá · edificio de producción',
          'Nave de 110 × 60 m · 150.000 L/día: yogures ≈ 57.000, quesos 50.000 y leche UHT 43.000 L/día · códigos de equipo iguales a los del modelo de Tecnomatix')
    y = leyenda(h, 1585, 200)
    tabla_areas(h, 1585, y + 10)
    rotulo(h, 'Distribución en planta · tres líneas')
    h.svg('layout_planta_3_lineas', 'Plano de la planta')

    # 2 · línea de yogures, paletizado manual
    h = Hoja()
    plano(h, 'yogur', 'PLANO DE DISTRIBUCIÓN · LÍNEA DE YOGURES · ESTADO ACTUAL', 'Línea de yogures · paletizado manual',
          'La línea de yogures en color y las demás áreas en gris · en U341 dos operarios estiban a mano las cajas que llegan por las bandas')
    for px_, py_ in ((98.3, 12.6), (100.8, 12.6)):                     # los dos operarios de paletizado
        h.S.append(f'<circle cx="{X(px_):.1f}" cy="{Y(py_):.1f}" r="5" fill="{PCC}"/><circle cx="{X(px_):.1f}" cy="{Y(py_):.1f}" r="9" fill="none" stroke="{PCC}" stroke-width="1"/>')
    y = leyenda(h, 1585, 200, 'yogur')
    h.S.append(f'<circle cx="{1600:.1f}" cy="{y - 14:.1f}" r="5" fill="{PCC}"/>')
    h.t(1627, y - 10, 'Operario de paletizado manual', 11.5)
    tabla_areas(h, 1585, y + 16, solo={'SILOS', 'PREPARACIÓN', 'FERMENTACIÓN', 'ACONDICIONAMIENTO', 'ENVASADO · SALA LIMPIA', 'PALETIZADO',
                                       'CÁMARA 2–4 °C', 'BODEGA DE ENVASES Y FRUTA', 'BODEGA DE INSUMOS'})
    rotulo(h, 'Distribución · línea de yogures')
    h.svg('layout_linea_yogures_actual', 'Plano de la línea de yogures')

    # 3 y 4 · espagueti actual y propuesto
    h = Hoja()
    plano(h, 'yogur', 'DIAGRAMA DE ESPAGUETI · ESTADO ACTUAL', 'Recorridos de la línea de yogures hoy',
          'Cada línea es una ruta que se repite durante el día: más líneas, más viajes · viajes estimados para ≈ 57.600 L/día de leche a yogures', etiquetas_equipo=False)
    filas, tot_act = espagueti(h, ACTUAL, False)
    tabla_rutas(h, filas, tot_act, 1585, 200, False)
    rotulo(h, 'Espagueti · línea de yogures, hoy')
    h.svg('espagueti_linea_yogures_actual', 'Espagueti actual')

    h = Hoja()
    plano(h, 'yogur', 'DIAGRAMA DE ESPAGUETI · PROPUESTA DE AUTOMATIZACIÓN', 'Recorridos de la línea de yogures con la propuesta',
          'Celda robotizada en U341, llenadora FFS que forma el vaso desde bobina, pH en línea y registro en el MES', etiquetas_equipo=False)
    filas, tot_pro = espagueti(h, PROPUESTO, True)
    y = tabla_rutas(h, filas, tot_pro, 1585, 200, True, tot_act)
    h.t(1585, y + 4, 'Qué cambia', 15, ACC, 800, FD)
    for i, s in enumerate(['Robot en U341: nadie estiba cajas a mano.', 'FFS: bobinas en lugar de vasos preformados.', 'pH en línea en el MES: el analista solo verifica.',
                           'MES: el supervisor deja las planillas.']):
        h.t(1585, y + 28 + i * 18, s, 11)
    yb = y + 120
    h.t(1585, yb, 'Metros recorridos por día', 13, ACC, 800, FD)
    for i, (lab, v, c) in enumerate((('Hoy', tot_act, PCC), ('Propuesta', tot_pro, OK))):
        yy = yb + 18 + i * 30
        h.t(1585, yy + 14, lab, 11, INK, 600)
        h.rect(1670, yy, 230 * v / tot_act, 18, c, 'none', 0, 3, 'fill-opacity="0.85"')
        h.t(1678 + 230 * v / tot_act, yy + 14, f'{v / 1000:.1f} km'.replace('.', ','), 12, c, 800, FD)
    rotulo(h, 'Espagueti · línea de yogures, propuesta')
    h.svg('espagueti_linea_yogures_propuesto', 'Espagueti propuesto')
    print('ok', round(tot_act), round(tot_pro))
    for f in cuadro_areas():
        print(f'{f[0]:28s} {f[1]:6.0f} m²  ocupado {f[2]:6.0f}  libre {f[3] * 100:3.0f} %')
