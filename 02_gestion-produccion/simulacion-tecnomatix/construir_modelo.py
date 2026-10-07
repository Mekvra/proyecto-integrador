# Construye y corre el modelo de la planta láctea en Tecnomatix Plant Simulation 2404 (licencia estudiantil) por COM.
# Uso: python construir_modelo.py <base|prop> <salida.spp|-> [dias] [demanda|capacidad] [ajustes_json] [mtbf_json]
# Simplificación: la licencia no deja crear métodos SimTalk por COM, así que U202 (compartida) se modela como carga
# en la cadena de yogur (cada lote de yogur ocupa además su parte del tiempo de kéfir y de los cambios de producto),
# y el kéfir pasa por un tramo propio de U202 con su tiempo de proceso.
import sys, time, json
import win32com.client as w

H = 3600.0
esc = sys.argv[1]
out = sys.argv[2]
DIAS = float(sys.argv[3]) if len(sys.argv) > 3 else 30
MODO = sys.argv[4] if len(sys.argv) > 4 else 'demanda'

P = {
    'base': dict(y_incub=7.0, y_enfr=1.5, y_cip=1.0, lib=0.5, pulm=1, pulm_cip=0.75, drain_y=2.94 / 0.854, u202_cambios=4,
                 k_ferm=24.0, k_vac=0.75, k_ferms=3, k_cip=1.0, k_madur=True, madur=24.0, k_tq=3, drain_k=2.37 / 0.84,
                 q_corte=0.25, q_acid=3.0, emp_q=1.63 / 0.85),
    'prop': dict(y_incub=5.0, y_enfr=1.25, y_cip=0.75, lib=0.0, pulm=2, pulm_cip=0.5, drain_y=2.72 / 0.948, u202_cambios=1,
                 k_ferm=20.0, k_vac=0.5, k_ferms=4, k_cip=0.75, k_madur=False, madur=12.0, k_tq=2, drain_k=2.19 / 0.95,
                 q_corte=0.0, q_acid=2.5, emp_q=1.51 / 0.92),
}[esc]
if len(sys.argv) > 5:
    P.update(json.loads(sys.argv[5]))


def h(x):
    return int(round(x * H))


u202_y = 1.25 + (3 * 0.75 + P['u202_cambios'] * 0.75 + 1.5) / 6
ferm_y = 0.25 + P['y_incub'] + P['y_enfr']
ferm_k = 0.33 + 0.25 + P['k_ferm'] + 0.5 + P['k_vac']
pulm_y = P['lib'] + P['drain_y']
iy, ik, iq = (h(4.0), h(8.0), h(4.8)) if MODO == 'demanda' else (60, 60, 60)
tk_name = 'Maduracion_Kefir' if P['k_madur'] else 'Pulmon_Envasado_Kefir'



def one(var, cls, name, x, y, proc=None):
    s = [f'var {var}: object := .MaterialFlow.{cls}.createObject(m, {x}, {y})', f'{var}.Name := "{name}"']
    if proc is not None:
        s.append(f'{var}.ProcTime := {h(proc)}')
    return s


GRUPOS = {}
L = ['var m: object := .Models.Model']
CON = []


def grupo(prefijo, n, proc, x, y0):
    GRUPOS[prefijo] = [f'{prefijo}_{i + 1}' for i in range(n)]
    out = []
    for i in range(n):
        out += one(f'{prefijo.lower()}{i}', 'Station', f'{prefijo}_{i + 1}', x, y0 + 95 * i, proc)
    return out


# yogur (CIP sumado a la ocupación de cada equipo)
L += one('sy', 'Source', 'Pedidos_Yogur', 64, 170) + [f'sy.Interval := {iy}']
L += one('cy', 'Buffer', 'Cola_Yogur', 192, 170) + ['cy.Capacity := -1']
L += one('u201', 'Station', 'U201_Formulacion', 320, 170, 1.1 + 0.5)
L += one('u202', 'Station', 'U202_Base', 448, 170, u202_y)
L += grupo('Fermentador_Yogur', 3, ferm_y + P['y_cip'], 608, 75)
# un pulmón está siempre con el lote que se envasa; los demás pulmones son espera
env_y = pulm_y + (P['pulm_cip'] if P['pulm'] == 1 else 0)
L += one('env', 'Station', 'Envasado_U311_U312', 832, 170, env_y)
L += one('dy', 'Drain', 'Camara_Yogur', 992, 170)
CON += [('sy', 'cy'), ('cy', 'u201'), ('u201', 'u202')]
CON += [('u202', f'fermentador_yogur{i}') for i in range(3)]
if P['pulm'] > 1:
    L += one('pe', 'Buffer', 'Pulmones_en_espera', 736, 170) + [f"pe.Capacity := {P['pulm'] - 1}"]
    CON += [(f'fermentador_yogur{i}', 'pe') for i in range(3)] + [('pe', 'env')]
else:
    CON += [(f'fermentador_yogur{i}', 'env') for i in range(3)]
CON += [('env', 'dy')]
# kéfir
L += one('sk', 'Source', 'Pedidos_Kefir', 64, 520) + [f'sk.Interval := {ik}']
L += one('ck', 'Buffer', 'Cola_Kefir', 192, 520) + ['ck.Capacity := -1']
L += one('u202k', 'Station', 'U202_Tramo_Kefir', 448, 520, 0.75)
L += grupo('Fermentador_Kefir', P['k_ferms'], ferm_k + P['k_cip'], 608, 380)
tq_proc = (P['madur'] if P['k_madur'] else 0) + 0.5 + P['drain_k'] + (0.75 if P['k_madur'] else 0.5)
L += grupo('Tanque_Kefir', P['k_tq'], tq_proc, 768, 470)
L += one('dk', 'Drain', 'Camara_Kefir', 928, 520)
CON += [('sk', 'ck'), ('ck', 'u202k')]
CON += [('u202k', f'fermentador_kefir{i}') for i in range(P['k_ferms'])]
CON += [(f'fermentador_kefir{i}', f'tanque_kefir{j}') for i in range(P['k_ferms']) for j in range(P['k_tq'])]
CON += [(f'tanque_kefir{j}', 'dk') for j in range(P['k_tq'])]
# mozzarella
L += one('sq', 'Source', 'Pedidos_Mozzarella', 64, 1080) + [f'sq.Interval := {iq}']
L += one('cq', 'Buffer', 'Cola_Mozzarella', 192, 1080) + ['cq.Capacity := -1']
L += one('tq', 'Station', 'U221_Tina', 320, 1080, 2.93 + P['q_corte'] + 0.5)
L += one('bq', 'Station', 'U222_Acidificacion', 448, 1080, P['q_acid'] + 0.25)
L += one('hq', 'Station', 'U223_Hiladora', 576, 1080, 500 / 600 + 0.25)
L += grupo('Salmuera', 4, 3.0, 704, 940)
L += one('eq', 'Station', 'U321_Empaque', 864, 1080, P['emp_q'])
L += one('dq', 'Drain', 'Camara_Queso', 992, 1080)
CON += [('sq', 'cq'), ('cq', 'tq'), ('tq', 'bq'), ('bq', 'hq')]
CON += [('hq', f'salmuera{i}') for i in range(4)] + [(f'salmuera{i}', 'eq') for i in range(4)] + [('eq', 'dq')]
for a, b in CON:
    L.append(f'.MaterialFlow.Connector.connect({a}, {b})')
L.append(f'm.EventController.End := {h(24 * DIAS)}')

# --- fallas de equipo (perfil "Falla": disponibilidad y MTTR, cuenta solo mientras la máquina procesa) ---
# Envasadoras: MTBF/MTTR del modelo de capacidad (base 40 h / 1 h; propuesta con TPM 60 h / 0,75 h).
# Equipos de proceso: supuesto base 80 h / 1,5 h; propuesta con TPM 120 h / 1 h. Tanques y fermentadores sin fallas
# (su parada es el CIP, ya incluido en el tiempo). El tiempo del envasado de yogur ya no descuenta fallas.
# La llenadora de kéfir U331 vacía los tanques de kéfir: sus fallas siguen dentro del factor de drain_k.
MTBF = {'base': {'env': (40.0, 1.0), 'proc': (80.0, 1.5)}, 'prop': {'env': (60.0, 0.75), 'proc': (120.0, 1.0)}}[esc]
if len(sys.argv) > 6:
    MTBF.update(json.loads(sys.argv[6]))
FALLAS = {'Envasado_U311_U312': 'env', 'U321_Empaque': 'env', 'U201_Formulacion': 'proc', 'U202_Base': 'proc',
          'U202_Tramo_Kefir': 'proc', 'U221_Tina': 'proc', 'U222_Acidificacion': 'proc', 'U223_Hiladora': 'proc'}
for nm, tipo in FALLAS.items():
    mtbf, mttr = MTBF[tipo]
    disp = round(100 * mtbf / (mtbf + mttr), 2)
    L += [f'm.{nm}.Failures.createFailure("Falla")', f'm.{nm}.Failures.Falla.AvailabilityOn := true',
          f'm.{nm}.Failures.Falla.Availability := {disp}', f'm.{nm}.Failures.Falla.MTTR := {h(mttr)}',
          f'm.{nm}.Failures.Falla.Mode := "ProcessingTime"']

# --- presentación: iconos a color y rótulos por línea ---
import os
ICO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iconos')
ICONOS = {'Pedidos_Yogur': 'pedidos_yogur', 'Cola_Yogur': 'cola_yogur', 'U201_Formulacion': 'formulacion', 'U202_Base': 'u202',
          'Envasado_U311_U312': 'llenadora_yogur', 'Camara_Yogur': 'camara_yogur', 'Pulmones_en_espera': 'pulmones',
          'Pedidos_Kefir': 'pedidos_kefir', 'Cola_Kefir': 'cola_kefir', 'U202_Tramo_Kefir': 'u202', 'Camara_Kefir': 'camara_kefir',
          'Pedidos_Mozzarella': 'pedidos_queso', 'Cola_Mozzarella': 'cola_queso', 'U221_Tina': 'tina', 'U222_Acidificacion': 'banda',
          'U223_Hiladora': 'hiladora', 'U321_Empaque': 'llenadora_queso', 'Camara_Queso': 'camara_queso'}
for g, f in (('Fermentador_Yogur', 'fermentador_yogur'), ('Fermentador_Kefir', 'fermentador_kefir'), ('Tanque_Kefir', 'tanque_kefir'), ('Salmuera', 'salmuera')):
    for nm in GRUPOS.get(g, []):
        ICONOS[nm] = f
VIS = []
for nm, f in ICONOS.items():
    if any(f"Name := \"{nm}\"" in x for x in L):
        p = os.path.join(ICO, f + '.bmp').replace(chr(92), chr(92) * 2)
        VIS.append(f'm.{nm}.setIconFromFile(1, "{p}")')
titulo = 'Escenario base (antes de la propuesta)' if esc == 'base' else 'Escenario propuesto'
for i, (txt, x, y) in enumerate([(f'Planta láctea Mekvra · {titulo}', 64, 20), ('Línea 1 · Yogur con trozos de fresa', 64, 70),
                                  ('Línea 3 · Kéfir natural', 64, 360), ('Línea 2 · Queso mozzarella', 64, 900)]):
    VIS += [f'var t{i}: object := .UserInterface.Comment.createObject(m, {x}, {y})', f't{i}.Name := "Rotulo_{i}"', f't{i}.Text := "{txt}"']


ps = w.Dispatch("Tecnomatix.PlantSimulation.RemoteControl.24.4")
ps.SetLicenseType("Student")
ps.NewModel()
ps.ExecuteSimTalk('\n'.join(L))
ps.ExecuteSimTalk('var m: object := .Models.Model\n' + '\n'.join(VIS))
t0 = time.time()
ps.ExecuteSimTalk('.Models.Model.EventController.startWithoutAnimation')
time.sleep(1)
while ps.IsSimulationRunning() and time.time() - t0 < 600:
    time.sleep(0.5)

R = {'escenario': esc, 'modo': MODO, 'dias': DIAS, 'ajustes': sys.argv[5] if len(sys.argv) > 5 else '', 'seg_reales': round(time.time() - t0, 1)}
for nm in ('Camara_Yogur', 'Camara_Kefir', 'Camara_Queso'):
    R[nm] = ps.GetValue(f'.Models.Model.{nm}.StatNumIn')
for nm in ('Cola_Yogur', 'Cola_Kefir', 'Cola_Mozzarella'):
    R[nm] = ps.GetValue(f'.Models.Model.{nm}.NumMU')
U = {}
def stat(o):
    wk = ps.GetValue(f'.Models.Model.{o}.StatWorkingPortion')
    bl = ps.GetValue(f'.Models.Model.{o}.StatBlockingPortion')
    wt = ps.GetValue(f'.Models.Model.{o}.StatWaitingPortion')
    fa = ps.GetValue(f'.Models.Model.{o}.StatFailPortion')
    return wk, bl, wt, fa
for o in ('U201_Formulacion', 'U202_Base', 'Envasado_U311_U312', 'U202_Tramo_Kefir', 'U221_Tina', 'U222_Acidificacion', 'U223_Hiladora', 'U321_Empaque'):
    wk, bl, wt, fa = stat(o)
    U[o] = dict(trabajando=round(wk, 4), bloqueado=round(bl, 4), en_falla=round(fa, 4), esperando=round(wt, 4), ocupacion=round(1 - wt, 4))
for g, names in GRUPOS.items():
    vals = [stat(o) for o in names]
    n = len(vals)
    U[g + f' (x{n})'] = dict(trabajando=round(sum(v[0] for v in vals) / n, 4), bloqueado=round(sum(v[1] for v in vals) / n, 4),
                             en_falla=round(sum(v[3] for v in vals) / n, 4), esperando=round(sum(v[2] for v in vals) / n, 4),
                             ocupacion=round(sum(1 - v[2] for v in vals) / n, 4))
R['recursos'] = U
print(json.dumps(R, ensure_ascii=False))
if out != '-':
    # analizador de cuellos de botella: barras de estado (trabajando, bloqueado, en falla...) sobre cada equipo
    ps.ExecuteSimTalk('var b: object := .Tools.BottleneckAnalyzer.BottleneckAnalyzer.createObject(.Models.Model, 760, 20)\n'
                      'b.Name := "Analizador_cuellos"\nb.analyzeModel')
    ps.SaveModel(out)
ps.Quit()
