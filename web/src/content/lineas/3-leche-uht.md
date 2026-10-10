---
nombre: Leche UHT
orden: 3
resumen: 43.000 L/día de leche de larga vida, entera, descremada y con chocolate, en envase aséptico de 1 L. Reemplaza al kéfir desde el acta del 9 de octubre.
etapas:
  - nombre: Mezcla y estandarización
    tipo: Batch
    variables:
      - "Tanque L201 con tolva de cacao"
      - "Chocolate: azúcar 6 %, cacao 1,2 %"
  - nombre: Esterilización UHT
    tipo: Continuo
    variables:
      - "Homogeneización 200/50 bar"
      - "137 °C × 4 s (PCC-L1)"
  - nombre: Tanque aséptico
    tipo: Batch
    variables:
      - "L203 de 20.000 L con aire estéril"
  - nombre: Envasado aséptico
    tipo: Discreto
    variables:
      - "L311, ≈ 7.000 envases de 1 L por hora"
      - "Material esterilizado con H₂O₂"
  - nombre: Liberación
    tipo: Batch
    variables:
      - "Bodega a temperatura ambiente"
      - "Prueba rápida de esterilidad por lote"
---
