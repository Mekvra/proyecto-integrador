---
# orden 0 = etapas compartidas por las tres líneas (se muestran antes de las pestañas)
nombre: Preparación de la leche
orden: 0
resumen: Recursos compartidos por las tres líneas, desde que llega el carrotanque hasta que la leche queda lista en el silo.
etapas:
  - nombre: Recepción
    tipo: Discreto · Batch
    variables:
      - "Temperatura en cisterna ≤ 4–6 °C"
      - "Acidez 13–18 °D"
      - "Crioscopia −0,512 a −0,550 °C"
      - "Antibióticos: negativo"
  - nombre: Refrigeración
    tipo: Continuo
    variables:
      - "Salida 2–4 °C"
      - "Caudal 10 000–50 000 L/h"
  - nombre: Filtración por membranas
    tipo: Continuo
    variables:
      - "Presión transmembrana 1–10 bar"
      - "Flux 15–50 L/(m²·h)"
  - nombre: Normalización
    tipo: Continuo
    variables:
      - "Centrífuga 4 000–6 500 rpm"
      - "Separación 45–55 °C"
  - nombre: Pasteurización HTST
    tipo: Continuo
    variables:
      - "72–75 °C durante 15–20 s"
      - "Válvula FDV recircula si T < 72 °C"
  - nombre: Almacenamiento en silos
    tipo: Batch
    variables:
      - "2–4 °C"
      - "Agitación 20–30 rpm"
      - "Residencia máx. 24–48 h"
---
