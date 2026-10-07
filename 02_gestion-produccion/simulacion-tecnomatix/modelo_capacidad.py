# Modelo de capacidad de la planta láctea Mekvra (valores de diseño, a validar en Tecnomatix).
# Fuentes: ISA88_Planta_Lactea_MEVKRA (capacidades, recetas, velocidades), TIEMPOS ANTES PROPUESTA
# (escenario base) y supuestos de operación declarados en SUP.

H = 24.0
DIAS_SEM = 6          # lunes a sábado; domingo = CIP profundo + mantenimiento preventivo
DIAS_ANO = DIAS_SEM * 52

# --- Escenarios -------------------------------------------------------------------------------
ESC = {
    'base': dict(
        nombre='Escenario base (antes de la propuesta)',
        perf=0.85, rech=0.015, desc=1.5, turno=0.5, cip_llen=1.5, formato=0.75, mtbf=40.0, mttr=1.0,
        y_incub=7.0, y_enfr=1.5, y_cip_f=1.0, y_lib=0.5, y_pulm=1, y_overlap=False, u202_cambios=4,
        q_corte=0.25, q_acid=3.0,
        k_ferm=24.0, k_vaciado=0.75, k_ferms=3, k_madur=24.0, k_tq_madur=3, k_madur_en_tanque=True,
        crudo_h=6.0, silo_h=12.0, pt_h=24.0, esp_u202=0.5,
        n_formato={'U311': 0, 'U312': 2, 'U321': 2, 'U322': 0, 'U331': 3},
    ),
    'prop': dict(
        nombre='Escenario propuesto',
        perf=0.92, rech=0.008, desc=0.0, turno=0.25, cip_llen=1.0, formato=1/3, mtbf=60.0, mttr=0.75,
        y_incub=5.0, y_enfr=1.25, y_cip_f=0.75, y_lib=0.0, y_pulm=2, y_overlap=True, u202_cambios=1,
        q_corte=0.0, q_acid=2.5,
        k_ferm=20.0, k_vaciado=0.5, k_ferms=4, k_madur=12.0, k_tq_madur=2, k_madur_en_tanque=False,
        crudo_h=4.0, silo_h=4.0, pt_h=24.0, esp_u202=0.25,
        n_formato={'U311': 0, 'U312': 1, 'U321': 1, 'U322': 0, 'U331': 2},
    ),
}

# --- Referencias ------------------------------------------------------------------------------
# código, línea, gramos, velocidad nominal (und/h), envasadora, unidades por caja
REFS = [
    ('YF150', 'Y', 150, 12000, 'U311', 24),
    ('YF1000', 'Y', 1000, 4000, 'U312', 12),
    ('YF1750', 'Y', 1750, 2500, 'U312', 6),
    ('QM250', 'Q', 250, 1200, 'U322', 20),
    ('QM400', 'Q', 400, 900, 'U321', 12),
    ('QM1000', 'Q', 1000, 450, 'U321', 8),
    ('KF240', 'K', 240, 6000, 'U331', 24),
    ('KF500', 'K', 500, 4500, 'U331', 12),
    ('KF1000', 'K', 1000, 3000, 'U331', 12),
]
MIX = {'YF150': .45, 'YF1000': .35, 'YF1750': .20,
       'QM250': .20, 'QM400': .40, 'QM1000': .40,
       'KF240': .40, 'KF500': .35, 'KF1000': .25}
LOTES = {'Y': 6, 'Q': 5, 'K': 3}
LOTE_KG = {'Y': 10000, 'Q': 500, 'K': 5000}          # producto terminado por lote
LECHE_L = {'Y': 55000, 'Q': 25000, 'K': 15000}        # leche asignada por día (ISA-88)
DEM_KG = {l: LOTES[l] * LOTE_KG[l] for l in LOTES}

def rate_kg(code):
    r = next(x for x in REFS if x[0] == code)
    return r[2] / 1000 * r[3]

def kg_dia(code):
    lin = next(x for x in REFS if x[0] == code)[1]
    return DEM_KG[lin] * MIX[code]

def r1(x, n=1):
    return round(x + 1e-9, n)

# --- Envasadoras ------------------------------------------------------------------------------
def llenadora(F, e):
    s = ESC[e]
    refs = [r for r in REFS if r[4] == F]
    run = sum(kg_dia(r[0]) / (rate_kg(r[0]) * s['perf']) for r in refs)
    rech = run * s['rech'] / (1 - s['rech'])
    fallas = (run + rech) / s['mtbf'] * s['mttr']
    formato = s['n_formato'][F] * s['formato']
    fijo = s['cip_llen'] + s['desc'] + s['turno']
    total = run + rech + fallas + formato + fijo
    return dict(run=run, rech=rech, fallas=fallas, formato=formato, cip=s['cip_llen'],
                desc=s['desc'], turno=s['turno'], total=total, util=total / H)

# --- Utilización por recurso ------------------------------------------------------------------
def recursos(e):
    s = ESC[e]
    R = []
    def add(linea, unidad, nombre, horas, unidades=1, nota=''):
        R.append(dict(linea=linea, unidad=unidad, nombre=nombre, horas=horas, unidades=unidades,
                      util=horas / (H * unidades), nota=nota))
    leche = sum(LECHE_L.values())
    add('Tronco', 'U111/U112', 'Bahías de recepción', leche / 10000 * 0.45 + 1.0, 2)
    add('Tronco', 'U121', 'Clarificadora-estandarizadora', leche / 20000 + 1.5)
    add('Tronco', 'U122', 'Pasteurizador HTST', leche / 20000 + 1.5 + 0.5)
    # yogur
    add('Yogur', 'U201', 'Tanque de formulación', LOTES['Y'] * (1.1 + 1.0 + 0.5))
    u202 = LOTES['Y'] * 1.25 + LOTES['K'] * 0.75 + s['u202_cambios'] * 0.75 + 1.5
    add('Compartido', 'U202', 'Homogenizador + pasteurizador de base', u202)
    ferm_y = 1.0 + 0.25 + s['y_incub'] + s['y_enfr'] + s['y_cip_f']
    add('Yogur', 'U211–U213', 'Fermentadores de yogur', LOTES['Y'] * ferm_y, 3)
    f311 = llenadora('U311', e)
    eff311 = rate_kg('YF150') * s['perf']
    drain = (LOTE_KG['Y'] * MIX['YF150']) / eff311
    pulm = (0.25 if s['y_overlap'] else 1.0) + s['y_lib'] + drain + (0.5 if s['y_overlap'] else 0.75)
    add('Yogur', 'U214' if s['y_pulm'] == 1 else 'U214/U215', 'Tanque pulmón y saborización', LOTES['Y'] * pulm, s['y_pulm'])
    add('Yogur', 'U311', 'Llenadora de vasos (YF150)', f311['total'])
    add('Yogur', 'U312', 'Llenadora de botellas (YF1000/1750)', llenadora('U312', e)['total'])
    # mozzarella
    tina = 3 * (2.85 + s['q_corte'] + 0.5) + 2 * (3.05 + s['q_corte'] + 0.5)
    add('Mozzarella', 'U221', 'Tina quesera cerrada', tina)
    add('Mozzarella', 'U222', 'Banda de acidificación', LOTES['Q'] * (s['q_acid'] + 0.25))
    add('Mozzarella', 'U223', 'Hiladora-moldeadora', LOTES['Q'] * (LOTE_KG['Q'] / 600 + 0.25))
    add('Mozzarella', 'U224', 'Enfriamiento y salmuera', 3 * 1.5 + 2 * 4.0, 4)
    add('Mozzarella', 'U321', 'Termoformadora al vacío', llenadora('U321', e)['total'])
    add('Mozzarella', 'U322', 'Llenadora de tarrinas', llenadora('U322', e)['total'])
    # kéfir
    ferm_k = 0.5 + 0.33 + 0.25 + s['k_ferm'] + 0.5 + s['k_vaciado'] + (1.0 if e == 'base' else 0.75)
    add('Kéfir', 'U231–U233' if s['k_ferms'] == 3 else 'U231–U233 + U235', 'Fermentadores de kéfir', LOTES['K'] * ferm_k, s['k_ferms'])
    u331 = llenadora('U331', e)
    eff_k = sum(kg_dia(c) for c in ('KF240', 'KF500', 'KF1000')) / sum(kg_dia(c) / (rate_kg(c) * s['perf']) for c in ('KF240', 'KF500', 'KF1000'))
    drain_k = LOTE_KG['K'] / eff_k
    if s['k_madur_en_tanque']:
        add('Kéfir', 'U234A–C', 'Tanques de maduración (3 × 5.000 L)', LOTES['K'] * (0.5 + s['k_madur'] + drain_k + 0.75), s['k_tq_madur'])
    else:
        add('Kéfir', 'U234A–B', 'Tanques pulmón de llenado (2 × 5.000 L)', LOTES['K'] * (0.5 + drain_k + 0.5), s['k_tq_madur'])
    add('Kéfir', 'U331', 'Llenadora de botellas de kéfir', u331['total'])
    # fin de línea
    cajas = sum(kg_dia(r[0]) * 1000 / r[2] / r[5] for r in REFS)
    add('Fin de línea', 'U341', 'Celda robotizada de paletizado', cajas / 750 + 3 * (0.25 if e == 'base' else 0.1))
    return R, dict(drain_y=drain, pulm=pulm, ferm_y=ferm_y, ferm_k=ferm_k, drain_k=drain_k, cajas=cajas, u202=u202)

def capacidad(e):
    R, _ = recursos(e)
    out = {}
    for lin, key in (('Y', 'Yogur'), ('Q', 'Mozzarella'), ('K', 'Kéfir')):
        rs = [r for r in R if r['linea'] in (key, 'Compartido', 'Tronco', 'Fin de línea')]
        m = max(rs, key=lambda r: r['util'])
        lotes = LOTES[lin] / max(1.0, m['util'])
        out[lin] = dict(cuello=m['unidad'], util=m['util'], lotes=lotes, kg=lotes * LOTE_KG[lin])
    return out

# --- Duración de lote por referencia ---------------------------------------------------------
def lote_ref(e):
    s = ESC[e]
    rows = []
    for code, lin, g, rate, F, caja in REFS:
        und = LOTE_KG[lin] * 1000 / g
        env = LOTE_KG[lin] / (rate_kg(code) * s['perf'])
        if lin == 'Y':
            proc = 1.1 + 1.25 + 0.25 + s['y_incub'] + s['y_enfr'] + s['y_lib']
            post = 12.0
        elif lin == 'Q':
            sal = {'QM250': 0.6, 'QM400': 1.25, 'QM1000': 3.5}[code]
            cocc = 3.05 if code == 'QM1000' else 2.85
            proc = cocc + s['q_corte'] + s['q_acid'] + LOTE_KG['Q'] / 600 + 0.5 + sal
            post = 0.0
        else:
            proc = 0.75 + 0.33 + 0.25 + s['k_ferm'] + 0.5 + s['k_vaciado'] + (s['k_madur'] if s['k_madur_en_tanque'] else 0)
            post = 0.0 if s['k_madur_en_tanque'] else s['k_madur']
        rows.append(dict(code=code, lin=lin, und=und, proc=proc, env=env, post=post, total=proc + env + post, filler=F))
    return rows

# --- Pérdidas de tiempo (semana) en la llenadora cuello de botella U311 -----------------------
def cascada(e):
    s = ESC[e]
    cal = 7 * H
    noprog = H
    prog = cal - noprog
    cip = s['cip_llen'] * DIAS_SEM
    desc = s['desc'] * DIAS_SEM
    turno = s['turno'] * DIAS_SEM
    disp = prog - cip - desc - turno
    fallas = disp * (1 - s['mtbf'] / (s['mtbf'] + s['mttr']))
    oper = disp - fallas
    vel = oper * (1 - s['perf'])
    neto = oper - vel
    cal_loss = neto * s['rech']
    valor = neto - cal_loss
    A = oper / disp
    oee = A * s['perf'] * (1 - s['rech'])
    return dict(cal=cal, noprog=noprog, prog=prog, cip=cip, desc=desc, turno=turno, disp=disp, fallas=fallas,
                oper=oper, vel=vel, neto=neto, calidad=cal_loss, valor=valor, A=A, P=s['perf'], Q=1 - s['rech'], oee=oee,
                teep=valor / cal)

# --- VSM ----------------------------------------------------------------------------------------
def vsm(lin, e):
    s = ESC[e]
    R, aux = recursos(e)
    if lin == 'Y':
        inv = [('Tanque de crudo', s['crudo_h']), ('Silo S1', s['silo_h']), ('Cola U202', s['esp_u202']),
               ('Liberación + pulmón', s['y_lib'] + aux['drain_y'] / 2), ('Cámara 4 °C + PT', 12.0 + s['pt_h'])]
        proc = [('Recepción y HTST', 'U111–U125', 0.45, 0.45, '—', 2),
                ('Formulación', 'U201', 1.1, 1.1, '0,5 h CIP', 2),
                ('Homog. + past. 85 °C', 'U202', 1.25, 1.0, '0,75 h', 1),
                ('Incubación', 'U211–U213', 0.25 + s['y_incub'], 0.25 + 5.0, f"{r1(s['y_cip_f'],2)} h CIP".replace('.', ','), 1),
                ('Romper y enfriar', 'U211–U213', s['y_enfr'], 0.5, '—', 1),
                ('Saborizar y envasar', 'U311 · U312', aux['drain_y'], aux['drain_y'], f"{round(s['formato']*60)} min", 3)]
    elif lin == 'Q':
        inv = [('Tanque de crudo', s['crudo_h']), ('Silo S2', s['silo_h']), ('Cuajada en banda', 0.25),
               ('Salmuera', 0.25), ('PT 2–4 °C', s['pt_h'])]
        proc = [('Recepción y HTST', 'U111–U124', 0.25, 0.25, '—', 2),
                ('Coagular y cocer', 'U221', 2.85 + s['q_corte'], 2.85, '0,5 h CIP', 1),
                ('Acidificar cuajada', 'U222', s['q_acid'], 2.5, '—', 1),
                ('Hilar y moldear', 'U223', LOTE_KG['Q'] / 600, LOTE_KG['Q'] / 600, '—', 2),
                ('Enfriar y salar', 'U224', 2.5, 2.5, '—', 1),
                ('Empacar', 'U321/U322', LOTE_KG['Q'] / (rate_kg('QM400') * s['perf']), LOTE_KG['Q'] / (rate_kg('QM400') * s['perf']), f"{round(s['formato']*60)} min", 2)]
    else:
        inv = [('Tanque de crudo', s['crudo_h']), ('Silo S3', s['silo_h']), ('Cola U202', s['esp_u202']),
               ('Pulmón de llenado', aux['drain_k'] / 2), ('PT 2–4 °C', s['pt_h'])]
        proc = [('Recepción y HTST', 'U111–U125', 0.25, 0.25, '—', 2),
                ('Homog. + past. 90–95 °C', 'U202', 0.75, 0.5, '0,75 h', 1),
                ('Inocular y fermentar', 'U231–U233' if e == 'base' else 'U231–3 · U235', 0.58 + s['k_ferm'], 0.58 + 20.0, '1 h CIP', 1),
                ('Enfriar' + (' y tamizar' if e == 'base' else ''), 'fermentador', 0.5 + s['k_vaciado'], 0.5, '—', 1),
                (('Madurar en tanque' if s['k_madur_en_tanque'] else 'Madurar en envase'), 'U234A–C' if s['k_madur_en_tanque'] else 'cámara', s['k_madur'], 12.0, '—', 0),
                ('Envasar', 'U331', aux['drain_k'], aux['drain_k'], f"{round(s['formato']*60)} min", 2)]
        if not s['k_madur_en_tanque']:
            proc = proc[:4] + [proc[5], proc[4]]
    lt = sum(i[1] for i in inv) + sum(p[2] for p in proc)
    va = sum(p[3] for p in proc)
    return dict(inv=inv, proc=proc, lt=lt, va=va, pce=va / lt)

def todo():
    out = {}
    for e in ESC:
        R, aux = recursos(e)
        out[e] = dict(recursos=R, aux=aux, capacidad=capacidad(e), lote_ref=lote_ref(e), cascada=cascada(e),
                      llen={F: llenadora(F, e) for F in ('U311', 'U312', 'U321', 'U322', 'U331')},
                      vsm={l: vsm(l, e) for l in 'YQK'})
    return out

if __name__ == '__main__':
    D = todo()
    for e in ESC:
        print('==', e)
        for r in D[e]['recursos']:
            print(f"  {r['unidad']:<11} {r['nombre']:<42} {r['horas']:6.1f} h /{r['unidades']}  {r['util']*100:5.0f}%")
        print('  capacidad', {k: (v['cuello'], round(v['util']*100), r1(v['lotes'], 2), round(v['kg'])) for k, v in D[e]['capacidad'].items()})
        c = D[e]['cascada']
        print('  cascada', {k: round(v, 3) for k, v in c.items()})
        for l in 'YQK':
            v = D[e]['vsm'][l]
            print('  vsm', l, round(v['lt'], 1), round(v['va'], 1), round(v['pce'] * 100, 1))
        for r in D[e]['lote_ref']:
            print('  lote', r['code'], round(r['und']), r1(r['proc']), r1(r['env']), r1(r['post']), r1(r['total']))
        print('  cajas', round(D[e]['aux']['cajas']))
    for k in MIX:
        print(k, kg_dia(k), rate_kg(k))
