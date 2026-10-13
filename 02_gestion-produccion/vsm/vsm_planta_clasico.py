# VSM del estado actual de la planta completa (tronco común + yogurts, quesos y leche UHT) con la notación clásica
# de Rother y Shook, igual que vsm_clasico.py. Datos: simulación planta-150k (12 semanas) y recetas de la planta.
# Uso: python vsm_planta_clasico.py → vsm_planta_3_lineas_clasico.svg / .html (exportar con exportar.mjs 1800 1200)
import os

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, 'vsm_clasico.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- hoja')].replace('W, H = 1800, 1100', 'W, H = 1800, 1200'))

U = {k: v['ocupado'] for k, v in R['uso'].items()}   # solo la simulación de la planta
rect(0, 0, W, H, '#fff', '#fff', 0)
rect(14, 14, W - 28, H - 28, 'none', K, 1.2)
t(36, 52, 'Mapa de flujo de valor – estado actual', 24, K, 700)
t(36, 76, 'Planta completa: tronco común y líneas de yogurts, quesos y leche UHT · Lácteos Altos de Teusacá', 15, G)

# ---------------- proveedor, control y cliente ----------------
fabrica(52, 100, 'Ganaderos')
caja_datos(52, 188, 150, ['150.000 L/día', '91 lotes/semana'], 12.5)
rect(700, 100, 400, 92)
t(900, 128, 'Control de producción', 16, K, 700, 'middle')
t(900, 152, 'Programa semanal en hoja de cálculo', 13, K, 400, 'middle')
t(900, 172, '35 lotes yogurt · 30 queso · 26 leche UHT', 13, K, 400, 'middle')
fabrica(1612, 100, 'Clientes')
caja_datos(1390, 100, 205, ['Supermercados, tiendas', 'y distribuidores', 'Despacho diario por línea'], 12.5)
rayo(1386, 150, 1104, 'Pedidos diarios por línea')
rayo(696, 150, 206, 'Programa de acopio semanal')
flecha(900, 192, 900, 352)
t(910, 252, 'Programa impreso por turno a cada línea', 12.5)
kaizen(1250, 240, 'MES + ISA-95', 'un solo programa', 92, 32)
camion(60, 262, '')
t(156, 290, '≈ 8 cisternas/día', 12.5)
envio_v(103, 312, 346)

# ---------------- tronco común ----------------
def proceso(x, y, nom, sub, datos, bw=150, grueso=1.5, ops=None):
    rect(x, y, bw, 70, '#fff', K, grueso)
    line(x, y + 28, x + bw, y + 28, 1)
    t(x + bw / 2, y + 20, nom, 14, K, 700, 'middle')
    t(x + bw / 2, y + 48, sub, 11, G, 400, 'middle')
    if ops:
        operario(x + 20, y + 60, ops)
    caja_datos(x, y + 78, bw, datos, 12.5)


proceso(28, 350, 'Recepción', 'U111 · U112', ['C/T = 0,6 h', f'Uso = {pct("U111_Recepcion")}'])
inventario(103, 488, '4 h', 'leche cruda')
proceso(28, 570, 'Pasteurización', 'U121 · U122 HTST', ['C/T = 0,5 h', f'Uso = {pct("U121_Pasteurizador")}'])
inventario(103, 708, '2 h', 'silos por línea')
t(103, 792, 'U123 · U124 · U125', 11.5, G, 400, 'middle')
line(28, 815, 178, 815, 0.8)
t(103, 835, 'Tronco común', 13, K, 700, 'middle')
t(103, 853, '150.000 L/día', 12, G, 400, 'middle')
line(190, 380, 190, 350 + 2 * 240 + 44, 1.5)      # reparto a las tres líneas

# ---------------- tres líneas ----------------
LINEAS = [
    ('Yogurts', '≈ 57.500 L/día', [
        ('Formulación', 'U201 · U202', '3,1 h', pct('U202_Tratamiento'), '1'),
        ('Fermentación', '4 × 12.000 L', '8,1–9,0 h', pct('U211_Fermentador'), '2'),
        ('Acondicionam.', 'U215 · U216', '1,0–1,7 h', pct('U215_Enfriamiento'), None),
        ('Envasado', 'U311 · U312 · U313', '3,5 h', pct('U311_Vasos'), '4'),
        ('Paletizado', 'manual · U341', '150 s/bulto', pct('U341_Paletizado'), '2')],
     (2, '≤ 8 h', 'pulmones'), ('12 h', 'cámara'), 3, (35, 10.5), ('Llenadora FFS', '21.600 vasos/h')),
    ('Quesos', '≈ 49.400 L/día', [
        ('Tinas', 'U221A–C', '3,5 h', pct('U221A_Tina'), '2'),
        ('Hilado', 'U223', '1,0 h', pct('U223_Hilado'), '1'),
        ('Salmuera', 'U224', '8,0 h', '—', None),
        ('Empaque', 'U321 al vacío', '1,2 h', pct('U321_Empaque_vacio'), '1'),
        ('Paletizado', 'manual', '108 s/bulto', pct('Paletizado_quesos'), '2')],
     None, ('12 h', 'cámara'), None, (32, 13.7), ('Paletizado', 'robotizado común')),
    ('Leche UHT', '≈ 43.100 L/día', [
        ('Mezcla', 'U231', '1,0 h', pct('U231_Mezcla'), '1'),
        ('UHT', 'U232', '1,0 h', pct('U232_UHT'), None),
        ('Tanque aséptico', 'U233', 'pulmón', '—', None),
        ('Envasado', 'U331 aséptica', '2,0 h', pct('U331_Envasadora_aseptica'), '1'),
        ('Paletizado', 'manual', '72 s/bulto', pct('Paletizado_leche'), '2')],
     None, ('24 h', 'cuarentena'), None, (35, 4.5), ('Liberación', 'con prueba rápida')),
]
BW, GAP, X0, Y0, LH = 150, 50, 236, 350, 240
for k, (nom, cap, procs, inv_mid, inv_fin, cuello, (lead, va), kz) in enumerate(LINEAS):
    y = Y0 + k * LH
    if k:
        line(206, y - 22, W - 30, y - 22, 0.8, '#999', 'stroke-dasharray="6 4"')
    t(X0, y - 4, f'{nom} · {cap}', 14, K, 700)
    empuje(190, X0 - 4, y + 44)
    for i, (pn, ps, ct, uso, ops) in enumerate(procs):
        x = X0 + i * (BW + GAP)
        proceso(x, y + 8, pn, ps, [f'C/T = {ct}', f'Uso = {uso}'], BW, 2.4 if cuello == i else 1.5, ops)
        if i < len(procs) - 1:
            empuje(x + BW + 5, x + BW + GAP - 5, y + 44)
            if inv_mid and inv_mid[0] == i:
                inventario(x + BW + GAP / 2, y + 96, inv_mid[1], inv_mid[2])
    if cuello is not None:
        t(X0 + cuello * (BW + GAP) + BW / 2, y + 160, 'Cuello de botella', 13, RED, 700, 'middle')
    xc = X0 + 5 * (BW + GAP) + 6
    flecha(xc - 52, y + 44, xc - 16, y + 44)
    inventario(xc, y + 26, inv_fin[0], inv_fin[1])
    rect(1300, y + 8, 200, 70)
    t(1310, y + 32, f'Lead time = {lead} h', 14, K, 700)
    t(1310, y + 52, f'T. valor agregado = {str(va).replace(".", ",")} h', 12.5)
    t(1310, y + 70, f'({va / lead * 100:.0f} % del lead time)', 12, G)
    kaizen(1620, y + 44, kz[0], kz[1], 100, 34)
    envio(1504, 1540, y + 140) if False else None
# ---------------- pie y cajetín ----------------
t(36, H - 70, 'C/T por lote de 10.000 L, según las recetas. Uso = trabajo + alistamiento + fallas, de la simulación de 12 semanas (modelo planta-150k).', 12.5, G)
t(36, H - 50, 'Solo la línea de yogurts está al límite (llenadora de vasos U311); quesos y leche UHT tienen holgura.', 12.5, G)
defs = (f'<defs><marker id="p" markerWidth="12" markerHeight="12" refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{K}"/></marker></defs>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}' + '\n'.join(s for s in S if s) + '</svg>'
N = 'vsm_planta_3_lineas_clasico'
open(os.path.join(D, N + '.svg'), 'w', encoding='utf-8').write(svg)
open(os.path.join(D, N + '.html'), 'w', encoding='utf-8').write(
    '<!doctype html><html lang="es"><head><meta charset="utf-8"><title>VSM planta</title>'
    f'<style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;background:#fff}}svg{{display:block}}</style></head><body>{svg}</body></html>')
print('ok')
