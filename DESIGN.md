# Mekvra — Style Reference
> Monolito de obsidiana a la luz de una vela, con una planta automatizada trabajando dentro: lienzo casi negro, un único acento champaña que corta como una cuchilla, y máquinas que se mueven en silencio.

**Theme:** dark

Base visual: sistema **Atoms** (monocromo negro, crema y champaña; tipografía Switzer apretada; bordes finos sin sombras). Sobre esa base se integran tres modificaciones pedidas por el equipo:

1. **Gráficas de instrumento** tomadas del sistema **Factory**: marco de dashboard, recuadros de métrica con valor grande y minigráfica, voz monoespaciada para etiquetas y unidades, indicador de estado.
2. **Logo de partículas que cambia de forma**, tomado del campo de partículas de **Aaru**: cientos de teselas que se ensamblan en el logo de Mekvra y se transforman en otras figuras del mundo de la empresa.
3. **Automatización en movimiento**: un brazo robot articulado que hace pick & place sobre una banda transportadora, con sensores y lecturas en vivo.

Mekvra opera en una disciplina casi totalmente monocroma: lienzos negros, texto crema cálido y un solo acento champaña. El color no decora; crema para texto, oro para énfasis, negro para profundidad, como titanio mecanizado bajo luz de tungsteno. La única excepción cromática son dos colores **de dato** (verde métrica y naranja señal), que solo aparecen dentro de gráficas e indicadores de estado, igual que en una HMI ISA-101: el color significa estado, nunca adorno.

A diferencia de Atoms, este sistema **sí se mueve**, en cuatro lugares con significado: el logo de partículas, el brazo robot con su banda, los datos en vivo de las gráficas y **la entrada de cada elemento al hacer scroll** (estilo Factory): el contenido sube, pasa de desenfocado a nítido y entra en cascada. Una vez colocado, queda quieto.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Champagne Gold | `#c8ad86` | `--color-champagne-gold` | Acento de marca: partículas del logo, títulos de acento, pills de categoría, trazo principal de gráficas, bordes decorativos. Nunca como relleno de superficie completa |
| Candlelight Cream | `#fff7dd` | `--color-candlelight-cream` | Texto principal, bordes finos (al 12–30 %), líneas del brazo robot, iconos |
| Obsidian Black | `#000000` | `--color-obsidian-black` | Lienzo de página, superficie de tarjetas y del dashboard |
| Ember Ash | `#66635f` | `--color-ember-ash` | **Solo** rejillas, bordes, barras "antes" y superficies apagadas. No sirve para texto: su contraste (3,5:1) no cumple WCAG AA |
| Warm Granite | `#8a8380` | `--color-warm-granite` | *(de Factory)* Texto secundario, etiquetas de instrumento, notas y fuentes. Contraste 5,6:1 sobre negro y 5:1 sobre `#141312` |
| Carbon Lift | `#141312` | `--color-carbon-lift` | *(de Factory)* Fondo del marco del dashboard y de la barra de ventana; un paso sobre el negro |
| Ash Stroke | `#2b2926` | `--color-ash-stroke` | *(de Factory)* Divisiones de 1 px entre recuadros de métrica y líneas de rejilla |
| Metric Green | `#a0ca92` | `--color-metric-green` | *(de Factory)* **Solo datos:** tendencia positiva, equipo en marcha, lote aprobado |
| Signal Orange | `#ee6018` | `--color-signal-orange` | *(de Factory)* **Solo datos:** alarma, tendencia negativa, pulso de estado "en vivo" |

## Tokens — Typography

### Switzer — tipografía principal · `--font-switzer`
Todos los títulos, cuerpo y navegación. Sans geométrica con tracking negativo muy ajustado en tamaños grandes (-0.042em a 44px), que da formas compactas y mecanizadas. Peso 400 para cuerpo, 500 para etiquetas y tags.
- **Fuente:** Fontshare (gratuita)
- **Sustituto:** General Sans, Satoshi
- **Pesos:** 400, 500
- **Tamaños:** 10, 12, 14, 16, 20, 28, 44, 64px
- **Line height:** 1.00–1.13 en títulos; 1.5 en párrafos
- **Letter spacing:** -2.7px a 64px, -1.85px a 44px, -0.5px a 16px, 0.18px a 10px

### Geist Mono — voz de instrumento · `--font-geist-mono`
*(de Factory)* Etiquetas de métricas, unidades, tags de instrumento (TT-101, PLC-01), títulos de ventana del dashboard, lecturas de sensores. Siempre en mayúsculas a 10–12px. Cuando aparece la mono, el lector sabe que está viendo un instrumento, no una página de marketing.
- **Fuente:** Google Fonts
- **Pesos:** 400
- **Tamaños:** 10, 11, 12px
- **Letter spacing:** 0.04em en mayúsculas

### Barlow Condensed — titular del inicio · `--font-display`
Solo para el titular principal (H1). Condensada industrial inspirada en DIN, la letra de la señalética de planta y de las placas de máquinas. Peso 600, siempre en MAYÚSCULAS, tracking 0.005em, line-height 0.95. Referencia de composición: Balsa (titular condensado, grueso y sereno).
- **Fuente:** Google Fonts
- **Tamaño:** `clamp(40px, min(8vw, 9svh), 92px)`

### Type Scale

| Role | Family | Weight | Size | Line Height | Letter Spacing | Token |
|------|--------|--------|------|-------------|----------------|-------|
| caption | Switzer | 500 | 10px | 1.2 | 0.18px | `--text-caption` |
| label-mono | Geist Mono | 400 | 11px | 1.2 | 0.44px, mayúsculas | `--text-label` |
| body | Switzer | 400 | 14px | 1.5 | — | `--text-body` |
| body-lg | Switzer | 400 | 16px | 1.5 | -0.2px | `--text-body-lg` |
| subheading | Switzer | 500 | 20px | 1.2 | -0.5px | `--text-subheading` |
| metric | Switzer | 400 | 28px | 1.0 | -1px, números tabulares | `--text-metric` |
| heading | Switzer | 400 | 44px | 1.13 | -1.85px | `--text-heading` |
| display | Switzer | 400 | 64px | 1.0 | -2.7px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compacta dentro de los componentes, generosa entre secciones.

### Spacing Scale

| Name | Value | Token |
|------|-------|-------|
| 4 | 4px | `--spacing-4` |
| 8 | 8px | `--spacing-8` |
| 10 | 10px | `--spacing-10` |
| 16 | 16px | `--spacing-16` |
| 20 | 20px | `--spacing-20` |
| 24 | 24px | `--spacing-24` |
| 32 | 32px | `--spacing-32` |
| 40 | 40px | `--spacing-40` |
| 56 | 56px | `--spacing-56` |
| 80 | 80px | `--spacing-80` |
| 120 | 120px | `--spacing-120` |

### Border Radius

| Element | Value |
|---------|-------|
| tags / pills | 100px |
| cards | 4px |
| buttons | 4px |
| dashboard frame | 6px |
| tabs | 0px (subrayado, no cápsula) |

### Layout

- **Page max-width:** 1200px
- **Section gap:** 120px (80px en móvil)
- **Card padding:** 32px (20px en móvil)
- **Element gap:** 8–16px

## Components

### Particle Morph Logo — *modificación 2*
**Role:** Marca principal en el hero; el logo es la animación.

Un campo de ~900 teselas cuadradas (2–3px) en `#c8ad86`, con ligeras variaciones de opacidad (55–100 %) para dar la textura metálica del mosaico de Atoms. Las teselas se ensamblan en el **monograma de Mekvra**: una "M" construida sobre una retícula de 9×9 módulos cuyo vértice central es una articulación circular, como el eje de un brazo robot.

Secuencia (bucle de ~16 s, 3 s de reposo en cada figura):
1. **Monograma M** (figura de reposo y figura inicial)
2. **Engranaje** de 12 dientes: mecatrónica
3. **Brazo robot** en silueta: automatización
4. **Pirámide ISA-95** de 5 niveles: integración OT/IT
5. **Gota de leche**: el cliente lácteo
6. Vuelta al monograma M

Transición entre figuras: cada tesela viaja a su nuevo destino con ease-out exponencial (900–1400 ms, desfasadas por distancia), con una breve dispersión en forma de nube como en el campo de Aaru. El cursor repele las teselas en un radio de 60px y estas vuelven a su sitio con resorte suave. Ocupa ~40 % de la altura del hero, sin fondo, directo sobre el negro. Bajo `prefers-reduced-motion`: se muestra el monograma quieto.

En la barra de navegación, el **lockup** es el monograma estático (mismas teselas, 20px) + el nombre `Mekvra` en Switzer 500, 16px, crema.

### Robot Arm Cell — *modificación 3*
**Role:** Escena de automatización en vivo; demuestra lo que hace la empresa.

Dibujo lineal en SVG, trazos de 1.5px en `#fff7dd`, articulaciones como círculos de 6px con borde champaña. Un brazo de 3 ejes (base giratoria, hombro, codo) + pinza, resuelto con cinemática inversa de 2 eslabones, hace un ciclo de **pick & place**: toma bloques de queso (rectángulos redondeados con borde champaña) de una banda transportadora y los apila en una estiba.

Elementos de automatización alrededor, todos en línea fina:
- **Banda transportadora** con rodillos que giran y productos que avanzan.
- **Sensor fotoeléctrico** con haz punteado; al cortarse el haz, un punto `#a0ca92` se enciende y el brazo arranca su ciclo.
- **Etiquetas de instrumento** en Geist Mono (`FT-201`, `PLC-01 · RUN`, `CICLO 4.2 s`, `PIEZAS 128`) que se actualizan en vivo.
- **Pulso de estado** (`#ee6018` al fallar, `#a0ca92` en marcha).

El ciclo dura ~4 s. El usuario puede pausar y reanudar. Bajo `prefers-reduced-motion`: pose fija con los valores quietos.

### Dashboard Frame — *modificación 1*
**Role:** Contenedor de las gráficas del proyecto (KPIs, variables de proceso, simulación).

Panel `#141312` con radio de 6px y borde de 1px crema al 12 %. Barra de ventana superior de 36px: tres puntos de 8px en `#2b2926` a la izquierda, título en Geist Mono 11px mayúsculas crema al 70 % y, a la derecha, un **pulso de estado** con la etiqueta `EN VIVO` o `SIMULACIÓN`. Interior: retícula de recuadros de métrica separados por divisiones de 1px `#2b2926`.

### Metric Tile
**Role:** Una celda de dato dentro del dashboard.

Sin fondo, divisiones de 1px `#2b2926`, padding 20px.
- **Etiqueta:** Geist Mono 11px mayúsculas `#66635f` (p. ej. `OEE · LÍNEA QUESOS`).
- **Valor:** Switzer 28px peso 400, `#fff7dd`, tracking -1px, números tabulares; la unidad en Geist Mono 11px champaña (`%`, `°C`, `min`, `kg/h`).
- **Minigráfica:** 40px de alto, trazo de 1.5px. Champaña para la serie principal; `#a0ca92` si la tendencia es positiva y `#ee6018` si cruza un límite. Área bajo la curva en el mismo color al 8 %.
- **Delta:** Geist Mono 11px en verde o naranja con flecha `↑` / `↓`.

### Chart Panel
**Role:** Gráficas grandes (tendencias de proceso, comparación antes/después, VSM, OEE).

Dentro de un Dashboard Frame. Rejilla de líneas horizontales `#2b2926` de 1px, ejes y ticks en Geist Mono 10px `#66635f`, sin bordes de ejes gruesos. Series:
- Principal: champaña `#c8ad86`, 1.5px.
- Secundaria / referencia: crema al 40 %, 1px, punteada `4 4`.
- Límites de control y setpoints: línea punteada naranja `#ee6018` con etiqueta mono.
- Barras (antes vs. después): antes en `#66635f`, después en `#c8ad86`; ancho fijo, radio 2px arriba.

Al pasar el cursor, una línea vertical crema al 30 % sigue al puntero y una etiqueta mono muestra el valor exacto. Las series se dibujan de izquierda a derecha la primera vez que entran en pantalla (600 ms).

### Status Pulse
*(de Factory)* Círculo de 6px en `#ee6018` o `#a0ca92` antes de una etiqueta. Late suavemente (opacidad 1 → 0.35, 1.6 s) solo cuando el estado es "en vivo".

### Instrument Tabs
**Role:** Pestañas interactivas para cambiar de línea (Queso · Yogurt · Kéfir), de nivel ISA-95 o de módulo.

Fila de etiquetas Geist Mono 11px mayúsculas con numeración (`01 QUESO`, `02 YOGURT`, `03 KÉFIR`), separadas 24px, sobre una línea de 1px crema al 12 %. La pestaña activa pasa a crema al 100 % y un subrayado champaña de 1px se desliza hasta ella (250 ms, ease-out). Las inactivas quedan en `#66635f`, y al pasar el cursor suben a crema al 70 %. Se usan con flechas del teclado. El contenido cambia con un fundido de 150 ms, sin desplazamiento.

### Numbered Annotation Row
*(de Aaru)* Para listas de pasos, niveles ISA-95 o etapas del proceso: prefijo numérico `01–05` en Geist Mono 11px champaña, título en Switzer 20px crema y línea de 1px crema al 12 % encima. Puede expandirse (acordeón) mostrando el cuerpo a 14px con sangría alineada al título.

### Hero (inicio)
Composición serena, centrada, que cabe completa en la primera pantalla (referencia: Balsa):
0. **Franja de tecnologías** (arriba, bajo el menú): las herramientas y estándares reales del proyecto en Geist Mono 11px `#8a8380`, separados por cuadritos champaña de 4px (el mosaico del logo), entre dos líneas de 1px crema al 8 %. Se desplaza lento (48 s por vuelta), se pausa al pasar el cursor y se queda quieta con movimiento reducido. Bordes desvanecidos con máscara. Lista editable en `sitio.json` → `tecnologias`.
1. **Píldora:** fondo `#141312`, borde 1px crema al 16 %, radio 6px, Switzer 12px peso 500 crema y flecha champaña. Enlaza al repositorio.
2. **Titular:** Barlow Condensed 600 en mayúsculas, crema, sin punto final. Una línea en computador; en celular las palabras cortas se unen a la siguiente para que no queden sueltas.
3. **Bajada:** Switzer 14px, crema al 70 %, máximo 46ch.
4. **Un solo ghost link** ("Conoce la propuesta →").
5. **Logo de partículas debajo**, como pieza central: `min(360px, 64vw, 34svh)`.

### Ghost Text Link
Texto de 12–14px en `#fff7dd` con flecha `→`. Sin subrayado ni botón. Al pasar el cursor cambia a `#c8ad86` y la flecha avanza 3px.

### Top Navigation Bar
Barra negra fija, 20px de padding vertical y 40px horizontal (16px en móvil). Izquierda: lockup de Mekvra. Derecha: enlaces de sección en Switzer 14px crema al 70 % (crema al 100 % en la sección activa) y un ghost link `Repositorio →`. Al hacer scroll aparece una línea inferior de 1px crema al 8 %.

### Card
Fondo `#000000`, borde de 1px crema al 16 % (o champaña para destacar), radio 4px, padding 32px. Contiene: área de figura o ícono, título Switzer 16px peso 500, pill de categoría y descripción a 14px crema al 70 %. Al pasar el cursor, el borde sube a champaña al 60 % (150 ms).

### Category Tag Pill
Radio 100px, borde de 1px `#c8ad86`, sin relleno. Texto Switzer 10px peso 500, `#c8ad86`, tracking 0.18px. Padding 4px 10px. Variante de estado para entregables: `EN DESARROLLO` en `#66635f` y `COMPLETADO` en `#a0ca92`.

### Section Header
Número de sección en Geist Mono champaña + título Switzer 44px crema, alineado a la izquierda, con un párrafo de introducción de 16px crema al 70 %, ancho máximo 60ch.

## Do's and Don'ts

### Do
- Usar `#fff7dd` para todo el texto principal y los bordes finos sobre negro, y `#8a8380` para el texto secundario.
- En pantallas táctiles, todo control (enlace, pestaña, botón) mide al menos 44 px de alto.
- Ningún texto por debajo de 11 px, salvo las pills (10 px, peso 500).
- Reservar `#c8ad86` para el logo de partículas, tags, títulos de acento, bordes decorativos y la serie principal de las gráficas.
- Usar `#a0ca92` y `#ee6018` **solo dentro de gráficas, indicadores y estados**: son colores de dato, no de interfaz.
- Aplicar tracking negativo a Switzer en tamaños ≥ 16px.
- Usar Geist Mono en mayúsculas para cualquier etiqueta de instrumento, unidad o tag de equipo.
- Mantener radios de 4px en tarjetas y botones, 6px en el dashboard y 100px solo en pills.
- Separar con bordes de 1px, nunca con sombras.
- Limitar el movimiento a los cuatro lugares con significado: logo de partículas, celda robótica, datos en vivo y entrada al hacer scroll.
- Etiquetar como `SIMULACIÓN` o `VALORES ILUSTRATIVOS` cualquier número que todavía no sea un resultado del proyecto.

### Don't
- No usar sombras, brillos (glow) ni desenfoques para dar elevación.
- No introducir más colores: ni azules, ni morados, ni degradados.
- No usar blanco puro `#ffffff` para texto.
- No rellenar tarjetas ni secciones con color de fondo: todo va sobre el negro.
- No usar radios de 12px o más en rectángulos.
- No inventar animaciones nuevas por componente: toda entrada usa la misma animación de scroll (una sola gramática de movimiento).
- No usar el verde o el naranja en botones, títulos ni fondos.
- No presentar valores inventados como si fueran resultados.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 0 | Canvas | `#000000` | Fondo de página completo |
| 1 | Card | `#000000` | Tarjetas: igual al lienzo, definidas solo por borde de 1px |
| 2 | Instrument | `#141312` | Marco del dashboard, barra de ventana, paneles de gráficas |
| 3 | Muted | `#66635f` | Variaciones apagadas, barras "antes" en comparaciones |

## Elevation

La elevación se logra con bordes finos y contraste de valor, nunca con sombras. Las tarjetas están sobre el mismo negro y se separan solo por bordes de 1px. El dashboard es la única superficie que sube un paso (`#141312`), como una pantalla de instrumento incrustada en el monolito.

## Imagery

Nada de fotografía de stock. La imagen de la marca son sus propias máquinas y datos:
- El **logo de partículas** como artefacto de marca.
- La **celda robótica** en dibujo lineal como demostración de automatización.
- **Gráficas e instrumentos** (dashboards, trazas, diagramas ISA-95/ISA-88) como evidencia técnica.
- Los diagramas del equipo (P&ID, layout, VSM, Grafcet) se muestran dentro de marcos de 1px crema al 16 % sobre negro. Si el diagrama tiene fondo blanco, va dentro de un Dashboard Frame con su barra de título.

## Layout

Lienzo negro a sangre con zonas de contenido centradas de 1200px máximo.
1. **Hero:** píldora, titular condensado, bajada breve y un ghost link; debajo, el logo de partículas. Todo en la primera pantalla.
2. **Automatización:** a pantalla dividida, la celda robótica a la izquierda y un Dashboard Frame con métricas en vivo a la derecha.
3. **Secciones del proyecto:** encabezado numerado a la izquierda y contenido en retícula de 3 columnas de tarjetas, o pestañas de instrumento cuando hay variantes (líneas, niveles ISA-95).
4. **Gráficas:** siempre dentro de Dashboard Frames, a ancho completo o en retícula de 2.
5. **Cierre:** propuesta de valor centrada, equipo y enlaces.

En móvil todo pasa a una columna, el logo baja a ~260px de ancho y la celda robótica queda sobre el dashboard.

## Motion

| Elemento | Movimiento | Duración | Curva |
|---|---|---|---|
| Logo de partículas | Ensamble y cambio de figura | 900–1400 ms por transición, 3 s en reposo | ease-out exponencial |
| Brazo robot | Ciclo pick & place continuo | ~4 s por ciclo | ease-in-out entre poses |
| Minigráficas / series | Dibujo inicial; luego avance en vivo cada 1–2 s | 600 ms | ease-out |
| Pestañas | Subrayado deslizante + fundido del contenido | 250 ms / 150 ms | ease-out |
| Entrada al hacer scroll | Sube 28px, de desenfoque 6px a nítido, opacidad 0 → 1; en cascada de 70 ms entre hermanos (máx. 6) | 800–1000 ms | ease-out exponencial |
| Entrada de paneles (dashboard, celda, tronco común) | Igual, pero sube 40px desde escala 0,975, como un monitor que se enciende | 1000 ms | ease-out exponencial |
| Hover de enlaces y tarjetas | Color y borde | 150 ms | `cubic-bezier(0.4, 0, 0.2, 1)` |

Todo movimiento continuo se pausa cuando sale de la pantalla y se congela con `prefers-reduced-motion`.

## Similar Brands

- **Atoms**: el lienzo obsidiana, la tipografía crema y el acento champaña.
- **Factory**: los dashboards de instrumento, las métricas con minigráfica y la voz monoespaciada.
- **Aaru**: el campo de partículas como marca viva.
- **Figure AI / Physical Intelligence**: robótica física presentada con sobriedad premium.

## Quick Start

### CSS Custom Properties

```css
:root {
  /* Colors */
  --color-champagne-gold: #c8ad86;
  --color-candlelight-cream: #fff7dd;
  --color-obsidian-black: #000000;
  --color-ember-ash: #66635f;
  --color-carbon-lift: #141312;
  --color-ash-stroke: #2b2926;
  --color-metric-green: #a0ca92;
  --color-signal-orange: #ee6018;

  /* Typography — Font Families */
  --font-switzer: 'Switzer', 'General Sans', ui-sans-serif, system-ui, sans-serif;
  --font-geist-mono: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  /* Typography — Scale */
  --text-caption: 10px;
  --text-label: 11px;
  --text-body: 14px;
  --text-body-lg: 16px;
  --text-subheading: 20px;
  --text-metric: 28px;
  --text-heading: 44px;
  --text-display: 64px;
  --tracking-heading: -1.85px;
  --tracking-display: -2.7px;

  /* Spacing */
  --spacing-4: 4px;
  --spacing-8: 8px;
  --spacing-10: 10px;
  --spacing-16: 16px;
  --spacing-20: 20px;
  --spacing-24: 24px;
  --spacing-32: 32px;
  --spacing-40: 40px;
  --spacing-56: 56px;
  --spacing-80: 80px;
  --spacing-120: 120px;

  /* Layout */
  --page-max-width: 1200px;
  --section-gap: 120px;
  --card-padding: 32px;

  /* Border Radius */
  --radius-md: 4px;
  --radius-frame: 6px;
  --radius-full: 100px;

  /* Surfaces */
  --surface-canvas: #000000;
  --surface-card: #000000;
  --surface-instrument: #141312;
  --surface-muted: #66635f;

  /* Motion */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-switch: cubic-bezier(0.4, 0, 0.2, 1);
}
```
