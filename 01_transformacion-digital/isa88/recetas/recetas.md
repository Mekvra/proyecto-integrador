# Recetas y lotes ISA-88

La receta responde **¿qué producto fabrico y bajo qué especificaciones?** Los equipos (modelo físico) definen lo que la planta puede hacer, el procedimiento organiza las acciones y la receta fija los valores para una referencia concreta.

Todos los rangos vienen de la investigación del Integrante 3 ([`08_investigacion`](../../../08_investigacion)). Dentro de cada rango se fijó un valor de consigna por referencia. Los valores marcados **(S)** son supuestos.

## Tipos de receta y dónde vive cada una

| Tipo ISA-88 | Contenido | Dónde vive (ISA-95) | Quién la mantiene |
|---|---|---|---|
| General | Proceso y fórmula sin equipo (el modelo de proceso) | Corporativo / I+D | Integrante 3 (investigación) |
| De sitio | General adaptada a la materia prima y normas locales (leche de la Sabana, Res. 2310 / Codex) | Nivel 4 · ERP | Calidad |
| **Maestra** | Fórmula + procedimiento + clases de unidad para una referencia | Nivel 3 · MES / gestor de lotes | Ingeniería de proceso |
| **De control** | Copia de la maestra para **un lote**: cantidades escaladas, unidades asignadas, código de lote | Nivel 3 → Nivel 2 · PLC | Se genera automáticamente con la orden de producción |

Cada receta maestra tiene cuatro partes: **encabezado** (código, versión, producto), **fórmula** (ingredientes y parámetros), **requerimientos de equipo** (clases de unidad) y **procedimiento** (ver [`modelo-procedimental`](../modelo-procedimental/modelo-procedimental.md)).

## Línea de yogur (detallada)

### Encabezado

| | Y1 | Y2 | Y3 |
|---|---|---|---|
| Código | RM-YOG-FRE-150 | RM-YOG-BEB-1000 | RM-YOG-FIR-1000 |
| Producto | Yogur batido semidescremado con fresa | Yogur bebible descremado natural endulzado | Yogur natural firme entero |
| Rol | **Referencia principal** | Secundaria | Secundaria |
| Procedimiento | PROC-YOG-BATIDO | PROC-YOG-BATIDO (sin fruta) | PROC-YOG-FIRME |
| Tamaño de lote | 5.000 L de base (≈ 5.200 kg) | 5.000 L de base (≈ 5.200 kg) | 2.500 L de base (≈ 2.600 kg) (S) |

### Fórmula · ingredientes por lote

| Ingrediente | Y1 | Y2 | Y3 |
|---|---|---|---|
| Leche estandarizada | 4.680 kg al 1,8 % MG | 4.836 kg al 0,1 % MG | 2.522 kg al 3,2 % MG |
| Leche en polvo descremada | 104 kg (2 %) | 52 kg (1 %) | 78 kg (3 %) |
| Azúcar | 416 kg (8 %) | 312 kg (6 %) | — |
| Cultivo DVI (*L. bulgaricus* + *S. thermophilus*) | 1,56 kg (0,03 %) | 1,56 kg (0,03 %) | 0,78 kg (0,03 %) |
| Preparado de fresa (45 °Bx) | 709 kg (12 % del producto final) | — | — |
| **Producto final** | ≈ 5.909 kg | ≈ 5.200 kg | ≈ 2.600 kg |

### Fórmula · parámetros de proceso

| Fase | Parámetro | Y1 | Y2 | Y3 | Rango (investigación) |
|---|---|---|---|---|---|
| Formulación | T de mezcla | 50 °C | 50 °C | 55 °C | 45–60 °C |
| | SNG objetivo | 12 % | 11 % | 13 % | 11–14 % |
| | Grados Brix | 14 °Bx | 12 °Bx | — | 12–18 °Bx |
| `TRATAR_BASE` | P etapa 1 / etapa 2 | 180 / 40 bar | 200 / 40 bar | 200 / 50 bar | 150–200 / 30–50 bar |
| | T homogeneización | 65 °C | 65 °C | 65 °C | 55–70 °C |
| | Tratamiento térmico | 95 °C · 30 s | 95 °C · 30 s | 85 °C · 5 min | 85 °C · 5 min o 95 °C · 15–30 s |
| | T salida (inoculación) | 43 °C | 43 °C | 43 °C | 42–45 °C |
| `DOSIFICAR_CULTIVO` + `AGITAR` | Dispersión | 12 min | 12 min | 12 min | 10–15 min |
| `INCUBAR` | Unidad | Fermentador | Fermentador | **Cámara U-350 (en envase)** | — |
| | T incubación | 43 °C | 43 °C | 43 °C | 42–43 °C |
| | pH de corte | 4,6 | 4,5 | 4,6 | 4,5–4,6 |
| | Acidez al corte | 75 °D | 80 °D | 75 °D | 70–85 °D |
| | t mínimo / t máximo | 4 h / 7 h | 4 h / 7 h | 4 h / 7 h | 4–7 h |
| `ROMPER_COAGULO` | Agitación | 20 rpm · 15 min | 40 rpm · 20 min (S) | No aplica | 15–25 rpm |
| `ENFRIAR_LINEA` | T de salida | 20 °C | 12 °C | No aplica | 18–22 °C, luego < 10 °C |
| `DOSIFICAR_FRUTA` | % fruta / T preparado | 12 % / 18 °C | — | — | 8–15 % / 15–20 °C |
| Calidad en línea | Viscosidad | 2.000–2.500 cP | ≤ 800 cP (S) | Gel firme (no se mide en línea) | 1.500–3.000 cP (batido) |
| `LLENAR_SELLAR` | Envase | Vaso PP 150 g | Botella PEAD 1.000 g | Tarro PP 1.000 g | — |
| | Llenadora | U-340 | U-341 | U-341 (cambio de formato) | — |
| | T de llenado | 12 °C | 12 °C | **43 °C** | 10–15 °C (batido) |
| | Tolerancia de peso | ± 1 % | ± 1 % | ± 1 % | ± 1 % |
| | T de termosellado | 200 °C | 200 °C | 200 °C | 180–220 °C |
| | Unidades por lote | ≈ 38.600 | ≈ 5.100 | ≈ 2.550 | 2 % de pérdidas (S) |
| `ENFRIAR_PRODUCTO` | Objetivo | 2–4 °C en cámara | 2–4 °C en cámara | < 6 °C en ≤ 10 h (túnel U-351) | < 6 °C en 10–12 h |
| Liberación | pH comercial | 4,2–4,4 | 4,2–4,4 | 4,2–4,4 | 4,2–4,4 |
| | Vida útil | 30 días | 25 días | 21 días | 21–45 días |

## Línea de quesos (secundaria)

Lote: 5.000 L de leche pasteurizada por tina. Rendimiento: 7,5 L de leche por kg de queso (S) → ≈ 667 kg por lote.

| Parámetro | Q1 · Queso campesino 250 g | Q2 · Cuajada 500 g | Q3 · Queso fresco bloque 2.100 g | Rango (investigación) |
|---|---|---|---|---|
| Código | RM-QUE-CAM-250 | RM-QUE-CUA-500 | RM-QUE-BLQ-2100 | — |
| T de coagulación | 34 °C | 32 °C | 35 °C | 32–36 °C |
| pH antes de cuajar | 6,45 | 6,5 | 6,4 | 6,4–6,5 |
| Cuajo (por lote) | 2 mL/10 L → 1.000 mL | 1,5 mL/10 L → 750 mL | 3 mL/10 L → 1.500 mL | 1–3 mL/10 L |
| CaCl₂ (por lote) | 15 g/100 L → 750 g | 10 g/100 L → 500 g | 20 g/100 L → 1.000 g | 10–20 g/100 L |
| Tiempo de coagulación | 40 min | 45 min | 30 min | 30–45 min |
| Tamaño de grano | 1,5 cm | 2 cm | 1 cm | 1–2 cm |
| Agitación | 20 rpm · 15 min · 36 °C | 15 rpm · 10 min · 35 °C | 30 rpm · 20 min · 38 °C | 15–30 rpm · 10–20 min · 35–38 °C |
| Desuerado | 40 % | 30 % | 50 % | 30–50 % |
| Salado | Salmuera 20 °Bé · 11 °C · 45 min | En masa, 1,5 % sobre cuajada | En masa, 2 % sobre cuajada | Salmuera 18–22 °Bé o en masa 1,5–2 % |
| Prensado | 1,0 bar · 30 min · 2 volteos | Sin prensado (gravedad 60 min) | 1,5 bar · 60 min · 3 volteos | 0,5–1,5 bar · 15–60 min |
| Empaque | Vacío | Bandeja con atmósfera modificada | Vacío | Vacío o MAP · sellado 130–160 °C |
| Humedad objetivo | 58 % | 64 % | 52 % | 50–65 % |
| Unidades por lote | ≈ 2.600 | ≈ 1.300 | ≈ 310 | — |

## Línea de kéfir (secundaria)

Lote: 5.000 L de base. Cultivo DVI. Los pasos 1–3 del kéfir (preparación de la base) no están en la investigación: se asume la misma preparación que el yogur en U-107 **(S)**.

| Parámetro | K1 · Kéfir natural entero 1 L | K2 · Kéfir con fresa 250 mL | K3 · Kéfir descremado natural 1 L | Rango (investigación) |
|---|---|---|---|---|
| Código | RM-KEF-NAT-1000 | RM-KEF-FRE-250 | RM-KEF-DES-1000 | — |
| % MG de la leche | 3,0 % | 1,5 % | ≤ 0,5 % | — |
| Tratamiento de base | 95 °C · 30 s (S) | 95 °C · 30 s (S) | 95 °C · 30 s (S) | No investigado |
| T de inoculación | 23 °C | 22 °C | 25 °C | 22–25 °C |
| Dosis DVI | 0,02 % (S) | 0,02 % (S) | 0,02 % (S) | Según fabricante |
| T de fermentación | 23 °C | 22 °C | 25 °C | 20–25 °C |
| pH de corte / t máximo | 4,4 / 24 h | 4,4 / 24 h | 4,5 / 20 h | 4,3–4,5 / 18–24 h |
| Acidez al corte | 90 °D | 90 °D | 85 °D | 80–100 °D |
| Maduración en frío | 9 °C · 16 h | 9 °C · 12 h | **No madura** | 8–10 °C · 12–24 h |
| Alcohol final | 0,3 % v/v | 0,3 % v/v | 0,1–0,2 % v/v | 0,2–0,5 % v/v |
| Fruta | — | 10 % preparado de fresa a 15 °C (S) | — | — |
| T de envasado | 6 °C | 6 °C | 6 °C | 4–8 °C |
| Espacio de cabeza | 8 % | 8 % | 8 % | 5–10 % |
| Envase | Botella 1.000 mL | Botella 250 mL | Botella 1.000 mL | — |
| Unidades por lote | ≈ 4.900 | ≈ 21.800 | ≈ 4.900 | 2 % de pérdidas (S) |
| Vida útil | 25 días | 25 días | 20 días | 20–30 días |

## Verificación: diferenciación no trivial (criterios del enunciado)

| Criterio del enunciado | Yogur | Quesos | Kéfir |
|---|---|---|---|
| Ingredientes y formulaciones | % MG, polvo, azúcar, fruta | Cuajo, CaCl₂, sal | % MG, fruta |
| Cantidades y dosificación | Tamaño de lote (5.000 vs 2.500 L), % fruta | Dosis de cuajo y sal | Dosis de fruta |
| Temperaturas y tiempos | 95 °C · 30 s vs 85 °C · 5 min | Coagulación 30–45 min | Con y sin maduración |
| Secuencias de operación | **Y3 fermenta en envase** | **Q1 salmuera, Q2 sin prensado** | **K3 omite la maduración** |
| Envase | Vaso 150 g, botella 1 kg, tarro 1 kg | 250 g, 500 g, 2.100 g | 250 mL, 1 L |
| Velocidades y capacidades | U-340 (12.000/h) vs U-341 (3.000/h) | Unidades por lote 2.600 vs 310 | 4.900 vs 21.800 botellas |
| Inspección y calidad | Viscosidad, % fruta, pH en cámara (Y3) | Humedad, sal | pH, alcohol, CO₂ |
| Interacción con robot | Cajas de vasos vs botellas vs tarros | Distintos patrones de estiba | Distintos patrones de estiba |

## Lotes y trazabilidad

### Identificación del lote

Formato: `L` + fecha `DDMMAA` + consecutivo del día `NN`, igual al usado en el curso (ej. `L230926-03`). El código de referencia va en el registro de lote.

Ejemplo: `L280926-03` = tercer lote del 28 de septiembre de 2026.

### Receta de control (ejemplo de un lote de Y1)

| Campo | Valor | Origen |
|---|---|---|
| Orden de producción | OP-2026-0917 | ERP (nivel 4) |
| Receta maestra | RM-YOG-FRE-150 v1.0 | MES |
| Lote | L280926-03 | MES |
| Cantidad programada | 38.600 vasos | ERP → MES |
| Unidades asignadas | U-301 · U-107 · **U-312** · U-320 · U-330 · U-340 | MES (fermentador libre) |
| Lotes de insumos | Leche: silo U-106B, lote R270926-07 · Polvo: LP-1142 · Fruta: FF-0381 · Cultivo: DVI-5520 | MES (inventario) |
| Parámetros | Tabla Y1 de este documento | Receta maestra |

### Registro de lote (lo que sube del PLC al MES)

| Dato | Fase que lo reporta | Uso en MES / ERP |
|---|---|---|
| Masas reales de leche, polvo, azúcar, cultivo y fruta | `CARGAR_LECHE`, `DOSIFICAR_SOLIDOS`, `DOSIFICAR_CULTIVO`, `DOSIFICAR_FRUTA` | Consumo real vs. teórico → inventario en ERP |
| Curva de T en el tubo de retención y n.º de desvíos | `TRATAR_BASE` | Liberación de inocuidad (HACCP) |
| Curva de pH, hora de inicio y fin de incubación | `INCUBAR` | Tiempo de ciclo real, trazabilidad |
| Unidades buenas, rechazadas y causa | `LLENAR_SELLAR` | Calidad del OEE, cumplimiento de la orden |
| Paradas y estados HELD con su causa | Todas | Disponibilidad del OEE, análisis de paradas |
| Resultados de laboratorio (pH, acidez, microbiología) | Registro manual en MES | Liberación del lote |

Con este registro se puede reconstruir la historia completa de un lote ante un reclamo: materias primas, equipos, fecha y turno, parámetros, controles de calidad y cantidades.
