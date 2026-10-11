# VSM del estado actual de la PLANTA COMPLETA (acta 9-oct-2026): tronco común de 150.000 L/día y tres líneas
# (yogures, quesos y leche UHT), cada una con sus procesos, inventarios, oportunidades kaizen y línea de tiempo.
# Datos: modelo de Tecnomatix planta-150k (12 semanas) y recetas (v1.8 de yogures y básicas de la planta).
# Genera vsm_planta_3_lineas.svg y .html. Uso: python vsm_planta.py
import os, json

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, 'vsm_actual.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- marco y título')].replace('W, H = 1800, 1060', 'W, H = 1800, 1270'))   # paleta y figuras
Q, QS, L_, LS, Y_, YS = '#a37c12', '#fbf3dc', '#3d8a52', '#e3f2e6', '#b8325a', '#f8e3ea'

S.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
rect(20, 20, W - 40, H - 40, PAPER, RULE, 1, 10)
t(48, 64, 'VSM · ESTADO ACTUAL · PLANTA COMPLETA', 12, MUTED, 600, FM, extra='letter-spacing="1.5"')
t(48, 96, 'Planta láctea · Lácteos Altos de Teusacá', 30, INK, 800, FD)
t(48, 122, f'150.000 L/día (acta 9-oct-2026) en tres líneas · 91 lotes de 10.000 L por semana · 6 días/semana · Tecnomatix: '
           f'{miles(R["recepcion_dia"])} L/día recibidos', 13, MUTED)
t(W - 48, 64, 'Mekvra · APM 2026-2S · UNAL', 12, MUTED, 600, FM, 'end')

fabrica(60, 160, 170, 'GANADEROS', ['Acopio de la Sabana', '150.000 L/día'])
fabrica(1570, 160, 170, 'CLIENTES', ['Supermercados, tiendas', 'y distribuidores'])
rect(700, 152, 400, 92, ACC_S, ACC, 1.6, 6)
t(900, 180, 'PLANEACIÓN DE LA PRODUCCIÓN', 15, ACC, 800, FD, 'middle')
t(900, 202, 'Programa semanal en hoja de cálculo · sin MES', 12.5, INK, 400, FB, 'middle')
t(900, 222, '35 lotes de yogur · 30 de queso · 26 de leche UHT', 12.5, INK, 400, FB, 'middle')
rayo(1566, 190, 1104, 190)
t(1335, 178, 'Pedidos diarios por línea', 11.5, MUTED, 400, FB, 'middle')
rayo(696, 190, 234, 190)
t(465, 178, 'Programa de acopio semanal', 11.5, MUTED, 400, FB, 'middle')
kaizen(1240, 270, 'MES + ISA-95', 'un solo programa')

# ---------------- tronco común (columna izquierda) ----------------
YL0 = 330
rect(40, YL0, 250, 790, '#eef1f6', '#5a6987', 1.2, 8)
t(165, YL0 + 26, 'TRONCO COMÚN', 14, '#5a6987', 800, FD, 'middle')
t(165, YL0 + 44, '150.000 L/día · 2 tanques', 11, MUTED, 400, FB, 'middle')
camion(125, YL0 + 60, 'Cisternas · ≈ 8 por día')
bloques = [('RECEPCIÓN', 'U111/U112', [('C/T', '0,6 h/lote'), ('Uso', pct('U111_Recepcion'))]),
           ('PASTEURIZACIÓN', 'U121/U122 · HTST 20 m³/h', [('C/T', '0,5 h/lote'), ('Uso', pct('U121_Pasteurizador'))])]
for i, (nom, sub, dat) in enumerate(bloques):
    y = YL0 + 140 + i * 210
    rect(65, y, 200, 56, PAPER, INK, 1.4)
    t(165, y + 24, nom, 13.5, INK, 800, FD, 'middle')
    t(165, y + 42, sub, 10.5, MUTED, 400, FB, 'middle')
    rect(65, y + 62, 200, 18 + 22 * len(dat), PAPER, RULE, 1)
    for j, (k, v) in enumerate(dat):
        t(77, y + 84 + 22 * j, k, 11, MUTED, 500, FM)
        t(253, y + 84 + 22 * j, v, 11.5, INK, 600, FB, 'end')
    if i == 0:
        inventario(165, y + 140, '≤ 4 h', 'leche cruda 2 × 60 m³')
        flecha(165, y + 118, 165, y + 138)
flecha(165, YL0 + 116, 165, YL0 + 138)
t(165, YL0 + 640, 'Silos por línea', 11.5, INK, 700, FB, 'middle')
t(165, YL0 + 658, 'U123A–C · U124 · U125', 10.5, MUTED, 400, FB, 'middle')
inventario(165, YL0 + 672, '≤ 2 h', 'leche pasteurizada')

# ---------------- tres franjas ----------------
LINEAS = [
    ('YOGURES', '≈ 57.500 L/día · 35 lotes/semana', Y_, YS, [
        ('FORMULACIÓN', 'U201 · U202 92 °C', '3,1 h', pct('U202_Tratamiento')),
        ('FERMENTACIÓN', '4 × 12.000 L', '8,1–9,0 h', pct('U211_Fermentador')),
        ('ACONDICIONAM.', 'U215 · U216 · pulmones', '1,0–1,7 h', pct('U215_Enfriamiento')),
        ('ENVASADO', 'U311 · U312 · U313', '≈ 3,5 h', pct('U311_Vasos')),
        ('FIN DE LÍNEA', 'U341 manual · 2 op.', '150 s/bulto', pct('U341_Paletizado'))],
     ('≤ 8 h', 'pulmones', 2), ('≥ 12 h', 'cámara 2–4 °C'), 3, (35.4, 10.45),
     f'{miles(R["vasos_U311_dia"])} vasos · {miles(R["botellas_U312_dia"])} botellas · {miles(R["griego_U313_dia"])} griego'),
    ('QUESOS', '≈ 49.400 L/día · 30 lotes/semana', Q, QS, [
        ('TINAS', 'Q201–Q203 · 10.000 L', '3,5 h', pct('Q201_Tina')),
        ('HILADO', 'Q301 hiladora', '1,0 h', pct('Q301_Hilado')),
        ('SALMUERA', 'Q302 · 20 % NaCl', '8,0 h', '—'),
        ('EMPAQUE', 'Q311 al vacío', '1,2 h', pct('Q311_Empaque_vacio')),
        ('PALETIZADO', 'Q341 manual · 2 op.', '108 s/bulto', pct('Q341_Paletizado'))],
     None, ('12 h', 'cámara quesos'), None, (32.3, 13.7), f'≈ {miles(R["queso_kg_dia"])} kg de queso'),
    ('LECHE UHT', '≈ 43.100 L/día · 26 lotes/semana', L_, LS, [
        ('MEZCLA', 'L201 · cacao en LC', '1,0 h', pct('L201_Mezcla')),
        ('UHT', 'L202 · 137 °C × 4 s', '1,0 h', pct('L202_UHT')),
        ('TANQUE ASÉPTICO', 'L203 · 20.000 L', 'pulmón', '—'),
        ('ENVASADO', 'L311 aséptica 1 L', '2,0 h', pct('L311_Envasadora_aseptica')),
        ('PALETIZADO', 'L341 manual · 2 op.', '72 s/bulto', pct('L341_Paletizado'))],
     None, ('24 h', 'cuarentena · bodega'), None, (35.1, 4.5), f'≈ {miles(R["leche_envases_dia"])} envases de 1 L'),
]
X0, BW, GAP, LH = 330, 182, 42, 262
for k, (nom, sub, c, cs, procs, inv_mid, inv_fin, cuello, (lead, va), salida) in enumerate(LINEAS):
    y0 = YL0 + k * LH
    rect(310, y0, 1450, LH - 14, cs, c, 1.2, 8)
    t(330, y0 + 26, nom, 15, c, 800, FD)
    t(330 + 11 * len(nom) + 22, y0 + 26, sub, 11.5, MUTED)
    t(1740, y0 + 26, salida, 11.5, INK, 600, FB, 'end')
    flecha(290, y0 + 96, X0 - 4, y0 + 96, c, 1.6)                              # leche desde el silo
    for i, (pn, ps, ct, uso) in enumerate(procs):
        x, yb = X0 + i * (BW + GAP), y0 + 64
        es_c = (cuello == i)
        rect(x, yb, BW, 52, PCC_S if es_c else PAPER, PCC if es_c else INK, 2 if es_c else 1.3)
        t(x + BW / 2, yb + 22, pn, 13, PCC if es_c else INK, 800, FD, 'middle')
        t(x + BW / 2, yb + 40, ps, 10.5, MUTED, 400, FB, 'middle')
        rect(x, yb + 58, BW, 62, PAPER, RULE, 1)
        t(x + 10, yb + 80, 'C/T', 11, MUTED, 500, FM)
        t(x + BW - 10, yb + 80, ct, 11.5, INK, 600, FB, 'end')
        t(x + 10, yb + 104, 'Uso', 11, MUTED, 500, FM)
        t(x + BW - 10, yb + 104, uso, 11.5, PCC if es_c else INK, 600, FB, 'end')
        if es_c:
            t(x + BW / 2, yb - 8, 'CUELLO DE BOTELLA', 10.5, PCC, 700, FM, 'middle')
        if i < len(procs) - 1:
            if inv_mid and i == inv_mid[2]:
                inventario(x + BW + GAP / 2, yb + 74, inv_mid[0], inv_mid[1])
            empuje(x + BW + 3, x + BW + GAP - 2, yb + 26)
    xf = X0 + 5 * (BW + GAP) - GAP + 20
    flecha(xf - 18, y0 + 90, xf + 30, y0 + 90, INK)
    inventario(xf + 60, y0 + 74, inv_fin[0], inv_fin[1])
    # mini línea de tiempo y lead time por línea
    yy = y0 + 214
    t(330, yy, f'Lead time ≈ {lead:.0f} h'.replace('.', ','), 13, ACC, 800, FD)
    t(500, yy, f'valor agregado ≈ {va:.1f} h ({va / lead * 100:.0f} %)'.replace('.', ','), 13, OK, 700, FD)
    w_va = 640 * va / lead
    rect(820, yy - 12, 640 * 0.85, 14, '#f3d6cb', PCC, 0.8, 3)
    rect(820, yy - 12, w_va * 0.85, 14, '#cfe8d8', OK, 0.8, 3)
kaizen(1680, YL0 + 178, 'Llenadora FFS', '+ SMED en U312')
kaizen(1680, YL0 + LH + 178, 'Celda robotizada', 'paletizado común')
kaizen(1680, YL0 + 2 * LH + 178, 'Liberación', 'con prueba rápida')

yN = YL0 + 3 * LH + 6
rect(40, yN, 1720, 92, BG, RULE, 1, 6)
t(60, yN + 26, 'Cómo leer', 13, ACC, 700, FD)
notas = [
    'Un VSM por línea sobre el mismo tronco común. Uso = trabajo + alistamiento + fallas en 12 semanas simuladas en Tecnomatix (modelo planta-150k). C/T por lote de 10.000 L.',
    'La única línea al límite es la de yogures (llenadora de vasos U311); quesos y leche UHT tienen holgura para crecer con el aumento de acopio del contrato. Valor agregado: tratamientos térmicos, fermentación o cuajado, hilado, salado y envasado.',
    'Las esperas en tanques (≤ 4 h), silos (≤ 2 h), cámara y cuarentena son supuestos del modelo; los tiempos de quesos y leche UHT salen de las recetas básicas de la planta v1.0.',
]
for i, s in enumerate(notas):
    t(60, yN + 48 + 18 * i, s, 11.5, INK)

defs = (f'<defs><pattern id="rayas" width="8" height="10" patternUnits="userSpaceOnUse"><rect width="8" height="10" fill="{PAPER}"/>'
        f'<rect width="4" height="10" fill="{INK}"/></pattern>'
        f'<marker id="punta" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
        f'<marker id="punta_a" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ACC}"/></marker></defs>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(S) + '</svg>'
open(os.path.join(D, 'vsm_planta_3_lineas.svg'), 'w', encoding='utf-8').write(svg)
html = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>VSM planta</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
        f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:{BG}}}svg{{display:block}}</style></head><body>{svg}</body></html>')
open(os.path.join(D, 'vsm_planta_3_lineas.html'), 'w', encoding='utf-8').write(html)
print('ok')
