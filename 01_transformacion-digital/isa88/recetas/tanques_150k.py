# Dimensionamiento de los tanques de leche cruda y de los silos de la línea de yogures con una recepción de
# 150.000 L/día (propuesta del equipo, 9-oct-2026). Simulación minuto a minuto de un día típico.
# Supuestos (los mismos de la sección 10.4 de las recetas, escalados):
#   - dos olas de camiones: 60 % entre 05:00 y 11:00 y 40 % entre 14:00 y 18:00, a caudal constante;
#   - el pasteurizador U121/U122 arranca 30 min después del primer camión (pruebas de plataforma),
#     hace un CIP-C de 1,4 h a las 11:00 y otro en la noche, y trabaja mientras haya leche cruda;
#   - la leche pasteurizada se reparte entre líneas según su cupo diario;
#   - la línea de yogures consume su silo de forma pareja las 24 h (un lote de 10.000 L cada 3 h con la propuesta).
import sys

RECEPCION = 150_000
CUPOS = {'yogures': 80_000, 'quesos': 60_000, 'kefir': 10_000}     # reparto acordado (L/día de leche a línea)


def simular(caudal_pasteurizador, yogur_dia, minutos_parada=0, hora_parada=8.0):
    olas = [(5.0, 11.0, 0.6 * RECEPCION), (14.0, 18.0, 0.4 * RECEPCION)]
    cip = [(11.0, 12.4), (21.0, 22.4)]
    crudo = silo_y = 0.0
    pico_crudo = 0.0
    traza = []
    # se simulan dos días seguidos y se mide el segundo (el silo arranca con el sobrante de la noche)
    for dia in range(2):
        for minuto in range(24 * 60):
            h = minuto / 60
            entra = sum(v / ((b - a) * 60) for a, b, v in olas if a <= h < b)
            crudo += entra
            parado = any(a <= h < b for a, b in cip) or h < 5.5 or (
                minutos_parada and hora_parada <= h < hora_parada + minutos_parada / 60)
            sale = 0.0 if parado else min(crudo, caudal_pasteurizador / 60)
            crudo -= sale
            silo_y += sale * yogur_dia / RECEPCION                   # parte de la pasteurizada que va a yogures
            silo_y -= yogur_dia / (24 * 60)                          # la línea consume parejo
            if dia == 1:
                pico_crudo = max(pico_crudo, crudo)
                if minuto % 60 == 0:
                    traza.append((int(h), round(crudo), round(silo_y)))
    return pico_crudo, traza


if __name__ == '__main__':
    for nombre, yog in (('actual (≈ 57.600 L/día a yogures)', 57_600), ('propuesta (80.000 L/día a yogures)', 80_000)):
        for q in (15_000, 20_000):
            pico, tr = simular(q, yog)
            silo = [s for _, _, s in tr]
            print(f'{nombre} · pasteurizador {q:,} L/h: pico leche cruda {pico:,.0f} L · '
                  f'volumen de trabajo de los silos de yogures {max(silo) - min(silo):,.0f} L')   # lo que sube y baja en el día
    pico, _ = simular(15_000, 80_000, minutos_parada=120, hora_parada=8.0)
    print(f'falla de 2 h del pasteurizador a las 08:00 (15.000 L/h): pico leche cruda {pico:,.0f} L')
