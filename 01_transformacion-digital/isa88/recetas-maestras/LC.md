# Receta maestra LC · Leche con chocolate UHT

Receta maestra ISA-88 de la referencia LC, ligada a la celda PC23 y a sus unidades. Sale del [modelo físico](../modelo-fisico/modelo-fisico.md), el [modelo procedimental](../modelo-procedimental/modelo-procedimental.md) y las [recetas de la planta](../recetas/recetas.md).

![Diagrama de procedimiento LC](../diagramas/pfc_LC.svg)

## 1. Encabezado

| Campo | Valor |
|---|---|
| Código | LC |
| Producto | Leche con chocolate UHT |
| Denominación | Leche saborizada de larga vida, esterilizada UAT y envasada en aséptico |
| Línea · celda | Leche UHT · PC23 |
| Tamaño del lote | 10.000 L de leche estandarizada |
| Lotes por semana | 6 |
| Orden de producción | Última del día, por el cacao |
| Leche base | Silo U125A, grasa 3,0 % |
| Producto por lote | 10.250 kg (≈ 9.520 cajas de 1 L) |
| Presentaciones | Caja 1 L en bandejas de 12 · U331 |
| Vida útil | 6 meses sin frío, sin abrir |

## 2. Fórmula por lote

| Materia prima o corriente | Cantidad |
|---|---|
| Leche pasteurizada (U125A) al 3,0 % | 9.210 L |
| Azúcar | 620 kg (6,0 %) |
| Cacao en polvo alcalinizado | 125 kg (1,2 %) |
| Carragenina kappa | 2,6 kg (0,025 %) |
| **Producto** | **10.250 kg (≈ 9.520 cajas de 1 L)** |

## 3. Requerimientos de equipo

U231 con la báscula WI-2312, la tolva y el mezclador EM-2313; U232, U233, U331, U413.

## 4. Procedimiento

Procedimientos de unidad en orden, con sus fases y los valores de esta receta. Antes del primero, el tronco común entrega un lote de leche base liberado (UP-LB1 recepción, UP-LB2 pasteurización a 75 °C por 15 s y UP-LB3 almacenamiento en U125A).

| Procedimiento de unidad | Unidad | Fase | Valor de receta | PCC |
|---|---|---|---|---|
| UP-L1 Mezcla | U231 | Cargar y calentar la leche | 9.210 L desde U125A a 60 a 65 °C |  |
|  |  | Premezclar en seco | carragenina con azúcar, 1 a 10 |  |
|  |  | Incorporar sólidos por la tolva | azúcar 620 kg, cacao 125 kg, carragenina 2,6 kg (WI-2312) |  |
|  |  | Mezclar | 20 min con recirculación (EM-2313) |  |
| UP-L2 Tratamiento UHT | U232 | Precalentar y desairear | regeneración y desaireador |  |
|  |  | Esterilizar | 137 °C por 4 s; desvío y recirculación si baja | PCC-8 |
|  |  | Homogeneizar en aséptico | 200/50 bar a unos 70 °C |  |
|  |  | Enfriar | 20 a 25 °C |  |
| UP-L3 Almacenamiento estéril | U233 | Guardar en estéril | presión positiva con aire estéril filtrado |  |
| UP-L4 Envasado aséptico | U331 | Esterilizar el envase | baño de H₂O₂ y secado con aire estéril caliente | PCC-9 |
|  |  | Llenar y sellar | caja de 1 L con tapa |  |
| UP-L5 Retención y liberación | U413 | Muestrear | cajas del inicio, del medio y del final |  |
|  |  | Incubar y probar | 30 a 35 °C por 7 días; ATP a las 24 a 48 h |  |
|  |  | Liberar | esterilidad comercial (NTC 4433) |  |
| UP-L6 Limpieza intermedia | U232 · U233 | Lavar la planta UHT | CIP intermedio de 30 min antes de volver a leche entera |  |

## 5. Especificación del producto terminado

- Grasa ≈ 2,7 % (≥ 2,5 %)
- Sólidos lácteos no grasos 7,7 a 8,0 %
- Acidez 0,12 a 0,16 %
- Esterilidad comercial (NTC 4433)
- Peróxido residual ≤ 0,5 ppm; carragenina lejos del máximo de 5 g/kg
- Vida útil: 6 meses sin frío, sin abrir

## 6. Puntos críticos de control

| Código | Control |
|---|---|
| PCC-1 | Antibióticos en cada cisterna (recepción) |
| PCC-2 | Pasteurización de la leche a 75 °C por 15 s |
| PCC-8 | Esterilización UHT a 137 °C por 4 s |
| PCC-9 | Esterilización del envase con H₂O₂ (envasado aséptico) |

Valores de diseño del proyecto; no son mediciones de planta.
