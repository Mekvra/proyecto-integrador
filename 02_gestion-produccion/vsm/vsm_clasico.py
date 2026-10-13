# VSM del estado actual de la línea de yogures con la notación clásica de Rother y Shook (Learning to See):
# íconos estándar en negro sobre blanco, cajas de datos, flechas de empuje, triángulos de inventario,
# escalera de tiempos y kaizen en rojo. Datos: recetas de la línea de yogures y simulación de 12 semanas
# (planta-150k/resultados_planta.json y linea-yogures/resultados_paletizado_manual.json).
# Uso: python vsm_clasico.py   → vsm_linea_yogures_clasico.svg / .html (exportar con exportar.mjs 1800 1100)
import json, os, math

D = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(D, '..', 'simulacion-tecnomatix', 'planta-150k', 'resultados_planta.json'), encoding='utf-8'))
M = json.load(open(os.path.join(D, '..', 'simulacion-tecnomatix', 'linea-yogures', 'resultados_paletizado_manual.json'), encoding='utf-8'))
U = {k: v['ocupado'] for k, v in R['uso'].items()}
U.update({k: v['ocupado'] for k, v in M['uso'].items()})


def pct(k):
    return f'{U[k] * 100:.0f} %'


def miles(x):
    return f'{x:,.0f}'.replace(',', '.')


W, H = 1800, 1100
K, G, RED = '#000000', '#555555', '#c00000'
F = 'Arial, Helvetica, sans-serif'
S = []


def t(x, y, s, size=13, fill=K, w=400, anchor='start', italic=False):
    s = str(s).replace('&', '&amp;').replace('<', '&lt;')
    st = ' font-style="italic"' if italic else ''
    S.append(f'<text x="{x}" y="{y}" font-family="{F}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{st}>{s}</text>')


def rect(x, y, w, h, fill='#fff', stroke=K, sw=1.5, extra=''):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, sw=1.5, stroke=K, extra=''):
    S.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def poly(pts, fill='#fff', stroke=K, sw=1.5, closed=True):
    tag = 'polygon' if closed else 'polyline'
    S.append(f'<{tag} points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"/>')


def fabrica(x, y, nombre):
    """Proveedor o cliente: fábrica con techo en sierra (ícono estándar)."""
    w, h = 150, 78
    poly([(x, y + h), (x, y + 26), (x + 50, y), (x + 50, y + 26), (x + 100, y), (x + 100, y + 26), (x + 150, y), (x + 150, y + h)])
    t(x + w / 2, y + 60, nombre, 15, K, 700, 'middle')


def caja_datos(x, y, w, filas, size=13):
    rect(x, y, w, 10 + 21 * len(filas))
    for i, s in enumerate(filas):
        t(x + 8, y + 23 + 21 * i, s, size)


def operario(cx, cy, n):
    S.append(f'<circle cx="{cx}" cy="{cy - 7}" r="5" fill="#fff" stroke="{K}" stroke-width="1.4"/>')
    S.append(f'<path d="M{cx - 9},{cy + 8} Q{cx},{cy - 6} {cx + 9},{cy + 8}" fill="none" stroke="{K}" stroke-width="1.4"/>')
    t(cx + 15, cy + 6, n, 13, K, 700)


def inventario(cx, y, arriba, abajo):
    poly([(cx, y), (cx - 20, y + 34), (cx + 20, y + 34)])
    t(cx, y + 29, 'I', 16, K, 700, 'middle')
    t(cx, y + 54, arriba, 13, K, 700, 'middle')
    t(cx, y + 70, abajo, 12, G, 400, 'middle')


def empuje(x1, x2, y):
    """Flecha de empuje: franjas blancas y negras."""
    n = int((x2 - x1 - 16) // 8)
    for i in range(n):
        rect(x1 + i * 8, y - 6, 8, 12, K if i % 2 == 0 else '#fff', K, 1)
    poly([(x1 + n * 8, y - 13), (x2, y), (x1 + n * 8, y + 13)], K, K, 1)


def flecha(x1, y1, x2, y2, sw=1.5):
    S.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{K}" stroke-width="{sw}" marker-end="url(#p)"/>')


def rayo(x1, y, x2, texto):
    """Información electrónica: flecha en zigzag."""
    m = (x1 + x2) / 2
    d = 1 if x2 > x1 else -1
    S.append(f'<polyline points="{x1},{y} {m - 14 * d},{y} {m + 6 * d},{y - 14} {m - 6 * d},{y + 14} {m + 14 * d},{y} {x2},{y}" '
             f'fill="none" stroke="{K}" stroke-width="1.5" marker-end="url(#p)"/>')
    t(m, y - 22, texto, 12.5, K, 400, 'middle')


def envio(x1, x2, y):
    """Flecha de envío: flecha gruesa hueca."""
    d = 1 if x2 > x1 else -1
    a = x2 - 22 * d
    poly([(x1, y - 7), (a, y - 7), (a, y - 15), (x2, y), (a, y + 15), (a, y + 7), (x1, y + 7)])


def envio_v(x, y1, y2):
    """Flecha de envío vertical (hueca), de y1 hacia y2."""
    d = 1 if y2 > y1 else -1
    a = y2 - 22 * d
    poly([(x - 7, y1), (x - 7, a), (x - 15, a), (x, y2), (x + 15, a), (x + 7, a), (x + 7, y1)])


def camion(x, y, texto):
    rect(x, y, 62, 32)
    rect(x + 62, y + 10, 24, 22)
    for cx in (x + 14, x + 46, x + 74):
        S.append(f'<circle cx="{cx}" cy="{y + 36}" r="6" fill="#fff" stroke="{K}" stroke-width="1.5"/>')
    t(x + 43, y + 62, texto, 12.5, K, 400, 'middle')


def kaizen(cx, cy, l1, l2='', rx=78, ry=34):
    pts = []
    for i in range(18):
        r = 1.0 if i % 2 == 0 else 0.72
        a = 2 * math.pi * i / 18 + 0.17
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    poly(pts, '#fff', RED, 1.8)
    t(cx, cy + (-2 if l2 else 5), l1, 12.5, RED, 700, 'middle')
    if l2:
        t(cx, cy + 14, l2, 11.5, RED, 400, 'middle')


# ---------------- hoja ----------------
rect(0, 0, W, H, '#fff', '#fff', 0)
rect(14, 14, W - 28, H - 28, 'none', K, 1.2)
t(36, 52, 'Mapa de flujo de valor – estado actual', 24, K, 700)
t(36, 76, 'Línea de yogures (natural, griego y fresa) · Lácteos Altos de Teusacá', 15, G)

# ---------------- proveedor, control de producción y cliente ----------------
fabrica(52, 100, 'Ganaderos')
caja_datos(52, 188, 150, ['150.000 L/día planta', f'{miles(R["litros_dia"])} L/día yogur'], 12.5)
camion(60, 262, '')
t(156, 290, '≈ 8 cisternas/día', 12.5)
envio_v(103, 312, 396)
fabrica(1612, 100, 'Clientes')
caja_datos(1390, 100, 205, [f'{miles(R["vasos_U311_dia"])} vasos/día', f'{miles(R["botellas_U312_dia"])} botellas/día',
                            f'{miles(R["griego_U313_dia"])} griego/día', '35 lotes/semana', 'Takt = 4,2 h/lote'], 12.5)
camion(1632, 200, '')
t(1622, 236, 'Despacho diario', 12.5, K, 400, 'end')
rect(700, 100, 400, 92)
t(900, 128, 'Control de producción', 16, K, 700, 'middle')
t(900, 152, 'Programa semanal en hoja de cálculo', 13, K, 400, 'middle')
t(900, 172, 'Registro de lotes en papel · sin MES', 13, K, 400, 'middle')
rayo(1386, 150, 1104, 'Pedidos diarios')
rayo(696, 150, 206, 'Programa de acopio semanal')
line(900, 192, 900, 320)
line(327, 320, 1527, 320)
for x in (327, 727, 1127, 1527):
    flecha(x, 320, x, 394)
t(910, 310, 'Programa impreso por turno', 12.5)

# ---------------- procesos ----------------
BW, GAP, X0, YB = 150, 50, 52, 400
P = [
    ('Recepción', 'U111 · U112', None, ['C/T = 0,6 h', 'C/O = —', 'Disp. = 100 %', f'Uso = {pct("U111_Recepcion")}']),
    ('Pasteurización', 'U121 · U122 HTST', None, ['C/T = 0,5 h', 'C/O = CIP 1,4 h', 'Disp. = 98 %', f'Uso = {pct("U121_Pasteurizador")}']),
    ('Formulación', 'U201', '1', ['C/T = 1,9 h', 'C/O = CIP 1/día', 'Disp. = 98 %', f'Uso = {pct("U201_Formulacion")}']),
    ('Tratamiento', 'U202 · 92 °C, 5 min', None, ['C/T = 1,2 h', 'C/O = CIP 1,4 h', 'Disp. = 98 %', f'Uso = {pct("U202_Tratamiento")}']),
    ('Fermentación', '4 tanques × 12.000 L', '2', ['C/T = 8,1–9,0 h', 'C/O = CIP 0,75 h', 'Disp. = 100 %', f'Uso = {pct("U211_Fermentador")}']),
    ('Acondicionam.', 'U215 · U216', None, ['C/T = 1,0–1,7 h', 'C/O = CIP 1/día', 'Disp. = 98 %', f'Uso = {pct("U215_Enfriamiento")}']),
    ('Envasado', 'U311 · U312 · U313', '4', ['C/T = 3,5 h', 'C/O = 0,75 h', 'OEE = 70 %', f'Uso U311 = {pct("U311_Vasos")}']),
    ('Paletizado', 'manual · U341', '2', ['C/T = 150 s/bulto', 'C/O = —', 'Disp. = 100 %', f'Uso = {pct("U341_Paletizado")}']),
]
XS = [X0 + i * (BW + GAP) for i in range(len(P))]
for i, (nom, sub, ops, datos) in enumerate(P):
    x = XS[i]
    rect(x, YB, BW, 86, '#fff', K, 2.4 if i == 6 else 1.5)
    line(x, YB + 30, x + BW, YB + 30, 1)
    t(x + BW / 2, YB + 21, nom, 15, K, 700, 'middle')
    t(x + BW / 2, YB + 50, sub, 11.5, G, 400, 'middle')
    if ops:
        operario(x + 22, YB + 70, ops)
    caja_datos(x, YB + 96, BW, datos)
    if i < len(P) - 1:
        empuje(x + BW + 5, x + BW + GAP - 5, YB + 43)
inventario(XS[0] + BW + GAP / 2, YB + 206, '4 h', 'leche cruda')
inventario(XS[1] + BW + GAP / 2, YB + 206, '2 h', 'silos')
inventario(XS[5] + BW + GAP / 2, YB + 206, '≤ 8 h', 'pulmones')
xc = 1675
inventario(xc, YB + 26, '12 h', 'cámara 2–4 °C')
flecha(XS[7] + BW + 4, YB + 43, xc - 16, YB + 43)
envio_v(xc, YB + 20, 252)

# kaizen: oportunidades que ataca la propuesta
kaizen(XS[6] + BW / 2, 360, 'Llenadora FFS', '21.600 vasos/h', 96, 32)
kaizen(XS[4] + BW / 2, 360, 'pH en línea', 'menos muestreo', 90, 32)
kaizen(1250, 250, 'MES + ISA-95', 'registro digital', 92, 32)
kaizen(XS[7] + BW / 2, YB + 300, 'Paletizado', 'robotizado', 84, 32)
t(XS[6] + BW / 2, YB + 212, 'Cuello de botella', 13, RED, 700, 'middle')

# ---------------- escalera de tiempos (un lote de fresa) ----------------
YT = 790
espera = {0: '4 h', 1: '2 h', 7: '12 h'}
proc = ['0,6 h', '0,5 h', '1,9 h', '1,2 h', '8,5 h', '1,1 h', '3,5 h', '0,1 h']
yh, yl = YT, YT + 46
pts = [(XS[0] - 30, yh)]
for i in range(len(P)):
    pts += [(XS[i], yh), (XS[i], yl), (XS[i] + BW, yl), (XS[i] + BW, yh)]
    t(XS[i] + BW / 2, yl + 22, proc[i], 14, K, 400, 'middle')
    if i in espera:
        cx = XS[i] + BW + GAP / 2 if i < 7 else xc
        t(cx, yh - 10, espera[i], 14, K, 400, 'middle')
pts.append((xc + 40, yh))
poly(pts, 'none', K, 1.6, closed=False)
rect(1560, YT + 70, 210, 76)
t(1572, YT + 96, 'Lead time = 35 h', 15, K, 700)
t(1572, YT + 120, 'T. valor agregado = 10,5 h', 13.5)
t(1572, YT + 138, '(30 % del lead time)', 12, G)

# ---------------- pie ----------------
t(36, H - 70, 'C/T y C/O por lote de 10.000 L, según las recetas. Uso = trabajo + alistamiento + fallas, de la simulación de 12 semanas.', 12.5, G)
t(36, H - 50, 'La espera en pulmones (≤ 8 h) no se suma al lead time: el lote se envasa mientras el siguiente fermenta.', 12.5, G)
defs = (f'<defs><marker id="p" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{K}"/></marker></defs>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(s for s in S if s) + '</svg>'
N = 'vsm_linea_yogures_clasico'
open(os.path.join(D, N + '.svg'), 'w', encoding='utf-8').write(svg)
open(os.path.join(D, N + '.html'), 'w', encoding='utf-8').write(
    '<!doctype html><html lang="es"><head><meta charset="utf-8"><title>VSM línea de yogures</title>'
    f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:#fff}}svg{{display:block}}</style></head><body>{svg}</body></html>')
print('ok')
