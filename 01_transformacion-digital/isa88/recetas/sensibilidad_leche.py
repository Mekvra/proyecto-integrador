# Sensibilidad de las recetas a la composición de la leche cruda (riesgo 1 de la sección 13).
# Recalcula el balance con leches andinas reportadas y con el mínimo legal, sin tocar recetas_yogures.json.
# Uso: python sensibilidad_leche.py
import importlib, os, sys

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
ESCENARIOS = [  # nombre, grasa, proteína, SNG (fracción); fuente
    ('Diseño (supuesto)', 0.036, 0.031, 0.086, 'recetas v1.3'),
    ('Manizales (42 muestras)', 0.0339, 0.0344, 0.1286 - 0.0339, 'estudio de 42 muestras, Manizales'),
    ('García Rovira (440 muestras)', 0.0369, 0.0331, 0.1231 - 0.0369, 'estudio de 440 muestras, Santander'),
    ('Mínimo legal (Dec. 616 + 1880)', 0.030, 0.029, 0.083, 'Decreto 616/2006'),
]
filas = []
for nombre, g, pr, sng, fuente in ESCENARIOS:
    os.environ['MEKVRA_CRUDA'] = f'{g},{pr},{sng}'
    if 'balance_recetas_yogures' in sys.modules:
        m = importlib.reload(sys.modules['balance_recetas_yogures'])
    else:
        m = importlib.import_module('balance_recetas_yogures')
    P, dia = m.PROD, m.OUT['dia']
    filas.append((nombre, g, pr, sng, P['YF']['grasa'], P['YN']['grasa'], P['YF']['prot'], P['YF']['base']['lpd_kg'],
                  P['YN']['base']['lpd_kg'], P['YG']['producto_kg'], P['YG']['prot'], dia['salidas_kg']['crema_excedente'],
                  dia['leche_cruda_L']))
os.environ.pop('MEKVRA_CRUDA')
print('| Leche cruda | Grasa / prot / SNG | Grasa YF · YN | Proteína YF | LPD YF · YN (kg/lote) | Griego (kg/lote) | Crema propia sobrante (kg/día) | Cruda (L/día) |')
print('|---|---|---|---|---|---|---|---|')
for f in filas:
    n, g, pr, sng, gyf, gyn, pyf, lyf, lyn, yg, pyg, cr, cl = f
    c = lambda x, d=2: f'{x:.{d}f}'.replace('.', ',')
    print(f'| {n} | {c(g*100)} / {c(pr*100)} / {c(sng*100)} % | {c(gyf*100)} · {c(gyn*100)} % | {c(pyf*100)} % | '
          f'{lyf:.0f} · {lyn:.0f} | {yg:,.0f} ({c(pyg*100)} % prot) | {cr:,.0f} | {cl:,.0f} |'.replace(',', 'X').replace('.', ',').replace('X', '.'))

