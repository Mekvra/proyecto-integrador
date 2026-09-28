---
titulo: Un solo flujo, del sensor al ERP.
resumen: La información sube desde la planta hasta la gerencia, y las órdenes, recetas y decisiones bajan de vuelta. Elige un nivel para ver qué hace.
# Niveles de la arquitectura ISA-95, de arriba (empresa) hacia abajo (proceso).
niveles:
  - codigo: N5
    nombre: ERP
    herramienta: SAP
    funcion: Gestiona la empresa. Pedidos, inventarios, compras, costos, ventas y logística. Horizonte de días a meses.
    sube:
      - "Producción real por orden"
      - "Consumo de materias primas"
      - "Costos de fabricación"
    baja:
      - "Órdenes de producción"
      - "Cantidades y fechas"
      - "Prioridades"
  - codigo: N4
    nombre: MES
    herramienta: Base de datos · Node-RED · Power BI
    funcion: Gestiona la ejecución de la producción. Órdenes, lotes, calidad, paradas, trazabilidad y OEE. Horizonte de turno o día.
    sube:
      - "Cumplimiento de órdenes"
      - "OEE por línea"
      - "Calidad y trazabilidad por lote"
    baja:
      - "Recetas y parámetros por lote"
      - "Programación de lotes"
  - codigo: N3
    nombre: SCADA
    herramienta: Ignition · OPC
    funcion: Supervisa el proceso bajo ISA-101. Estados de equipos, variables, alarmas, tendencias, receta activa y estado del lote.
    sube:
      - "Variables de proceso"
      - "Alarmas y paradas"
      - "Estado de los equipos"
    baja:
      - "Arranque y paro de lotes"
      - "Selección de receta"
      - "Setpoints"
  - codigo: N2
    nombre: Control
    herramienta: Logix Emulate (PLC)
    funcion: Ejecuta la lógica secuencial (Grafcet y Ladder) y la regulación de temperatura, nivel, caudal y presión.
    sube:
      - "Estados de las fases"
      - "Variables medidas"
    baja:
      - "Mando de válvulas, bombas y agitadores"
      - "Trayectorias del robot"
  - codigo: N1
    nombre: Campo
    herramienta: Sensores y actuadores virtuales
    funcion: Mide y actúa sobre el proceso. Transmisores de temperatura, caudal, nivel, presión y pH; válvulas, bombas, agitadores y el brazo robot.
    sube:
      - "Señales de 4–20 mA y digitales"
    baja:
      - "Señales de mando a los actuadores"
  - codigo: N0
    nombre: Proceso
    herramienta: Gemelo digital en Siemens NX
    funcion: La transformación física. La leche se recibe, se trata y se convierte en queso, yogurt y kéfir.
    sube: []
    baja: []
---
