# Genera el paquete ISA-88 de los nueve productos a partir de los datos del modelo físico, el modelo procedimental y
# las recetas de este repositorio (fuente: «Recetas y procesos de la planta», 11-oct-2026):
#   recetas-maestras/*.md          una receta maestra completa por producto (encabezado, fórmula, equipos,
#                                  procedimiento con operaciones y fases, especificación y PCC)
#   diagramas/modelo_fisico.svg    jerarquía empresa → sitio → áreas → celdas → unidades
#   diagramas/procedimiento_*.svg  modelo procedimental de cada línea (procedimientos de unidad y operaciones)
#   diagramas/pfc_*.svg            diagrama de procedimiento de cada producto
# Uso: python generar_isa88.py
import os, textwrap

D = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(D, 'recetas-maestras'), exist_ok=True)
os.makedirs(os.path.join(D, 'diagramas'), exist_ok=True)

PCC = {
    'PCC-1': 'Antibióticos en cada cisterna (recepción)',
    'PCC-2': 'Pasteurización de la leche a 75 °C por 15 s',
    'PCC-3': 'Pasteurización de la crema a 85 °C por 15 s',
    'PCC-4': 'Tratamiento de la base a 92 °C por 5 min',
    'PCC-5': 'Detector de metales antes de las llenadoras de yogurt',
    'PCC-6': 'Preparado de fruta: certificado, envase íntegro, máximo 24 h a 8 °C o menos',
    'PCC-7': 'Detector de metales antes de la empacadora de quesos',
    'PCC-8': 'Esterilización UHT a 137 °C por 4 s',
    'PCC-9': 'Esterilización del envase con H₂O₂ (envasado aséptico)',
    'PC-Q': 'Salmuera: concentración, temperatura y pH por turno (punto de control, no PCC)',
}

# ---------------- procedimientos de unidad por producto: (código, nombre, unidad, [(fase, valor, pcc)]) ----------------
Y1 = lambda leche, polvo: ('UP-Y1', 'Formulación', 'U201', [
    ('Cargar la leche', leche, None), ('Dosificar sólidos en el mezclador de vacío', polvo, None),
    ('Dispersar e hidratar', '50 °C por 20 min', None)])
Y2 = ('UP-Y2', 'Tratamiento de la base', 'U202', [
    ('Desairear', '68 °C', None), ('Homogeneizar en dos etapas', '200 + 50 bar a 65 a 70 °C', None),
    ('Calentar y retener', '92 °C por 5 min; desvío si baja de 90 °C', 'PCC-4'), ('Enfriar a inoculación', '43 °C ± 0,5', None)])
Y3 = lambda cultivo, horas, ph: ('UP-Y3', 'Fermentación', 'U211 · U212 · U213 · U218', [
    ('Inocular al llenar y agitar', f'{cultivo}; 10 min a 15 a 20 rpm', None), ('Incubar sin agitación', f'43 °C, {horas}', None),
    ('Cortar la fermentación', f'pH {ph}; alarma si pasan 6,5 h', None)])
Y4 = ('UP-Y4', 'Ruptura y enfriamiento', 'U215', [
    ('Romper el coágulo', '5 a 10 min a 20 rpm o menos, sin aire', None), ('Enfriar en placas', '20 °C (15 a 22 °C)', None)])
Y6 = lambda u, t, h: ('UP-Y6', 'Pulmón', u, [('Mantener hasta el llenado', f'{t}, máximo {h}', None)])
Y8 = lambda u, t: ('UP-Y8', 'Envasado', u, [
    ('Detectar metales en la tubería', 'sin metal sobre el patrón', 'PCC-5'),
    ('Llenar, sellar y codificar', f'llenado a {t}; mordaza a 180 a 220 °C', None)])
Y9 = ('UP-Y9', 'Cámara', 'U411', [('Enfriar y madurar', '6 °C o menos en 12 h; reposo de 12 h a 2 a 4 °C', None),
                                  ('Despachar', 'FEFO, camión de 2 a 6 °C', None)])
Q1 = lambda grasa, cultivo, cuajo, coccion, extra=(): ('UP-Q1', 'Tina', 'U221A · U221B · U221C', list(extra) + [
    ('Llenar y atemperar', f'leche al {grasa} a 32 a 35 °C en E-2210', None),
    ('Madurar', f'CaCl₂ 5 L + {cultivo}; 20 a 30 min, agitación lenta', None),
    ('Coagular', f'cuajo {cuajo}; reposo 30 a 40 min hasta corte limpio', None),
    ('Cortar', 'cubos de 1 a 1,5 cm; reposo de 5 min', None),
    ('Cocinar y desuerar', f'{coccion}; retirar el 85 % del suero', None)])
Q2 = lambda ph: ('UP-Q2', 'Acidificación', 'U222', [('Acidificar la cuajada', f'35 a 38 °C hasta pH {ph}; prueba de estiramiento', None)])
Q3 = lambda sal, molde: ('UP-Q3', 'Hilado y moldeo', 'U223', [
    ('Hilar', 'agua de hilado a 75 a 85 °C; pasta a 58 a 62 °C', None)] + ([('Salar en la hiladora', sal, None)] if sal else []) + [
    ('Moldear', molde, None)])
Q4 = lambda salmuera: ('UP-Q4', 'Enfriamiento y salado', 'U224', [('Enfriar', 'canal de agua a 4 a 10 °C', None)] + (
    [('Salar en salmuera', salmuera, 'PC-Q')] if salmuera else []))
Q5 = ('UP-Q5', 'Empaque', 'U321', [('Detectar metales', 'antes de la empacadora', 'PCC-7'),
                                   ('Empacar al vacío y sellar', 'etiqueta con lote, fecha y vencimiento', None)])
Q6 = ('UP-Q6', 'Cámara', 'U414', [('Conservar', '2 a 4 °C, reposo de 12 h; camión de 2 a 6 °C', None)])
L1 = lambda fases: ('UP-L1', 'Mezcla', 'U231', fases)
L2 = ('UP-L2', 'Tratamiento UHT', 'U232', [
    ('Precalentar y desairear', 'regeneración y desaireador', None), ('Esterilizar', '137 °C por 4 s; desvío y recirculación si baja', 'PCC-8'),
    ('Homogeneizar en aséptico', '200/50 bar a unos 70 °C', None), ('Enfriar', '20 a 25 °C', None)])
L3 = ('UP-L3', 'Almacenamiento estéril', 'U233', [('Guardar en estéril', 'presión positiva con aire estéril filtrado', None)])
L4 = ('UP-L4', 'Envasado aséptico', 'U331', [('Esterilizar el envase', 'baño de H₂O₂ y secado con aire estéril caliente', 'PCC-9'),
                                              ('Llenar y sellar', 'caja de 1 L con tapa', None)])
L5 = ('UP-L5', 'Retención y liberación', 'U413', [
    ('Muestrear', 'cajas del inicio, del medio y del final', None),
    ('Incubar y probar', '30 a 35 °C por 7 días; ATP a las 24 a 48 h', None), ('Liberar', 'esterilidad comercial (NTC 4433)', None)])

P = [
    dict(codigo='YF', nombre='Yogurt con fresa', linea='Yogurts', celda='PC21', lotes=13, orden='Último de la campaña',
         denominacion='Yogurt entero con dulce, con fresa (Res. 2310 de 1986, art. 21)', silo='U123A/B', grasa='3,50 %',
         producto='13.092 kg', presentaciones=['Vaso 150 g · U311', 'Botella 1.000 g · U312', 'Botella 1.750 g · U312'], vida='30 días a 2 a 6 °C',
         formula=[('Leche entera estandarizada (U123A/B)', '10.320 kg'), ('Leche en polvo descremada', '444 kg'), ('Azúcar', '626,5 kg'),
                  ('Preparado de fresa en trozos', '1.702 kg (13,0 %)'), ('Cultivo DVS (S. thermophilus y L. bulgaricus)', '400 U')],
         equipos='U201, U202, un fermentador (U211, U212, U213 o U218), U215, U214A, EM-2141, U311, U312, U411',
         up=[Y1('10.320 kg desde U123A/B (± 0,5 %)', 'leche en polvo 444 kg + azúcar 626,5 kg (± 1 %)'), Y2,
             Y3('400 U', 'unas 5,25 h (4,75 a 6,25 h)', '4,50'), Y4, Y6('U214A', '18 a 22 °C', '8 h'),
             ('UP-Y7', 'Saborizado', 'EM-2141', [('Dosificar el preparado de fresa en línea', '13,0 % ± 0,5', 'PCC-6')]),
             Y8('U311 · U312', '18 a 22 °C'), Y9],
         espec=['Grasa 2,79 % (≥ 2,5 %)', 'Proteína 3,60 % (≥ 2,7 %)', 'Sólidos no grasos 10,0 %', 'Acidez 0,86 % (0,70 a 1,50 %)',
                'pH de liberación 4,2 a 4,5', 'Fruta neta 6,5 % (≥ 3 %)', 'Cultivo viable ≥ 10⁷ UFC/g al vencimiento'],
         pcc=['PCC-1', 'PCC-2', 'PCC-4', 'PCC-5', 'PCC-6']),
    dict(codigo='YN', nombre='Yogurt natural', linea='Yogurts', celda='PC21', lotes=13, orden='Primero de la campaña',
         denominacion='Yogurt entero sin dulce', silo='U123A/B', grasa='3,50 %', producto='10.677 kg',
         presentaciones=['Vaso 200 g · U311', 'Botella 1.000 g · U312'], vida='30 días a 2 a 6 °C',
         formula=[('Leche entera estandarizada (U123A/B)', '10.320 kg'), ('Leche en polvo descremada', '357 kg'),
                  ('Cultivo DVS de baja postacidificación', '400 U')],
         equipos='U201, U202, un fermentador, U215, U214B, U311, U312, U411 (EM-2141 aislado con válvulas)',
         up=[Y1('10.320 kg desde U123A/B (± 0,5 %)', 'leche en polvo 357 kg, sin azúcar'), Y2,
             Y3('400 U de cultivo suave', 'unas 5,0 h (4,5 a 6,0 h)', '4,50'), Y4, Y6('U214B', '18 a 22 °C', '8 h'),
             Y8('U311 · U312', '18 a 22 °C'), Y9],
         espec=['Grasa 3,42 %', 'Proteína 4,14 %', 'Acidez 0,85 a 1,05 %; liberación ≥ 0,75 %', 'pH 4,2 a 4,5',
                'Sin sellos frontales: no lleva sal, azúcar ni grasa añadidas'],
         pcc=['PCC-1', 'PCC-2', 'PCC-4', 'PCC-5']),
    dict(codigo='YG', nombre='Yogurt griego', linea='Yogurts', celda='PC21', lotes=9, orden='Segundo de la campaña',
         denominacion='Yogurt griego natural semidescremado, concentrado por separación del suero', silo='U123C', grasa='0,05 % o menos',
         producto='3.242 kg', presentaciones=['Vaso 150 g · U313', 'Pote 500 g · U313'], vida='21 días a 2 a 6 °C',
         formula=[('Leche descremada (U123C)', '10.350 kg'), ('Cultivo DVS de pH estable', '400 U'), ('Crema pasteurizada al 40 % (U127)', '155 kg'),
                  ('Suero ácido que sale a U905', '7.263 kg')],
         equipos='U201, U202, un fermentador, U216, U127, U217A o U217B, U313, U411',
         up=[('UP-Y1', 'Formulación', 'U201', [('Cargar la leche', '10.350 kg desde U123C, sin leche en polvo', None)]),
             ('UP-Y2', 'Tratamiento de la base', 'U202', [('Homogeneizar (opcional)', '100 bar', None),
                                                         ('Calentar y retener', '92 °C por 5 min; desvío si baja de 90 °C', 'PCC-4'),
                                                         ('Enfriar a inoculación', '43 °C', None)]),
             Y3('400 U de cultivo de pH estable', 'unas 5,5 h (5,0 a 6,5 h)', '4,55'),
             ('UP-Y5', 'Separación', 'U216', [('Agitar', 'lento, 10 a 15 min', None),
                                              ('Separar el suero', '40 a 42 °C, 7.000 L/h (unas 1,4 h); proteína 9,6 ± 0,2 %', None),
                                              ('Enfriar el concentrado', '10 a 12 °C, de inmediato', None),
                                              ('Restituir la grasa', 'crema al 40 % de U127, 155 kg; solo crema liberada', 'PCC-3')]),
             Y6('U217A · U217B', '12 °C o menos, un lote por pulmón', '12 h'), Y8('U313', '10 a 12 °C (unas 3,2 h)'), Y9],
         espec=['Proteína 9,23 % (≥ 5,6 %)', 'Grasa 2,00 % (≥ 1,5 %)', 'Acidez de liberación ≤ 1,20 %; ≤ 1,50 % al vencimiento', 'pH 4,3 a 4,6'],
         pcc=['PCC-1', 'PCC-2', 'PCC-3', 'PCC-4', 'PCC-5']),
    dict(codigo='QM', nombre='Mozzarella', linea='Quesos', celda='PC22', lotes=10, orden='Primero del día',
         denominacion='Queso de pasta hilada de baja humedad, semiduro graso (Res. 2310, art. 45)', silo='U124A/B', grasa='3,0 %',
         producto='≈ 1.000 kg (≈ 10 L de leche por kg)', presentaciones=['Bloque 2,5 kg · U321', 'Barra 1 kg · U321'], vida='45 días al vacío a 2 a 4 °C',
         formula=[('Leche pasteurizada (U124A/B) al 3,0 %', '10.000 L'), ('Cloruro de calcio al 40 %', '5 L (2,0 kg de CaCl₂)'),
                  ('Cultivo termófilo', '200 U'), ('Cuajo de quimosina', '2,0 L'), ('Salmuera al 20 %', '8 h'), ('Suero dulce que sale a U905', '≈ 9.000 kg')],
         equipos='E-2210, una tina U221A/B/C, U222, U223, U224, U321, U414',
         up=[Q1('3,0 %', 'cultivo termófilo 200 U', '2,0 L', '40 a 42 °C'), Q2('5,1 a 5,3'), Q3(None, 'bloques de 2,5 kg y barras de 1 kg'),
             Q4('salmuera al 20 % (18 a 22 %) a 8 a 12 °C por 8 h'), Q5, Q6],
         espec=['Humedad 45 a 52 %', 'Grasa en extracto seco ≥ 45 % (diseño ≈ 50 %)', 'pH 5,1 a 5,4', 'Semiduro graso'],
         pcc=['PCC-1', 'PCC-2', 'PCC-7', 'PC-Q']),
    dict(codigo='QQ', nombre='Quesillo', linea='Quesos', celda='PC22', lotes=10, orden='Segundo del día',
         denominacion='Queso de pasta hilada fresca, semiduro a semiblando graso', silo='U124A/B', grasa='3,2 %',
         producto='≈ 1.110 kg (≈ 9 L de leche por kg)', presentaciones=['Bloque 500 g · U321', 'Bloque 1 kg · U321'], vida='25 días al vacío a 2 a 4 °C',
         formula=[('Leche pasteurizada (U124A/B) al 3,2 %', '10.000 L'), ('Cloruro de calcio al 40 %', '5 L'), ('Cultivo mesófilo', '100 U'),
                  ('Cuajo de quimosina', '2,0 L'), ('Sal', '1,5 % en la hiladora + salmuera de 1 h'), ('Suero dulce que sale a U905', '≈ 8.900 kg')],
         equipos='E-2210, una tina U221A/B/C, U222, U223 con la báscula de sal WI-2232, U224, U321, U414',
         up=[Q1('3,2 %', 'cultivo mesófilo 100 U', '2,0 L', '40 a 42 °C'), Q2('5,2 a 5,3'),
             Q3('sal al 1,5 % (báscula WI-2232)', 'bloques de 500 g y 1 kg'), Q4('salmuera corta de 1 h a 8 a 12 °C'), Q5, Q6],
         espec=['Humedad 50 a 56 %', 'Grasa en extracto seco ≥ 45 % (diseño ≈ 53 %)', 'pH 5,2 a 5,5', 'Semiduro a semiblando, graso'],
         pcc=['PCC-1', 'PCC-2', 'PCC-7', 'PC-Q']),
    dict(codigo='QD', nombre='Doble crema', linea='Quesos', celda='PC22', lotes=10, orden='Último del día',
         denominacion='Queso de pasta hilada con más grasa y humedad, semiduro graso', silo='U124A/B', grasa='3,6 % + crema (mezcla al 4,2 %)',
         producto='≈ 1.330 kg (≈ 7,5 L de leche por kg)', presentaciones=['Bloque 500 g · U321', 'Bloque 2,5 kg · U321'], vida='30 días al vacío a 2 a 4 °C',
         formula=[('Leche pasteurizada (U124A/B) al 3,6 %', '9.840 L'), ('Crema pasteurizada al 40 % (U127)', '160 L'), ('Cloruro de calcio al 40 %', '5 L'),
                  ('Cultivo mesófilo', '100 U'), ('Cuajo de quimosina', '2,2 L'), ('Sal', '1,2 % en la hiladora, sin salmuera'),
                  ('Suero dulce que sale a U905', '≈ 8.700 kg')],
         equipos='E-2210, U127 con el contador FQI-2212, una tina U221A/B/C, U222, U223 con WI-2232, U224, U321, U414',
         up=[Q1('3,6 %', 'cultivo mesófilo 100 U', '2,2 L', 'en el límite inferior (≈ 40 °C) para retener humedad',
                extra=[('Agregar la crema al llenar', '160 L al 40 % por FQI-2212; solo crema liberada', 'PCC-3')]),
             Q2('5,2 a 5,3'), Q3('sal al 1,2 % (báscula WI-2232)', 'bloques de 500 g y 2,5 kg'), Q4(None), Q5, Q6],
         espec=['Humedad 50 a 55 %', 'Grasa en extracto seco ≥ 45 % (diseño ≈ 58 %)', 'pH 5,1 a 5,4', 'Semiduro graso'],
         pcc=['PCC-1', 'PCC-2', 'PCC-3', 'PCC-7']),
    dict(codigo='LE', nombre='Leche entera UHT', linea='Leche UHT', celda='PC23', lotes=14, orden='Primera del día',
         denominacion='Leche de larga vida esterilizada a ultra alta temperatura (UAT, Decreto 616 de 2006), envasado aséptico', silo='U125A', grasa='3,0 %',
         producto='≈ 9.800 cajas de 1 L (2 % de merma)', presentaciones=['Caja 1 L en bandejas de 12 · U331'], vida='6 meses sin frío, sin abrir',
         formula=[('Leche pasteurizada (U125A) al 3,0 %', '10.000 L')],
         equipos='U231, U232, U233, U331, U413',
         up=[L1([('Cargar la leche', '10.000 L desde U125A', None), ('Verificar la grasa', '3,0 %; ajustar si hace falta', None)]), L2, L3, L4, L5],
         espec=['Grasa ≥ 3,0 % m/v', 'Acidez 0,13 a 0,17 %', 'Fosfatasa y peroxidasa negativas', 'Esterilidad comercial (NTC 4433)',
                'Peróxido residual en el envase ≤ 0,5 ppm'],
         pcc=['PCC-1', 'PCC-2', 'PCC-8', 'PCC-9']),
    dict(codigo='LD', nombre='Leche descremada UHT', linea='Leche UHT', celda='PC23', lotes=6, orden='Segunda del día',
         denominacion='Leche descremada de larga vida, esterilizada UAT y envasada en aséptico', silo='U125B', grasa='0,3 %',
         producto='≈ 9.800 cajas de 1 L (2 % de merma)', presentaciones=['Caja 1 L en bandejas de 12 · U331'], vida='6 meses sin frío, sin abrir',
         formula=[('Leche pasteurizada (U125B) al 0,3 %', '10.000 L'), ('Crema sobrante de la estandarización', 'sale de U121 a U126')],
         equipos='U231, U232, U233, U331, U413',
         up=[L1([('Cargar la leche', '10.000 L desde U125B', None), ('Verificar la grasa', '0,3 %; ajustar si hace falta', None)]), L2, L3, L4, L5],
         espec=['Grasa 0,1 a 0,5 % m/v', 'Acidez 0,13 a 0,17 %', 'Fosfatasa y peroxidasa negativas', 'Esterilidad comercial (NTC 4433)',
                'Peróxido residual en el envase ≤ 0,5 ppm'],
         pcc=['PCC-1', 'PCC-2', 'PCC-8', 'PCC-9']),
    dict(codigo='LC', nombre='Leche con chocolate UHT', linea='Leche UHT', celda='PC23', lotes=6, orden='Última del día, por el cacao',
         denominacion='Leche saborizada de larga vida, esterilizada UAT y envasada en aséptico', silo='U125A', grasa='3,0 %',
         producto='10.250 kg (≈ 9.520 cajas de 1 L)', presentaciones=['Caja 1 L en bandejas de 12 · U331'], vida='6 meses sin frío, sin abrir',
         formula=[('Leche pasteurizada (U125A) al 3,0 %', '9.210 L'), ('Azúcar', '620 kg (6,0 %)'), ('Cacao en polvo alcalinizado', '125 kg (1,2 %)'),
                  ('Carragenina kappa', '2,6 kg (0,025 %)')],
         equipos='U231 con la báscula WI-2312, la tolva y el mezclador EM-2313; U232, U233, U331, U413',
         up=[L1([('Cargar y calentar la leche', '9.210 L desde U125A a 60 a 65 °C', None),
                 ('Premezclar en seco', 'carragenina con azúcar, 1 a 10', None),
                 ('Incorporar sólidos por la tolva', 'azúcar 620 kg, cacao 125 kg, carragenina 2,6 kg (WI-2312)', None),
                 ('Mezclar', '20 min con recirculación (EM-2313)', None)]), L2, L3, L4, L5,
             ('UP-L6', 'Limpieza intermedia', 'U232 · U233', [('Lavar la planta UHT', 'CIP intermedio de 30 min antes de volver a leche entera', None)])],
         espec=['Grasa ≈ 2,7 % (≥ 2,5 %)', 'Sólidos lácteos no grasos 7,7 a 8,0 %', 'Acidez 0,12 a 0,16 %', 'Esterilidad comercial (NTC 4433)',
                'Peróxido residual ≤ 0,5 ppm; carragenina lejos del máximo de 5 g/kg'],
         pcc=['PCC-1', 'PCC-2', 'PCC-8', 'PCC-9']),
]

# ---------------- dibujo SVG (formato técnico: Arial, trazo negro, PCC en rojo) ----------------
K, G, R, F = '#000000', '#555555', '#b00020', '#f2f2f2'


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def t(x, y, s, size=13, color=K, w=400, anchor='start'):
    return (f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{w}" '
            f'fill="{color}" text-anchor="{anchor}">{esc(s)}</text>')


def rect(x, y, w, h, fill='none', stroke=K, sw=1.2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def line(x1, y1, x2, y2, sw=1.2, color=K, arrow=False):
    a = ' marker-end="url(#f)"' if arrow else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{a}/>'


def hoja(W, H, cuerpo):
    defs = ('<defs><marker id="f" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#000"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + '\n'.join(cuerpo) + '</svg>')


def low(s):
    return s[0].lower() + s[1:]


def wrap(s, n):
    return textwrap.wrap(s, n) or ['']


def pfc(p):
    """Diagrama de procedimiento de un producto: del lote de leche base al producto terminado."""
    W, X, BW = 900, 70, 760
    S, y = [], 34
    S.append(t(X, y, f'Receta maestra {p["codigo"]} · {p["nombre"]}', 22, K, 700)); y += 24
    S.append(t(X, y, f'Diagrama de procedimiento ISA-88 · celda {p["celda"]} · lote de 10.000 L · {p["lotes"]} lotes por semana', 13, G)); y += 26
    # inicio: tronco común
    h = 52
    S.append(rect(X, y, BW, h, rx=26, dash='5 4'))
    S.append(t(X + BW / 2, y + 22, 'Tronco común · UP-LB1 recepción → UP-LB2 pasteurización → UP-LB3 silo', 13, K, 700, 'middle'))
    S.append(t(X + BW / 2, y + 40, f'Lote de leche base liberado del silo {p["silo"]} · grasa {p["grasa"]}', 12.5, G, 400, 'middle'))
    S.append(t(X + BW - 14, y + 22, 'PCC-1 · PCC-2', 11.5, R, 700, 'end'))
    y += h
    for cod, nom, uni, fases in p['up']:
        S.append(line(X + BW / 2, y, X + BW / 2, y + 26, arrow=True)); y += 26
        filas = []
        for f, v, pc in fases:
            for i, l in enumerate(wrap(f'{f}: {v}', 92)):
                filas.append((l, pc if i == 0 else None, i == 0))
        h = 32 + 19 * len(filas) + 10
        S.append(rect(X, y, BW, h))
        S.append(rect(X, y, BW, 30, fill=F))
        S.append(t(X + 12, y + 20, f'{cod}  ·  {nom}', 14, K, 700))
        S.append(t(X + BW - 12, y + 20, uni, 12.5, K, 400, 'end'))
        yy = y + 30 + 20
        for l, pc, primera in filas:
            S.append(t(X + 22 if primera else X + 37, yy, ('–  ' + l) if primera else l, 12.5))
            if pc:
                S.append(t(X + BW - 12, yy, pc, 11.5, R, 700, 'end'))
            yy += 19
        y += h
    S.append(line(X + BW / 2, y, X + BW / 2, y + 26, arrow=True)); y += 26
    h = 52
    S.append(rect(X, y, BW, h, rx=26, sw=1.6))
    S.append(t(X + BW / 2, y + 22, f'Producto terminado · {p["producto"]}', 13, K, 700, 'middle'))
    S.append(t(X + BW / 2, y + 40, ' · '.join(p['presentaciones']), 12.5, G, 400, 'middle'))
    y += h + 30
    S.append(t(X, y, 'Rojo: punto crítico de control (PCC) del plan HACCP. Valores de diseño tomados de las recetas y del modelo procedimental.', 11.5, G))
    return hoja(W, y + 20, S)


LINEAS = {
    'Yogurts': ('procedimiento_yogurts', 'Elaborar un lote de yogurt (10.000 L)', ['YF', 'YN', 'YG']),
    'Quesos': ('procedimiento_quesos', 'Elaborar un lote de queso de pasta hilada (10.000 L)', ['QM', 'QQ', 'QD']),
    'Leche UHT': ('procedimiento_leche_uht', 'Elaborar un lote de leche UHT (10.000 L)', ['LE', 'LD', 'LC']),
}


def proc_linea(linea):
    """Modelo procedimental de una línea: procedimiento → procedimientos de unidad → operaciones, y qué referencias los usan."""
    nombre, titulo, cods = LINEAS[linea]
    prods = [p for p in P if p['codigo'] in cods]
    ups, usa = {}, {}
    for p in prods:
        for cod, nom, uni, fases in p['up']:
            u = ups.setdefault(cod, [nom, [], []])
            for x in uni.split(' · '):
                if x not in u[1]:
                    u[1].append(x)
            for f, _, _ in fases:
                if f not in u[2]:
                    u[2].append(f)
            usa.setdefault(cod, []).append(p['codigo'])
    ups = sorted(ups.items())
    n = len(ups)
    W = max(1200, 40 + n * 175)
    bw = (W - 80 - (n - 1) * 14) / n
    S = [t(40, 40, f'Modelo procedimental ISA-88 · línea de {low(linea)}', 22, K, 700),
         t(40, 64, 'Procedimiento → procedimientos de unidad → operaciones y fases. Las marcas indican qué referencia usa cada procedimiento de unidad.', 13, G)]
    S.append(rect(W / 2 - 260, 90, 520, 46, fill=F, sw=1.6))
    S.append(t(W / 2, 112, 'Procedimiento', 12, G, 400, 'middle'))
    S.append(t(W / 2, 128, titulo, 14, K, 700, 'middle'))
    S.append(line(W / 2, 136, W / 2, 160))
    S.append(line(40 + bw / 2, 160, 40 + (n - 1) * (bw + 14) + bw / 2, 160))
    cab = [(wrap(nom, int(bw / 7.6)), wrap(' · '.join(uni), int(bw / 7))) for _, (nom, uni, _) in ups]
    hh = 30 + max(17 * len(a) + 16 * len(b) for a, b in cab)
    opsh = [sum(20 + 16 * len(wrap(o, int(bw / 6.6))) for o in ops) for _, (_, _, ops) in ups]
    ychips = 184 + hh + 22 + 8 + max(opsh) + 30
    for i, ((cod, (nom, uni, ops)), (ln, lu)) in enumerate(zip(ups, cab)):
        x = 40 + i * (bw + 14)
        S.append(line(x + bw / 2, 160, x + bw / 2, 184, arrow=True))
        S.append(rect(x, 184, bw, hh, fill=F))
        S.append(t(x + 10, 204, cod, 12, G, 700))
        yy = 222
        for l in ln:
            S.append(t(x + 10, yy, l, 13.5, K, 700)); yy += 17
        for l in lu:
            S.append(t(x + 10, yy, l, 11.5, G)); yy += 16
        y = 184 + hh + 22
        S.append(t(x, y, 'Operaciones y fases', 11, G, 700)); y += 8
        for o in ops:
            ls = wrap(o, int(bw / 6.6))
            S.append(line(x + 6, y + 4, x + 6, y + 8 + 16 * len(ls), 1, '#999999'))
            yy = y + 18
            for l in ls:
                S.append(t(x + 14, yy, l, 11.5)); yy += 16
            y = yy + 2
        S.append(line(x, ychips - 20, x + bw, ychips - 20, 1, '#bbbbbb'))
        for j, c in enumerate(cods):
            on = c in usa[cod]
            S.append(rect(x + j * (bw / 3), ychips - 14, bw / 3 - 4, 22, fill=K if on else '#ffffff', stroke=K if on else '#bbbbbb', sw=1))
            S.append(t(x + j * (bw / 3) + (bw / 3 - 4) / 2, ychips + 2, c, 11.5, '#ffffff' if on else '#bbbbbb', 700, 'middle'))
    alto = ychips + 20
    S.append(t(40, alto + 24, 'Referencias: ' + ' · '.join(f'{p["codigo"]} {low(p["nombre"])}' for p in prods), 12, G))
    return nombre, hoja(W, alto + 44, S)


FISICO = [
    ('A1', 'Tronco común', [('PC11', 'Recepción', [('U111 · U112', 'Bahías de descarga'), ('U113 · U114', 'Leche cruda, 2 × 60.000 L')]),
                            ('PC12', 'Tratamiento común', [('U121', 'Separadora-clarificadora'), ('U122', 'Pasteurizador HTST'),
                                                           ('U123A/B · U123C', 'Silos de yogurt'), ('U124A/B', 'Silos de quesos'),
                                                           ('U125A/B', 'Silos de leche UHT'), ('U126 · U127', 'Pasteurizador y tanque de crema')])]),
    ('A2', 'Elaboración', [('PC21', 'Yogurts', [('U201', 'Formulación'), ('U202', 'Módulo térmico'), ('U211–U213 · U218', 'Fermentadores'),
                                                ('U215', 'Ruptura y enfriamiento'), ('U214A/B', 'Pulmones fresa y natural'), ('EM-2141', 'Dosificador de fruta'),
                                                ('U216', 'Separador del griego'), ('U217A/B', 'Pulmones del griego')]),
                           ('PC22', 'Quesos', [('U221A–C', 'Tinas queseras'), ('U222', 'Banda de acidificación'), ('U223', 'Hiladora-moldeadora'),
                                               ('U224', 'Enfriamiento y salmuera')]),
                           ('PC23', 'Leche UHT', [('U231', 'Tanque de mezcla'), ('U232', 'Planta UHT'), ('U233', 'Tanque aséptico')])]),
    ('A3', 'Envasado y fin de línea', [('PC31', 'Envasado de yogurts', [('U311', 'Llenadora de vasos'), ('U312', 'Llenadora de botellas'),
                                                                       ('U313', 'Llenadora del griego')]),
                                       ('PC32', 'Empaque de quesos', [('U321', 'Empacadora al vacío')]),
                                       ('PC33', 'Envasado aséptico', [('U331', 'Envasadora aséptica')]),
                                       ('PC34', 'Fin de línea', [('U341', 'Paletizado manual'), ('U342', 'Envolvedora')])]),
    ('A4', 'Almacenamiento y despacho', [('PC41', 'Frío, bodega y despacho', [('U411', 'Cámara de yogurts'), ('U412', 'Muelle de despacho'),
                                                                             ('U413', 'Bodega de leche UHT'), ('U414', 'Cámara de quesos')])]),
    ('A9', 'Servicios', [('PC90', 'Limpieza y suero', [('U901', 'CIP central'), ('U905', 'Manejo de suero')])]),
]


def fisico():
    celdas = [c for _, _, cs in FISICO for c in cs]
    n, gap, W = len(celdas), 12, 1900
    cw = (W - 80 - (n - 1) * gap) / n
    S = [t(40, 40, 'Modelo físico ISA-88 · Lácteos Altos de Teusacá', 22, K, 700),
         t(40, 64, 'Empresa → sitio → áreas → celdas de proceso → unidades. Códigos iguales a los de las recetas, los P&ID y el modelo de Tecnomatix.', 13, G)]
    for yb, a, b in ((90, 'Empresa', 'Lácteos Altos de Teusacá'), (166, 'Sitio', 'Planta de Zipaquirá · 150.000 L/día')):
        S.append(rect(W / 2 - 220, yb, 440, 46, fill=F, sw=1.6))
        S.append(t(W / 2, yb + 18, a, 11.5, G, 400, 'middle'))
        S.append(t(W / 2, yb + 36, b, 14, K, 700, 'middle'))
    S.append(line(W / 2, 136, W / 2, 166))
    S.append(line(W / 2, 212, W / 2, 236))
    # áreas
    i, centros = 0, []
    for cod, nom, cs in FISICO:
        xa = 40 + i * (cw + gap); wa = len(cs) * cw + (len(cs) - 1) * gap
        centros.append(xa + wa / 2)
        S.append(line(xa + wa / 2, 236, xa + wa / 2, 262, arrow=True))
        S.append(rect(xa, 262, wa, 44, fill=F))
        S.append(t(xa + wa / 2, 278, f'Área {cod}', 11.5, G, 400, 'middle'))
        na = wrap(nom, int(wa / 8))
        if len(na) == 1:
            S.append(t(xa + wa / 2, 297, nom, 13.5, K, 700, 'middle'))
        else:
            S.append(t(xa + wa / 2, 293, na[0], 11.5, K, 700, 'middle'))
            S.append(t(xa + wa / 2, 303, ' '.join(na[1:]), 11.5, K, 700, 'middle'))
        for j, (cc, cn, us) in enumerate(cs):
            xc = xa + j * (cw + gap)
            S.append(line(xc + cw / 2, 306, xc + cw / 2, 330, arrow=True))
            S.append(rect(xc, 330, cw, 60))
            S.append(t(xc + cw / 2, 350, f'Celda {cc}', 11.5, G, 400, 'middle'))
            for k, l in enumerate(wrap(cn, int(cw / 7.4))[:2]):
                S.append(t(xc + cw / 2, 367 + k * 15, l, 12.5, K, 700, 'middle'))
            y = 412
            for uc, un in us:
                ls = wrap(un, int(cw / 6.6))
                S.append(line(xc + 8, y - 22 if y > 412 else 390, xc + 8, y + 2, 1, '#999999'))
                S.append(line(xc + 8, y + 2, xc + 16, y + 2, 1, '#999999'))
                S.append(t(xc + 20, y + 6, uc, 12, K, 700))
                yy = y + 22
                for l in ls:
                    S.append(t(xc + 20, yy, l, 11.5, G)); yy += 15
                y = yy + 12
        i += len(cs)
    S.append(line(centros[0], 236, centros[-1], 236))
    alto = 412 + 8 * 52 + 40
    S.append(t(40, alto, 'Cada unidad contiene sus módulos de equipo y de control (tags de los P&ID); el detalle está en modelo-fisico.md.', 12, G))
    return hoja(W, alto + 20, S)


# ---------------- recetas maestras en markdown ----------------
def md(p):
    L = [f'# Receta maestra {p["codigo"]} · {p["nombre"]}', '',
         f'Receta maestra ISA-88 de la referencia {p["codigo"]}, ligada a la celda {p["celda"]} y a sus unidades. Sale del [modelo físico](../modelo-fisico/modelo-fisico.md), '
         f'el [modelo procedimental](../modelo-procedimental/modelo-procedimental.md) y las [recetas de la planta](../recetas/recetas.md).', '',
         f'![Diagrama de procedimiento {p["codigo"]}](../diagramas/pfc_{p["codigo"]}.svg)', '',
         '## 1. Encabezado', '', '| Campo | Valor |', '|---|---|',
         f'| Código | {p["codigo"]} |', f'| Producto | {p["nombre"]} |', f'| Denominación | {p["denominacion"]} |',
         f'| Línea · celda | {p["linea"]} · {p["celda"]} |', '| Tamaño del lote | 10.000 L de leche estandarizada |',
         f'| Lotes por semana | {p["lotes"]} |', f'| Orden de producción | {p["orden"]} |',
         f'| Leche base | Silo {p["silo"]}, grasa {p["grasa"]} |', f'| Producto por lote | {p["producto"]} |',
         f'| Presentaciones | {" · ".join(p["presentaciones"])} |', f'| Vida útil | {p["vida"]} |', '',
         '## 2. Fórmula por lote', '', '| Materia prima o corriente | Cantidad |', '|---|---|']
    L += [f'| {a} | {b} |' for a, b in p['formula']]
    L += [f'| **Producto** | **{p["producto"]}** |', '', '## 3. Requerimientos de equipo', '', p['equipos'] + '.', '',
          '## 4. Procedimiento', '',
          'Procedimientos de unidad en orden, con sus fases y los valores de esta receta. Antes del primero, el tronco común entrega un lote de leche base liberado '
          f'(UP-LB1 recepción, UP-LB2 pasteurización a 75 °C por 15 s y UP-LB3 almacenamiento en {p["silo"]}).', '',
          '| Procedimiento de unidad | Unidad | Fase | Valor de receta | PCC |', '|---|---|---|---|---|']
    for cod, nom, uni, fases in p['up']:
        for k, (f, v, pc) in enumerate(fases):
            L.append(f'| {f"{cod} {nom}" if k == 0 else ""} | {uni if k == 0 else ""} | {f} | {v} | {pc or ""} |')
    L += ['', '## 5. Especificación del producto terminado', ''] + [f'- {e}' for e in p['espec']] + [f'- Vida útil: {p["vida"]}', '',
          '## 6. Puntos críticos de control', '', '| Código | Control |', '|---|---|'] + [f'| {c} | {PCC[c]} |' for c in p['pcc']]
    L += ['', 'Valores de diseño del proyecto; no son mediciones de planta.', '']
    return '\n'.join(L)


def indice():
    L = ['# Recetas maestras ISA-88 de los nueve productos', '',
         'Una receta maestra por referencia, con la misma estructura: encabezado, fórmula, requerimientos de equipo, procedimiento con fases y valores, '
         'especificación y PCC. Cada una tiene su diagrama de procedimiento.', '',
         '| Línea | Código | Producto | Lotes por semana | Producto por lote | Receta | Diagrama |', '|---|---|---|---|---|---|---|']
    for p in P:
        L.append(f'| {p["linea"]} | {p["codigo"]} | {p["nombre"]} | {p["lotes"]} | {p["producto"]} | [{p["codigo"]}.md]({p["codigo"]}.md) | '
                 f'[pfc_{p["codigo"]}.svg](../diagramas/pfc_{p["codigo"]}.svg) |')
    L += ['', '## Diagramas de la planta', '', '- [Modelo físico](../diagramas/modelo_fisico.svg)'] + [
        f'- [Modelo procedimental de la línea de {low(l)}](../diagramas/{v[0]}.svg)' for l, v in LINEAS.items()]
    L += ['', 'Se generan con `python generar_isa88.py` (carpeta `isa88`).', '']
    return '\n'.join(L)


def guardar(ruta, txt):
    open(ruta, 'w', encoding='utf-8', newline='\n').write(txt)


guardar(os.path.join(D, 'recetas-maestras', 'README.md'), indice())
svgs = {'modelo_fisico': fisico()}
for l in LINEAS:
    k, s = proc_linea(l); svgs[k] = s
for p in P:
    guardar(os.path.join(D, 'recetas-maestras', f'{p["codigo"]}.md'), md(p))
    svgs[f'pfc_{p["codigo"]}'] = pfc(p)
for k, s in svgs.items():
    guardar(os.path.join(D, 'diagramas', k + '.svg'), s)

print('ok:', len(P), 'recetas ·', len(svgs), 'diagramas')
