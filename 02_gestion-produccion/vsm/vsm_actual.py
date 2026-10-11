# VSM del estado actual de la línea de yogures (Lácteos Altos de Teusacá, acta del 9-oct-2026).
# Datos: recetas v1.7 (tiempos de ciclo, personal, OEE) y simulación de Tecnomatix de 12 semanas
# (../simulacion-tecnomatix/planta-150k/resultados_planta.json, planta completa de 150.000 L/día). Genera vsm_linea_yogures_actual.svg y .html.
# Uso: python vsm_actual.py
import json, os, sys

D = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(D, '..', 'simulacion-tecnomatix', 'planta-150k', 'resultados_planta.json'), encoding='utf-8'))
U = {k: v['ocupado'] for k, v in R['uso'].items()}
# variante «manual»: misma línea con el paletizado U341 hecho por 2 operarios (modelo linea_yogures_actual_3d_paletizado_manual.spp)
MANUAL = len(sys.argv) > 1 and sys.argv[1] == 'manual'
if MANUAL:
    M = json.load(open(os.path.join(D, '..', 'simulacion-tecnomatix', 'linea-yogures', 'resultados_paletizado_manual.json'), encoding='utf-8'))
    U.update({k: v['ocupado'] for k, v in M['uso'].items()})
NOMBRE = 'vsm_linea_yogures_paletizado_manual' if MANUAL else 'vsm_linea_yogures_actual'


def pct(k):
    return f'{U[k] * 100:.0f} %'


def miles(x):
    return f'{x:,.0f}'.replace(',', '.')


W, H = 1800, 1060
INK, MUTED, RULE, PAPER, BG = '#14202b', '#5b6876', '#d9e0e7', '#ffffff', '#f6f8fa'
ACC, ACC_S, PCC, PCC_S, OK = '#1f4e79', '#e4edf6', '#b4441b', '#fbe8df', '#2e7d4f'
FD = "Archivo, 'Arial Narrow', Arial, sans-serif"
FB = "'IBM Plex Sans', 'Segoe UI', Arial, sans-serif"
FM = "'IBM Plex Mono', Consolas, monospace"
S = []


def t(x, y, s, size=13, fill=INK, w=400, fam=FB, anchor='start', extra=''):
    s = str(s).replace('&', '&amp;').replace('<', '&lt;')
    S.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{fill}" '
             f'text-anchor="{anchor}" {extra}>{s}</text>')


def rect(x, y, w, h, fill=PAPER, stroke=INK, sw=1.4, rx=0, extra=''):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=1.4, extra=''):
    S.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def fabrica(x, y, w, nombre, sub):
    """Ícono de fábrica (proveedor o cliente): techo en sierra."""
    h = 70
    pts = [(x, y + h), (x, y + 22), (x + w / 3, y), (x + w / 3, y + 22), (x + 2 * w / 3, y), (x + 2 * w / 3, y + 22),
           (x + w, y), (x + w, y + h)]
    S.append('<polygon points="' + ' '.join(f'{a},{b}' for a, b in pts) + f'" fill="{ACC_S}" stroke="{ACC}" stroke-width="1.6"/>')
    t(x + w / 2, y + 52, nombre, 14, ACC, 700, FD, 'middle')
    for i, s in enumerate(sub):
        t(x + w / 2, y + h + 20 + 16 * i, s, 11.5, MUTED, 400, FB, 'middle')


def camion(x, y, s):
    rect(x, y, 58, 30, ACC_S, ACC, 1.4, 2)
    rect(x + 58, y + 10, 22, 20, ACC_S, ACC, 1.4, 2)
    for cx in (x + 14, x + 44, x + 70):
        S.append(f'<circle cx="{cx}" cy="{y + 33}" r="6" fill="{PAPER}" stroke="{ACC}" stroke-width="1.4"/>')
    t(x + 40, y + 58, s, 11.5, MUTED, 400, FB, 'middle')


def inventario(cx, y, arriba, abajo, color=PCC):
    S.append(f'<polygon points="{cx},{y} {cx - 19},{y + 32} {cx + 19},{y + 32}" fill="{PCC_S}" stroke="{color}" stroke-width="1.6"/>')
    t(cx, y + 27, 'I', 15, color, 800, FD, 'middle')
    t(cx, y + 50, arriba, 11, INK, 600, FM, 'middle')
    t(cx, y + 64, abajo, 10, MUTED, 400, FB, 'middle')


def empuje(x1, x2, y):
    """Flecha de empuje (push): banda rayada."""
    S.append(f'<rect x="{x1}" y="{y - 5}" width="{x2 - x1 - 10}" height="10" fill="url(#rayas)" stroke="{INK}" stroke-width="1"/>')
    S.append(f'<polygon points="{x2 - 12},{y - 11} {x2},{y} {x2 - 12},{y + 11}" fill="{INK}"/>')


def flecha(x1, y1, x2, y2, color=INK, sw=1.4, dash=''):
    S.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" {dash} marker-end="url(#punta)"/>')


def rayo(x1, y1, x2, y2, color=ACC):
    """Flujo de información electrónico (zigzag)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    S.append(f'<polyline points="{x1},{y1} {mx + 10},{my - 8} {mx - 10},{my + 8} {x2},{y2}" fill="none" stroke="{color}" '
             f'stroke-width="1.6" marker-end="url(#punta_a)"/>')


def kaizen(cx, cy, s1, s2=''):
    import math
    pts = []
    for i in range(16):
        r = 36 if i % 2 == 0 else 25
        a = math.pi * 2 * i / 16 - math.pi / 2
        pts.append((cx + r * math.cos(a) * 1.75, cy + r * math.sin(a)))
    S.append('<polygon points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="#fff4d6" stroke="#c98a00" stroke-width="1.4"/>')
    t(cx, cy - 1 if s2 else cy + 4, s1, 10.5, '#7a5200', 700, FB, 'middle')
    if s2:
        t(cx, cy + 12, s2, 10, '#7a5200', 400, FB, 'middle')


# ---------------- marco y título ----------------
S.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
rect(20, 20, W - 40, H - 40, PAPER, RULE, 1, 10)
t(48, 64, 'VSM · ESTADO ACTUAL' + (' · PALETIZADO MANUAL' if MANUAL else ''), 12, MUTED, 600, FM, extra='letter-spacing="1.5"')
t(48, 96, 'Línea de yogures · Lácteos Altos de Teusacá', 30, INK, 800, FD)
LOTES_TXT = f'{R["lotes_dia"]:.2f}'.replace('.', ',')
t(48, 122, 'Planta de 150.000 L/día (acta 9-oct-2026) · línea de yogures sin automatización · un lote = 10.000 L de leche estandarizada · ' + LOTES_TXT + ' lotes/día · 6 días/semana', 13, MUTED)
t(W - 48, 64, 'Mekvra · APM 2026-2S · UNAL', 12, MUTED, 600, FM, 'end')

# ---------------- proveedor, control y cliente ----------------
fabrica(60, 170, 180, 'GANADEROS', ['Acopio de la Sabana', '150.000 L/día a la planta', f'≈ {miles(R["recepcion_dia"] * R["litros_dia"] / R["recepcion_dia"])} L/día a yogures'])
fabrica(1560, 170, 180, 'CLIENTES', ['Supermercados y distribuidores',
                                     f'{miles(R["vasos_U311_dia"])} vasos · {miles(R["botellas_U312_dia"])} botellas',
                                     f'{miles(R["griego_U313_dia"])} griego / día'])
rect(690, 160, 420, 104, ACC_S, ACC, 1.6, 6)
t(900, 190, 'PLANEACIÓN DE LA PRODUCCIÓN', 15, ACC, 800, FD, 'middle')
t(900, 212, 'Programa semanal en hoja de cálculo · sin MES', 12.5, INK, 400, FB, 'middle')
t(900, 230, '35 lotes/semana: 13 natural · 9 griego · 13 fresa', 12.5, INK, 400, FB, 'middle')
t(900, 248, 'Registro de lotes en papel', 12.5, INK, 400, FB, 'middle')
# flujos de información
rayo(1556, 200, 1114, 200)
t(1335, 188, 'Pedidos diarios (correo, teléfono)', 11.5, MUTED, 400, FB, 'middle')
rayo(686, 200, 244, 200)
t(465, 188, 'Programa de acopio semanal', 11.5, MUTED, 400, FB, 'middle')
flecha(900, 268, 900, 330, ACC, 1.4, 'stroke-dasharray="5 4"')
t(912, 312, 'Programa impreso por turno a cada área', 11.5, MUTED)
line(330, 330, 1470, 330, ACC, 1.2, 'stroke-dasharray="5 4"')
for x in (330, 710, 1090, 1470):
    flecha(x, 330, x, 392, ACC, 1.2, 'stroke-dasharray="5 4"')
camion(110, 300, 'Cisternas · ≈ 8 por día')
camion(1610, 300, 'Camión refrigerado · diario')

# ---------------- procesos ----------------
BW, GAP, X0, YB = 146, 46, 40, 400
P = [
    ('RECEPCIÓN', 'U111/U112', [('C/T', '0,6 h/lote'), ('C/O', '—'), ('Disp.', '100 %'), ('Uso', pct('U111_Recepcion')), ('Op.', 'común')]),
    ('PASTEURIZACIÓN', 'U121/U122 · HTST', [('C/T', '0,5 h/lote'), ('C/O', 'CIP-C 1,4 h ×2'), ('Disp.', '98 %'), ('Uso', pct('U121_Pasteurizador')), ('Op.', 'común')]),
    ('FORMULACIÓN', 'U201', [('C/T', '1,86 h/lote'), ('C/O', 'empuje · CIP 1/día'), ('Disp.', '98 %'), ('Uso', pct('U201_Formulacion')), ('Op.', '1 (con U202)')]),
    ('TRATAMIENTO', 'U202 · 92 °C × 5 min', [('C/T', '1,18 h/lote'), ('C/O', 'CIP-C 1,4 h ×3'), ('Disp.', '98 %'), ('Uso', pct('U202_Tratamiento')), ('Op.', '—')]),
    ('FERMENTACIÓN', '4 × 12.000 L', [('C/T', '8,1–9,0 h ciclo'), ('C/O', 'CIP-F 0,75 h'), ('Disp.', '100 %'), ('Uso', pct('U211_Fermentador')), ('Op.', '2')]),
    ('ACONDICIONAM.', 'U215 · U216 · pulmones', [('C/T', '1,0–1,7 h/lote'), ('C/O', 'CIP 1/día'), ('Disp.', '98 %'), ('Uso', f'{pct("U215_Enfriamiento")} · {pct("U216_Separador_griego")}'), ('Op.', '—')]),
    ('ENVASADO', 'U311 · U312 · U313', [('C/T', '≈ 3,5 h/lote'), ('C/O', 'formato 0,75 h'), ('OEE', '≈ 70 %'), ('Uso', f'{pct("U311_Vasos")} · {pct("U312_Botellas")} · {pct("U313_Griego")}'), ('Op.', '4')]),
    ('FIN DE LÍNEA', 'U321–U323 · U341 manual' if MANUAL else 'U321–U323 · U341 · U342', [('C/T', '150 s/bulto' if MANUAL else 'en línea'), ('C/O', '—'), ('Disp.', '100 %'),
     ('Uso', f'{pct("U321_Encajonadora_vasos")} · {pct("U341_Paletizado")}' if MANUAL else f'{pct("U321_Encajonadora_vasos")} · {pct("U342_Envolvedora")}'), ('Op.', '2 a mano' if MANUAL else '2')]),
]
XS = [X0 + i * (BW + GAP) for i in range(len(P))]
CUELLO = 6
for i, (nom, sub, datos) in enumerate(P):
    x = XS[i]
    borde = PCC if i == CUELLO else INK
    rect(x, YB, BW, 62, PCC_S if i == CUELLO else PAPER, borde, 2 if i == CUELLO else 1.4)
    t(x + BW / 2, YB + 26, nom, 14, borde, 800, FD, 'middle')
    t(x + BW / 2, YB + 46, sub, 10.5, MUTED, 400, FB, 'middle')
    rect(x, YB + 70, BW, 26 + 22 * len(datos), PAPER, RULE, 1)
    for j, (k, v) in enumerate(datos):
        yy = YB + 92 + 22 * j
        t(x + 10, yy, k, 11, MUTED, 500, FM)
        t(x + BW - 10, yy, v, 11.5, PCC if (i == CUELLO and k == 'Uso') else INK, 600, FB, 'end')
    if i < len(P) - 1:
        empuje(x + BW + 4, x + BW + GAP - 2, YB + 31)
t(XS[CUELLO] + BW / 2, YB - 12, 'CUELLO DE BOTELLA', 11, PCC, 700, FM, 'middle')
# inventarios (esperas) entre procesos
inventario(XS[0] + BW + GAP / 2, YB + 120, '≤ 4 h', 'leche cruda')
inventario(XS[1] + BW + GAP / 2, YB + 120, '≤ 2 h', 'silos')
inventario(XS[5] + BW + GAP / 2, YB + 120, '≤ 8 h', 'pulmones')
inventario(XS[7] + BW + 70, YB + 120, '≥ 12 h', 'cámara 2–4 °C')
flecha(XS[7] + BW + 4, YB + 31, XS[7] + BW + 70, YB + 31)
flecha(XS[7] + BW + 70, YB + 110, XS[7] + BW + 70, 380, INK)
flecha(XS[7] + BW + 70, 380, 1650, 362)
flecha(150, 368, 150, YB - 2)

# kaizen (oportunidades que atiende la propuesta de automatización)
kaizen(XS[6] + BW / 2, 330, 'Llenadora FFS', '21.600 vasos/h')
kaizen(XS[6] + BW / 2, YB + 238, 'SMED en U312', '0,75 → 0,33 h')
kaizen(1250, 262, 'MES + ISA-95', 'registro digital')
if MANUAL:
    kaizen(XS[7] + BW / 2, YB + 238, 'Celda robotizada', 'paletizado U341')

# ---------------- línea de tiempo (lote de fresa) ----------------
YT = 740
t(48, YT - 18, 'LÍNEA DE TIEMPO · un lote de yogur con fresa (10.000 L)', 12, MUTED, 600, FM, extra='letter-spacing="1"')
esperas = {0: ('4,0 h', 4.0), 1: ('2,0 h', 2.0), 5: ('≤ 8 h*', 0), 7: ('12,0 h', 12.0)}
procesos = ['0,6 h', '0,5 h', '1,9 h', '1,2 h', '8,5 h', '1,1 h', '3,5 h', '0,1 h']
val = [0.6, 0.5, 1.9, 1.2, 8.5, 1.1, 3.5, 0.1]
yh, yl = YT + 10, YT + 52
x = XS[0] - 20
pts = [(x, yh)]
for i in range(len(P)):
    pts += [(XS[i], yh), (XS[i], yl), (XS[i] + BW, yl), (XS[i] + BW, yh)]
    t(XS[i] + BW / 2, yl + 20, procesos[i], 13, INK, 700, FD, 'middle')
    if i in esperas:
        cx = XS[i] + BW + GAP / 2 if i < 7 else XS[i] + BW + 70
        t(cx, yh - 8, esperas[i][0], 12, PCC if esperas[i][1] else MUTED, 700, FD, 'middle')
pts.append((XS[7] + BW + 100, yh))
S.append('<polyline points="' + ' '.join(f'{a},{b}' for a, b in pts) + f'" fill="none" stroke="{INK}" stroke-width="1.6"/>')
lead = sum(val) + sum(v for _, v in esperas.values())
va = 0.5 + 1.2 + 5.25 + 3.5
bx, by = 1270, YT + 86                                       # cuadro horizontal debajo de la escalera
rect(bx, by, 490, 58, ACC_S, ACC, 1.4, 6)
t(bx + 18, by + 22, 'Lead time', 12, MUTED, 500)
t(bx + 18, by + 46, f'≈ {lead:.0f} h (≈ 1,5 días)'.replace('.', ','), 20, ACC, 800, FD)
t(bx + 262, by + 22, 'Valor agregado', 12, MUTED, 500)
t(bx + 262, by + 46, f'≈ {va + 1e-6:.1f} h · {va / lead * 100:.0f} %'.replace('.', ','), 20, OK, 800, FD)

# ---------------- notas ----------------
yN = 912
rect(40, yN, 1720, 112, BG, RULE, 1, 6)
t(60, yN + 26, 'Cómo leer', 13, ACC, 700, FD)
notas = [
    f'Takt: 24 h ÷ {R["lotes_dia"]:.2f} lotes/día ≈ {24 / R["lotes_dia"]:.1f} h por lote'.replace('.', ',') + '. ' + f'La llenadora de vasos U311 (≈ 3,5 h por lote, uso {pct("U311_Vasos")}) marca el ritmo: por ella la línea procesa ≈ {miles(R["litros_dia"])} L/día. * La espera en pulmones no se suma al lead time.',
    'Valor agregado: pasteurización, tratamiento térmico de la base, incubación (5,25 h) y llenado. Las esperas en tanques (≤ 4 h), silos (≤ 2 h) y cámara (reposo ≥ 12 h) son los supuestos del modelo de Tecnomatix.',
    'Fuentes: recetas v1.8 (tiempos de ciclo, OEE, personal) y Tecnomatix Plant Simulation, 12 semanas simuladas (uso de equipos). C/T por lote de 10.000 L; uso = trabajo + alistamiento + fallas.',
]
if MANUAL:
    notas[1] = (f'Paletizado manual: 2 operarios estiban cada bulto de cajas en ≈ 150 s; quedan al {pct("U341_Paletizado")} del tiempo, casi al límite: una pausa o una '
                'ausencia llena las bandas y frena las encajonadoras. La celda robotizada (kaizen) elimina ese riesgo.')
for i, s in enumerate(notas):
    t(60, yN + 50 + 20 * i, s, 12, INK)

defs = (f'<defs><pattern id="rayas" width="8" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">'
        f'<rect width="8" height="10" fill="{PAPER}"/><rect width="4" height="10" fill="{INK}"/></pattern>'
        f'<marker id="punta" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
        f'<marker id="punta_a" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ACC}"/></marker></defs>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(S) + '</svg>'
open(os.path.join(D, NOMBRE + '.svg'), 'w', encoding='utf-8').write(svg)
html = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>VSM línea de yogures</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
        f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:{BG}}}svg{{display:block}}</style></head><body>{svg}</body></html>')
open(os.path.join(D, NOMBRE + '.html'), 'w', encoding='utf-8').write(html)
print('ok', f'lead {lead:.1f} h, VA {va:.2f} h')
