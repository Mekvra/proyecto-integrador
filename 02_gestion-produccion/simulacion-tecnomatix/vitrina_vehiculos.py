# Genera SimTalk que convierte copias del Transporter en vehículos 3D hechos con primitivas
# (createCuboid / createConeFrustum): camión cisterna de leche, camión de despacho refrigerado y montacargas.
# Uso: python vitrina_vehiculos.py <clase> [archivo_salida]   clase = cisterna | despacho | montacargas | todos
import sys

def rgb(c):
    return f'makeRGBValue({c[0]}, {c[1]}, {c[2]})'

class Pieza:
    def __init__(self, cls):
        self.cls, self.L, self.n, self.dz = cls, [], 0, 0.0

    def _mat(self, v, color, brillo=None, transp=None):
        self.L += [f'{v}.MaterialActive := true', f'{v}.MaterialDiffuseColor := {rgb(color)}']
        if brillo is not None:
            self.L.append(f'{v}.MaterialShininess := {brillo}')
        if transp is not None:
            self.L.append(f'{v}.MaterialTransparency := {transp}')

    def caja(self, dim, pos, color, brillo=None, transp=None):
        self.n += 1; v = f'p{self.n}'
        self.L += [f'var {v}: any := g.createCuboid([{dim[0]}, {dim[1]}, {dim[2]}])', f'{v}.Position := [{pos[0]}, {pos[1]}, {round(pos[2] + self.dz, 3)}]']
        self._mat(v, color, brillo, transp)

    def cilindro(self, r, largo, pos, eje, color, r2=None, brillo=None):
        # eje: 'z' vertical (pos = centro de la base), 'x' a lo largo del vehículo, 'y' transversal (ruedas);
        # para 'x' e 'y' pos es el centro del cilindro. Rotation = [ángulo en grados, eje x, eje y, eje z].
        self.n += 1; v = f'p{self.n}'
        self.L.append(f'var {v}: any := g.createConeFrustum({r}, {r if r2 is None else r2}, {largo})')
        x, y, z = pos
        if eje == 'x':
            self.L.append(f'{v}.Rotation := [90.0, 0.0, 1.0, 0.0]'); x = round(x - largo / 2, 3)
        elif eje == 'y':
            self.L.append(f'{v}.Rotation := [90.0, 1.0, 0.0, 0.0]'); y = round(y + largo / 2, 3)
        self.L.append(f'{v}.Position := [{x}, {y}, {round(z + self.dz, 3)}]')
        self._mat(v, color, brillo)

    def codigo(self, largo):
        cab = [f'var c: object := .MUs.{self.cls}',
               'var g: any := c._3D.getGraphic("default")', 'var x: any',
               # oculta la figura de AGV (las piezas no se pueden borrar por SimTalk; se encogen a escala ~0)
               'for var i := 1 to 7', '\tif i /= 6', '\t\tx := c._3D.getGraphic("default", [i])', '\t\tx.Scale := [0.001, 0.001, 0.001]', '\tend', 'next',
               f'c.Length := {largo}', 'c._3D.ScaleAutomatically := false']
        return '\n'.join(cab + self.L)

NEGRO, GRIS, ACERO, BLANCO, VIDRIO = (25, 25, 28), (70, 72, 78), (205, 210, 218), (245, 245, 245), (40, 70, 110)

def ruedas(p, xs, ancho_y, r=0.5):
    for x in xs:
        for s in (-1, 1):
            p.cilindro(r, 0.4, (x, s * ancho_y, r), 'y', NEGRO)
            p.cilindro(r * 0.45, 0.42, (x, s * ancho_y, r), 'y', GRIS)

def cisterna():
    p = Pieza('Camion_Cisterna')
    p.caja((8.4, 2.3, 0.35), (0, 0, 0.75), GRIS)                     # chasis
    p.caja((2.1, 2.45, 2.3), (3.35, 0, 0.9), (200, 30, 40), 0.6)      # cabina roja
    p.caja((0.06, 2.1, 0.9), (4.42, 0, 2.05), VIDRIO, 0.9)            # parabrisas
    p.caja((0.3, 2.5, 0.35), (4.45, 0, 0.75), (30, 30, 30))           # parachoques
    p.cilindro(1.05, 5.8, (-0.95, 0, 2.15), 'x', ACERO, brillo=0.9)  # tanque de acero
    p.cilindro(1.08, 0.5, (-0.95, 0, 2.15), 'x', (25, 90, 170))      # franja azul
    p.cilindro(1.08, 0.25, (1.6, 0, 2.15), 'x', (25, 90, 170))
    p.cilindro(1.08, 0.25, (-3.5, 0, 2.15), 'x', (25, 90, 170))
    p.caja((0.6, 0.6, 0.15), (-0.95, 0, 3.25), (60, 60, 65))         # boca de carga
    ruedas(p, (3.3, -1.6, -3.0), 1.05)
    return p.codigo(9.0)

def despacho():
    p = Pieza('Camion_Despacho')
    p.caja((8.4, 2.3, 0.35), (0, 0, 0.75), GRIS)
    p.caja((2.1, 2.45, 2.3), (3.35, 0, 0.9), (20, 110, 190), 0.6)     # cabina azul
    p.caja((0.06, 2.1, 0.9), (4.42, 0, 2.05), VIDRIO, 0.9)
    p.caja((0.3, 2.5, 0.35), (4.45, 0, 0.75), (30, 30, 30))
    p.caja((6.0, 2.5, 2.6), (-0.9, 0, 1.1), BLANCO, 0.4)              # furgón refrigerado
    p.caja((6.02, 2.52, 0.35), (-0.9, 0, 2.6), (40, 160, 90))         # franja verde
    p.caja((0.6, 1.6, 0.5), (2.05, 0, 3.0), (150, 155, 165))          # equipo de frío
    ruedas(p, (3.3, -1.6, -3.0), 1.05)
    return p.codigo(9.0)

def montacargas():
    p = Pieza('Montacargas')
    p.caja((1.9, 1.1, 0.7), (0, 0, 0.25), (245, 170, 20), 0.5)        # cuerpo amarillo
    p.caja((0.6, 1.05, 0.5), (-0.75, 0, 0.95), (60, 60, 60))          # contrapeso
    p.caja((0.5, 0.5, 0.15), (-0.1, 0, 0.95), NEGRO)                  # asiento
    for s in (-1, 1):                                                 # techo de protección
        p.caja((0.07, 0.07, 1.3), (-0.45, s * 0.48, 0.95), NEGRO)
        p.caja((0.07, 0.07, 1.3), (0.45, s * 0.48, 0.95), NEGRO)
    p.caja((1.0, 1.05, 0.06), (0, 0, 2.25), NEGRO)
    p.caja((0.12, 0.9, 2.3), (1.0, 0, 0.1), (50, 50, 55))             # mástil
    for s in (-1, 1):
        p.caja((1.1, 0.12, 0.06), (1.6, s * 0.3, 0.15), (50, 50, 55))  # horquillas
    p.caja((1.2, 1.0, 0.15), (1.65, 0, 0.21), (160, 110, 60))         # estiba de madera
    p.caja((1.1, 0.9, 0.8), (1.65, 0, 0.36), (235, 90, 120))          # carga (yogur)
    for x in (0.65, -0.65):
        for s in (-1, 1):
            p.cilindro(0.25, 0.22, (x, s * 0.5, 0.25), 'y', NEGRO)
    return p.codigo(2.6)

GEN = {'cisterna': cisterna, 'despacho': despacho, 'montacargas': montacargas}

if __name__ == '__main__':
    q = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    partes = [GEN[k]() for k in (GEN if q == 'todos' else [q])]
    txt = 'simtalk\n' + '\n'.join(partes) + '\n'
    if out:
        open(out, 'w', encoding='utf-8').write(txt)
    else:
        print(txt)
