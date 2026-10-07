# Modelo VSM de la planta láctea en Plant Simulation 2404 (licencia estudiantil, sin la librería VSM de Siemens).
# Flujo de valor completo: cisternas -> recepción -> leche cruda -> clarificación/HTST -> silos S1/S2/S3 ->
# líneas de yogur, mozzarella y kéfir -> envasado por presentación -> paletizado U341 -> cámara U411 -> clientes.
# El mapa VSM (zonas, carteles, cajas de datos, flujo de información y escalera de tiempos) se dibuja en el Frame.
# Uso: python construir_vsm.py <base|prop> <salida.spp|-> [dias]
import sys, os, time, json
import win32com.client as w
import modelo_capacidad as MC

D = os.path.dirname(os.path.abspath(__file__))
ICO = os.path.join(D, 'iconos')
H = 3600.0
esc = sys.argv[1]
OUT = sys.argv[2]
DIAS = float(sys.argv[3]) if len(sys.argv) > 3 else 30
S = MC.ESC[esc]
CAP = MC.todo()[esc]


def h(x):
    return int(round(x * H))


def n1(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


# ---------------- tiempos (mismos supuestos de construir_modelo.py) ----------------
P = {
    'base': dict(y_incub=7.0, y_enfr=1.5, y_cip=1.0, lib=0.5, pulm=1, pulm_cip=0.75, u202_cambios=4, k_ferm=24.0, k_vac=0.75,
                 k_ferms=3, k_cip=1.0, madur=24.0, k_tq=3, tq_cip=0.75, q_corte=0.25, q_acid=3.0, disp=0.854),
    'prop': dict(y_incub=5.0, y_enfr=1.25, y_cip=0.75, lib=0.0, pulm=2, pulm_cip=0.5, u202_cambios=1, k_ferm=20.0, k_vac=0.5,
                 k_ferms=4, k_cip=0.75, madur=0.0, k_tq=2, tq_cip=0.5, q_corte=0.0, q_acid=2.5, disp=0.948),
}[esc]
perf, A = S['perf'], P['disp']           # rendimiento de llenadoras y disponibilidad de tiempo (CIP, descansos, turnos)
fmt = S['formato']                        # cambio de formato (h)
u202_y = 1.25 + (3 * 0.75 + P['u202_cambios'] * 0.75 + 1.5) / 6
ferm_y = 0.25 + P['y_incub'] + P['y_enfr'] + P['y_cip']
ferm_k = 0.33 + 0.25 + P['k_ferm'] + 0.5 + P['k_vac'] + P['k_cip']


def llen(kg, und_h, g):                   # horas de llenado de una presentación, con rendimiento y disponibilidad
    return kg / (und_h * g / 1000 * perf) / A


# yogur: lote 10.000 kg = 45 % YF150 (U311) + 35 % YF1000 + 20 % YF1750 (U312)
t_yf150 = llen(4500, 12000, 150)
t_yf1000, t_yf1750 = llen(3500, 4000, 1000), llen(2000, 2500, 1750)
U311 = P['lib'] + t_yf150 + (P['pulm_cip'] if P['pulm'] == 1 else 0)   # el pulmón U214 alimenta a U311 (cuello)
U312 = (t_yf1000 + t_yf1750 + S['n_formato']['U312'] * fmt / 6) / 2      # promedio por presentación
# mozzarella: lote ≈ 500 kg = 20 % QM250 (U322) + 40 % QM400 + 40 % QM1000 (U321)
t_qm250, t_qm400, t_qm1000 = llen(100, 1200, 250), llen(200, 900, 400), llen(200, 450, 1000)
U321 = (t_qm400 + t_qm1000 + S['n_formato']['U321'] * fmt / 5) / 2
U322 = t_qm250
# kéfir: lote 5.000 kg = 40 % KF240 + 35 % KF500 + 25 % KF1000, todo en U331
t_kf240, t_kf500, t_kf1000 = llen(2000, 6000, 240), llen(1750, 4500, 500), llen(1250, 3000, 1000)
U331 = (t_kf240 + t_kf500 + t_kf1000 + S['n_formato']['U331'] * fmt / 3) / 3
TQK = P['madur'] + 0.5 + P['tq_cip']      # tanque de kéfir: maduración + vaciado + CIP; se libera al pasar a U331
U341 = CAP['aux']['cajas'] / 750 / 42     # celda de paletizado: 750 cajas/h, 42 sub-lotes por día

MTBF = {'env': (40.0, 1.0), 'proc': (80.0, 1.5)} if esc == 'base' else {'env': (60.0, 0.75), 'proc': (120.0, 1.0)}

# ---------------- objetos ----------------
MF = '.MaterialFlow'
L = ['var m: object := .Models.Model', 'var o: object', 'var t: table']
ICONOS, CON = {}, []
COORD = {}


def obj(name, cls, x, y, proc=None, icon=None, extra=()):
    global L
    L += [f'o := {cls}.createObject(m, {x}, {y})', f'o.Name := "{name}"']
    if proc is not None:
        L.append(f'o.ProcTime := {h(proc)}')
    L += [x_.replace('@', 'o') for x_ in extra]
    if icon:
        ICONOS[name] = icon
    COORD[name] = (x, y)


def mu(name):
    L.append(f'o := .MUs.Part.duplicate(.MUs, "{name}")')


for n in ('Lote_Yogur', 'YF1000', 'YF1750', 'Lote_Queso', 'QM1000', 'QM250', 'Lote_Kefir', 'KF500', 'KF1000'):
    mu(n)

# franjas (y) de cada zona
YT, YY, YQ, YK = 262, 445, 845, 1245       # fila de objetos: tronco, yogur, mozzarella, kéfir
XS = 480                                   # columna de los silos

# secuencia diaria de 14 lotes (6 yogur, 5 mozzarella, 3 kéfir)
SEQ = 'YQYKYQYQYKYQKQ'
obj('Secuencia_lotes', '.InformationFlow.DataTable', 1360, 285)
L += ['o.setDataType(1, "object")', 'o.setDataType(2, "integer")', 'o.setDataType(3, "string")']
for i, c in enumerate(SEQ, 1):
    nm = {'Y': 'Lote_Yogur', 'Q': 'Lote_Queso', 'K': 'Lote_Kefir'}[c]
    L += [f'o[1, {i}] := .MUs.{nm}', f'o[2, {i}] := 1', f'o[3, {i}] := "{nm}"']

# tronco común
obj('Cisternas', MF + '.Source', 80, YT, icon='vsm_cisterna',
    extra=['@.MUSelection := "Sequence Cyclical"', '@.Path := m.Secuencia_lotes', f'@.Interval := {h(24 / 14)}'])
obj('U111_U112', MF + '.Station', 210, YT, 0.5, 'vsm_recepcion')
obj('U113_U114', MF + '.Buffer', 340, YT, icon='vsm_crudo', extra=['@.Capacity := -1', f'@.ProcTime := {h(S["crudo_h"])}'])
obj('U121_U122', MF + '.Station', 440, YT, 0.35, 'vsm_htst')
CON += [('Cisternas', 'U111_U112'), ('U111_U112', 'U113_U114'), ('U113_U114', 'U121_U122')]
for sname, y, ic, dx in (('S1', YY, 'vsm_silo1', 0), ('S2', YQ, 'vsm_silo2', 30), ('S3', YK, 'vsm_silo3', 60)):
    obj(sname, MF + '.Buffer', XS + dx, y, icon=ic, extra=['@.Capacity := -1', f'@.ProcTime := {h(S["silo_h"])}'])
    CON.append(('U121_U122', sname))
RUTA_HTST = [('Lote_Yogur', 1), ('Lote_Queso', 2), ('Lote_Kefir', 3)]

# línea 1 · yogur
obj('U201', MF + '.Station', 680, YY, 1.1 + 0.5, 'formulacion')
obj('U202', MF + '.Station', 790, YY, u202_y, 'u202')
for i, x in enumerate((900, 965, 1030)):
    obj(f'U21{i + 1}', MF + '.Station', x, YY + (-28, 0, 28)[i], ferm_y, 'fermentador_yogur')
CON += [('S1', 'U201'), ('U201', 'U202')] + [('U202', f'U21{i}') for i in (1, 2, 3)]
prev = [f'U21{i}' for i in (1, 2, 3)]
if P['pulm'] > 1:
    obj('U215', MF + '.Buffer', 1110, YY, icon='pulmones', extra=[f'@.Capacity := {P["pulm"] - 1}'])
    CON += [(p, 'U215') for p in prev]
    prev = ['U215']
obj('U214', MF + '.DismantleStation', 1190, YY, 0.0, 'vsm_pulmon',
    extra=['t := @.DismantleTable', 't[1, 1] := .MUs.YF1000', 't[2, 1] := 1', 't[3, 1] := 2',
           't[1, 2] := .MUs.YF1750', 't[2, 2] := 1', 't[3, 2] := 2', '@.DismantleTable := t', '@.MainMU := 1', '@.Sequence := "MUs exiting independent of other MUs"'])
CON += [(p, 'U214') for p in prev]
obj('U311', MF + '.Station', 1330, YY - 55, U311, 'vsm_u311')
obj('U312', MF + '.Station', 1330, YY + 55, U312, 'vsm_u312')
CON += [('U214', 'U311'), ('U214', 'U312')]

# línea 2 · mozzarella
obj('U221', MF + '.Station', 680, YQ, 2.93 + P['q_corte'] + 0.5, 'tina')
obj('U222', MF + '.Station', 790, YQ, P['q_acid'] + 0.25, 'banda')
obj('U223', MF + '.Station', 900, YQ, 500 / 600 + 0.25, 'hiladora')
for i, dy in enumerate((-90, -30, 30, 90)):
    obj(f'U224_{i + 1}', MF + '.Station', 1020, YQ + dy, 3.0, 'salmuera')
obj('U224_salida', MF + '.DismantleStation', 1190, YQ, 0.0, 'vsm_reparto_q',
    extra=['t := @.DismantleTable', 't[1, 1] := .MUs.QM1000', 't[2, 1] := 1', 't[3, 1] := 1',
           't[1, 2] := .MUs.QM250', 't[2, 2] := 1', 't[3, 2] := 2', '@.DismantleTable := t', '@.MainMU := 1', '@.Sequence := "MUs exiting independent of other MUs"'])
obj('U321', MF + '.Station', 1330, YQ - 55, U321, 'vsm_u321')
obj('U322', MF + '.Station', 1330, YQ + 55, U322, 'vsm_u322')
CON += [('S2', 'U221'), ('U221', 'U222'), ('U222', 'U223')] + [('U223', f'U224_{i}') for i in (1, 2, 3, 4)]
CON += [(f'U224_{i}', 'U224_salida') for i in (1, 2, 3, 4)] + [('U224_salida', 'U321'), ('U224_salida', 'U322')]

# línea 3 · kéfir
obj('U202_K', MF + '.Station', 790, YK, 0.75, 'u202')
FK = ['U231', 'U232', 'U233'] + (['U235'] if P['k_ferms'] == 4 else [])
for i, nm in enumerate(FK):
    obj(nm, MF + '.Station', 900 + 65 * i, YK + (-28, 0, 28, 0)[i], ferm_k, 'fermentador_kefir')
TK = ['U234A', 'U234B', 'U234C'][:P['k_tq']]
for i, nm in enumerate(TK):
    dy = (-70, 0, 70)[i] if len(TK) == 3 else (-40, 40)[i]
    obj(nm, MF + '.DismantleStation', 1190, YK + dy, TQK, 'tanque_kefir',
        extra=['t := @.DismantleTable', 't[1, 1] := .MUs.KF500', 't[2, 1] := 1', 't[3, 1] := 1',
               't[1, 2] := .MUs.KF1000', 't[2, 2] := 1', 't[3, 2] := 1', '@.DismantleTable := t', '@.MainMU := 1', '@.Sequence := "MUs exiting independent of other MUs"'])
obj('U331', MF + '.Station', 1330, YK, U331, 'vsm_u331')
CON += [('S3', 'U202_K')] + [('U202_K', f) for f in FK] + [(f, t_) for f in FK for t_ in TK] + [(t_, 'U331') for t_ in TK]

# fin de línea y despacho
XF = 1560
obj('U341', MF + '.Station', XF, YQ, U341, 'vsm_paletizado')
obj('U411', MF + '.Buffer', XF + 130, YQ, icon='vsm_camara', extra=['@.Capacity := -1', f'@.ProcTime := {h(S["pt_h"])}'])
obj('Clientes_yogur', MF + '.Drain', 1830, YY, icon='vsm_despacho_y')
obj('Clientes_mozzarella', MF + '.Drain', 1830, YQ, icon='vsm_despacho_q')
obj('Clientes_kefir', MF + '.Drain', 1830, YK, icon='vsm_despacho_k')
CON += [(f, 'U341') for f in ('U311', 'U312', 'U321', 'U322', 'U331')] + [('U341', 'U411')]
CON += [('U411', 'Clientes_yogur'), ('U411', 'Clientes_mozzarella'), ('U411', 'Clientes_kefir')]
RUTA_CAMARA = [(n, 1) for n in ('Lote_Yogur', 'YF1000', 'YF1750')] + [(n, 2) for n in ('Lote_Queso', 'QM1000', 'QM250')] + \
              [(n, 3) for n in ('Lote_Kefir', 'KF500', 'KF1000')]

for a, b in CON:
    L.append(f'.MaterialFlow.Connector.connect(m.{a}, m.{b})')


def ruta(nm, filas):
    out = [f'm.{nm}.ExitStrategy := "MU Attribute"', f'm.{nm}.AttributeType := "String"', f't := m.{nm}.ExitStrategyMUAttributeList']
    for i, (v, sc) in enumerate(filas, 1):
        out += [f't[1, {i}] := "Name"', f't[2, {i}] := "{v}"', f't[3, {i}] := {sc}']
    return out + [f'm.{nm}.ExitStrategyMUAttributeList := t']


L += ruta('U121_U122', RUTA_HTST) + ruta('U411', RUTA_CAMARA)
FALLAS = {n: 'env' for n in ('U311', 'U312', 'U321', 'U322', 'U331')}
FALLAS.update({n: 'proc' for n in ('U201', 'U202', 'U202_K', 'U221', 'U222', 'U223', 'U121_U122')})
for nm, tipo in FALLAS.items():
    mtbf, mttr = MTBF[tipo]
    L += [f'm.{nm}.Failures.createFailure("Falla")', f'm.{nm}.Failures.Falla.AvailabilityOn := true',
          f'm.{nm}.Failures.Falla.Availability := {round(100 * mtbf / (mtbf + mttr), 2)}',
          f'm.{nm}.Failures.Falla.MTTR := {h(mttr)}', f'm.{nm}.Failures.Falla.Mode := "ProcessingTime"']
L.append(f'm.EventController.End := {h(24 * DIAS)}')
L += ['m.EventController.Speed := 60', 'm.EventController.XPos := 1290', 'm.EventController.YPos := 285']
for nm, f in ICONOS.items():
    p = os.path.join(ICO, f + '.bmp').replace(chr(92), chr(92) * 2)
    L.append(f'm.{nm}.setIconFromFile(1, "{p}")')

# ---------------- dibujo del mapa VSM ----------------
G = []
NAVY, INK, SOFT, ACC = (27, 42, 120), (20, 33, 61), (91, 100, 117), (163, 72, 11)
ZONA = {'T': ((232, 235, 242), (120, 130, 150)), 'Y': ((252, 226, 234), (200, 70, 105)),
        'Q': ((253, 242, 205), (190, 140, 20)), 'K': ((222, 236, 250), (50, 110, 175)), 'F': ((236, 238, 243), (90, 100, 120))}


def rgb(c):
    return f'makeRGBValue({c[0]}, {c[1]}, {c[2]})'


def rect(x, y, w_, h_, c, lw=-1, layer=1):
    G.append(f'm.drawRectangle({layer}, {int(x)}, {int(y)}, {int(w_)}, {int(h_)}, {rgb(c)}, {lw})')


def line(x1, y1, x2, y2, c, lw=2, layer=2):
    G.append(f'm.drawLine({layer}, {int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}, {rgb(c)}, {lw})')


def dash(x1, y1, x2, y2, c, lw=2, seg=10):
    import math
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) // (seg * 2)))
    for i in range(n):
        a, b = i / n, (i + 0.5) / n
        line(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a, x1 + (x2 - x1) * b, y1 + (y2 - y1) * b, c, lw)


def text(x, y, s, size=12, c=INK):
    s = s.replace('"', "'")
    G.append(f'm.drawText(3, {int(x)}, {int(y)}, {rgb(c)}, {size}, "{s}")')


def flecha(x1, y, x2, c=NAVY):       # flecha horizontal de información
    dash(x1, y, x2, y, c)
    d = 8 if x2 > x1 else -8
    line(x2, y, x2 - d, y - 6, c)
    line(x2, y, x2 - d, y + 6, c)


def fabrica(x, y, w_, h_, l1, l2):
    rect(x, y + 28, w_, h_ - 28, (255, 255, 255))
    rect(x, y + 28, w_, h_ - 28, NAVY, 2, 2)
    for i in range(3):                 # techo en diente de sierra
        x0 = x + i * 36
        line(x0, y + 28, x0 + 30, y + 4, NAVY)
        line(x0 + 30, y + 4, x0 + 30, y + 28, NAVY)
    text(x + 12, y + 58, l1, 13, INK)
    text(x + 12, y + 78, l2, 11, SOFT)


def zona(k, x, y, w_, h_, titulo, sub='', tx=None):
    fondo, borde = ZONA[k]
    rect(x, y, w_, h_, fondo)
    rect(x, y, w_, h_, borde, 3, 2)
    rect(x, y, 12, h_, borde)
    tx = x + 24 if tx is None else tx
    text(tx, y + 28, titulo, 17, borde)
    for i, s_ in enumerate(sub.split('|') if sub else []):
        text(tx, y + 48 + 16 * i, s_, 10, SOFT)


def rotulo(cx, y, s, c=INK, size=10):
    text(cx - len(s) * size * 0.27, y, s, size, c)


def tri(cx, y, horas):                # triángulo de inventario VSM
    c = ACC
    for k in range(3):
        line(cx - 14 + k, y + 24, cx, y + k, c, 2)
        line(cx + 14 - k, y + 24, cx, y + k, c, 2)
    line(cx - 14, y + 24, cx + 14, y + 24, c, 2)
    text(cx - 3, y + 21, 'I', 11, c)
    text(cx - 16, y + 40, f'{n1(horas)} h', 10, c)


TIT = 'Escenario actual (antes de la propuesta)' if esc == 'base' else 'Escenario propuesto (después de la automatización)'
text(70, 32, f'Mapa de flujo de valor (VSM) · Planta láctea Mekvra · {TIT}', 20, NAVY)
text(70, 54, 'Lote = entidad. Cada línea termina en sus envasadoras por presentación; el paletizado U341 y la cámara U411 son comunes.', 11, SOFT)

# flujo de información
fabrica(20, 70, 230, 92, 'Proveedor: ganaderos', '14 cisternas/día · 93.000 L')
rect(760, 86, 420, 70, (255, 255, 255))
rect(760, 86, 420, 70, NAVY, 2, 2)
text(780, 114, 'Control de producción', 14, NAVY)
text(780, 136, 'ERP (SAP) · MES · plan diario y recetas ISA-88', 11, SOFT)
fabrica(1650, 70, 250, 92, 'Clientes', 'yogur · mozzarella · kéfir')
flecha(760, 120, 254)
text(360, 112, 'pedido diario de leche', 10, SOFT)
flecha(1650, 120, 1184)
text(1300, 112, 'pedidos y pronóstico', 10, SOFT)
dash(970, 156, 970, 190, NAVY)
text(985, 182, 'órdenes de producción y recetas a cada línea (MES)', 10, SOFT)

# zonas
zona('T', 20, 170, 1460, 140, 'RECEPCIÓN Y TRATAMIENTO DE LECHE (tronco común)',
     'Bahías U111/U112 · tanques de crudo U113/U114 · clarificadora U121 + HTST U122|14 lotes de leche al día en secuencia; cada lote va a su silo: S1 yogur, S2 mozzarella, S3 kéfir', tx=600)
for k, y0, t1, t2 in (('Y', YY - 120, 'LÍNEA 1 · YOGUR CON TROZOS DE FRESA', '6 lotes/día × 10.000 kg|S1 → formulación → U202|→ fermentación → pulmón|→ envasado en 3 presentaciones'),
                      ('Q', YQ - 120, 'LÍNEA 2 · QUESO MOZZARELLA', '5 lotes/día × 5.000 L|S2 → tina → acidificación|→ hilado → salmuera|→ empaque en 3 presentaciones'),
                      ('K', YK - 120, 'LÍNEA 3 · KÉFIR NATURAL', '3 lotes/día × 5.000 L|S3 → U202 (compartida)|→ fermentación → tanques|→ envasado en 3 presentaciones')):
    zona(k, 20, y0, 1460, 380, t1.split(' · ')[0])
    text(44, y0 + 52, t1.split(' · ')[1], 14, ZONA[k][1])
    for i_, s_ in enumerate(t2.split('|')):
        text(44, y0 + 76 + 16 * i_, s_, 10, SOFT)
zona('F', 1500, 170, 420, 1340, 'FIN DE LÍNEA Y DESPACHO', 'Encajonado y paletizado U341 (robot)|Cámara fría 2–4 °C U411 · despacho FEFO')

# rótulos de etapas
def etapa(cx, y, s, k):
    rotulo(cx, y, s, ZONA[k][1], 10)


etapa(XS, YY - 96, 'Silo S1', 'Y'); etapa(680, YY - 96, 'Formulación', 'Y'); etapa(790, YY - 96, 'Homog.+past.', 'Y')
etapa(965, YY - 96, 'Fermentación 42 °C (3 × 10.000 L)', 'Y'); etapa(1190, YY - 96, 'Pulmón y fruta', 'Y')
etapa(1330, YY - 112, 'Envasado por presentación', 'Y')
text(1378, YY - 50, 'U311 · vasos 150 g · 12.000/h', 9, ZONA['Y'][1])
text(1378, YY + 60, 'U312 · botellas 1000 g (4.000/h)', 9, ZONA['Y'][1])
text(1378, YY + 74, 'y 1750 g (2.500/h)', 9, ZONA['Y'][1])
etapa(XS + 30, YQ - 96, 'Silo S2', 'Q'); etapa(680, YQ - 96, 'Coagular y cocer', 'Q'); etapa(790, YQ - 96, 'Acidificar', 'Q')
etapa(900, YQ - 96, 'Hilar y moldear', 'Q'); etapa(1020, YQ - 112, 'Salmuera (4 canales)', 'Q'); etapa(1190, YQ - 96, 'A empaque', 'Q')
text(1378, YQ - 50, 'U321 · vacío 400 g (900/h)', 9, ZONA['Q'][1])
text(1378, YQ - 36, 'y 1000 g (450/h)', 9, ZONA['Q'][1])
text(1378, YQ + 60, 'U322 · tarrina 250 g · 1.200/h', 9, ZONA['Q'][1])
etapa(XS + 60, YK - 96, 'Silo S3', 'K'); etapa(790, YK - 96, 'U202 compartida', 'K')
etapa(900 + 32 * (len(FK) - 1), YK - 96, f'Fermentación 22–25 °C ({len(FK)} × 5.000 L)', 'K')
etapa(1190, YK - 112, 'Maduración en tanque' if esc == 'base' else 'Pulmón de llenado', 'K')
text(1378, YK - 14, 'U331 · botellas 240 g (6.000/h),', 9, ZONA['K'][1])
text(1378, YK, '500 g (4.500/h) y 1000 g (3.000/h)', 9, ZONA['K'][1])
dash(790, YY + 40, 790, YK - 40, (120, 130, 150), 1, 6)
text(800, YY + 92, 'U202 compartida con kéfir', 9, SOFT)
text(XF - 40, YQ - 96, 'Paletizado', 10, ZONA['F'][1]); text(XF + 100, YQ - 96, 'Cámara fría', 10, ZONA['F'][1])
for y, s in ((YY - 96, 'Clientes yogur'), (YQ - 96, 'Clientes mozzarella'), (YK - 96, 'Clientes kéfir')):
    text(1770, y, s, 10, ZONA['F'][1])

# cajas de datos VSM y escalera de tiempos por línea (valores de diseño del modelo de capacidad)
def inventarios(lin):
    a = CAP['aux']
    if lin == 'Y':
        return {0: S['crudo_h'], 1: S['silo_h'], 2: S['esp_u202'], 5: S['y_lib'] + a['drain_y'] / 2, 6: 12.0 + S['pt_h']}
    if lin == 'Q':
        return {0: S['crudo_h'], 1: S['silo_h'], 2: 0.25, 4: 0.25, 6: S['pt_h']}
    if esc == 'base':
        return {0: S['crudo_h'], 1: S['silo_h'] + S['esp_u202'], 4: 0.5, 5: a['drain_k'] / 2, 6: S['pt_h']}
    return {0: S['crudo_h'], 1: S['silo_h'] + S['esp_u202'], 4: a['drain_k'] / 2, 6: S['pt_h']}


def tira(lin, k, ybase):
    V = CAP['vsm'][lin]
    inv = inventarios(lin)
    x0, bw, gap = 70, 140, 46
    ycaja = ybase + 65
    for i, (nm, unit, ct, va, co, ops) in enumerate(V['proc']):
        x = x0 + gap + i * (bw + gap)
        rect(x, ycaja, bw, 62, (255, 255, 255))
        rect(x, ycaja, bw, 62, ZONA[k][1], 2, 2)
        text(x + 6, ycaja + 14, nm[:24], 9, INK)
        text(x + 6, ycaja + 28, unit, 8, SOFT)
        text(x + 6, ycaja + 42, f'C/T {n1(ct)} h · C/O {co}', 8, INK)
        text(x + 6, ycaja + 56, f'Operarios {ops}', 8, INK)
    for g, hrs in inv.items():
        tri(x0 + gap / 2 + g * (bw + gap), ycaja + 4, hrs)
    yi, yv = ycaja + 92, ycaja + 112           # escalera: arriba inventario, abajo valor agregado
    prev = None
    for g in range(7):
        a = x0 + g * (bw + gap)
        segs = [(a, a + gap, yi if g in inv else yv, n1(inv[g]) + ' h' if g in inv else '')]
        if g < 6:
            segs.append((a + gap, a + gap + bw, yv, n1(V['proc'][g][3]) + ' h'))
        for sa, sb, yy, tt in segs:
            line(sa, yy, sb, yy, INK, 2)
            if prev is not None and prev != yy:
                line(sa, prev, sa, yy, INK, 2)
            prev = yy
            if tt:
                text((sa + sb) / 2 - 12, yy - 4 if yy == yi else yy + 13, tt, 9, ACC if yy == yi else NAVY)
    xr = x0 + 6 * (bw + gap) + gap + 10
    rect(xr, ycaja + 80, 200, 50, (255, 255, 255))
    rect(xr, ycaja + 80, 200, 50, ZONA[k][1], 2, 2)
    text(xr + 8, ycaja + 98, f'Lead time {n1(V["lt"])} h', 11, INK)
    text(xr + 8, ycaja + 120, f'Valor agregado {n1(V["va"])} h ({n1(V["pce"] * 100)} %)', 9, NAVY)


tira('Y', 'Y', YY + 40)
tira('Q', 'Q', YQ + 40)
tira('K', 'K', YK + 40)

json.dump({'esc': esc, 'coord': COORD, 'FK': FK, 'TK': TK, 'pulm': P['pulm'], 'YT': YT, 'YY': YY, 'YQ': YQ, 'YK': YK, 'XF': XF},
          open(os.path.join(D, f'vsm_coords_{esc}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------------- construir, correr y guardar ----------------
ps = w.Dispatch("Tecnomatix.PlantSimulation.RemoteControl.24.4")
ps.SetLicenseType("Student")
ps.NewModel()
ps.ExecuteSimTalk('\n'.join(L))
print('objetos', flush=True)
for i in range(0, len(G), 150):
    ps.ExecuteSimTalk('var m: object := .Models.Model\n' + '\n'.join(G[i:i + 150]))
print('dibujo', len(G), flush=True)
t0 = time.time()
ps.ExecuteSimTalk('.Models.Model.EventController.startWithoutAnimation')
time.sleep(1)
while ps.IsSimulationRunning() and time.time() - t0 < 600:
    time.sleep(0.5)
R = {'escenario': esc, 'dias': DIAS}
DEM = {'yogur': 6, 'mozzarella': 5, 'kefir': 3}
for lin in DEM:
    n = ps.GetValue(f'.Models.Model.Clientes_{lin}.StatNumIn')
    R[lin] = dict(lotes=n // 3, pedidos=int(DEM[lin] * DIAS))
    for a in ('StatAvgLifeSpan',):
        try:
            R[lin]['vida_media_h'] = round(ps.GetValue(f'.Models.Model.Clientes_{lin}.{a}') / H, 1)
            break
        except Exception:
            pass
U = {}
for o in ['U111_U112', 'U121_U122', 'U201', 'U202', 'U211', 'U214', 'U311', 'U312', 'U221', 'U222', 'U223', 'U224_salida',
          'U321', 'U322', 'U202_K', 'U231', TK[0], 'U331', 'U341']:
    try:
        U[o] = {k: round(ps.GetValue(f'.Models.Model.{o}.Stat{a}Portion'), 3)
                for k, a in (('trabajando', 'Working'), ('bloqueado', 'Blocking'), ('en_falla', 'Fail'), ('esperando', 'Waiting'))}
    except Exception as e:
        U[o] = str(e)[:60]
R['recursos'] = U
R['tiempos_h'] = {k: round(v, 3) for k, v in dict(U311=U311, U312=U312, U321=U321, U322=U322, U331=U331, U341=U341, tanque_kefir=TQK,
                                                   ferm_y=ferm_y, ferm_k=ferm_k, u202=u202_y).items()}

# resultados de la corrida dibujados en el mapa
res = [f'Simulación {int(DIAS)} días (Plant Simulation 2404, fallas aleatorias, una corrida):']
for lin, nom in (('yogur', 'Yogur'), ('mozzarella', 'Mozzarella'), ('kefir', 'Kéfir')):
    r = R[lin]
    res.append(f'{nom}: {r["lotes"]} de {r["pedidos"]} lotes despachados')
G2 = [f'm.drawRectangle(1, 1520, 1330, 380, 170, {rgb((255, 255, 255))}, -1)',
      f'm.drawRectangle(2, 1520, 1330, 380, 170, {rgb(NAVY)}, 2)']
for i, s in enumerate(res):
    G2.append(f'm.drawText(3, 1532, {1356 + i * 24}, {rgb(NAVY if i == 0 else INK)}, {10 if i == 0 else 12}, "{s}")')
ps.ExecuteSimTalk('var m: object := .Models.Model\n' + '\n'.join(G2))
print(json.dumps(R, ensure_ascii=False), flush=True)
if OUT != '-':
    ps.ExecuteSimTalk('var b: object := .Tools.BottleneckAnalyzer.BottleneckAnalyzer.createObject(.Models.Model, 1430, 285)\n'
                      'b.Name := "Analizador_cuellos"\nb.analyzeModel')
    ps.SaveModel(OUT)
    print('guardado', flush=True)
ps.Quit()
