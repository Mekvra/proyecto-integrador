# Corrige las tablas de reparto (DismantleTable) de los modelos de la línea de yogures ya guardados, sin regenerar la
# escena 3D. Error encontrado el 10-oct-2026: al construir, la variable de tabla arrastraba filas del reparto anterior y
# Reparto_natural tenía una 3.ª fila (12 fragmentos de YF1750 hacia U312 botellas) y Reparto_griego otra (hacia el registro).
# Para cada .spp: arregla las tablas, simula de nuevo las 12 semanas, redibuja el cuadro de resultados del 2D, deja el
# modelo en caliente (30 h) y lo guarda en el mismo archivo. Uso: python corregir_repartos.py <archivo.spp> [...]
import sys, os, time, json
import win32com.client as w

D = os.path.dirname(os.path.abspath(__file__))
H = 3600
DIAS = 72
FILAS = {'Reparto_fresa': [('YF150', 65, 1), ('YF1000', 23, 2), ('YF1750', 12, 2)],
         'Reparto_natural': [('YN200', 43, 1), ('YN1000', 32, 2)],
         'Reparto_griego': [('YG150', 43, 1), ('YG500', 22, 1)]}
UND_LOTE = {r['codigo']: r['und_lote'] for r in json.load(open(os.path.join(D, '..', '..', '..', '01_transformacion-digital', 'isa88',
                                                                             'recetas', 'recetas_yogures.json'), encoding='utf-8'))['referencias']}


def n1(x, d=0):
    return f'{x:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


ps = w.Dispatch("Tecnomatix.PlantSimulation.RemoteControl.24.4")
ps.SetLicenseType("Student")
for spp in sys.argv[1:]:
    ruta = os.path.abspath(spp)
    ps.LoadModel(ruta)
    gv = lambda p: ps.GetValue('.Models.Model.' + p)
    L = ['var m: object := .Models.Model', 'var t: table', 'm.EventController.reset']
    for r, filas in FILAS.items():
        L += [f't := m.{r}.DismantleTable', 't.delete']
        for i, (mu, n, suc) in enumerate(filas, 1):
            L += [f't[1, {i}] := .MUs.{mu}', f't[2, {i}] := {n}', f't[3, {i}] := {suc}']
        L.append(f'm.{r}.DismantleTable := t')
    L += ['m.EventController.RealTime := false', f'm.EventController.End := {DIAS * 24 * H}', 'm.EventController.startWithoutAnimation']
    ps.ExecuteSimTalk('\n'.join(L))
    time.sleep(1)
    t0 = time.time()
    while ps.IsSimulationRunning() and time.time() - t0 < 900:
        time.sleep(0.5)
    filas = [gv(f'{r}.DismantleTable.YDim') for r in FILAS]
    lotes = sum(gv(f'{r}.StatNumIn') for r in FILAS) / DIAS
    chunks = {c: n for f in FILAS.values() for c, n, _ in f}
    und = {c: gv(f'Despacho_{c}.StatNumIn') * UND_LOTE[c] / chunks[c] / DIAS for c in UND_LOTE}
    uso = lambda o: gv(f'{o}.StatWorkingPortion') + gv(f'{o}.StatSetupPortion') + gv(f'{o}.StatFailPortion')
    ferm = sum(uso(f) for f in ('U211_Fermentador', 'U212_Fermentador', 'U213_Fermentador', 'U218_Fermentador')) / 4
    R = {'archivo': os.path.basename(ruta), 'lotes_dia': lotes, 'litros_dia': lotes * 10000, 'unidades_dia': und,
         'vasos_U311_dia': und['YF150'] + und['YN200'], 'botellas_U312_dia': und['YF1000'] + und['YF1750'] + und['YN1000'],
         'griego_U313_dia': und['YG150'] + und['YG500'],
         'uso': {o: round(uso(o), 4) for o in ('U111_Recepcion', 'U121_Pasteurizador', 'U201_Formulacion', 'U202_Tratamiento',
                                               'U311_Vasos', 'U312_Botellas', 'U313_Griego')}, 'fermentadores': round(ferm, 4)}
    res = [f'Resultados de la simulación ({DIAS} días de producción) · corregido 10-oct-2026',
           f'Leche a yogures: {n1(R["litros_dia"])} L/día ({n1(lotes, 2)} lotes/día)',
           f'Envases por día: {n1(R["vasos_U311_dia"])} vasos · {n1(R["botellas_U312_dia"])} botellas · {n1(R["griego_U313_dia"])} griego',
           f'Uso U311 vasos: {n1(R["uso"]["U311_Vasos"] * 100)} % · U312: {n1(R["uso"]["U312_Botellas"] * 100)} % · U313: {n1(R["uso"]["U313_Griego"] * 100)} %',
           f'Fermentadores: {n1(ferm * 100)} % · cuello de botella: U311 vasos']
    G = ['var m: object := .Models.Model', 'm.drawRectangle(1, 1140, 778, 860, 180, makeRGBValue(255, 255, 255), -1)',
         'm.drawRectangle(2, 1150, 785, 840, 150, makeRGBValue(27, 42, 120), 2)']
    for i, s in enumerate(res):
        c = 'makeRGBValue(27, 42, 120)' if i == 0 else 'makeRGBValue(20, 33, 61)'
        G.append(f'm.drawText(3, 1168, {795 + i * 25}, {c}, {12 if i == 0 else 11}, "{s}")')
    ps.ExecuteSimTalk('\n'.join(G))
    # arranque en caliente y animación a ×30, como lo deja generar_3d.ps1
    ps.ExecuteSimTalk('var m: object := .Models.Model\nm.EventController.reset\nm.EventController.End := 108000\nm.EventController.startWithoutAnimation')
    time.sleep(1)
    while ps.IsSimulationRunning():
        time.sleep(0.5)
    ps.ExecuteSimTalk(f'var m: object := .Models.Model\nm.EventController.End := {DIAS * 24 * H}\nm.EventController.Speed := 100\n'
                      'm.EventController.RealTime := true\nm.EventController.RealTimeScale := 30')
    ps.SaveModel(ruta)
    print(json.dumps({'filas': filas, **{k: R[k] for k in ('archivo', 'litros_dia', 'botellas_U312_dia')}, 'uso': R['uso']}, ensure_ascii=False), flush=True)
    if os.path.basename(ruta) == 'linea_yogures_actual.spp':
        viejo = json.load(open(os.path.join(D, 'resultados_actual.json'), encoding='utf-8'))
        viejo.update({k: R[k] for k in ('lotes_dia', 'litros_dia', 'unidades_dia', 'vasos_U311_dia', 'botellas_U312_dia', 'griego_U313_dia')})
        for o, v in R['uso'].items():
            viejo['uso'][o]['ocupado'] = v
        viejo['corregido'] = '10-oct-2026: tablas de reparto'
        json.dump(viejo, open(os.path.join(D, 'resultados_actual.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ps.Quit()
