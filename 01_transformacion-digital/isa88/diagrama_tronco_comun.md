# Tronco común y líneas de producto (ISA-88)

La planta arranca con un **tronco común** que recibe los 150.000 L/día de leche, la estandariza y la pasteuriza en continuo, y la deja en silos separados por línea. Cada línea toma un lote de leche base liberado de su silo, así que la trazabilidad queda encadenada desde la cisterna hasta el producto terminado.

```mermaid
flowchart TB
    subgraph A1["A1 · Tronco común"]
        direction LR
        REC["U111 / U112<br/>Recepción e inspección<br/>PCC-1 antibióticos"] --> CRU["U113 / U114<br/>Leche cruda<br/>4 °C o menos, máx. 24 h"]
        CRU --> SEP["U121<br/>Clarificación y<br/>estandarización"]
        SEP --> HTST["U122<br/>Pasteurización HTST<br/>75 °C por 15 s · PCC-2"]
        SEP -.->|"crema al 40 %"| CR["U126 → U127<br/>Crema pasteurizada<br/>85 °C por 15 s · PCC-3"]
        HTST --> SY["U123A/B · U123C<br/>Silos de yogures"]
        HTST --> SQ["U124A/B<br/>Silos de quesos"]
        HTST --> SL["U125A/B<br/>Silos de leche UHT"]
    end

    subgraph Y["PC21 · Yogures · 35 lotes/semana"]
        direction TB
        Y1["U201 Formulación"] --> Y2["U202 Tratamiento<br/>92 °C por 5 min · PCC-4"]
        Y2 --> Y3["U211 a U218<br/>Fermentación a 43 °C"]
        Y3 --> Y4["U215 Ruptura y enfriamiento<br/>U214A/B Pulmones<br/>EM-2141 Fruta · PCC-6"]
        Y3 --> Y5["U216 Separación del griego<br/>U217A/B Pulmones"]
        Y4 --> Y6["U311 · U312 · U313<br/>Envasado · PCC-5"]
        Y5 --> Y6
    end

    subgraph Q["PC22 · Quesos · 30 lotes/semana"]
        direction TB
        Q1["U221A/B/C Tinas<br/>coagular, cortar, cocer"] --> Q2["U222 Acidificación"]
        Q2 --> Q3["U223 Hilado"]
        Q3 --> Q4["U224 Enfriamiento y salmuera"]
        Q4 --> Q5["U321 Empaque al vacío<br/>PCC-7"]
    end

    subgraph L["PC23 · Leche UHT · 26 lotes/semana"]
        direction TB
        L1["U231 Mezcla"] --> L2["U232 Planta UHT<br/>137 °C por 4 s · PCC-8"]
        L2 --> L3["U233 Tanque aséptico"]
        L3 --> L4["U331 Envasado aséptico<br/>PCC-9"]
    end

    subgraph FIN["Fin de línea, almacenamiento y servicios"]
        direction LR
        PAL["U341 Paletizado manual<br/>U342 Envolvedora"] --> FRIO["U411 Cámara de yogures<br/>U414 Cámara de quesos<br/>U413 Bodega UHT"]
        FRIO --> DES["U412 Despacho"]
        SERV["U901 CIP · U905 Suero<br/>vapor · frío · aire · agua"]
    end

    SY --> Y1
    SQ --> Q1
    SL --> L1
    CR -.->|griego| Y5
    CR -.->|"doble crema"| Q1
    Y6 --> PAL
    Q5 --> PAL
    L4 --> PAL
```

| Línea | Productos | Silos | Leche por día |
|---|---|---|---|
| Yogures | Fresa, natural y griego | U123A/B (3,50 %) y U123C (0,05 % o menos) | ≈ 58.300 L |
| Quesos | Mozzarella, quesillo y doble crema | U124A/B (3,0, 3,2 o 3,6 %) | 50.000 L |
| Leche UHT | Entera, descremada y con chocolate | U125A (3,0 %) y U125B (0,3 %) | ≈ 43.300 L |

Los silos A y B de cada línea trabajan en alternancia: uno se llena con la grasa del siguiente producto mientras el otro alimenta la línea. Códigos ISA-88: A = área, PC = celda de proceso, U = unidad, EM = módulo de equipo. El detalle de cada nivel está en el [modelo físico](modelo-fisico/modelo-fisico.md).
