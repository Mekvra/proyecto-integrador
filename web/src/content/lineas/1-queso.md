---
nombre: Queso fresco
orden: 1
detallada: true
resumen: Línea detallada del proyecto. Aquí desarrollamos la automatización, la celda robotizada y el gemelo digital.
etapas:
  - nombre: Coagulación
    tipo: Batch
    variables:
      - "Leche a 32–36 °C, pH 6,4–6,5"
      - "Cuajo 1–3 mL por cada 10 L"
      - "CaCl₂ 10–20 g por cada 100 L"
      - "Reposo 30–45 min"
  - nombre: Corte de la cuajada
    tipo: Batch
    variables:
      - "Grano de 1–2 cm"
      - "Liras a 10–20 rpm"
      - "5–10 min"
  - nombre: Agitación y desuerado
    tipo: Batch
    variables:
      - "15–30 rpm, 35–38 °C"
      - "10–20 min"
      - "Retiro del 30–50 % del suero"
  - nombre: Moldeo y prensado
    tipo: Batch · Discreto
    variables:
      - "Moldes de 250 g, 500 g o 1 kg"
      - "Masa a 30–35 °C"
      - "Prensado 0,5–1,5 bar, 15–60 min"
  - nombre: Salado
    tipo: Batch
    variables:
      - "Salmuera 18–22 °Bé, 10–12 °C"
      - "Sal final 1,2–2,0 %"
  - nombre: Empaque
    tipo: Discreto
    variables:
      - "Producto ≤ 4–6 °C"
      - "Sellado 130–160 °C"
      - "Peso 500 g ± 5 g"
---
