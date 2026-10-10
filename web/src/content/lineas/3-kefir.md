---
nombre: Kéfir
orden: 3
resumen: Bebida láctea fermentada con bacterias y levaduras, con una fermentación larga a temperatura ambiente controlada.
etapas:
  - nombre: Inoculación
    tipo: Batch
    variables:
      - "Leche a 22–25 °C"
      - "Gránulos 2–5 % o cultivo DVI"
      - "Mezcla 10–15 min a 15–20 rpm"
  - nombre: Fermentación
    tipo: Batch
    variables:
      - "20–25 °C durante 18–24 h"
      - "pH final 4,3–4,5"
      - "Acidez 80–100 °D"
  - nombre: Separación de gránulos
    tipo: Batch · Discreto
    variables:
      - "Malla de 1–2 mm"
      - "Líquido < 20 °C"
  - nombre: Maduración en frío
    tipo: Batch
    variables:
      - "8–10 °C durante 12–24 h"
      - "Alcohol 0,2–0,5 % v/v"
  - nombre: Envasado y refrigeración
    tipo: Continuo · Discreto
    variables:
      - "Envasado a 4–8 °C"
      - "Espacio de cabeza 5–10 %"
      - "Vida útil 20–30 días"
---
