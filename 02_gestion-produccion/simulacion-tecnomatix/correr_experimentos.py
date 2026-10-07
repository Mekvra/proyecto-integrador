# Corre los experimentos de capacidad (20 días, pedidos sin límite) y los guarda en resultados/experimentos_capacidad.jsonl.
# Uso: python correr_experimentos.py
import subprocess, sys, os, json

D = os.path.dirname(os.path.abspath(__file__))
F = 2.72 / 0.948 / 0.45   # horas de envasado del lote por fracción de YF150 en la mezcla
EXP = [
    ('base', {}, None),
    ('prop', {}, None),
    ('prop', {'y_incub': 4.5}, None),
    ('prop', {'y_incub': 6}, None),
    ('prop', {'y_incub': 7}, None),
    ('prop', {'y_incub': 8}, None),
    ('prop', {'pulm': 1, 'pulm_cip': 0.5}, None),
    ('prop', {'k_ferms': 3}, None),
    ('prop', {'drain_y': round(F * 0.55, 4)}, None),
    ('prop', {'drain_y': round(F * 0.65, 4)}, None),
    ('prop', {}, {'env': [40.0, 1.0], 'proc': [80.0, 1.5]}),     # propuesta sin TPM (fallas del escenario base)
    ('prop', {}, {'env': [30.0, 0.75], 'proc': [60.0, 1.0]}),    # MTBF a la mitad
]
with open(os.path.join(D, 'resultados', 'experimentos_capacidad.jsonl'), 'w', encoding='utf-8') as f:
    for esc, aj, mtbf in EXP:
        args = [sys.executable, os.path.join(D, 'construir_modelo.py'), esc, '-', '20', 'capacidad', json.dumps(aj)]
        if mtbf:
            args.append(json.dumps(mtbf))
        r = json.loads(subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
        r['fallas'] = mtbf or 'del escenario'
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(esc, aj, mtbf, r['Camara_Yogur'], r['Camara_Kefir'], r['Camara_Queso'], flush=True)
