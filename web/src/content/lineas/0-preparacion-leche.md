---
# orden 0 = etapas compartidas por las tres líneas (se muestran antes de las pestañas)
nombre: Tronco común · 150.000 L/día
orden: 0
resumen: Recursos compartidos por las tres líneas, desde que llega la cisterna hasta que la leche queda lista en el silo de cada línea.
etapas:
  - nombre: Recepción
    tipo: Discreto · Batch
    variables:
      - "≈ 8 cisternas de 20.000 L al día"
      - "Leche ≤ 6 °C al llegar"
      - "Antibióticos: negativo (PCC-1)"
  - nombre: Leche cruda
    tipo: Batch
    variables:
      - "2 tanques de 60.000 L"
      - "≤ 4 °C, máximo 24 h"
  - nombre: Clarificación y estandarización
    tipo: Continuo
    variables:
      - "Grasa a la medida de cada línea"
      - "La crema sobrante va a U126"
  - nombre: Pasteurización HTST
    tipo: Continuo
    variables:
      - "≥ 72 °C × 15 s (75 °C de diseño)"
      - "20.000 L/h, válvula de desvío (PCC-2)"
  - nombre: Silos por línea
    tipo: Batch
    variables:
      - "Yogures U123A–C · quesos U124 · leche U125"
      - "2–4 °C, máximo 24 h"
---
