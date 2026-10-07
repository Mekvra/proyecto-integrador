# Genera las órdenes SimTalk que se aplican a la vitrina DESPUÉS de crear la escena 3D (botón Open 2D/3D):
# colores (look3d), operarios caminando, vehículos propios, acopio, muelle y decoración de la planta.
# Escribe post_01.txt, post_02.txt, ... (cada uno es una orden "simtalk" independiente para live.py).
import os
import vitrina_vehiculos as vehiculos, vitrina_decoracion as decoracion, vitrina_planta_deco as planta_deco, vitrina_carteles as carteles

D = os.path.dirname(os.path.abspath(__file__))

ORDENES = []
ORDENES.append(open(os.path.join(D, 'vitrina_colores.txt'), encoding='utf-8').read())
PUESTOS = ['Recepcion_de_leche', 'U221_Tina', 'U223_Hiladora', 'U311', 'U312', 'U321', 'U322', 'U331', 'U341_Paletizado', 'Muelle_de_despacho']
pu = ['var m: object := .Models.Model', 'var k: object']
for i, n in enumerate(PUESTOS, 1):   # un puesto de trabajo junto a cada estación atendida
    pu += [f'k := .Resources.Workplace.createObject(m, m.{n}.XPos, m.{n}.YPos + 45)', f'k.Name := "Puesto_{i}"',
           f'k.Station := m.{n}', 'k.SupportedServices := ["Processing"]']
ORDENES.append('\n'.join(pu))
ORDENES.append('\n'.join([
    'var m: object := .Models.Model',
    'm.EventController.reset',
    'm.Operarios.WorkersCanWorkRemotely := false',          # con 3D los operarios caminan hasta su puesto
    # estaciones donde paran los camiones: se bajan 1 m para que el camión quede a ras de piso
    'm.Recepcion_de_leche._3D.Position := [m.Recepcion_de_leche._3D.Position.X, m.Recepcion_de_leche._3D.Position.Y, -1]',
    'm.Muelle_de_despacho._3D.Position := [m.Muelle_de_despacho._3D.Position.X, m.Muelle_de_despacho._3D.Position.Y, -1]',
    'var a: object := .MUs.Transporter.duplicate(.MUs, "Camion_Cisterna")',
    'var b: object := .MUs.Transporter.duplicate(.MUs, "Camion_Despacho")',
    'var d: object := .MUs.Transporter.duplicate(.MUs, "Montacargas")']))
for f in (vehiculos.cisterna, vehiculos.despacho, vehiculos.montacargas):
    ORDENES.append(f())
ORDENES.append('\n'.join([
    'var m: object := .Models.Model',
    'm.Cisternas_de_leche.Path := .MUs.Camion_Cisterna',
    'm.Camiones_despacho.Path := .MUs.Camion_Despacho',
    'm.Montacargas.Path := .MUs.Montacargas']))
ORDENES.append(decoracion.acopio())
ORDENES.append(decoracion.muelle())
ORDENES.append(planta_deco.planta())
ORDENES += carteles.construir()          # carteles por zona y proceso, envasadoras por presentación y paletizado
ORDENES.append('\n'.join(['var m: object := .Models.Model'] + [f'm.{n}._3D.Scale := [0.02, 0.02, 0.02]' for n in carteles.OCULTAR]))
ORDENES.append('\n'.join([   # la decoración agranda la caja de estos objetos; no deben estorbar a los operarios
    'var m: object := .Models.Model',
    'm.Muelle_de_despacho._3D.ObstacleForWorker := "(None)"',
    'm.Recepcion_de_leche._3D.ObstacleForWorker := "(None)"',
    'm.Salida_cisternas._3D.ObstacleForWorker := "(None)"',
    'm.EventController.Speed := 40']))

if __name__ == '__main__':
    for i, o in enumerate(ORDENES, 1):
        open(os.path.join(D, f'post_{i:02d}.txt'), 'w', encoding='utf-8').write('simtalk\n' + o + '\n')
    print(len(ORDENES), 'órdenes')
