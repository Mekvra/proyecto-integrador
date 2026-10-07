# Modelo "vitrina 3D" de la planta láctea (escenario propuesto) para Plant Simulation 2404, licencia estudiantil.
# Misma lógica de build_model.py (prop) + camiones cisterna, silos y fermentadores como tanques 3D, bandas,
# montacargas, muelle de despacho y operarios que caminan. Uso: python construir_vitrina_3d.py <salida.spp> [dias]
import sys, os, time, json
import win32com.client as w

H = 3600.0
OUT = sys.argv[1]
DIAS = float(sys.argv[2]) if len(sys.argv) > 2 else 30
ICO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iconos')
DX, DY = 360, 160  # desplazamiento de la lógica para dejar espacio a recepción y silos


def h(x):
    return int(round(x * H))


P = dict(y_incub=5.0, y_enfr=1.25, y_cip=0.75, drain_y=2.72 / 0.948, u202_cambios=1, k_ferm=20.0, k_vac=0.5, k_cip=0.75,
         drain_k=2.19 / 0.95, q_acid=2.5, emp_q=1.51 / 0.92)
u202_y = 1.25 + (3 * 0.75 + P['u202_cambios'] * 0.75 + 1.5) / 6
L, CON, ICONOS, DECOR, WORK = ['var m: object := .Models.Model'], [], {}, [], []


def obj(var, cls, name, x, y, proc=None, icon=None, shift=True):
    if shift:
        x, y = x + DX, y + DY
    s = [f'var {var}: object := {cls}.createObject(m, {x}, {y})', f'{var}.Name := "{name}"']
    if proc is not None:
        s.append(f'{var}.ProcTime := {h(proc)}')
    if icon:
        ICONOS[name] = icon
    return s


MF = '.MaterialFlow'
# clases de lote por línea y de presentación (las crea la DismantleStation de cada línea)
for n in ('Lote_Yogur', 'YF1000', 'YF1750', 'Lote_Queso', 'QM1000', 'QM250', 'Lote_Kefir', 'KF500', 'KF1000'):
    L.append(f'var mu_{n.lower()}: object := .MUs.Part.duplicate(.MUs, "{n}")')
# tiempos de envasado por presentación, iguales a construir_vsm.py (escenario propuesto)
T_ENV = dict(U311=2.866, U312=0.791, U321=0.607, U322=0.382, U331=1.061, U341=0.414, TQK=1.0)


def reparto(var, filas):
    out = [f't := {var}.DismantleTable']
    for i, (mu, sc) in enumerate(filas, 1):
        out += [f't[1, {i}] := .MUs.{mu}', f't[2, {i}] := 1', f't[3, {i}] := {sc}']
    return out + [f'{var}.DismantleTable := t', f'{var}.MainMU := 1', f'{var}.Sequence := "MUs exiting independent of other MUs"']


L.append('var t: table')
# ---- línea 1: yogur ----
L += obj('sy', MF + '.Source', 'Pedidos_Yogur', 64, 170, icon='pedidos_yogur') + ['sy.Interval := ' + str(h(4.0)), 'sy.Path := .MUs.Lote_Yogur']
L += obj('cy', MF + '.Buffer', 'Cola_Yogur', 192, 170, icon='cola_yogur') + ['cy.Capacity := -1']
L += obj('u201', MF + '.Station', 'U201_Formulacion', 320, 170, 1.1 + 0.5, 'formulacion')
L += obj('u202', MF + '.Station', 'U202_Base', 448, 170, u202_y, 'u202')
for i in range(3):
    L += obj(f'fy{i}', MF + '.Station', f'Fermentador_Yogur_{i + 1}', 608, 75 + 95 * i, 0.25 + P['y_incub'] + P['y_enfr'] + P['y_cip'], 'fermentador_yogur')
L += obj('pe', MF + '.Buffer', 'Pulmones_en_espera', 736, 170, icon='pulmones') + ['pe.Capacity := 1']
L += obj('u214', MF + '.DismantleStation', 'U214_Pulmon', 832, 170, 0.0, 'pulmones') + reparto('u214', [('YF1000', 2), ('YF1750', 2)])
L += obj('u311', MF + '.Station', 'U311', 920, 120, T_ENV['U311'], 'vsm_u311')
L += obj('u312', MF + '.Station', 'U312', 920, 220, T_ENV['U312'], 'vsm_u312')
L += obj('cvy', MF + '.Conveyor', 'Banda_Yogur', 990, 170) + ['cvy.Length := 4']
L += obj('dy', MF + '.Drain', 'Camara_Yogur', 1060, 170, icon='camara_yogur')
CON += [('sy', 'cy'), ('cy', 'u201'), ('u201', 'u202')] + [('u202', f'fy{i}') for i in range(3)] + [(f'fy{i}', 'pe') for i in range(3)]
CON += [('pe', 'u214'), ('u214', 'u311'), ('u214', 'u312'), ('u311', 'cvy'), ('u312', 'cvy'), ('cvy', 'u341')]
# ---- línea 3: kéfir ----
L += obj('sk', MF + '.Source', 'Pedidos_Kefir', 64, 520, icon='pedidos_kefir') + ['sk.Interval := ' + str(h(8.0)), 'sk.Path := .MUs.Lote_Kefir']
L += obj('ck', MF + '.Buffer', 'Cola_Kefir', 192, 520, icon='cola_kefir') + ['ck.Capacity := -1']
L += obj('u202k', MF + '.Station', 'U202_Tramo_Kefir', 448, 520, 0.75, 'u202')
for i in range(4):
    L += obj(f'fk{i}', MF + '.Station', f'Fermentador_Kefir_{i + 1}', 608, 380 + 95 * i, 0.33 + 0.25 + P['k_ferm'] + 0.5 + P['k_vac'] + P['k_cip'], 'fermentador_kefir')
for j in range(2):
    L += obj(f'tk{j}', MF + '.DismantleStation', f'Tanque_Kefir_{j + 1}', 768, 470 + 95 * j, T_ENV['TQK'], 'tanque_kefir') + \
        reparto(f'tk{j}', [('KF500', 1), ('KF1000', 1)])
L += obj('u331', MF + '.Station', 'U331', 870, 520, T_ENV['U331'], 'vsm_u331')
L += obj('cvk', MF + '.Conveyor', 'Banda_Kefir', 960, 520) + ['cvk.Length := 4']
L += obj('dk', MF + '.Drain', 'Camara_Kefir', 1060, 520, icon='camara_kefir')
CON += [('sk', 'ck'), ('ck', 'u202k')] + [('u202k', f'fk{i}') for i in range(4)] + [(f'fk{i}', f'tk{j}') for i in range(4) for j in range(2)]
CON += [(f'tk{j}', 'u331') for j in range(2)] + [('u331', 'cvk'), ('cvk', 'u341')]
# ---- línea 2: mozzarella ----
yq = 1080
L += obj('sq', MF + '.Source', 'Pedidos_Mozzarella', 64, yq, icon='pedidos_queso') + ['sq.Interval := ' + str(h(4.8)), 'sq.Path := .MUs.Lote_Queso']
L += obj('cq', MF + '.Buffer', 'Cola_Mozzarella', 192, yq, icon='cola_queso') + ['cq.Capacity := -1']
L += obj('tq', MF + '.Station', 'U221_Tina', 320, yq, 2.93 + 0.5, 'tina')
L += obj('bq', MF + '.Station', 'U222_Acidificacion', 448, yq, P['q_acid'] + 0.25, 'banda')
L += obj('hq', MF + '.Station', 'U223_Hiladora', 576, yq, 500 / 600 + 0.25, 'hiladora')
for i in range(4):
    L += obj(f'sa{i}', MF + '.Station', f'Salmuera_{i + 1}', 704, yq - 140 + 95 * i, 3.0, 'salmuera')
L += obj('rq', MF + '.DismantleStation', 'Reparto_Queso', 840, yq, 0.0, 'vsm_reparto_q') + reparto('rq', [('QM1000', 1), ('QM250', 2)])
L += obj('u321', MF + '.Station', 'U321', 920, yq - 50, T_ENV['U321'], 'vsm_u321')
L += obj('u322', MF + '.Station', 'U322', 920, yq + 50, T_ENV['U322'], 'vsm_u322')
L += obj('cvq', MF + '.Conveyor', 'Banda_Queso', 990, yq) + ['cvq.Length := 4']
L += obj('dq', MF + '.Drain', 'Camara_Queso', 1060, yq, icon='camara_queso')
CON += [('sq', 'cq'), ('cq', 'tq'), ('tq', 'bq'), ('bq', 'hq')] + [('hq', f'sa{i}') for i in range(4)] + [(f'sa{i}', 'rq') for i in range(4)]
CON += [('rq', 'u321'), ('rq', 'u322'), ('u321', 'cvq'), ('u322', 'cvq'), ('cvq', 'u341')]
# ---- fin de línea común: encajonado y paletizado U341 -> cámara de cada línea ----
L += obj('u341', MF + '.Station', 'U341_Paletizado', 1240, 960, T_ENV['U341'], 'vsm_paletizado', shift=False)
CON += [('u341', 'dy'), ('u341', 'dk'), ('u341', 'dq')]
RUTA = [(n, 1) for n in ('Lote_Yogur', 'YF1000', 'YF1750')] + [(n, 2) for n in ('Lote_Kefir', 'KF500', 'KF1000')] + \
       [(n, 3) for n in ('Lote_Queso', 'QM1000', 'QM250')]
L += ['u341.ExitStrategy := "MU Attribute"', 'u341.AttributeType := "String"', 't := u341.ExitStrategyMUAttributeList']
for i_, (n_, s_) in enumerate(RUTA, 1):
    L += [f't[1, {i_}] := "Name"', f't[2, {i_}] := "{n_}"', f't[3, {i_}] := {s_}']
L.append('u341.ExitStrategyMUAttributeList := t')

# ---- recepción de leche: camiones cisterna (10 al día) ----
L += obj('sc', MF + '.Source', 'Cisternas_de_leche', 40, 60, shift=False) + ['sc.Path := .MUs.Transporter', 'sc.Interval := ' + str(h(2.4))]
L += obj('via1', MF + '.Track', 'Via_de_ingreso', 120, 60, shift=False) + ['via1.Length := 12']
L += obj('rec', MF + '.Station', 'Recepcion_de_leche', 380, 60, 0.45, shift=False)
L += obj('via2', MF + '.Track', 'Via_de_salida', 440, 60, shift=False) + ['via2.Length := 14']
L += obj('dc', MF + '.Drain', 'Salida_cisternas', 740, 60, shift=False)
CON += [('sc', 'via1'), ('via1', 'rec'), ('rec', 'via2'), ('via2', 'dc')]
# ---- despacho: camiones de producto terminado ----
L += obj('sd', MF + '.Source', 'Camiones_despacho', 1500, 1480, shift=False) + ['sd.Path := .MUs.Transporter', 'sd.Interval := ' + str(h(1.5))]
L += obj('via3', MF + '.Track', 'Via_al_muelle', 1580, 1480, shift=False) + ['via3.Length := 10']
L += obj('mue', MF + '.Station', 'Muelle_de_despacho', 1800, 1480, 0.5, shift=False)
L += obj('via4', MF + '.Track', 'Via_de_despacho', 1860, 1480, shift=False) + ['via4.Length := 12']
L += obj('dd', MF + '.Drain', 'Salida_despacho', 2120, 1480, shift=False)
CON += [('sd', 'via3'), ('via3', 'mue'), ('mue', 'via4'), ('via4', 'dd')]
# ---- montacargas en el pasillo de las cámaras frías ----
L += obj('sm', MF + '.Source', 'Montacargas', 1500, 300, shift=False) + ['sm.Path := .MUs.Transporter', 'sm.Interval := 900']
L += obj('pas', MF + '.Track', 'Pasillo_de_bodega', 1580, 300, shift=False) + ['pas.Length := 40']
L += obj('dm', MF + '.Drain', 'Fin_pasillo', 2420, 300, shift=False)
CON += [('sm', 'pas'), ('pas', 'dm')]
# ---- operarios ----
L += obj('wp', '.Resources.WorkerPool', 'Operarios', 900, 820, shift=False)
L += obj('bk', '.Resources.Broker', 'Coordinador', 1000, 820, shift=False)
WORK = ['rec', 'tq', 'hq', 'u311', 'u312', 'u321', 'u322', 'u331', 'u341', 'mue']
# ---- silos y tanques decorativos (Fluids.Tank) ----
TANQUES = [('Tanque_crudo_1', 120, 300, 'comun'), ('Tanque_crudo_2', 220, 300, 'comun'),
           ('Silo_S1_yogur', 120, 520, 'yogur'), ('Silo_S2_queso', 220, 520, 'queso'), ('Silo_S3_kefir', 320, 520, 'kefir')]
for i, (nm, x, y, c) in enumerate(TANQUES):
    L += obj(f'tt{i}', '.Fluids.Tank', nm, x, y, shift=False)
    DECOR.append((nm, c, [2.2, 2.2, 3.2]))
for i in range(3):
    DECOR.append((f'Fermentador_Yogur_{i + 1}', 'yogur', None))
for i in range(4):
    DECOR.append((f'Fermentador_Kefir_{i + 1}', 'kefir', None))
for nm, c, _ in list(DECOR):
    pass

for a, b in CON:
    L.append(f'.MaterialFlow.Connector.connect({a}, {b})')
L.append(f'm.EventController.End := {h(24 * DIAS)}')
# fallas de equipo, iguales a construir_modelo.py (escenario propuesto con TPM)
for nm, (mtbf, mttr) in {'U311': (60.0, 0.75), 'U312': (60.0, 0.75), 'U321': (60.0, 0.75), 'U322': (60.0, 0.75),
                         'U331': (60.0, 0.75), 'U201_Formulacion': (120.0, 1.0),
                         'U202_Base': (120.0, 1.0), 'U202_Tramo_Kefir': (120.0, 1.0), 'U221_Tina': (120.0, 1.0),
                         'U222_Acidificacion': (120.0, 1.0), 'U223_Hiladora': (120.0, 1.0)}.items():
    L += [f'm.{nm}.Failures.createFailure("Falla")', f'm.{nm}.Failures.Falla.AvailabilityOn := true',
          f'm.{nm}.Failures.Falla.Availability := {round(100 * mtbf / (mtbf + mttr), 2)}', f'm.{nm}.Failures.Falla.MTTR := {h(mttr)}',
          f'm.{nm}.Failures.Falla.Mode := "ProcessingTime"']
# operarios: pool, broker, tabla de creación y estaciones atendidas
L += ['m.Operarios.BrokerPath := m.Coordinador', 'm.Operarios.WorkersTravelMode := "Move freely within area"',
      'm.Operarios.WorkersCanWorkRemotely := true', 'm.Operarios.getCreationTable(t)',
      't[1, 1] := .Resources.Worker', 't[2, 1] := 11', 'm.Operarios.setCreationTable(t)']
for v in WORK:
    L += [f'{v}.Imp.Active := true', f'{v}.Imp.BrokerPath := m.Coordinador']
# Sin escena 3D los operarios trabajan "remoto" (la corrida de resultados es sin animación). Los puestos de trabajo
# (Workplace) y WorkersCanWorkRemotely := false se agregan después de crear el 3D (vitrina_post3d.py), porque un operario
# que camina exige la escena 3D.
# iconos 2D y rótulos
VIS = []
for nm, f in ICONOS.items():
    p = os.path.join(ICO, f + '.bmp').replace(chr(92), chr(92) * 2)
    VIS.append(f'm.{nm}.setIconFromFile(1, "{p}")')
for i, (txt, x, y) in enumerate([('Planta láctea Mekvra · vista 3D del escenario propuesto', 40, 10),
                                  ('Recepción de leche y silos', 40, 160), ('Línea 1 · Yogur con trozos de fresa', DX + 64, DY + 30),
                                  ('Línea 3 · Kéfir natural', DX + 64, DY + 360), ('Línea 2 · Queso mozzarella', DX + 64, DY + 900),
                                  ('Cámaras frías y bodega', 1500, 250), ('Muelle de despacho', 1500, 1430),
                                  ('Envasado por presentación', DX + 900, DY + 60), ('Fin de línea: paletizado U341', 1180, 900)]):
    VIS.append(f'm.drawText(3, {x}, {y + 22}, makeRGBValue(27, 42, 120), {16 if i == 0 else 13}, "{txt}")')

# ---- tanques 3D sobre fermentadores y formulación, colores por línea ----
CY, CK, CQ, CG = (236, 112, 140), (70, 140, 200), (232, 180, 40), (150, 160, 175)
DEC3 = []
def tanque(nm, x, y, c, sc, ocultar):
    VIS.extend([f'var {nm.lower()}: object := .Fluids.Tank.createObject(m, {x}, {y})', f'{nm.lower()}.Name := "{nm}"'])
    DEC3.append((nm, c, sc, ocultar))
for i in range(3):
    tanque(f'TQ_Ferm_Yogur_{i + 1}', 608 + DX, 75 + DY + 95 * i, CY, [1.6, 1.6, 2.4], f'Fermentador_Yogur_{i + 1}')
for i in range(4):
    tanque(f'TQ_Ferm_Kefir_{i + 1}', 608 + DX, 380 + DY + 95 * i, CK, [1.4, 1.4, 2.2], f'Fermentador_Kefir_{i + 1}')
for j in range(2):
    tanque(f'TQ_Pulmon_Kefir_{j + 1}', 768 + DX, 470 + DY + 95 * j, CK, [1.2, 1.2, 1.6], f'Tanque_Kefir_{j + 1}')
tanque('TQ_Formulacion', 320 + DX, 170 + DY, CY, [1.6, 1.6, 2.0], 'U201_Formulacion')
for nm, c in (('Tanque_crudo_1', CG), ('Tanque_crudo_2', CG), ('Silo_S1_yogur', CY), ('Silo_S2_queso', CQ), ('Silo_S3_kefir', CK)):
    DEC3.append((nm, c, [2.2, 2.2, 3.2], None))
COL3 = {CY: ['Pedidos_Yogur', 'Cola_Yogur', 'U202_Base', 'Pulmones_en_espera', 'U214_Pulmon', 'Banda_Yogur', 'Camara_Yogur'],
        CK: ['Pedidos_Kefir', 'Cola_Kefir', 'U202_Tramo_Kefir', 'Banda_Kefir', 'Camara_Kefir'],
        CQ: ['Pedidos_Mozzarella', 'Cola_Mozzarella', 'U221_Tina', 'U222_Acidificacion', 'U223_Hiladora', 'Salmuera_1', 'Salmuera_2',
             'Salmuera_3', 'Salmuera_4', 'Reparto_Queso', 'Banda_Queso', 'Camara_Queso'],
        CG: ['Recepcion_de_leche', 'Muelle_de_despacho']}
LOOK = []
for nm, c, sc, oc in DEC3:
    LOOK += [f'm.{nm}._3D.Scale := [{sc[0]}, {sc[1]}, {sc[2]}]', f'm.{nm}._3D.MaterialActive := true',
             f'm.{nm}._3D.MaterialDiffuseColor := makeRGBValue({c[0]}, {c[1]}, {c[2]})']
    if oc:
        LOOK.append(f'm.{oc}._3D.Scale := [0.02, 0.02, 0.02]')
for c, names in COL3.items():
    for n in names:
        LOOK += [f'm.{n}._3D.MaterialActive := true', f'm.{n}._3D.MaterialDiffuseColor := makeRGBValue({c[0]}, {c[1]}, {c[2]})']
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'look3d.txt'), 'w', encoding='utf-8').write('var m: object := .Models.Model' + chr(10) + chr(10).join(LOOK))

ps = w.Dispatch("Tecnomatix.PlantSimulation.RemoteControl.24.4")
ps.SetLicenseType("Student")
ps.NewModel()
ps.ExecuteSimTalk('\n'.join(L))
print('logica', flush=True)
ps.ExecuteSimTalk('var m: object := .Models.Model\n' + '\n'.join(VIS))
print('iconos', flush=True)
try:
    ps.ExecuteSimTalk(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'look3d.txt'), encoding='utf-8').read())
    print('look 3D aplicado antes del 3D', flush=True)
except Exception as e:
    print('look 3D falló', str(e)[:120], flush=True)
t0 = time.time()
ps.ExecuteSimTalk('.Models.Model.EventController.startWithoutAnimation')
time.sleep(1)
while ps.IsSimulationRunning() and time.time() - t0 < 600:
    time.sleep(0.5)
R = {n: ps.GetValue(f'.Models.Model.{n}.StatNumIn') for n in ('Camara_Yogur', 'Camara_Kefir', 'Camara_Queso', 'Salida_cisternas', 'Salida_despacho')}
for n_ in ('Camara_Yogur', 'Camara_Kefir', 'Camara_Queso'):
    R[n_] = R[n_] // 3          # 3 presentaciones por lote
R['cola_yogur'] = ps.GetValue('.Models.Model.Cola_Yogur.NumMU')
print(json.dumps(R), flush=True)
ps.ExecuteSimTalk('.Models.Model.EventController.reset')
ps.SaveModel(OUT)
print('guardado', flush=True)
json.dump(DECOR, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decor.json'), 'w'))
ps.Quit()
