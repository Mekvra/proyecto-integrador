---
nombre: Yogurt
orden: 2
resumen: Leche fermentada con Lactobacillus bulgaricus y Streptococcus thermophilus. Comparte pasteurización, fermentación y llenado con la línea de kéfir.
etapas:
  - nombre: Estandarización y formulación
    tipo: Batch · Continuo
    variables:
      - "Grasa 0,1 % · 1,5–2,0 % · ≥ 3,0 %"
      - "Sólidos no grasos 11–14 %"
      - "Azúcar 12–18 °Bx"
      - "Mezcla a 45–60 °C"
  - nombre: Homogeneización
    tipo: Continuo
    variables:
      - "150–250 bar en dos etapas"
      - "55–70 °C"
      - "Glóbulo de grasa < 1 µm"
  - nombre: Tratamiento térmico
    tipo: Continuo
    variables:
      - "85 °C por 5 min o 95 °C por 15–30 s"
      - "Desnaturalización de suero > 70–80 %"
  - nombre: Inoculación
    tipo: Batch
    variables:
      - "Base a 42–45 °C"
      - "Cultivo 0,02–0,05 % (liofilizado)"
      - "Dispersión 10–15 min"
  - nombre: Fermentación
    tipo: Batch
    variables:
      - "42–43 °C durante 4–7 h"
      - "pH de corte 4,5–4,6"
      - "Acidez 70–85 °D"
  - nombre: Enfriamiento y batido
    tipo: Batch · Continuo
    variables:
      - "Enfriar a 18–22 °C y luego < 10 °C"
      - "Batido a 15–25 rpm"
      - "Viscosidad 1 500–3 000 cP"
  - nombre: Adición de fruta
    tipo: Continuo · Batch
    variables:
      - "Preparado de fruta 8–15 %"
      - "Fruta a 40–55 °Bx, 15–20 °C"
  - nombre: Envasado
    tipo: Discreto
    variables:
      - "Producto a 10–15 °C"
      - "125 g · 250 g · 1 000 g, ± 1 %"
      - "Termosellado 180–220 °C"
  - nombre: Refrigeración y maduración
    tipo: Batch
    variables:
      - "Cámara a 2–4 °C"
      - "pH final 4,2–4,4"
      - "Vida útil 21–45 días"
---
