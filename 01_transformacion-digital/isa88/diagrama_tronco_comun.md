# Planta de derivados lácteos – Tronco común y ramas de producto (ISA-88)

**MEVKRA** · Proyecto Integrador APM 2026-2S

La planta arranca con un tronco común que produce lotes de leche base (LB), uno por silo. Luego se ramifica en tres líneas batch. Cada rama consume un lote LB de su silo, lo que encadena la trazabilidad desde la cisterna hasta el producto terminado.

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear", "nodeSpacing": 30, "rankSpacing": 40}, "themeVariables": {"fontFamily": "Arial", "fontSize": "15px", "primaryTextColor": "#000000", "lineColor": "#1F4E79", "clusterBkg": "#FFFFFF", "titleColor": "#000000"}}}%%
flowchart TB
    subgraph TRONCO["A1 · TRONCO COMÚN · Recepción y tratamiento de leche"]
        direction LR
        REC["U111 / U112<br/>Recepción e inspección"] --> CRU["U113 / U114<br/>Leche cruda ≤ 4 °C"]
        CRU --> SEP["U121<br/>Clarificación y<br/>estandarización"]
        SEP --> HTST["U122<br/>Pasteurización HTST<br/>72–75 °C · 15–20 s"]
        HTST --> S1["U123 · Silo S1<br/>LB yogur · MG 3,4 %"]
        HTST --> S2["U124 · Silo S2<br/>LB queso · MG 3,0–3,2 %"]
        HTST --> S3["U125 · Silo S3<br/>LB kéfir · MG 3,0 %"]
    end

    subgraph YOGUR["RAMA 1 · YOGUR DE FRESA"]
        direction TB
        Y1["U201 · Formulación<br/>polvos y azúcar · 55 °C"] --> Y2["U202 · Homogenización +<br/>tratamiento térmico 85 °C · 5 min"]
        Y2 --> Y3["U211–U213 · Fermentación<br/>42 °C hasta pH 4,6"]
        Y3 --> Y4["U214 · Enfriamiento +<br/>dosificación de fruta"]
        Y4 --> Y5["PC31 · Envasado<br/>150 g · 1000 g · 1750 g"]
    end

    subgraph QUESO["RAMA 2 · QUESO MOZZARELLA"]
        direction TB
        Q1["U221 · Coagulación y corte<br/>33–35 °C"] --> Q2["U222 · Acidificación<br/>de cuajada · pH 5,1–5,3"]
        Q2 --> Q3["U223 · Hilado<br/>agua 75–85 °C"]
        Q3 --> Q4["U224 · Enfriamiento<br/>y salmuera"]
        Q4 --> Q5["PC32 · Empaque<br/>250 g · 400 g · 1000 g"]
    end

    subgraph KEFIR["RAMA 3 · KÉFIR NATURAL"]
        direction TB
        K1["U202 · Homogenización +<br/>tratamiento térmico 90–95 °C<br/>(compartida con yogur)"] --> K2["U231–U233 · Fermentación<br/>22–25 °C hasta pH 4,5"]
        K2 --> K3["U234 · Maduración<br/>8–10 °C"]
        K3 --> K4["PC33 · Envasado<br/>240 g · 500 g · 1000 g"]
    end

    subgraph FIN["FIN DE LÍNEA Y SERVICIOS COMUNES"]
        direction LR
        PAL["U341 · Celda robotizada<br/>encajonado y paletizado"] --> CAM["A4 · Cámara fría 2–4 °C<br/>y despacho"]
        SERV["A9 · Servicios<br/>CIP · vapor · agua helada · aire"]
    end

    S1 --> Y1
    S2 --> Q1
    S3 --> K1
    Y5 --> PAL
    Q5 --> PAL
    K4 --> PAL

    classDef comun fill:#DDEBF7,stroke:#1F4E79,stroke-width:1.5px,color:#000;
    classDef yogur fill:#FFE699,stroke:#7F6000,stroke-width:1.5px,color:#000;
    classDef queso fill:#C6E0B4,stroke:#375623,stroke-width:1.5px,color:#000;
    classDef kefir fill:#D9C3E9,stroke:#5B3A7A,stroke-width:1.5px,color:#000;
    classDef serv fill:#F2F2F2,stroke:#7F7F7F,stroke-width:1px,stroke-dasharray:4 3,color:#000;

    class REC,CRU,SEP,HTST,PAL,CAM comun;
    class S1,Y1,Y2,Y3,Y4,Y5 yogur;
    class S2,Q1,Q2,Q3,Q4,Q5 queso;
    class S3,K1,K2,K3,K4 kefir;
    class SERV serv;

    style TRONCO fill:#F4F8FC,stroke:#1F4E79,stroke-width:2px,color:#000
    style YOGUR fill:#FFF8E1,stroke:#BF9000,stroke-width:2px,color:#000
    style QUESO fill:#EEF6E8,stroke:#548235,stroke-width:2px,color:#000
    style KEFIR fill:#F5EEFA,stroke:#7030A0,stroke-width:2px,color:#000
    style FIN fill:#F4F8FC,stroke:#1F4E79,stroke-width:2px,color:#000
```

| Color | Significado |
|---|---|
| Azul | Tronco común y fin de línea (recursos compartidos por las tres ramas) |
| Amarillo | Rama 1 · Yogur de fresa |
| Verde | Rama 2 · Queso mozzarella |
| Morado | Rama 3 · Kéfir natural |
| Gris punteado | Servicios auxiliares |

La unidad U202 aparece en las ramas de yogur y kéfir porque es un recurso compartido: se usa para un lote a la vez y cambia su receta (85 °C para yogur, 90–95 °C para kéfir).

Códigos ISA-88: A = área, PC = celda de proceso, U = unidad, LB = lote de leche base.
