# Plano de la planta con tres líneas (yogures, quesos y leche UHT): solo la nave, sin exteriores.
# Genera layout_planta_3_lineas.svg y .html (mismo nombre que antes, para no romper los enlaces de la página).
import os
from plano import Hoja, plano, rotulo

D = os.path.dirname(os.path.abspath(__file__))
h = Hoja()
plano(h, 'PLANO DE DISTRIBUCIÓN · NAVE DE PRODUCCIÓN · ESTADO ACTUAL', 'Planta de Lácteos Altos de Teusacá · tres líneas',
      'Nave de 110 × 60 m · 150.000 L/día · yogures, quesos y leche UHT · equipos con los códigos del modelo de Tecnomatix · '
      'medidas propuestas por Mekvra (sin plano del terreno)')
rotulo(h, 'Distribución en planta · tres líneas')
h.svg(D, 'layout_planta_3_lineas', 'Plano de la planta')
print('ok')
