# Genera la orden SimTalk que colorea en 3D los equipos de planta_lactea_base.spp o planta_lactea_prop.spp por línea.
# Se aplica después de crear la escena con Open 2D/3D. Uso: python colores_3d.py <base|prop> <salida.txt>
import sys

Y, K, Q, G = (236, 112, 140), (70, 140, 200), (232, 180, 40), (150, 160, 175)
esc = sys.argv[1]
nfk, ntk = (3, 3) if esc == 'base' else (4, 2)
NOMBRES = {
    Y: ['Pedidos_Yogur', 'Cola_Yogur', 'U201_Formulacion', 'Envasado_U311_U312', 'Camara_Yogur']
       + [f'Fermentador_Yogur_{i}' for i in (1, 2, 3)] + ([] if esc == 'base' else ['Pulmones_en_espera']),
    G: ['U202_Base', 'U202_Tramo_Kefir'],
    K: ['Pedidos_Kefir', 'Cola_Kefir', 'Camara_Kefir'] + [f'Fermentador_Kefir_{i}' for i in range(1, nfk + 1)]
       + [f'Tanque_Kefir_{i}' for i in range(1, ntk + 1)],
    Q: ['Pedidos_Mozzarella', 'Cola_Mozzarella', 'U221_Tina', 'U222_Acidificacion', 'U223_Hiladora', 'U321_Empaque', 'Camara_Queso']
       + [f'Salmuera_{i}' for i in (1, 2, 3, 4)],
}
L = []
for c, names in NOMBRES.items():
    for n in names:
        L += [f'.Models.Model.{n}._3D.MaterialActive := true', f'.Models.Model.{n}._3D.MaterialDiffuseColor := makeRGBValue({c[0]}, {c[1]}, {c[2]})']
open(sys.argv[2], 'w', encoding='utf-8').write('simtalk\n' + '\n'.join(L) + '\n')
