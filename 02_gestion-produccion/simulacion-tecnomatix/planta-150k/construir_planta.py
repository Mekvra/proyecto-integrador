# Modelo de Plant Simulation 2404 (licencia estudiantil) de la PLANTA COMPLETA de Lácteos Altos de Teusacá según el acta
# del 9-oct-2026: 150.000 L/día de leche que el tronco común reparte en tres líneas: yogures ≈ 57.000 L/día (detalle de las
# recetas v1.7), quesos 50.000 L/día (mozzarella, quesillo y doble crema) y leche UHT 43.000 L/día (entera, descremada y
# chocolate). Escenario actual, sin automatización. Los tiempos de quesos y de leche UHT son supuestos de diseño hasta que
# existan sus recetas. Ocho secciones con su franja y su cartel en el 2D; la escena 3D se decora después (decorar_planta.py).
# Uso: python construir_planta.py <salida.spp|-> [semanas]
import sys, os, time, json, math
import win32com.client as w

D = os.path.dirname(os.path.abspath(__file__))
ICO = os.path.join(os.path.dirname(D), 'iconos')
REC = json.load(open(os.path.join(D, '..', '..', '..', '01_transformacion-digital', 'isa88', 'recetas', 'recetas_yogures.json'),
                     encoding='utf-8'))
OUT = sys.argv[1] if len(sys.argv) > 1 else '-'
SEMANAS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
H = 3600.0
DIAS = 6 * SEMANAS                                    # se simulan solo los días de producción (lunes a sábado)


def h(x):
    return int(round(x * H))


def n1(x, d=1):
    return f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


# ---------------- datos de las recetas ----------------
T = REC['tiempos']
REFS = {r['codigo']: r for r in REC['referencias']}
OEE = REC['dia']['oee']['actual']                     # A 0,90 · P 0,80 · Q 0,97 · paradas 3,5 h
VEL_U311 = {'YF150': 12000, 'YN200': 10000}            # llenadora actual de vasos preformados
CHUNK_H = 0.05                                        # cada MU de llenado = 3 min de llenado a velocidad nominal
F_TIEMPO = (1 / (OEE['P'] * OEE['Q'])) * (24 / (24 - OEE['paradas_h']))   # desempeño, calidad y paradas planeadas
T_CHUNK = CHUNK_H * F_TIEMPO
T_ENC = T_CHUNK * 0.7                                 # la encajonadora va más rápido que su llenadora
FILLER = {'YF150': 'U311_Vasos', 'YN200': 'U311_Vasos', 'YF1000': 'U312_Botellas', 'YF1750': 'U312_Botellas',
          'YN1000': 'U312_Botellas', 'YG150': 'U313_Griego', 'YG500': 'U313_Griego'}
CHUNKS, UND_CHUNK = {}, {}
for c, r in REFS.items():
    vel = VEL_U311.get(c, r['und_h'])
    horas = r['und_lote'] / vel
    CHUNKS[c] = max(1, round(horas / CHUNK_H))
    UND_CHUNK[c] = r['und_lote'] / CHUNKS[c]
prom = lambda k: sum(T[p][k] * n for p, n in REC['supuestos']['lotes_semana_actual'].items()) / 35
T_U201, T_U202 = prom('U201_total'), prom('U202_total')
T_FERM = sum((T[p]['fermentador_total'] - T[p]['fermentador']['llenar']) * n
             for p, n in REC['supuestos']['lotes_semana_actual'].items()) / 35   # el llenado coincide con U202
T_U215 = (T['YF']['fermentador']['vaciar_enfriar'] + T['YN']['fermentador']['vaciar_enfriar']) / 2
T_U216 = T['YG']['fermentador']['separar'] + T['U216_arranque']
SUP = dict(recepcion=0.6, crudo=4.0, htst=0.5, silo=2.0, camara=12.0, paletizado=0.02, cip_c=85 / 60, formato=0.75)

# programa semanal: 35 lotes, siempre natural → griego → fresa dentro del día
DIAS_PROG = [['YN', 'YN', 'YG', 'YG', 'YF', 'YF'], ['YN', 'YN', 'YG', 'YG', 'YF', 'YF'], ['YN', 'YN', 'YG', 'YG', 'YF', 'YF'],
             ['YN', 'YN', 'YG', 'YF', 'YF', 'YF'], ['YN', 'YN', 'YN', 'YG', 'YF', 'YF'], ['YN', 'YN', 'YG', 'YF', 'YF']]
SEQ = [p for d in DIAS_PROG for p in d]
assert len(SEQ) == 35 and SEQ.count('YN') == 13 and SEQ.count('YG') == 9 and SEQ.count('YF') == 13
# quesos: 30 lotes/semana (50.000 L/día), 10 de cada tipo; QM mozzarella, QQ quesillo, QD doble crema
DIAS_Q = [['QM', 'QM', 'QQ', 'QQ', 'QD'], ['QM', 'QM', 'QQ', 'QD', 'QD'], ['QM', 'QQ', 'QQ', 'QD', 'QD']] * 2
# leche UHT: 26 lotes/semana (≈ 43.000 L/día); entera → descremada → chocolate dentro del día (el cacao va al final)
DIAS_L = [['LE'] * n + ['LD', 'LC'] for n in (3, 3, 2, 2, 2, 2)]
SEQ_Q = [p for d in DIAS_Q for p in d]
SEQ_L = [p for d in DIAS_L for p in d]
assert len(SEQ_Q) == 30 and all(SEQ_Q.count(c) == 10 for c in ('QM', 'QQ', 'QD'))
assert len(SEQ_L) == 26 and SEQ_L.count('LE') == 14 and SEQ_L.count('LD') == 6 and SEQ_L.count('LC') == 6
_ev = []
for j, sq in enumerate((SEQ, SEQ_Q, SEQ_L)):
    _ev += [((k + 0.5) / len(sq), j, p) for k, p in enumerate(sq)]
SEQ_PLANTA = [p for _, _, p in sorted(_ev)]                 # cada línea conserva su orden; las tres se intercalan parejas
QUESOS, LECHES = ('QM', 'QQ', 'QD'), ('LE', 'LD', 'LC')
# supuestos de diseño de quesos y leche UHT (por lote de 10.000 L)
SQ = dict(tina=3.0, cip_tina=0.5, hilado=1.0, cambio_hilado=0.5, salmuera=8.0, empaque=1.2, bultos=20, paletizar=0.03, camara=12.0)
SL = dict(mezcla=1.0, cambio_mezcla=0.5, uht=1.0, empaque=2.0, bultos=40, paletizar=0.02, cuarentena=24.0)
INTERVALO = 6 * 24 / len(SEQ_PLANTA)
RECEPCION_DIA = len(SEQ_PLANTA) * 10_000 / 6

# ---------------- objetos ----------------
MF = '.MaterialFlow'
L = ['var m: object := .Models.Model', 'var o: object', 'var t: table', 'var s: object']
ICONOS, CON, COORD = {}, [], {}


def obj(name, cls, x, y, proc=None, icon=None, extra=()):
    global L
    L += [f'o := {cls}.createObject(m, {x}, {y})', f'o.Name := "{name}"']
    if proc is not None:
        L.append(f'o.ProcTime := {h(proc)}')
    L += [e.replace('@', 'o') for e in extra]
    if icon:
        ICONOS[name] = icon
    COORD[name] = (x, y)


for nm in ('Lote_YF', 'Lote_YN', 'Lote_YG') + tuple('Lote_' + c for c in QUESOS + LECHES) + tuple(REFS) + ('Bulto_queso', 'Bulto_leche'):
    L.append(f'o := .MUs.Part.duplicate(.MUs, "{nm}")')

Y0, YQ, YL = 330, 765, 1035                  # filas de yogures, quesos y leche UHT
# 1 · recepción y tronco común
obj('Programa_semanal', '.InformationFlow.DataTable', 70, 1110)
L += ['o.setDataType(1, "object")', 'o.setDataType(2, "integer")', 'o.setDataType(3, "string")']
for i, p in enumerate(SEQ_PLANTA, 1):
    L += [f'o[1, {i}] := .MUs.Lote_{p}', f'o[2, {i}] := 1', f'o[3, {i}] := "Lote_{p}"']
obj('Cisternas', MF + '.Source', 80, Y0, icon='vsm_cisterna',
    extra=['@.MUSelection := "Sequence Cyclical"', '@.Path := m.Programa_semanal', f'@.Interval := {h(INTERVALO)}'])
obj('U111_Recepcion', MF + '.Station', 180, Y0, SUP['recepcion'], 'vsm_recepcion')
obj('U113_Leche_cruda', MF + '.Buffer', 280, Y0, icon='vsm_crudo', extra=['@.Capacity := -1', f'@.ProcTime := {h(SUP["crudo"])}'])
obj('U121_Pasteurizador', MF + '.Station', 380, Y0, SUP['htst'], 'vsm_htst')
obj('U123AB_Silo_entera', MF + '.Buffer', 480, Y0 - 70, icon='vsm_silo1', extra=['@.Capacity := -1', f'@.ProcTime := {h(SUP["silo"])}'])
obj('U123C_Silo_descremada', MF + '.Buffer', 480, Y0 + 70, icon='vsm_silo3', extra=['@.Capacity := -1', f'@.ProcTime := {h(SUP["silo"])}'])
obj('U124_Silo_quesos', MF + '.Buffer', 480, YQ, icon='vsm_silo2', extra=['@.Capacity := -1', f'@.ProcTime := {h(SUP["silo"])}'])
obj('U125_Silo_leche', MF + '.Buffer', 480, YL, icon='vsm_silo3', extra=['@.Capacity := -1', f'@.ProcTime := {h(SUP["silo"])}'])
CON += [('Cisternas', 'U111_Recepcion'), ('U111_Recepcion', 'U113_Leche_cruda'), ('U113_Leche_cruda', 'U121_Pasteurizador'),
        ('U121_Pasteurizador', 'U123AB_Silo_entera'), ('U121_Pasteurizador', 'U123C_Silo_descremada')]
CON += [('U121_Pasteurizador', 'U124_Silo_quesos'), ('U121_Pasteurizador', 'U125_Silo_leche')]   # sucesores 3 y 4 de U121
# 2 · preparación de la base
obj('U201_Formulacion', MF + '.Station', 640, Y0, T_U201, 'formulacion')
obj('U202_Tratamiento', MF + '.Station', 760, Y0, T_U202, 'u202', extra=[f'@.SetupTime := {h(SUP["cip_c"])}'])
CON += [('U123AB_Silo_entera', 'U201_Formulacion'), ('U123C_Silo_descremada', 'U201_Formulacion'), ('U201_Formulacion', 'U202_Tratamiento')]
# 3 · fermentación (4 tanques)
FERM = ['U211_Fermentador', 'U212_Fermentador', 'U213_Fermentador', 'U218_Fermentador']
for i, nm in enumerate(FERM):
    obj(nm, MF + '.Station', 900 + 110 * (i % 2), Y0 - 60 + 120 * (i // 2), T_FERM, 'fermentador_yogur')
    CON.append(('U202_Tratamiento', nm))
# 4 · acondicionamiento
obj('U215_Enfriamiento', MF + '.Station', 1170, Y0 - 70, T_U215, 'banda')
obj('U216_Separador_griego', MF + '.Station', 1170, Y0 + 90, T_U216, 'tanque_kefir')
for f in FERM:
    CON += [(f, 'U215_Enfriamiento'), (f, 'U216_Separador_griego')]
# cada producto tiene su propio tanque pulmón: fresa (U214A) y natural (U214B) no comparten tanque
obj('U214A_Pulmon_fresa', MF + '.Buffer', 1280, Y0 - 120, icon='pulmones', extra=['@.Capacity := 1'])
obj('U214B_Pulmon_natural', MF + '.Buffer', 1280, Y0 - 20, icon='pulmones', extra=['@.Capacity := 1'])
obj('U217_Pulmones_griego', MF + '.Buffer', 1280, Y0 + 90, icon='pulmones', extra=['@.Capacity := 2'])
CON += [('U215_Enfriamiento', 'U214A_Pulmon_fresa'), ('U215_Enfriamiento', 'U214B_Pulmon_natural'),
        ('U216_Separador_griego', 'U217_Pulmones_griego')]


def reparto(name, x, y, filas):
    ext = ['t := @.DismantleTable', 't.delete']   # sin delete, t arrastra filas del reparto anterior
    for i, (mu, n, suc) in enumerate(filas, 1):
        ext += [f't[1, {i}] := .MUs.{mu}', f't[2, {i}] := {n}', f't[3, {i}] := {suc}']
    ext += ['@.DismantleTable := t', '@.Sequence := "MUs exiting independent of other MUs"']
    obj(name, MF + '.DismantleStation', x, y, 0.0, 'vsm_reparto_y', extra=ext)


# sucesores de cada reparto: 1 = llenadora de vasos o griego, 2 = botellas, el último = registro de lotes
reparto('Reparto_fresa', 1390, Y0 - 120, [('YF150', CHUNKS['YF150'], 1), ('YF1000', CHUNKS['YF1000'], 2), ('YF1750', CHUNKS['YF1750'], 2)])
reparto('Reparto_natural', 1390, Y0 - 20, [('YN200', CHUNKS['YN200'], 1), ('YN1000', CHUNKS['YN1000'], 2)])
reparto('Reparto_griego', 1390, Y0 + 90, [('YG150', CHUNKS['YG150'], 1), ('YG500', CHUNKS['YG500'], 1)])
CON += [('U214A_Pulmon_fresa', 'Reparto_fresa'), ('U214B_Pulmon_natural', 'Reparto_natural'), ('U217_Pulmones_griego', 'Reparto_griego')]
# 5 · envasado y encajonado: cada llenadora entrega a su encajonadora (forma la caja de cartón, mete los envases y la cierra)
for nm, y, ic in (('U311_Vasos', Y0 - 120, 'vsm_u311'), ('U312_Botellas', Y0 - 20, 'vsm_u312'), ('U313_Griego', Y0 + 90, 'llenadora_yogur')):
    obj(nm, MF + '.Station', 1520, y, T_CHUNK, ic, extra=[f'@.SetupTime := {h(SUP["formato"])}'])
CON += [('Reparto_fresa', 'U311_Vasos'), ('Reparto_fresa', 'U312_Botellas'), ('Reparto_natural', 'U311_Vasos'),
        ('Reparto_natural', 'U312_Botellas'), ('Reparto_griego', 'U313_Griego')]
obj('Registro_de_lotes', MF + '.Drain', 1390, Y0 + 210, icon='pedidos_yogur')
CON += [('Reparto_fresa', 'Registro_de_lotes'), ('Reparto_natural', 'Registro_de_lotes'), ('Reparto_griego', 'Registro_de_lotes')]
L += [f'm.{r}.MainMU := 3' for r in ('Reparto_fresa', 'Reparto_natural')] + ['m.Reparto_griego.MainMU := 2']
ENC = {'U311_Vasos': 'U321_Encajonadora_vasos', 'U312_Botellas': 'U322_Encajonadora_botellas', 'U313_Griego': 'U323_Encajonadora_griego'}
for fil, enc in ENC.items():
    obj(enc, MF + '.Station', 1650, COORD[fil][1], T_ENC, 'vsm_u321')
    CON.append((fil, enc))


# 6 · paletizado, cámara y despacho. Bandas transportadoras reales (Conveyor) con tramos: (giro en grados, largo en m)
def banda(nombre, clase, x, y, tramos, vel=None):
    global L
    L += [f'o := {MF}.{clase}.createObject(m, {x}, {y})', f'o.Name := "{nombre}"', f'o.Length := {tramos[0][1]}',
          'o.getCurveSegments(s)', 's.MaxYDim := 10']
    for i, (giro, largo) in enumerate(tramos, 2):
        L += [f's[1, {i}] := {float(giro)}', f's[2, {i}] := {float(largo)}', f's[5, {i}] := false']
    L += ['o.setCurveSegments(s)'] + ([f'o.Speed := {vel}'] if vel else [])
    COORD[nombre] = (x, y)


L += ['s := .InformationFlow.DataTable.createObject(m, 40, 900)']        # tabla auxiliar para los tramos (se borra al final)
# velocidades pensadas para la animación en tiempo real ×30 (cada caja del modelo = 3 min de llenado)
VEL_BANDA, VEL_MONTACARGAS, TIEMPO_REAL = 0.03, 0.06, 30
banda('Banda_cajas_vasos', 'Conveyor', 1676, Y0 - 120, [(0, 2.2), (90, 3.5), (-90, 3.5)], VEL_BANDA)
banda('Banda_cajas_botellas', 'Conveyor', 1676, Y0 - 20, [(0, 5.7)], VEL_BANDA)
banda('Banda_cajas_griego', 'Conveyor', 1676, Y0 + 90, [(0, 2.2), (-90, 4.0), (90, 3.5)], VEL_BANDA)
CON += [('U321_Encajonadora_vasos', 'Banda_cajas_vasos'), ('U322_Encajonadora_botellas', 'Banda_cajas_botellas'),
        ('U323_Encajonadora_griego', 'Banda_cajas_griego')]
obj('U341_Paletizado', MF + '.Station', 1830, Y0 - 20, 150 / 3600, 'vsm_paletizado')   # paletizado MANUAL (estado actual): 2 operarios, ≈ 150 s por bulto
obj('U342_Envolvedora', MF + '.Station', 1920, Y0 - 20, SUP['paletizado'], 'vsm_paletizado')
obj('U411_Camara', MF + '.Buffer', 2080, Y0, icon='vsm_camara', extra=['@.Capacity := -1', f'@.ProcTime := {h(SUP["camara"])}'])
CON += [('Banda_cajas_vasos', 'U341_Paletizado'), ('Banda_cajas_botellas', 'U341_Paletizado'), ('Banda_cajas_griego', 'U341_Paletizado'),
        ('U341_Paletizado', 'U342_Envolvedora'), ('U342_Envolvedora', 'U411_Camara')]
# montacargas: recorre la ruta envolvedora ↔ cámara (pista de ida y vuelta); el método Init lo crea al iniciar
L += ['o := .MUs.Transporter.duplicate(.MUs, "Montacargas")', f'o.Speed := {VEL_MONTACARGAS}']
banda('Pista_ida', 'Track', 1935, Y0 + 60, [(0, 4.5)])
banda('Pista_vuelta', 'Track', 2025, Y0 + 80, [(180, 4.5)])
CON += [('Pista_ida', 'Pista_vuelta'), ('Pista_vuelta', 'Pista_ida')]
L += ['o := str_to_obj(".InformationFlow.Method").createObject(m, 330, 120)', 'o.Name := "Init"',
      'o.Program := "var x: object := .MUs.Montacargas.create(.Models.Model.Pista_ida)"']
DESP = list(REFS)
for i, c in enumerate(DESP):
    obj(f'Despacho_{c}', MF + '.Drain', 2190, Y0 - 165 + 55 * i, icon='vsm_despacho_y')
    CON.append(('U411_Camara', f'Despacho_{c}'))



def empaque(name, x, y, proc, mu, n, icon):
    """Empacadora: recibe el lote, lo empaca (proc) y entrega los bultos a la banda; el lote vacío va al registro."""
    ext = ['t := @.DismantleTable', 't.delete', f't[1, 1] := .MUs.{mu}', f't[2, 1] := {n}', 't[3, 1] := 1', '@.DismantleTable := t',
           '@.Sequence := "MUs exiting independent of other MUs"']
    obj(name, MF + '.DismantleStation', x, y, proc, icon, extra=ext)


# 7 · línea de quesos (supuestos SQ)
TINAS = ['Q201_Tina', 'Q202_Tina', 'Q203_Tina']
for i, nm in enumerate(TINAS):
    obj(nm, MF + '.Station', 680, YQ - 75 + 75 * i, SQ['tina'] + SQ['cip_tina'], 'tina')
    CON += [('U124_Silo_quesos', nm), (nm, 'Q301_Hilado')]
obj('Q301_Hilado', MF + '.Station', 900, YQ, SQ['hilado'], 'hiladora', extra=[f'@.SetupTime := {h(SQ["cambio_hilado"])}'])
obj('Q302_Salmuera', MF + '.Buffer', 1080, YQ, icon='salmuera', extra=['@.Capacity := -1', f'@.ProcTime := {h(SQ["salmuera"])}'])
empaque('Q311_Empaque_vacio', 1280, YQ, SQ['empaque'], 'Bulto_queso', SQ['bultos'], 'llenadora_queso')
obj('Q312_Registro', MF + '.Drain', 1280, YQ + 90, icon='pedidos_queso')
banda('Q321_Banda_quesos', 'Conveyor', 1310, YQ, [(0, 16.0)], VEL_BANDA)
obj('Q341_Paletizado', MF + '.Station', 1680, YQ, SQ['paletizar'], 'vsm_paletizado')
obj('Q411_Camara_quesos', MF + '.Buffer', 1880, YQ, icon='camara_queso', extra=['@.Capacity := -1', f'@.ProcTime := {h(SQ["camara"])}'])
obj('Despacho_quesos', MF + '.Drain', 2120, YQ, icon='vsm_despacho_q')
CON += [('Q301_Hilado', 'Q302_Salmuera'), ('Q302_Salmuera', 'Q311_Empaque_vacio'), ('Q311_Empaque_vacio', 'Q321_Banda_quesos'),
        ('Q311_Empaque_vacio', 'Q312_Registro'), ('Q321_Banda_quesos', 'Q341_Paletizado'), ('Q341_Paletizado', 'Q411_Camara_quesos'),
        ('Q411_Camara_quesos', 'Despacho_quesos')]
# 8 · línea de leche UHT (supuestos SL)
obj('L201_Mezcla', MF + '.Station', 680, YL, SL['mezcla'], 'formulacion', extra=[f'@.SetupTime := {h(SL["cambio_mezcla"])}'])
obj('L202_UHT', MF + '.Station', 900, YL, SL['uht'], 'vsm_htst')
obj('L203_Tanque_aseptico', MF + '.Buffer', 1080, YL, icon='tanque_kefir', extra=['@.Capacity := 2'])
empaque('L311_Envasadora_aseptica', 1280, YL, SL['empaque'], 'Bulto_leche', SL['bultos'], 'llenadora_kefir')
obj('L312_Registro', MF + '.Drain', 1280, YL + 90, icon='pedidos_kefir')
banda('L321_Banda_leche', 'Conveyor', 1310, YL, [(0, 16.0)], VEL_BANDA)
obj('L341_Paletizado', MF + '.Station', 1680, YL, SL['paletizar'], 'vsm_paletizado')
obj('L411_Bodega_ambiente', MF + '.Buffer', 1880, YL, icon='vsm_camara', extra=['@.Capacity := -1', f'@.ProcTime := {h(SL["cuarentena"])}'])
obj('Despacho_leche', MF + '.Drain', 2120, YL, icon='vsm_despacho_k')
CON += [('U125_Silo_leche', 'L201_Mezcla'), ('L201_Mezcla', 'L202_UHT'), ('L202_UHT', 'L203_Tanque_aseptico'),
        ('L203_Tanque_aseptico', 'L311_Envasadora_aseptica'), ('L311_Envasadora_aseptica', 'L321_Banda_leche'),
        ('L311_Envasadora_aseptica', 'L312_Registro'), ('L321_Banda_leche', 'L341_Paletizado'), ('L341_Paletizado', 'L411_Bodega_ambiente'),
        ('L411_Bodega_ambiente', 'Despacho_leche')]
L += ['m.Q311_Empaque_vacio.MainMU := 2', 'm.L311_Envasadora_aseptica.MainMU := 2', 's.deleteObject']

for a, b in CON:
    L.append(f'.MaterialFlow.Connector.connect(m.{a}, m.{b})')


def ruta(nm, filas):
    out = [f'm.{nm}.ExitStrategy := "MU Attribute"', f'm.{nm}.AttributeType := "String"', f't := m.{nm}.ExitStrategyMUAttributeList']
    for i, (v, sc) in enumerate(filas, 1):
        out += [f't[1, {i}] := "Name"', f't[2, {i}] := "{v}"', f't[3, {i}] := {sc}']
    return out + [f'm.{nm}.ExitStrategyMUAttributeList := t']


L += ruta('U121_Pasteurizador', [('Lote_YF', 1), ('Lote_YN', 1), ('Lote_YG', 2)] + [('Lote_' + c, 3) for c in QUESOS] + [('Lote_' + c, 4) for c in LECHES])
for f in FERM:
    L += ruta(f, [('Lote_YF', 1), ('Lote_YN', 1), ('Lote_YG', 2)])
L += ruta('U215_Enfriamiento', [('Lote_YF', 1), ('Lote_YN', 2)])
L += ruta('U411_Camara', [(c, i) for i, c in enumerate(DESP, 1)])
MTBF = {'llenadora': (OEE['A'], 1.0), 'proceso': (0.98, 1.5)}
FALLAS = {n: 'llenadora' for n in ('U311_Vasos', 'U312_Botellas', 'U313_Griego')}
FALLAS.update({n: 'proceso' for n in ('U121_Pasteurizador', 'U201_Formulacion', 'U202_Tratamiento', 'U215_Enfriamiento', 'U216_Separador_griego',
                                      'Q301_Hilado', 'L202_UHT')})
FALLAS.update({n: 'llenadora' for n in ('Q311_Empaque_vacio', 'L311_Envasadora_aseptica')})
for nm, k in FALLAS.items():
    a, mttr = MTBF[k]
    L += [f'm.{nm}.Failures.createFailure("Falla")', f'm.{nm}.Failures.Falla.AvailabilityOn := true',
          f'm.{nm}.Failures.Falla.Availability := {round(a * 100, 2)}', f'm.{nm}.Failures.Falla.MTTR := {h(mttr)}',
          f'm.{nm}.Failures.Falla.Mode := "ProcessingTime"']
L += [f'm.EventController.End := {h(24 * DIAS)}', 'm.EventController.Speed := 60',
      'm.EventController.XPos := 60', 'm.EventController.YPos := 120']
for nm, f in ICONOS.items():
    p = os.path.join(ICO, f + '.bmp').replace('\\', '\\\\')
    L.append(f'm.{nm}.setIconFromFile(1, "{p}")')

# ---------------- dibujo 2D: seis secciones con franja y cartel ----------------
G = []
NAVY, INK, SOFT, ACC = (27, 42, 120), (20, 33, 61), (91, 100, 117), (163, 72, 11)
SECC = [  # (número, título, subtítulo, x0, x1, y0, y1, color de fondo, color de borde)
    ('1', 'RECEPCIÓN Y TRONCO COMÚN', '150.000 L/día · 2 tanques · pasteurización · 5 silos', 30, 545, 150, 1160, (232, 236, 244), (90, 105, 135)),
    ('2', 'PREPARACIÓN', 'formulación · 92 °C × 5 min', 565, 825, 150, 620, (226, 240, 236), (45, 125, 105)),
    ('3', 'FERMENTACIÓN', '4 × 12.000 L · 43 °C · pH 4,50', 845, 1065, 150, 620, (252, 236, 225), (200, 105, 40)),
    ('4', 'ACONDICIONAMIENTO', 'un pulmón por producto', 1085, 1440, 150, 620, (238, 232, 248), (115, 85, 165)),
    ('5', 'ENVASADO Y ENCAJONADO', 'llenadoras → encajonadoras', 1460, 1700, 150, 620, (252, 228, 236), (195, 60, 100)),
    ('6', 'PALETIZADO, CÁMARA Y DESPACHO', 'robot · envolvedora · montacargas · cámara 2–4 °C', 1720, 2240, 150, 620, (228, 238, 248), (45, 105, 165)),
    ('7', 'LÍNEA DE QUESOS · 50.000 L/día', 'tinas · hilado y moldeo · salmuera · empaque al vacío · cámara 2–4 °C', 565, 2240, 640, 890, (250, 243, 220), (163, 124, 18)),
    ('8', 'LÍNEA DE LECHE UHT · 43.000 L/día', 'mezcla · UHT 137 °C × 4 s · envasado aséptico · bodega ambiente', 565, 2240, 910, 1160, (227, 242, 230), (61, 138, 82)),
]


def rgb(c):
    return f'makeRGBValue({c[0]}, {c[1]}, {c[2]})'


def rect(x, y, w_, h_, c, lw=-1, layer=1):
    G.append(f'm.drawRectangle({layer}, {int(x)}, {int(y)}, {int(w_)}, {int(h_)}, {rgb(c)}, {lw})')


def line(x1, y1, x2, y2, c, lw=2, layer=2):
    G.append(f'm.drawLine({layer}, {int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}, {rgb(c)}, {lw})')


def text(x, y, s, size=12, c=INK):
    G.append(f'm.drawText(3, {int(x)}, {int(y)}, {rgb(c)}, {size}, "{s.replace(chr(34), chr(39))}")')


text(60, 28, 'Planta láctea · Lácteos Altos de Teusacá · 150.000 L/día · Escenario actual (sin automatización)', 22, NAVY)
text(1500, 34, 'Acta 9-oct-2026: yogures ≈ 57.000 · quesos 50.000 · leche UHT 43.000 L/día', 11, ACC)
text(60, 80, 'Plant Simulation 2404 · un lote = 10.000 L · 91 lotes por semana: 35 de yogur (13 natural, 9 griego, 13 fresa), 30 de queso y 26 de leche UHT · OEE de llenadoras ≈ 70 %', 11, SOFT)
line(60, 104, 2230, 104, NAVY, 2)
for num, tit, sub, x0, x1, YT, YB, fondo, borde in SECC:
    rect(x0, YT, x1 - x0, YB - YT, fondo)
    rect(x0, YT, x1 - x0, YB - YT, borde, 2, 2)
    hc = 58 if YB - YT > 300 else 44                         # cartel de la sección (más bajo en las franjas de quesos y leche)
    rect(x0, YT, x1 - x0, hc, borde)
    rect(x0 + 10, YT + 8, hc - 16, hc - 16, (255, 255, 255))
    text(x0 + 10 + (hc - 16) / 2 - 6, YT + 10, num, 18 if hc == 58 else 14, borde)
    text(x0 + hc, YT + 7, tit, 14 if hc == 58 else 12, (255, 255, 255))
    text(x0 + hc, YT + (34 if hc == 58 else 26), sub, 9, (255, 255, 255))
ETIQ = {'Cisternas': 'Cisternas', 'U111_Recepcion': 'Recepción U111/U112', 'U113_Leche_cruda': 'Leche cruda 2 × 60.000 L',
        'U121_Pasteurizador': 'Clarificación + HTST', 'U123AB_Silo_entera': 'Silos leche entera', 'U123C_Silo_descremada': 'Silo descremada',
        'U201_Formulacion': 'Formulación U201', 'U202_Tratamiento': 'Tratamiento U202', 'U215_Enfriamiento': 'Ruptura y enfriamiento',
        'U216_Separador_griego': 'Separador griego', 'U214A_Pulmon_fresa': 'Pulmón fresa U214A', 'U214B_Pulmon_natural': 'Pulmón natural U214B',
        'U217_Pulmones_griego': 'Pulmones griego',
        'Reparto_fresa': 'Reparto fresa', 'Reparto_natural': 'Reparto natural', 'Reparto_griego': 'Reparto griego',
        'U311_Vasos': 'U311 vasos 12.000/h', 'U312_Botellas': 'U312 botellas', 'U313_Griego': 'U313 griego',
        'Registro_de_lotes': 'Registro de lotes', 'U341_Paletizado': 'Paletizado U341', 'U411_Camara': 'Cámara 2–4 °C'}
for i, f in enumerate(FERM):
    ETIQ[f] = f.split('_')[0]
for c in DESP:
    ETIQ[f'Despacho_{c}'] = c
# leyenda
rect(30, 1190, 1100, 160, (255, 255, 255))
rect(30, 1190, 1100, 160, NAVY, 2, 2)
text(50, 1200, 'Cómo leer el modelo', 13, NAVY)
text(50, 1225, f'Cada lote es una entidad de 10.000 L. En las llenadoras, cada entidad es {int(CHUNK_H * 60)} min de llenado a velocidad nominal (≈ {n1(T_CHUNK * 60)} min reales con OEE y paradas planeadas).', 10, INK)
text(50, 1247, 'U202 hace un CIP-C de 1,4 h al cambiar de producto; las llenadoras, un cambio de formato de 0,75 h. El orden es natural → griego → fresa.', 10, INK)
text(50, 1269, 'Yogures: recetas v1.8. Quesos y leche UHT: Recetas_basicas_planta_v1.0, valores de diseño por lote (tina 3,5 h; hilado 1 h; salmuera 8 h; UHT 1 h;', 10, INK)
text(50, 1291, 'envasado aséptico 2 h; cuarentena UHT 24 h) hasta tener sus recetas. Se simulan solo los días de producción (6 por semana).', 10, INK)
text(50, 1313, 'Cada bulto de queso o de leche que pasa por la banda es 1/20 o 1/40 del lote.', 10, INK)

json.dump({'coord': COORD, 'ferm': FERM, 'desp': DESP, 'secciones': SECC, 'Y0': Y0, 'YQ': YQ, 'YL': YL, 'tinas': TINAS},
          open(os.path.join(D, 'coords_planta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

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
while ps.IsSimulationRunning() and time.time() - t0 < 900:
    time.sleep(0.5)
print('simulado', round(time.time() - t0), 's', flush=True)
gv = lambda p: ps.GetValue('.Models.Model.' + p)
R = {'dias_produccion': DIAS, 'chunks': CHUNKS, 't_chunk_h': T_CHUNK}
lotes = {p: gv(f'Reparto_{n}.StatNumIn') for p, n in (('YF', 'fresa'), ('YN', 'natural'), ('YG', 'griego'))}
R['lotes'] = lotes
R['lotes_dia'] = sum(lotes.values()) / DIAS
R['litros_dia'] = R['lotes_dia'] * 10000
und = {c: gv(f'Despacho_{c}.StatNumIn') * UND_CHUNK[c] / DIAS for c in DESP}
R['unidades_dia'] = und
R['recepcion_dia'] = gv('U111_Recepcion.StatNumOut') * 10000 / DIAS
R['quesos_lotes_dia'] = gv('Q311_Empaque_vacio.StatNumIn') / DIAS
R['leche_lotes_dia'] = gv('L311_Envasadora_aseptica.StatNumIn') / DIAS
R['debug'] = {k: gv(k + '.StatNumIn') for k in ('Q312_Registro', 'Q341_Paletizado', 'Despacho_quesos', 'L312_Registro', 'L341_Paletizado', 'Despacho_leche', 'U124_Silo_quesos', 'U125_Silo_leche')}
R['quesos_L_dia'] = R['quesos_lotes_dia'] * 10000
R['leche_L_dia'] = R['leche_lotes_dia'] * 10000
R['queso_kg_dia'] = R['quesos_lotes_dia'] * (1000 + 1110 + 1330) / 3   # kg por lote según las recetas básicas (10 · 9 · 7,5 L/kg)
R['leche_envases_dia'] = R['leche_lotes_dia'] * (14 * 9800 + 12 * 9875) / 26   # envases de 1 L por lote (recetas básicas)
R['vasos_U311_dia'] = und['YF150'] + und['YN200']
R['botellas_U312_dia'] = und['YF1000'] + und['YF1750'] + und['YN1000']
R['griego_U313_dia'] = und['YG150'] + und['YG500']
U = {}
for o in ['U111_Recepcion', 'U121_Pasteurizador', 'U201_Formulacion', 'U202_Tratamiento'] + FERM + \
         ['U215_Enfriamiento', 'U216_Separador_griego', 'U311_Vasos', 'U312_Botellas', 'U313_Griego', 'U321_Encajonadora_vasos', 'U322_Encajonadora_botellas',
          'U323_Encajonadora_griego', 'U341_Paletizado', 'U342_Envolvedora'] + TINAS + \
         ['Q301_Hilado', 'Q311_Empaque_vacio', 'Q341_Paletizado', 'L201_Mezcla', 'L202_UHT', 'L311_Envasadora_aseptica', 'L341_Paletizado']:
    U[o] = {k: round(gv(f'{o}.Stat{a}Portion'), 4) for k, a in (('trabajando', 'Working'), ('cambio', 'Setup'), ('falla', 'Fail'),
                                                                   ('bloqueado', 'Blocking'), ('esperando', 'Waiting'))}
    U[o]['ocupado'] = round(U[o]['trabajando'] + U[o]['cambio'] + U[o]['falla'], 4)
R['uso'] = U
R['cola_en_cisternas'] = gv('Cisternas.StatNumOut')
print(json.dumps(R, ensure_ascii=False), flush=True)
json.dump(R, open(os.path.join(D, 'resultados_planta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# resultados dibujados en el modelo
res = [f'Resultados de la simulación ({DIAS} días de producción)',
       f'Tronco común: {n1(R["recepcion_dia"], 0)} L/día recibidos · pasteurizador {n1(U["U121_Pasteurizador"]["ocupado"] * 100, 0)} %',
       f'Quesos: {n1(R["quesos_L_dia"], 0)} L/día ≈ {n1(R["queso_kg_dia"], 0)} kg de queso · hilado {n1(U["Q301_Hilado"]["ocupado"] * 100, 0)} % · tinas {n1(sum(U[x]["ocupado"] for x in TINAS) / 3 * 100, 0)} %',
       f'Leche UHT: {n1(R["leche_L_dia"], 0)} L/día ≈ {n1(R["leche_envases_dia"], 0)} envases de 1 L · UHT {n1(U["L202_UHT"]["ocupado"] * 100, 0)} % · envasadora {n1(U["L311_Envasadora_aseptica"]["ocupado"] * 100, 0)} %',
       f'Leche a yogures: {n1(R["litros_dia"], 0)} L/día ({n1(R["lotes_dia"], 2)} lotes/día)',
       f'Envases por día: {n1(R["vasos_U311_dia"], 0)} vasos · {n1(R["botellas_U312_dia"], 0)} botellas · {n1(R["griego_U313_dia"], 0)} griego',
       f'Uso U311 vasos: {n1(U["U311_Vasos"]["ocupado"] * 100, 0)} % · U312: {n1(U["U312_Botellas"]["ocupado"] * 100, 0)} % · U313: {n1(U["U313_Griego"]["ocupado"] * 100, 0)} %',
       f'Fermentadores: {n1(sum(U[f]["ocupado"] for f in FERM) / 4 * 100, 0)} % · cuello de botella: U311 vasos']
G2 = [f'm.drawRectangle(1, 1150, 1190, 1090, 215, {rgb((255, 255, 255))}, -1)', f'm.drawRectangle(2, 1150, 1190, 1090, 215, {rgb(NAVY)}, 2)']
for i, s in enumerate(res):
    G2.append(f'm.drawText(3, 1168, {1200 + i * 25}, {rgb(NAVY if i == 0 else INK)}, {12 if i == 0 else 11}, "{s}")')
ps.ExecuteSimTalk('var m: object := .Models.Model\n' + '\n'.join(G2))
if OUT != '-':
    ps.ExecuteSimTalk('var b: object := .Tools.BottleneckAnalyzer.BottleneckAnalyzer.createObject(.Models.Model, 200, 120)\n'
                      'b.Name := "Analizador_cuellos"\nb.analyzeModel')
    ps.ExecuteSimTalk('.Models.Model.EventController.reset')
    ps.ExecuteSimTalk('.Models.Model.EventController.Speed := 100\n.Models.Model.EventController.RealTime := true\n'
                      f'.Models.Model.EventController.RealTimeScale := {TIEMPO_REAL}')
    ps.SaveModel(os.path.abspath(OUT))
    print('guardado', flush=True)
ps.Quit()
