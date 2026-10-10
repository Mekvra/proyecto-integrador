---
nombre: Quesos
orden: 2
resumen: 50.000 L/día de leche para mozzarella, quesillo y doble crema, tres quesos de pasta hilada que comparten tinas, hiladora y salmuera.
etapas:
  - nombre: Coagulación
    tipo: Batch
    variables:
      - "Tinas Q201–Q203 de 10.000 L"
      - "Leche a 32–35 °C, CaCl₂ y cultivo"
      - "Cuajo: coagula en 30–40 min"
  - nombre: Corte y cocción
    tipo: Batch
    variables:
      - "Cubos de 1–1,5 cm"
      - "Cocción hasta 40–42 °C"
      - "Se retira ≈ 85 % del suero"
  - nombre: Acidificación
    tipo: Batch
    variables:
      - "Cuajada hasta pH 5,1–5,3"
      - "Tina: 3,5 h por lote con CIP"
  - nombre: Hilado y moldeo
    tipo: Continuo
    variables:
      - "Hiladora Q301, 1.000–1.300 kg/h"
      - "Agua de hilado a 75–85 °C"
  - nombre: Salmuera
    tipo: Batch
    variables:
      - "NaCl 18–22 % a 8–12 °C"
      - "8 h por lote"
  - nombre: Empaque
    tipo: Discreto
    variables:
      - "Al vacío en Q311"
      - "Cámara de quesos a 2–4 °C"
---
