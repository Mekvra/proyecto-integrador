---
nombre: Yogurts
orden: 1
detallada: true
resumen: La línea que desarrollamos en detalle. Yogurt con fresa, natural y griego en lotes de 10.000 L; hoy procesa ≈ 57.600 L/día porque la llenadora de vasos está al límite.
productos:
  - codigo: YF
    nombre: Yogurt con fresa
    descripcion: Yogurt batido con azúcar y preparado de fresa en trozos, que se mezcla en línea al 13 % después de fermentar.
    datos:
      - { k: Lotes por semana, v: "13" }
      - { k: Fermentación, v: "43 °C hasta pH 4,50 · 5,25 h" }
      - { k: Producto por lote, v: "≈ 13.100 kg" }
      - { k: Grasa · proteína, v: "2,8 % · 3,6 %" }
    presentaciones:
      - "Vaso 150 g · U311"
      - "Botella 1.000 g · U312"
      - "Botella 1.750 g · U312"
  - codigo: YN
    nombre: Yogurt natural
    descripcion: Yogurt batido sin azúcar ni fruta. Abre la semana de producción para no arrastrar azúcar ni fruta a los demás lotes.
    datos:
      - { k: Lotes por semana, v: "13" }
      - { k: Fermentación, v: "43 °C hasta pH 4,50 · 5,0 h" }
      - { k: Producto por lote, v: "≈ 10.700 kg" }
      - { k: Grasa · proteína, v: "3,4 % · 4,1 %" }
    presentaciones:
      - "Vaso 200 g · U311"
      - "Botella 1.000 g · U312"
  - codigo: YG
    nombre: Yogurt griego
    descripcion: Yogurt colado en el separador U216, que retira el suero ácido para concentrar la proteína; se usan ≈ 3,2 kg de leche por kg.
    datos:
      - { k: Lotes por semana, v: "9" }
      - { k: Fermentación, v: "43 °C hasta pH 4,55 · 5,5 h" }
      - { k: Producto por lote, v: "≈ 3.240 kg" }
      - { k: Grasa · proteína, v: "2,0 % · 9,2 %" }
    presentaciones:
      - "Vaso 150 g · U313"
      - "Pote 500 g · U313"
etapas:
  - nombre: Formulación
    tipo: Batch
    variables:
      - "U201 de 12.000 L con tolva de polvos"
      - "Leche entera + leche en polvo (+ azúcar en fresa)"
  - nombre: Tratamiento de la base
    tipo: Continuo
    variables:
      - "Homogeneización y 92 °C × 5 min (PCC-4)"
      - "U202 a 10 m³/h"
  - nombre: Fermentación
    tipo: Batch
    variables:
      - "4 fermentadores de 12.000 L"
      - "43 °C hasta pH 4,50 (5,0–5,5 h)"
  - nombre: Acondicionamiento
    tipo: Batch · Continuo
    variables:
      - "Ruptura y enfriamiento a 20 °C"
      - "Separador U216 para el griego"
      - "Un pulmón por producto"
  - nombre: Envasado
    tipo: Discreto
    variables:
      - "U311 vasos 12.000/h · U312 botellas · U313 potes"
      - "Fruta en línea al 13 % en fresa"
  - nombre: Fin de línea y frío
    tipo: Discreto · Batch
    variables:
      - "Encajonado, estiba y envoltura"
      - "Cámara 2–4 °C, reposo ≥ 12 h"
---
