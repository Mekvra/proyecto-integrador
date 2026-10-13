# Receta maestra QD · Doble crema

Receta maestra ISA-88 de la referencia QD, ligada a la celda PC22 y a sus unidades. Sale del [modelo físico](../modelo-fisico/modelo-fisico.md), el [modelo procedimental](../modelo-procedimental/modelo-procedimental.md) y las [recetas de la planta](../recetas/recetas.md).

![Diagrama de procedimiento QD](../diagramas/pfc_QD.svg)

## 1. Encabezado

| Campo | Valor |
|---|---|
| Código | QD |
| Producto | Doble crema |
| Denominación | Queso de pasta hilada con más grasa y humedad, semiduro graso |
| Línea · celda | Quesos · PC22 |
| Tamaño del lote | 10.000 L de leche estandarizada |
| Lotes por semana | 10 |
| Orden de producción | Último del día |
| Leche base | Silo U124A/B, grasa 3,6 % + crema (mezcla al 4,2 %) |
| Producto por lote | ≈ 1.330 kg (≈ 7,5 L de leche por kg) |
| Presentaciones | Bloque 500 g · U321 · Bloque 2,5 kg · U321 |
| Vida útil | 30 días al vacío a 2 a 4 °C |

## 2. Fórmula por lote

| Materia prima o corriente | Cantidad |
|---|---|
| Leche pasteurizada (U124A/B) al 3,6 % | 9.840 L |
| Crema pasteurizada al 40 % (U127) | 160 L |
| Cloruro de calcio al 40 % | 5 L |
| Cultivo mesófilo | 100 U |
| Cuajo de quimosina | 2,2 L |
| Sal | 1,2 % en la hiladora, sin salmuera |
| Suero dulce que sale a U905 | ≈ 8.700 kg |
| **Producto** | **≈ 1.330 kg (≈ 7,5 L de leche por kg)** |

## 3. Requerimientos de equipo

E-2210, U127 con el contador FQI-2212, una tina U221A/B/C, U222, U223 con WI-2232, U224, U321, U414.

## 4. Procedimiento

Procedimientos de unidad en orden, con sus fases y los valores de esta receta. Antes del primero, el tronco común entrega un lote de leche base liberado (UP-LB1 recepción, UP-LB2 pasteurización a 75 °C por 15 s y UP-LB3 almacenamiento en U124A/B).

| Procedimiento de unidad | Unidad | Fase | Valor de receta | PCC |
|---|---|---|---|---|
| UP-Q1 Tina | U221A · U221B · U221C | Agregar la crema al llenar | 160 L al 40 % por FQI-2212; solo crema liberada | PCC-3 |
|  |  | Llenar y atemperar | leche al 3,6 % a 32 a 35 °C en E-2210 |  |
|  |  | Madurar | CaCl₂ 5 L + cultivo mesófilo 100 U; 20 a 30 min, agitación lenta |  |
|  |  | Coagular | cuajo 2,2 L; reposo 30 a 40 min hasta corte limpio |  |
|  |  | Cortar | cubos de 1 a 1,5 cm; reposo de 5 min |  |
|  |  | Cocinar y desuerar | en el límite inferior (≈ 40 °C) para retener humedad; retirar el 85 % del suero |  |
| UP-Q2 Acidificación | U222 | Acidificar la cuajada | 35 a 38 °C hasta pH 5,2 a 5,3; prueba de estiramiento |  |
| UP-Q3 Hilado y moldeo | U223 | Hilar | agua de hilado a 75 a 85 °C; pasta a 58 a 62 °C |  |
|  |  | Salar en la hiladora | sal al 1,2 % (báscula WI-2232) |  |
|  |  | Moldear | bloques de 500 g y 2,5 kg |  |
| UP-Q4 Enfriamiento y salado | U224 | Enfriar | canal de agua a 4 a 10 °C |  |
| UP-Q5 Empaque | U321 | Detectar metales | antes de la empacadora | PCC-7 |
|  |  | Empacar al vacío y sellar | etiqueta con lote, fecha y vencimiento |  |
| UP-Q6 Cámara | U414 | Conservar | 2 a 4 °C, reposo de 12 h; camión de 2 a 6 °C |  |

## 5. Especificación del producto terminado

- Humedad 50 a 55 %
- Grasa en extracto seco ≥ 45 % (diseño ≈ 58 %)
- pH 5,1 a 5,4
- Semiduro graso
- Vida útil: 30 días al vacío a 2 a 4 °C

## 6. Puntos críticos de control

| Código | Control |
|---|---|
| PCC-1 | Antibióticos en cada cisterna (recepción) |
| PCC-2 | Pasteurización de la leche a 75 °C por 15 s |
| PCC-3 | Pasteurización de la crema a 85 °C por 15 s |
| PCC-7 | Detector de metales antes de la empacadora de quesos |

Valores de diseño del proyecto; no son mediciones de planta.
