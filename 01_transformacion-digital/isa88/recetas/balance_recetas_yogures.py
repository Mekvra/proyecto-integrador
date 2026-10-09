# Balance de masas y tiempos de las recetas maestras de la línea de yogures Mekvra (versión 1.3, auditada en 3 ciclos).
# Una sola fuente de cifras: el documento de recetas, la página y el modelo de Tecnomatix leen recetas_yogures.json.
# Uso: python balance_recetas_yogures.py   (escribe recetas_yogures.json junto a este archivo)
import json, os, sys

D = os.path.dirname(os.path.abspath(__file__))

# ---------------- Supuestos de materias primas (valores de diseño, se reemplazan por mediciones) ----------------
DENS = dict(entera=1.032, descremada=1.035)                # kg/L a 15 °C (Decreto 616: cruda entera 1,030–1,033)
CRUDA = dict(grasa=0.036, prot=0.031, sng=0.086)           # leche de la Sabana (Holstein), promedio de diseño
if os.environ.get('MEKVRA_CRUDA'):                         # sensibilidad: "grasa,prot,sng" en fracción (sensibilidad_leche.py)
    CRUDA = dict(zip(('grasa', 'prot', 'sng'), map(float, os.environ['MEKVRA_CRUDA'].split(','))))
GRASA_CREMA = 0.40                                         # crema del separador U121
_suero_leche = {k: CRUDA[k] / (1 - CRUDA['grasa']) for k in ('prot', 'sng')}     # fase no grasa de la cruda
CREMA = dict(grasa=GRASA_CREMA, prot=_suero_leche['prot'] * (1 - GRASA_CREMA), sng=_suero_leche['sng'] * (1 - GRASA_CREMA))
LPD = dict(grasa=0.010, prot=0.34, sng=0.950)              # leche en polvo descremada (≥ 34 % proteína)
GRASA_DESCREMADA = 0.0005
SUERO = dict(prot=0.005, grasa=0.0003)                     # suero ácido: proteína medida 0,41–0,68 % (Foods 2022, 11, 3953)
PROT_CONC, GRASA_YG = 0.096, 0.020                         # concentrado griego y grasa final del producto
PREP = dict(frac=0.13, fruta=0.50, sacarosa=0.35, grasa=0.0, prot=0.0)  # preparado de fresa (grasa y proteína despreciables)
LOTE_L, LOTE_MAX_L = 10000, 10500                          # lote nominal y máximo (holgura de los tanques de 12.000 L)
CAUDAL_KG_H = 10500                                        # U202 y transferencias: 10 m³/h de base, tomados como 10.500 kg/h (≈ 1,05 kg/L)
RITMO_H = 24 / 8                                           # un lote cada 3 h, en operación continua
SEPARADOR_L_H = 7000                                       # U216, alimentación
SECUENCIA = ['YN', 'YN', 'YN', 'YG', 'YG', 'YF', 'YF', 'YF']  # sin dulce antes que con dulce
LOTES_DIA = {p: SECUENCIA.count(p) for p in ('YN', 'YG', 'YF')}


def estandarizar(grasa_obj, tipo):
    """Leche cruda necesaria y crema retirada para un lote de leche estandarizada (balance de grasa en U121).
    Si la cruda trae menos grasa que la consigna, c sale negativa: es crema propia que U121 remezcla (la aporta el
    descremado del griego); el balance diario verifica que la crema propia alcance."""
    s = LOTE_L * DENS[tipo]
    c = s * (CRUDA['grasa'] - grasa_obj) / (CREMA['grasa'] - CRUDA['grasa'])
    r = s + c
    return dict(cruda_kg=r, cruda_L=r / DENS['entera'], crema_kg=c, leche_kg=s, leche_L=LOTE_L, grasa=grasa_obj,
                prot=(CRUDA['prot'] * r - CREMA['prot'] * c) / s, sng=(CRUDA['sng'] * r - CREMA['sng'] * c) / s)


def base_fortificada(leche, sng_obj, azucar_frac):
    """LPD y azúcar para llevar la base a sng_obj con azucar_frac de sacarosa sobre la base."""
    m, sng = leche['leche_kg'], leche['sng']
    k = 1 - azucar_frac
    p = (sng_obj * m / k - sng * m) / (LPD['sng'] - sng_obj / k)
    if p < 0:
        raise ValueError('La leche ya supera el SNG objetivo: no se necesita LPD')
    b = (m + p) / k
    return dict(lpd_kg=p, azucar_kg=azucar_frac * b, base_kg=b, sng=sng_obj,
                grasa=(leche['grasa'] * m + LPD['grasa'] * p) / b, prot=(leche['prot'] * m + LPD['prot'] * p) / b)


# ---------------- YF · Yogur con trozos de fresa (entero, con dulce) ----------------
lyf = estandarizar(0.035, 'entera')
byf = base_fortificada(lyf, 0.115, 0.055)
yf_kg = byf['base_kg'] / (1 - PREP['frac'])
prep_kg = yf_kg - byf['base_kg']
YF = dict(codigo='YF', nombre='Yogur con trozos de fresa', leche=lyf, base=byf, preparado_kg=prep_kg, producto_kg=yf_kg,
          grasa=byf['grasa'] * byf['base_kg'] / yf_kg, prot=byf['prot'] * byf['base_kg'] / yf_kg,
          sng=byf['sng'] * byf['base_kg'] / yf_kg, fruta_neta=PREP['fruta'] * prep_kg / yf_kg,
          azucar_añadida=(byf['azucar_kg'] + PREP['sacarosa'] * prep_kg) / yf_kg,
          dilucion_base=byf['base_kg'] / yf_kg, ph_corte=4.50)

# ---------------- YN · Yogur natural (entero, sin dulce) ----------------
lyn = estandarizar(0.035, 'entera')
byn = base_fortificada(lyn, 0.115, 0.0)
YN = dict(codigo='YN', nombre='Yogur natural', leche=lyn, base=byn, producto_kg=byn['base_kg'],
          grasa=byn['grasa'], prot=byn['prot'], sng=byn['sng'], azucar_añadida=0.0, ph_corte=4.50)

# ---------------- YG · Yogur griego (leche fermentada concentrada) ----------------
lyg = estandarizar(GRASA_DESCREMADA, 'descremada')
f = lyg['leche_kg']
conc = (lyg['prot'] - SUERO['prot']) * f / (PROT_CONC - SUERO['prot'])      # balance de proteína en U216
suero = f - conc
grasa_conc = (lyg['grasa'] * f - SUERO['grasa'] * suero) / conc
crema_yg = conc * (GRASA_YG - grasa_conc) / (CREMA['grasa'] - GRASA_YG)      # crema pasteurizada en U126
yg_kg = conc + crema_yg
YG = dict(codigo='YG', nombre='Yogur griego', leche=lyg, concentrado_kg=conc, grasa_concentrado=grasa_conc,
          suero_acido_kg=suero, crema_kg=crema_yg, crema_sobre_concentrado=crema_yg / conc, producto_kg=yg_kg,
          grasa=GRASA_YG, prot=(PROT_CONC * conc + CREMA['prot'] * crema_yg) / yg_kg,
          leche_kg_por_kg=f / yg_kg, suero_kg_por_kg=suero / yg_kg, rendimiento_kg_L=yg_kg / LOTE_L,
          azucar_añadida=0.0, ph_corte=4.55)

PROD = {'YF': YF, 'YN': YN, 'YG': YG}

# ---------------- Presentaciones y llenadoras (velocidad nominal de diseño) ----------------
# código, producto, g, envase, llenadora, und/h nominales, und/caja, fracción del lote
REFS = [
    ('YF150', 'YF', 150, 'Vaso PP termoformado, tapa foil termosellada', 'U311', 15000, 24, 0.45),
    ('YF1000', 'YF', 1000, 'Botella PEAD, tapa rosca y sello de inducción', 'U312', 4000, 12, 0.35),
    ('YF1750', 'YF', 1750, 'Botella PEAD con asa, tapa rosca y sello de inducción', 'U312', 2500, 6, 0.20),
    ('YN200', 'YN', 200, 'Vaso PP termoformado, tapa foil termosellada', 'U311', 12000, 24, 0.40),
    ('YN1000', 'YN', 1000, 'Botella PEAD, tapa rosca y sello de inducción', 'U312', 4000, 12, 0.60),
    ('YG150', 'YG', 150, 'Vaso PP con foil y sobretapa', 'U313', 6000, 24, 0.60),
    ('YG500', 'YG', 500, 'Pote PP con foil y sobretapa', 'U313', 2400, 12, 0.40),
]
refs = []
for code, p, g, env, fill, uh, caja, frac in REFS:
    kg = PROD[p]['producto_kg'] * frac
    und = kg * 1000 / g
    refs.append(dict(codigo=code, producto=p, gramos=g, envase=env, llenadora=fill, und_h=uh, und_caja=caja, fraccion=frac,
                     kg_lote=kg, und_lote=und, cajas_lote=und / caja, h_nominal_lote=und / uh,
                     kg_dia=kg * LOTES_DIA[p], und_dia=und * LOTES_DIA[p]))

# ---------------- Tiempos de ciclo por unidad (h) ----------------
def base_kg(p):
    return PROD[p]['base']['base_kg'] if 'base' in PROD[p] else PROD[p]['leche']['leche_kg']


INCUBAR = {'YF': 5.25, 'YN': 5.0, 'YG': 5.5}
T = {}
for p in PROD:
    b = base_kg(p)
    t201 = dict(cargar=PROD[p]['leche']['leche_L'] / 20000, dispersar_hidratar=0.33, transferir=b / CAUDAL_KG_H)
    t202 = dict(procesar=b / CAUDAL_KG_H, empuje=0.15)
    if p == 'YG':
        salida = dict(agitar=0.20, separar=(b / 1.04) / SEPARADOR_L_H)        # yogur fermentado ≈ 1,04 kg/L
    else:
        salida = dict(romper=0.15, vaciar_enfriar=b / CAUDAL_KG_H)
    ferm = dict(llenar=b / CAUDAL_KG_H, inocular_agitar=0.17, incubar=INCUBAR[p], **salida, cip=0.75)
    T[p] = dict(U201=t201, U201_total=sum(t201.values()), U202=t202, U202_total=sum(t202.values()),
                fermentador=ferm, fermentador_total=sum(ferm.values()))
T['U216_arranque'] = 0.25

h_ferm = sum(T[p]['fermentador_total'] * n for p, n in LOTES_DIA.items())
h_201 = sum(T[p]['U201_total'] * n for p, n in LOTES_DIA.items())
h_202 = sum(T[p]['U202_total'] * n for p, n in LOTES_DIA.items())
horas_llen = {fl: sum(r['h_nominal_lote'] * LOTES_DIA[r['producto']] for r in refs if r['llenadora'] == fl)
              for fl in ('U311', 'U312', 'U313')}
# U311 con la velocidad anterior (12.000 vasos/h de 150 g; 10.000/h de 200 g) y factores base de la propuesta de Pablo
u311_12k = sum(r['und_dia'] / {'YF150': 12000, 'YN200': 10000}[r['codigo']] for r in refs if r['llenadora'] == 'U311')
APQ_BASE = 0.85 * (40 / 41) * 0.985
FIJO_BASE = 1.5 + 1.5 + 0.5                                  # CIP + pausa + relevo (h/día), tabla 6 de Pablo

ing = dict(lpd_kg=sum(PROD[p]['base']['lpd_kg'] * LOTES_DIA[p] for p in ('YF', 'YN')),
           azucar_kg=YF['base']['azucar_kg'] * LOTES_DIA['YF'], preparado_kg=YF['preparado_kg'] * LOTES_DIA['YF'],
           cultivo_U=400 * sum(LOTES_DIA.values()))
cruda_kg = sum(PROD[p]['leche']['cruda_kg'] * n for p, n in LOTES_DIA.items())
crema_total = sum(PROD[p]['leche']['crema_kg'] * n for p, n in LOTES_DIA.items())
salidas = dict(**{p: PROD[p]['producto_kg'] * n for p, n in LOTES_DIA.items()},
               suero_acido=YG['suero_acido_kg'] * LOTES_DIA['YG'],
               crema_excedente=crema_total - YG['crema_kg'] * LOTES_DIA['YG'])

if salidas['crema_excedente'] < 0:
    raise ValueError(f'La crema propia no alcanza: faltan {-salidas["crema_excedente"]:.0f} kg/día')

# ---------------- Energía para calentar la carga de U201 a 50 °C (EM-2014) ----------------
CP_LECHE = 3.93                                            # kJ/(kg·K)
ENERGIA = {}
for p in PROD:
    q_kj = PROD[p]['leche']['leche_kg'] * CP_LECHE * (50 - 4)
    ENERGIA[p] = dict(kWh_lote=q_kj / 3600, kW_en_carga=q_kj / 3600 / T[p]['U201']['cargar'])
ENERGIA['kWh_dia'] = sum(ENERGIA[p]['kWh_lote'] * n for p, n in LOTES_DIA.items())

# ---------------- Vida útil de diseño y acidez (sección 5.3, 6.3 y 7.3 del documento) ----------------
VIDA_UTIL = dict(YF=dict(dias=30, acidez_dia1=0.86, aumento_max=0.30), YN=dict(dias=30, acidez_dia1=0.95, aumento_max=0.30),
                 YG=dict(dias=21, acidez_dia1=1.15, aumento_max=0.30, liberacion_max=1.20))
for p, v in VIDA_UTIL.items():
    v['acidez_al_vencimiento'] = v['acidez_dia1'] + v['aumento_max']
    if v['acidez_al_vencimiento'] > 1.50:
        raise ValueError(f'{p}: acidez al vencimiento {v["acidez_al_vencimiento"]:.2f} % supera 1,50 %')

# ---------------- Verificación de cierre por componente (grasa y proteína) ----------------
def componente(k):
    ent = sum(PROD[p]['leche']['cruda_kg'] * n for p, n in LOTES_DIA.items()) * CRUDA[k] + ing['lpd_kg'] * LPD[k] + ing['preparado_kg'] * PREP[k]
    sal = sum(PROD[p]['producto_kg'] * PROD[p][k] * n for p, n in LOTES_DIA.items()) + salidas['suero_acido'] * SUERO[k] \
        + salidas['crema_excedente'] * CREMA[k]
    return ent, sal


CIERRE = {}
for k in ('grasa', 'prot'):
    e_, s_ = componente(k)
    CIERRE[k] = dict(entra_kg=e_, sale_kg=s_)
    # el suero sale con 0,0003 de grasa fijado, así que la grasa del concentrado absorbe la diferencia: se exige < 0,5 kg/día
    if abs(e_ - s_) > 0.5:
        raise AssertionError(f'El balance de {k} no cierra: {e_:.2f} vs {s_:.2f} kg/día')
if abs(cruda_kg + ing['lpd_kg'] + ing['azucar_kg'] + ing['preparado_kg'] - sum(salidas.values())) > 1e-6:
    raise AssertionError('El balance de masa total no cierra')

# ---------------- Programa de un lote cada RITMO_H h: fermentadores ocupados a la vez ----------------
eventos = []
for d in range(3):                                           # tres días seguidos, para ver el régimen
    for i, p in enumerate(SECUENCIA):
        t0 = (d * len(SECUENCIA) + i) * RITMO_H
        ini = t0 + T[p]['U201']['cargar'] + T[p]['U201']['dispersar_hidratar']   # el llenado coincide con la transferencia
        eventos += [(ini, 1), (ini + T[p]['fermentador_total'], -1)]
ocup = mx = 0
for _, s_ in sorted(eventos, key=lambda e: (e[0], e[1])):
    ocup += s_
    mx = max(mx, ocup)
PROGRAMA = dict(ritmo_h=RITMO_H, max_fermentadores_simultaneos=mx,
                hueco_U202_h=RITMO_H - max(T[p]['U202_total'] for p in PROD), CIP_C_U202_h=85 / 60)

OUT = dict(
    version='1.3',
    supuestos=dict(densidad=DENS, leche_cruda=CRUDA, crema=CREMA, lpd=LPD, grasa_descremada=GRASA_DESCREMADA,
                   suero_acido=SUERO, proteina_concentrado=PROT_CONC, grasa_griego=GRASA_YG, preparado_fresa=PREP,
                   lote_L=LOTE_L, lote_max_L=LOTE_MAX_L, caudal_base_kg_h=CAUDAL_KG_H, separador_L_h=SEPARADOR_L_H,
                   secuencia=SECUENCIA, lotes_dia=LOTES_DIA),
    productos=PROD, referencias=refs, tiempos=T,
    dia=dict(leche_linea_L=LOTE_L * len(SECUENCIA), leche_cruda_kg=cruda_kg, leche_cruda_L=cruda_kg / DENS['entera'],
             ingredientes=ing, salidas_kg=salidas, entradas_total_kg=cruda_kg + ing['lpd_kg'] + ing['azucar_kg'] + ing['preparado_kg'],
             salidas_total_kg=sum(salidas.values()), cierre_componentes=CIERRE, programa=PROGRAMA, energia_U201=ENERGIA,
             vida_util=VIDA_UTIL, horas_llenadora=horas_llen,
             horas_fermentadores=h_ferm, carga_4_fermentadores=h_ferm / 96, carga_3_fermentadores=h_ferm / 72,
             horas_U201=h_201, horas_U202=h_202,
             U311_12000=dict(h_nominal=u311_12k, h_con_APQ_y_paradas=u311_12k / APQ_BASE + FIJO_BASE),
             U311_15000=dict(h_nominal=horas_llen['U311'], h_con_APQ_y_paradas=horas_llen['U311'] / APQ_BASE + FIJO_BASE)),
)


def r(x):
    if isinstance(x, float):
        return round(x, 6)
    if isinstance(x, dict):
        return {k: r(v) for k, v in x.items()}
    if isinstance(x, list):
        return [r(v) for v in x]
    return x


if __name__ == '__main__':
    with open(os.path.join(D, 'recetas_yogures.json'), 'w', encoding='utf-8') as fh:
        json.dump(r(OUT), fh, ensure_ascii=False, indent=1)
    out = sys.stdout
    for p in ('YF', 'YN', 'YG'):
        x = PROD[p]
        l = x['leche']
        print(f"== {p}: producto {x['producto_kg']:.1f} kg/lote | grasa {x['grasa']*100:.2f} % | prot {x['prot']*100:.2f} % | "
              f"azucar anadida {x['azucar_añadida']*100:.2f} % | cruda {l['cruda_L']:.0f} L -> leche {l['leche_kg']:.0f} kg "
              f"(prot {l['prot']*100:.2f}, sng {l['sng']*100:.2f}) + crema {l['crema_kg']:.1f} kg", file=out)
        if 'base' in x:
            b = x['base']
            print(f"   LPD {b['lpd_kg']:.1f} | azucar {b['azucar_kg']:.1f} | base {b['base_kg']:.1f}", file=out)
        print('   tiempos', {k: round(v, 3) for k, v in T[p]['fermentador'].items()}, 'ferm', round(T[p]['fermentador_total'], 2),
              'U201', round(T[p]['U201_total'], 2), 'U202', round(T[p]['U202_total'], 2), file=out)
    print(f"YF preparado {prep_kg:.1f} fruta {YF['fruta_neta']*100:.2f} % dil {YF['dilucion_base']:.4f}", file=out)
    print(f"YG conc {conc:.1f} suero {suero:.1f} crema {crema_yg:.1f} ({YG['crema_sobre_concentrado']*100:.2f} % del conc) "
          f"leche/kg {YG['leche_kg_por_kg']:.3f} suero/kg {YG['suero_kg_por_kg']:.3f} rend {YG['rendimiento_kg_L']:.4f} kg/L", file=out)
    for x in refs:
        print(f"   {x['codigo']:7} {x['llenadora']} {x['kg_lote']:8.1f} kg {x['und_lote']:8.0f} und {x['und_dia']:8.0f} und/d "
              f"{x['cajas_lote']:6.0f} cajas {x['h_nominal_lote']:.3f} h", file=out)
    print('dia', json.dumps(r(OUT['dia']), ensure_ascii=False), file=out)
