# ISA-88 · Producción por lotes

Modelo ISA-88 de la planta láctea de **Lácteos Altos de Teusacá**.

**Responsables:** Luis Alberto Mendoza (líder de automatización) y Janan Libardo Carreño (líder de instrumentación y software).
**Línea desarrollada en detalle:** yogurts (fresa, natural y griego). Quesos y leche UHT se modelan con el mismo método y con el detalle necesario para la planta completa.

## Documentos

| Documento | Pregunta que responde | Contenido |
|---|---|---|
| [`modelo-fisico/modelo-fisico.md`](modelo-fisico/modelo-fisico.md) | ¿Con qué produzco? | Empresa, sitio, áreas, celdas de proceso, unidades con su capacidad, módulos de equipo y módulos de control (tags de los P&ID) |
| [`modelo-procedimental/modelo-procedimental.md`](modelo-procedimental/modelo-procedimental.md) | ¿Qué acciones ejecuto? | Modelo de proceso, procedimientos de las tres líneas y del tronco común, operaciones y fases con sus parámetros, estados y modos, recursos compartidos |
| [`Recetas_y_procesos_planta.pdf`](Recetas_y_procesos_planta.pdf) | ¿Qué producto fabrico y con qué especificación? | Fórmulas, procedimientos, parámetros, PCC y equipos de los nueve productos de las tres líneas |
| [`recetas-maestras/`](recetas-maestras) | ¿Cómo se hace cada uno de los nueve productos? | Una receta maestra completa por referencia (encabezado, fórmula, equipos, procedimiento con fases y valores, especificación y PCC), cada una con su diagrama de procedimiento |
| [`diagrama_tronco_comun.md`](diagrama_tronco_comun.md) | ¿Cómo se conectan las líneas? | Tronco común y las tres ramas de producto con sus unidades |

## Cómo encajan las piezas

```mermaid
flowchart TD
    MP["Modelo de proceso<br/>qué le pasa al producto"] --> RG["Receta general<br/>sin equipos"]
    RG --> RS["Receta de sitio<br/>normativa colombiana"]
    RS --> RM["Receta maestra<br/>una por referencia"]
    MF["Modelo físico<br/>unidades y módulos"] --> RM
    PR["Modelo procedimental<br/>procedimientos y fases"] --> RM
    RM --> RC["Receta de control<br/>un lote concreto"]
    RC --> EJ["Ejecución del lote<br/>hoy: orden impresa y operador"]
    EJ --> RL["Registro de lote<br/>hoy: planillas y Excel"]
```

En la empresa base la receta de control es una **orden de lote impresa** y su ejecución depende del operador y de los controladores locales de cada equipo. Pasar esa cadena a un MES y a fases ejecutadas por PLC es parte de la propuesta de automatización.

## Bases de diseño

| Dato | Valor |
|---|---|
| Leche recibida | 150.000 L/día (acta del 9 de octubre de 2026) |
| Días de producción | 6 por semana |
| Tamaño de lote | 10.000 L de leche estandarizada en las tres líneas |
| Lotes por semana | 91: 35 de yogurts, 30 de quesos y 26 de leche UHT |
| Leche por línea | Yogurts ≈ 58.300 L/día · quesos 50.000 L/día · leche UHT ≈ 43.300 L/día |
| Referencias | 9: tres por línea |
| Ampliación prevista | Contrato a un año para recibir 30.000 L/día más, destinados a yogurts o quesos |

Los litros por día salen de los lotes por semana divididos entre 6 días. Por ejemplo, en yogurts 35 × 10.000 L ÷ 6 ≈ 58.300 L/día. La suma de las tres líneas da ≈ 151.700 L/día; la diferencia de 1,1 % con los 150.000 L/día se acepta como variación normal del acopio.

Todas las cantidades son **valores de diseño** del grupo, tomados de la normativa colombiana, el Codex y la bibliografía técnica (Tetra Pak). La empresa es un caso de estudio y ninguna cifra es una medición de planta.

## Norma de referencia

ANSI/ISA-88.00.01 (IEC 61512-1), *Batch Control Part 1: Models and Terminology*. Los símbolos y las letras de los instrumentos siguen ANSI/ISA-5.1.
