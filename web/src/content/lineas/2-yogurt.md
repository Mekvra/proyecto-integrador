---
nombre: Yogures
orden: 1
detallada: true
resumen: La línea que desarrollamos en detalle. Yogur con fresa, natural y griego en lotes de 10.000 L; hoy procesa ≈ 57.000 L/día porque la llenadora de vasos está al límite.
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
