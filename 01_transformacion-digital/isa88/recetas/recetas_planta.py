# Recetas básicas de la PLANTA COMPLETA de Lácteos Altos de Teusacá (acta 9-oct-2026): 150.000 L/día en tres líneas
# (yogures, quesos y leche UHT) con su tronco común. Las tres recetas de yogur van resumidas (el detalle está en
# Recetas_linea_yogures_v1.8.pdf); quesos y leche UHT van con fórmula por lote, etapas, máquinas y controles.
# Los tiempos por lote son los mismos del modelo de Tecnomatix (planta-150k/construir_planta.py, diccionarios SQ y SL).
# Genera recetas_planta.html; el PDF sale con pdf_planta.mjs.
import os, re

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, 'recetas_yogures.html'), encoding='utf-8').read()
HEAD = src[:src.index('</style>')] + '''
.q { --c: #a37c12; --cs: #fbf3dc; } .l { --c: #3d8a52; --cs: #e3f2e6; } .y { --c: #b8325a; --cs: #f8e3ea; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .q { --c: #e0bb55; --cs: #33290f; } :root:not([data-theme="light"]) .l { --c: #7fcc95; --cs: #14301d; } }
.line-head { display: flex; align-items: baseline; gap: 14px; border-bottom: 3px solid var(--c); padding-bottom: 8px; }
.line-head .code { font-family: var(--font-display); font-weight: 800; font-size: 34px; font-stretch: 80%; color: var(--c); line-height: 1; }
.chip { display: inline-block; font-family: var(--font-mono); font-size: 11px; padding: 1px 7px; border-radius: 999px; background: var(--cs); color: var(--c); border: 1px solid var(--c); }
</style>'''
src = src.replace('<title>', '<title>', 1)
HEAD = re.sub(r'<title>.*?</title>', '<title>Recetas básicas de la planta</title>', HEAD, flags=re.S)


def miles(x):
    return f'{x:,.0f}'.replace(',', '.')


def tabla(cab, filas, der=()):
    th = ''.join(f'<th{" class=\"r\"" if i in der else ""}>{c}</th>' for i, c in enumerate(cab))
    tr = []
    for f in filas:
        cls = ' class="total"' if f and str(f[0]).startswith('Total') else ''
        tr.append(f'<tr{cls}>' + ''.join(f'<td{" class=\"r\"" if i in der else ""}>{c}</td>' for i, c in enumerate(f)) + '</tr>')
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{"".join(tr)}</tbody></table></div>'


# ---------------- datos de diseño ----------------
QUESOS = [  # código, nombre, leche (grasa), rendimiento L/kg, kg por lote, rasgos
    ('QM', 'Mozzarella', '3,0 %', 10.0, 'pasta hilada de acidificación con cultivo termófilo; bloque de 2,5 kg y barra de 1 kg'),
    ('QQ', 'Quesillo', '3,2 %', 9.0, 'pasta hilada fresca, típica del Huila y el Tolima; bloque de 500 g y 1 kg'),
    ('QD', 'Doble crema', '4,2 % (leche + crema propia)', 7.5, 'pasta hilada con más grasa y humedad; bloque de 500 g y 2,5 kg'),
]
LECHES = [  # código, nombre, grasa, envases/lote, rasgos
    ('LE', 'Leche entera UHT', '≥ 3,0 %', 9800, 'leche estandarizada y homogeneizada; 14 lotes por semana'),
    ('LD', 'Leche descremada UHT', '≤ 0,5 %', 9800, 'leche descremada con la crema retirada en U121; 6 lotes por semana'),
    ('LC', 'Leche con chocolate UHT', '≥ 3,0 % en la leche base', 9950, 'leche entera con azúcar, cacao y carragenina; 6 lotes por semana'),
]
kg_q = {c: round(10000 / r, -1) for c, _, _, r, _ in QUESOS}
kg_q_dia = sum(kg_q.values()) * 10 / 6
env_l_dia = (14 * 9800 + 6 * 9800 + 6 * 9950) / 6

B = []
B.append('''<div class="wrap">
<nav class="toc" aria-label="Contenido">
  <p>Contenido</p>
  <ol>
    <li><a href="#resumen"><span class="n">00</span>Resumen de la planta</a></li>
    <li><a href="#tronco"><span class="n">01</span>Tronco común</a></li>
    <li><a href="#yogures"><span class="n">02</span>Línea de yogures</a></li>
    <li><a href="#quesos"><span class="n">03</span>Línea de quesos</a></li>
    <li><a href="#uht"><span class="n">04</span>Línea de leche UHT</a></li>
    <li><a href="#fin"><span class="n">05</span>Fin de línea y despacho</a></li>
    <li><a href="#tiempos"><span class="n">06</span>Tiempos y programa</a></li>
    <li><a href="#haccp"><span class="n">07</span>Controles críticos</a></li>
    <li><a href="#fuentes"><span class="n">08</span>Supuestos y fuentes</a></li>
  </ol>
</nav>
<main>
<header class="head">
  <span class="eyebrow">Recetas básicas ISA-88 · Planta completa</span>
  <h1>Planta láctea de Lácteos Altos de Teusacá</h1>
  <p>Tres líneas sobre un mismo tronco común: yogures, quesos y leche UHT. Para cada producto, la fórmula por lote, las etapas con sus parámetros, las máquinas que las hacen y los controles que no se pueden saltar.</p>
  <div class="meta"><span>Versión <b>1.0</b></span><span>Fecha <b>10 oct 2026</b></span><span>Base <b>acta del 9-oct-2026</b></span></div>
  <p class="note">Todas las cantidades son valores de diseño de Mekvra, no resultados medidos en planta. Las tres recetas de yogur están completas en <span class="mono">Recetas_linea_yogures_v1.8.pdf</span>. Las de quesos y leche UHT son recetas básicas: sus parámetros salen de Tetra Pak, el Codex y la normativa colombiana, y se afinan cuando el equipo defina cada producto. Los tiempos por lote son los mismos del modelo de Tecnomatix de la planta.</p>
</header>
''')

B.append(f'''<section id="resumen">
  <span class="eyebrow">00 · Resumen</span>
  <h2>150.000 L de leche al día, 91 lotes por semana</h2>
  <div class="kpis">
    <div><b>150.000 L</b><span>de leche cruda por día, 6 días por semana</span></div>
    <div><b>91 lotes</b><span>por semana de 10.000 L: 35 de yogur, 30 de queso y 26 de leche</span></div>
    <div><b>≈ {miles(kg_q_dia)} kg</b><span>de queso por día</span></div>
    <div><b>≈ {miles(env_l_dia)}</b><span>envases de leche UHT de 1 L por día</span></div>
  </div>
  <div class="products">
    <article class="prod y"><span class="code">Y</span><h3>Yogures · ≈ 57.000 L/día</h3>
      <dl><dt>Productos</dt><dd>Fresa (YF), natural (YN) y griego (YG)</dd><dt>Lotes/semana</dt><dd>35 (13 · 13 · 9)</dd>
      <dt>Producto</dt><dd>≈ 56.400 kg/día en vasos, botellas y potes</dd><dt>Cuello de botella</dt><dd>Llenadora de vasos U311</dd></dl></article>
    <article class="prod q"><span class="code">Q</span><h3>Quesos · 50.000 L/día</h3>
      <dl><dt>Productos</dt><dd>Mozzarella (QM), quesillo (QQ) y doble crema (QD)</dd><dt>Lotes/semana</dt><dd>30 (10 de cada uno)</dd>
      <dt>Producto</dt><dd>≈ {miles(kg_q_dia)} kg/día, empacado al vacío</dd><dt>Equipo clave</dt><dd>3 tinas de 10.000 L y una hiladora</dd></dl></article>
    <article class="prod l"><span class="code">L</span><h3>Leche UHT · 43.000 L/día</h3>
      <dl><dt>Productos</dt><dd>Entera (LE), descremada (LD) y con chocolate (LC)</dd><dt>Lotes/semana</dt><dd>26 (14 · 6 · 6)</dd>
      <dt>Producto</dt><dd>≈ {miles(env_l_dia)} envases asépticos de 1 L/día</dd><dt>Equipo clave</dt><dd>Esterilizador UHT y envasadora aséptica</dd></dl></article>
  </div>
  <p>La leche UHT reemplaza al kéfir del alcance anterior (acta del 9-oct). La línea de yogures tiene un cupo de diseño de 80.000 L/día, pero hoy procesa ≈ 57.000 porque la llenadora de vasos está al límite; la propuesta de automatización la lleva a 80.000 con el aumento de acopio del contrato de un año.</p>
</section>
''')

B.append('''<section id="tronco">
  <span class="eyebrow">01 · Tronco común · Origen y Pureza</span>
  <h2>Recepción, pasteurización y silos para las tres líneas</h2>
  <p>La leche llega en cisternas, se analiza en plataforma, se enfría y espera en tanques. Luego se clarifica, se descrema y estandariza, y se pasteuriza en flujo continuo. Cada línea toma su leche de su propio silo.</p>
''' + tabla(['Etapa', 'Equipo', 'Parámetros', 'Control'], [
    ['Recepción y aceptación', '2 bahías U111/U112 · laboratorio de calidad', 'Cisternas de ≈ 20.000 L, ≈ 8 por día. Leche ≤ 6 °C; prueba de antibióticos, alcohol, acidez, densidad y grasa', '<b>PCC-1:</b> antibióticos negativos o se rechaza la cisterna'],
    ['Leche cruda', 'Tanques U113/U114, 2 × 60.000 L', '≤ 4 °C con agitación, máximo 24 h', 'Temperatura continua'],
    ['Clarificación y estandarización', 'Separadora-clarificadora U121', 'Grasa a la medida de cada línea; la crema sobrante va a U126', 'Densímetro y analizador de grasa en línea'],
    ['Pasteurización HTST', 'Intercambiador de placas U122, 20.000 L/h', '≥ 72 °C × 15 s (75 °C de diseño) y enfriamiento a ≤ 4 °C', '<b>PCC-2:</b> registro de temperatura y válvula de desvío'],
    ['Silos de leche pasteurizada', 'U123A/B y U123C (yogures) · U124 (quesos) · U125 (leche UHT)', '2–4 °C, máximo 24 h', 'Temperatura y tiempo por silo'],
], ()) + '''
  <p>Carga del tronco con 150.000 L/día: recepción 24 % de las 16 h de ventana, pasteurizador 45 % del día (10,8 h con lavados y arranques). Bastan los dos tanques de leche cruda: el pico de un día normal es de ≈ 7.500 L. El cálculo está en <span class="mono">tanques_150k.py</span>.</p>
</section>
''')

B.append('''<section id="yogures" class="y">
  <div class="line-head"><span class="code">Y</span><h2>Línea de yogures · ≈ 57.000 L/día</h2></div>
  <p>Resumen de las recetas maestras v1.8. El detalle (fórmulas, balances, especificaciones y HACCP) está en <span class="mono">Recetas_linea_yogures_v1.8.pdf</span>.</p>
''' + tabla(['Producto', 'Base por lote', 'Proceso clave', 'Presentaciones', 'Por lote'], [
    ['<span class="chip">YF</span> Yogur con fresa', '10.000 L de leche entera estandarizada + leche en polvo + azúcar', 'Base a 92 °C × 5 min → fermentación a 43 °C hasta pH 4,50 → ruptura y enfriamiento → fruta en línea (13 %)', 'Vaso 150 g · botella 1000 y 1750 g', '13.092 kg'],
    ['<span class="chip">YN</span> Yogur natural', '10.000 L de leche entera estandarizada + leche en polvo', 'Igual que YF, sin azúcar ni fruta', 'Vaso 200 g · botella 1000 g', '10.677 kg'],
    ['<span class="chip">YG</span> Yogur griego', '10.000 L de leche descremada', 'Fermentación a 43 °C → separación del suero en U216 → crema propia al final', 'Vaso 150 g · pote 500 g', '3.242 kg'],
], (4,)) + tabla(['Etapa', 'Máquinas', 'Capacidad'], [
    ['Formulación y tratamiento de la base', 'U201 tanque de formulación con tolva de polvos · U202 homogeneizador + placas, 92 °C × 5 min', '12.000 L · 10 m³/h'],
    ['Fermentación', 'U211, U212, U213 y U218, fermentadores de 12.000 L', 'Ciclo de 8,1–9,0 h por lote'],
    ['Acondicionamiento', 'U215 ruptura y enfriamiento · U216 separador del griego · pulmones U214A (fresa), U214B (natural) y U217A/B (griego)', '7.000 L/h en U216'],
    ['Envasado y encajonado', 'U311 vasos · U312 botellas · U313 potes · U321–U323 encajonadoras', 'U311: 12.000 vasos/h de 150 g'],
    ['Fin de línea', 'U341 paletizado (manual en la planta actual) · U342 envolvedora · U411 cámara 2–4 °C', 'Reposo ≥ 12 h antes de despacho'],
], ()) + '</section>\n')

# ---------------- quesos ----------------
qrows = []
for c, n, g, r, rasgo in QUESOS:
    qrows.append([f'<span class="chip">{c}</span> {n}', g, f'≈ {r:.1f} L/kg'.replace('.', ','), f'≈ {miles(kg_q[c])} kg', rasgo])
B.append('''<section id="quesos" class="q">
  <div class="line-head"><span class="code">Q</span><h2>Línea de quesos · 50.000 L/día</h2></div>
  <p>Tres quesos de pasta hilada, muy consumidos en Colombia, que comparten las mismas máquinas: la diferencia está en la grasa de la leche, en cómo se acidifica la cuajada y en la sal. Lote de 10.000 L de leche pasteurizada del silo U124.</p>
''' + tabla(['Queso', 'Grasa de la leche', 'Rendimiento', 'Queso por lote', 'Rasgos'], qrows, (2, 3)) + '''
  <h3>Fórmula por lote (10.000 L de leche estandarizada)</h3>
''' + tabla(['Insumo', 'Mozzarella QM', 'Quesillo QQ', 'Doble crema QD', 'Función'], [
    ['Leche pasteurizada (U124)', '10.000 L al 3,0 %', '10.000 L al 3,2 %', '9.840 L al 3,6 % + 160 L de crema al 40 % (≈ 4,2 %)', 'Base; la crema sale de U126'],
    ['Cloruro de calcio (solución al 40 %)', '5 L', '5 L', '5 L', 'Repone el calcio que se pierde al pasteurizar y da firmeza a la cuajada'],
    ['Cultivo', 'Termófilo (<i>S. thermophilus</i> + <i>L. bulgaricus</i>), dosis del proveedor', 'Mesófilo láctico, dosis del proveedor', 'Mesófilo láctico, dosis del proveedor', 'Acidifica la cuajada hasta el pH de hilado'],
    ['Cuajo de quimosina', '≈ 2,0 L', '≈ 2,0 L', '≈ 2,2 L', 'Coagula en 30–40 min (dosis del proveedor)'],
    ['Sal', 'Salmuera al 20 %, 8 h', '1,5 % en el hilado + salmuera corta', '1,2 % en el hilado', 'Sabor, conservación y corteza'],
    ['Suero dulce', '≈ 9.000 kg', '≈ 8.900 kg', '≈ 8.700 kg', 'Va a venta o a la PTAR; no se bota sin tratar'],
], ()) + '''
  <h3>Procedimiento y parámetros</h3>
''' + tabla(['Fase', 'Máquina', 'Parámetros', 'Tiempo por lote'], [
    ['Llenar y madurar', 'Tina quesera Q201, Q202 o Q203 (10.000 L, doble pared, liras)', 'Leche a 32–35 °C, CaCl₂ y cultivo; maduración 20–30 min', 'Incluido en la tina'],
    ['Coagular y cortar', 'La misma tina', 'Cuajo; coagulación 30–40 min; corte en cubos de 1–1,5 cm', 'Incluido en la tina'],
    ['Cocinar y desuerar', 'La misma tina', 'Cocción hasta 40–42 °C con agitación; se retira ≈ 85 % del suero', 'Tina: <b>3,0 h</b> + CIP 0,5 h'],
    ['Acidificar la cuajada', 'Banda de cuajada hacia la hiladora', 'Hasta pH 5,1–5,3 (QM) o 5,2–5,3 (QQ y QD), que es cuando la cuajada hila', 'Dentro del tiempo de la tina'],
    ['Hilar y moldear', 'Hiladora-moldeadora Q301 de tornillos (1.000–1.300 kg/h)', 'Agua de hilado a 75–85 °C; la pasta sale a 58–62 °C; sal en QQ y QD', '<b>1,0 h</b> (0,5 h al cambiar de queso)'],
    ['Enfriar y salar', 'Piscinas de salmuera Q302', 'Salmuera al 18–22 % de NaCl a 8–12 °C; QM 8 h', '<b>8,0 h</b>'],
    ['Empacar', 'Empacadora al vacío Q311 (termoformadora)', 'Vacío y sellado; etiqueta con lote y fecha; detector de metales antes', '<b>1,2 h</b>'],
    ['Paletizar y enfriar', 'Paletizado manual Q341 · cámara de quesos Q411', 'Cámara a 2–4 °C, reposo de 12 h antes del despacho', '12 h'],
], (3,)) + '''
  <h3>Especificación del producto (valores de diseño)</h3>
''' + tabla(['Queso', 'Humedad', 'Grasa en extracto seco', 'pH', 'Vida útil a 2–4 °C'], [
    ['Mozzarella QM', '45–52 %', '≥ 40 %', '5,1–5,4', '45 días al vacío'],
    ['Quesillo QQ', '50–56 %', '≥ 40 %', '5,2–5,5', '25 días al vacío'],
    ['Doble crema QD', '50–55 %', '≥ 45 %', '5,1–5,4', '30 días al vacío'],
], ()) + '</section>\n')

# ---------------- leche UHT ----------------
B.append('''<section id="uht" class="l">
  <div class="line-head"><span class="code">L</span><h2>Línea de leche UHT · 43.000 L/día</h2></div>
  <p>Leche de larga vida, esterilizada a ultra alta temperatura y envasada en condiciones asépticas en cajas de 1 L. Se guarda sin frío. Lote de 10.000 L de leche pasteurizada del silo U125; el orden del día es entera → descremada → chocolate, porque el cacao va al final.</p>
''' + tabla(['Producto', 'Grasa', 'Envases de 1 L por lote', 'Rasgos'],
            [[f'<span class="chip">{c}</span> {n}', g, f'≈ {miles(e)}', r] for c, n, g, e, r in LECHES], (2,)) + '''
  <h3>Fórmula por lote</h3>
''' + tabla(['Insumo', 'Entera LE', 'Descremada LD', 'Chocolate LC', 'Función'], [
    ['Leche pasteurizada (U125)', '10.000 L al 3,0 %', '10.000 L al ≤ 0,5 %', '9.210 L al 3,0 %', 'Base'],
    ['Azúcar', '—', '—', '620 kg (6,0 %)', 'Dulzor'],
    ['Cacao en polvo alcalinizado', '—', '—', '125 kg (1,2 %)', 'Sabor y color'],
    ['Carragenina', '—', '—', '2,6 kg (0,025 %)', 'Mantiene el cacao en suspensión'],
    ['Producto por lote', '≈ 10.000 L', '≈ 10.000 L', '≈ 10.250 kg (≈ 9.950 L)', '2 % de merma en purgas y arranques'],
], ()) + '''
  <h3>Procedimiento y parámetros</h3>
''' + tabla(['Fase', 'Máquina', 'Parámetros', 'Tiempo por lote'], [
    ['Mezclar y estandarizar', 'Tanque de mezcla L201 con tolva y mezclador de alto cizallamiento', 'Ajuste de grasa y sólidos; en LC se dispersan azúcar, cacao y carragenina a 60–65 °C', '<b>1,0 h</b> (0,5 h de lavado al cambiar de producto)'],
    ['Homogeneizar y esterilizar', 'Planta UHT indirecta L202 (placas y tubos, 10.000 L/h) con homogeneizador aséptico', 'Homogeneización 200/50 bar a 70 °C · esterilización a <b>137 °C × 4 s</b> · enfriamiento a 20–25 °C', '<b>1,0 h</b>'],
    ['Guardar en estéril', 'Tanque aséptico L203 (20.000 L)', 'Presión positiva con aire estéril; alimenta la envasadora sin parar el UHT', 'Pulmón'],
    ['Envasar', 'Envasadora aséptica L311 (≈ 7.000 envases/h)', 'Esterilización del material con peróxido de hidrógeno; sellado de la caja de 1 L; tapa', '<b>2,0 h</b>'],
    ['Paletizar y liberar', 'Paletizado manual L341 · bodega ambiente L411', 'Retención por lote hasta la liberación: prueba rápida de esterilidad (24–48 h) y muestras incubadas 7 días a 30 °C', '24 h en el modelo'],
], (3,)) + '''
  <p>Especificación: leche entera con ≥ 3,0 % de grasa y descremada con ≤ 0,5 %; esterilidad comercial; vida útil de 6 meses a temperatura ambiente sin abrir.</p>
</section>
''')

B.append('''<section id="fin">
  <span class="eyebrow">05 · Fin de línea</span>
  <h2>Cajas, estibas y despacho</h2>
''' + tabla(['Línea', 'Encajonado', 'Paletizado', 'Almacén', 'Despacho'], [
    ['Yogures', 'Encajonadoras U321–U323', 'U341 (2 operarios en la planta actual) + envolvedora U342', 'Cámara U411 a 2–4 °C, reposo ≥ 12 h', 'Camión refrigerado a 2–6 °C'],
    ['Quesos', 'A la salida de la empacadora Q311', 'Q341 manual, 2 operarios', 'Cámara de quesos Q411 a 2–4 °C', 'Camión refrigerado a 2–6 °C'],
    ['Leche UHT', 'En la envasadora L311 (bandejas de 12)', 'L341 manual, 2 operarios', 'Bodega L411 a temperatura ambiente', 'Camión seco'],
], ()) + '</section>\n')

B.append('''<section id="tiempos">
  <span class="eyebrow">06 · Tiempos por lote (insumo de Tecnomatix)</span>
  <h2>Programa semanal y tiempos por lote</h2>
''' + tabla(['Línea', 'Lotes por semana', 'Orden dentro del día', 'Etapas y tiempos por lote'], [
    ['Yogures', '35 (13 YN · 9 YG · 13 YF)', 'Natural → griego → fresa', 'U201 1,9 h · U202 1,2 h · fermentador 8,1–9,0 h · U215 1,1 h · llenado ≈ 3,5 h'],
    ['Quesos', '30 (10 QM · 10 QQ · 10 QD)', 'Mozzarella → quesillo → doble crema', 'Tina 3,5 h · hilado 1,0 h · salmuera 8,0 h · empaque 1,2 h · cámara 12 h'],
    ['Leche UHT', '26 (14 LE · 6 LD · 6 LC)', 'Entera → descremada → chocolate', 'Mezcla 1,0 h · UHT 1,0 h · envasado 2,0 h · retención 24 h'],
], ()) + '''
  <p>En el modelo de la planta (12 semanas simuladas, con fallas) el tronco recibe ≈ 151.700 L/día, el cuello de botella sigue siendo la llenadora de vasos de yogur (88 %) y las líneas de quesos y leche UHT quedan holgadas: tinas al 24 %, hiladora al 27 % y envasadora aséptica al 40 %.</p>
</section>
''')

B.append('''<section id="haccp">
  <span class="eyebrow">07 · Controles críticos</span>
  <h2>Puntos críticos de control de la planta</h2>
''' + tabla(['PCC', 'Línea', 'Peligro', 'Límite crítico', 'Monitoreo y acción'], [
    ['PCC-1', 'Tronco', 'Antibióticos en la leche', 'Prueba negativa', 'Kit rápido por cisterna; se rechaza'],
    ['PCC-2', 'Tronco', 'Patógenos en la leche', '≥ 72 °C × 15 s', 'Registro continuo y válvula de desvío'],
    ['PCC-Y', 'Yogures', 'Ver el plan de la línea de yogures', '92 °C × 5 min, pH, metales', 'Recetas de yogures v1.8, sección 9'],
    ['PCC-Q1', 'Quesos', 'Metales en el producto', 'Sin metal ≥ patrón validado', 'Detector antes de Q311; se rechaza y reinspecciona'],
    ['PC-Q', 'Quesos', 'Salmuera contaminada', 'NaCl 18–22 %, 8–12 °C', 'Medición por turno; filtrado y pasteurización de la salmuera'],
    ['PCC-L1', 'Leche UHT', 'Supervivencia de esporas', '≥ 137 °C × 4 s', 'Registro continuo; si baja, se desvía y se reprocesa'],
    ['PCC-L2', 'Leche UHT', 'Contaminación del envase', 'Concentración y temperatura del H₂O₂ del fabricante', 'Registro continuo; el lote queda retenido'],
], ()) + '</section>\n')

B.append('''<section id="fuentes">
  <span class="eyebrow">08 · Supuestos y fuentes</span>
  <h2>De dónde salen los números</h2>
  <ul>
    <li>Reparto de 150.000 L/día y cambio de kéfir por leche UHT: acta de Mekvra del 9 de octubre de 2026.</li>
    <li>Leche y leche UHT: Decreto 616 de 2006 (Ministerio de la Protección Social), requisitos de la leche y tratamiento UAT de 135–150 °C por 2–4 s.</li>
    <li>Derivados lácteos y quesos: Resolución 2310 de 1986 y NTC 750; mozzarella, norma Codex CXS 262-2006.</li>
    <li>Procesos de queso de pasta hilada y de leche UHT: Tetra Pak, <i>Dairy Processing Handbook</i>, capítulos de queso y de leche de larga vida.</li>
    <li>Rendimientos de queso (10, 9 y 7,5 L de leche por kg), dosis de cuajo y cultivo y vidas útiles: valores de diseño por confirmar con los proveedores y con pruebas piloto.</li>
    <li>Tiempos por lote de quesos y leche UHT: supuestos de diseño, los mismos del modelo de Tecnomatix de la planta (<span class="mono">planta-150k/construir_planta.py</span>).</li>
  </ul>
</section>
</main></div>
''')
html = HEAD + '\n' + ''.join(B)
open(os.path.join(D, 'recetas_planta.html'), 'w', encoding='utf-8').write(html)
print('ok', miles(kg_q_dia), miles(env_l_dia))
