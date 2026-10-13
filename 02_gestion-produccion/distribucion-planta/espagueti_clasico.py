# Diagramas de espagueti de la línea de yogurts con presentación de plano técnico: Arial, trazo negro, equipos sin
# relleno de color, cajetín con cuadrícula. Usa la misma geometría y las mismas rutas de plano.py; las rutas conservan
# sus colores (la de la analista es morada). Genera espagueti_linea_yogures_actual_clasico y _propuesto_clasico (svg + html).
import plano as P

A = 'Arial, Helvetica, sans-serif'
P.FD = P.FB = P.FM = A
P.INK, P.MUTED, P.RULE, P.BG, P.ACC = '#000000', '#444444', '#000000', '#ffffff', '#000000'
P.LINEA = {'tronco': '#000000', 'yogurt': '#000000', 'queso': '#9a9a9a', 'uht': '#9a9a9a', 'serv': '#9a9a9a', 'frio': '#000000'}
P.GRIS = '#9a9a9a'
P.tinte = lambda c, a=0.13: '#ffffff'
P.ALMACENES = [a for a in P.ALMACENES if a[0] != 'U411']   # la cámara ya lleva su nombre; el rótulo chocaba con la ruta amarilla


def rotulo(h, plano_txt, hoja):
    x, y, w = 1575, 1250, 395
    h.rect(x, y, w, 136, '#fff', '#000', 1.2)
    for yy in (y + 34, y + 68, y + 102):
        h.line(x, yy, x + w, yy, '#000', 0.8)
    h.line(x + 250, y + 68, x + 250, y + 136, '#000', 0.8)
    h.t(x + 8, y + 23, 'Mekvra · Grupo 6 · APM 2026-2S · UNAL', 12.5, '#000', 700, A)
    h.t(x + 8, y + 57, plano_txt, 12.5, '#000', 400, A)
    h.t(x + 8, y + 91, 'Lácteos Altos de Teusacá', 12, '#000', 400, A)
    h.t(x + 258, y + 91, 'Escala 1:750', 12, '#000', 400, A)
    h.t(x + 8, y + 125, 'Elaboró: J. Carreño · cotas en m', 12, '#000', 400, A)
    h.t(x + 258, y + 125, f'12-oct-2026 · {hoja}', 12, '#000', 400, A)


def hoja(titulo, sub):
    h = P.Hoja()
    P.plano(h, 'yogurt', '', titulo, sub, etiquetas_equipo=False)
    # marco recto (sin esquinas redondeadas) y título más sobrio
    h.S = [s.replace('rx="10"', 'rx="0"').replace('font-size="30" font-weight="800"', 'font-size="26" font-weight="700"') for s in h.S]
    xp = f'x="{P.X(86):.1f}"'
    h.S = [s.replace(xp, f'x="{P.X(91.5):.1f}"') if 'PASILLO' in s else s for s in h.S if 'Mekvra · APM 2026-2S · UNAL' not in s]
    return h


h = hoja('Diagrama de espagueti – estado actual', 'Línea de yogurts · recorridos que se repiten cada día (viajes estimados para ≈ 57.600 L/día de leche a yogurts)')
filas, tot_act = P.espagueti(h, P.ACTUAL, False)
P.tabla_rutas(h, filas, tot_act, 1585, 200, False)
h.svg('espagueti_linea_yogures_actual_clasico', 'Espagueti actual')

h = hoja('Diagrama de espagueti – con la propuesta', 'Línea de yogurts · robot en U341, llenadora FFS, pH en línea y registro en el MES')
filas, tot_pro = P.espagueti(h, P.PROPUESTO, True)
y = P.tabla_rutas(h, filas, tot_pro, 1585, 200, True, tot_act)
h.t(1585, y + 4, 'Qué cambia', 15, '#000', 700, A)
for i, s in enumerate(['Robot en U341: nadie estiba cajas a mano.', 'FFS: bobinas en lugar de vasos preformados.',
                       'pH en línea en el MES: el analista solo verifica.', 'MES: el supervisor deja las planillas.']):
    h.t(1585, y + 28 + i * 18, s, 11.5, '#000', 400, A)
h.svg('espagueti_linea_yogures_propuesto_clasico', 'Espagueti propuesto')

# layout de la planta (tres líneas) y de la línea de yogurts en el mismo formato, con el color de cada línea en el contorno
P.LINEA = {'tronco': '#000000', 'yogurt': '#c33c64', 'queso': '#a37c12', 'uht': '#3d8a52', 'serv': '#6b7682', 'frio': '#2b7bb0'}
for nombre, enf, tit, sub in (('layout_planta_3_lineas_clasico', None, 'Distribución en planta – tres líneas',
                               'Edificio de 110 × 60 m · yogurts, quesos y leche UHT · 150.000 L/día · paletizado manual'),
                              ('layout_linea_yogures_actual_clasico', 'yogurt', 'Distribución en planta – línea de yogurts',
                               'La línea de yogurts en color y las demás áreas en gris · paletizado manual con dos operarios')):
    h = P.Hoja()
    P.plano(h, enf, '', tit, sub)
    h.S = [s.replace('rx="10"', 'rx="0"').replace('font-size="30" font-weight="800"', 'font-size="26" font-weight="700"') for s in h.S if 'Mekvra · APM 2026-2S · UNAL' not in s]
    for px_, py_ in ((98.3, 12.6), (100.8, 12.6)):
        h.S.append(f'<circle cx="{P.X(px_):.1f}" cy="{P.Y(py_):.1f}" r="5" fill="#c00000"/>')
    y = P.leyenda(h, 1585, 200, enf)
    h.S.append(f'<circle cx="1600" cy="{y - 14:.1f}" r="5" fill="#c00000"/>')
    h.t(1627, y - 10, 'Operario de paletizado manual', 11.5, '#000', 400, A)
    P.tabla_areas(h, 1585, y + 16)
    h.svg(nombre, tit)
print('ok', round(tot_act), round(tot_pro))
