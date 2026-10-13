# 01 · Transformación Digital Industrial

Arquitectura integral de automatización según **ISA-95** y modelos de producción por lotes según **ISA-88**.

**Responsables:** Integrante 1 (Luis Alberto Mendoza), ISA-88 · Integrante 2 (Pablo de Jesús Arcila), ISA-95 y arquitectura
**Entrega:** intermedia, 5 de octubre de 2026

## Entregables

- [ ] **Arquitectura ISA-95** ([`arquitectura-isa95/`](arquitectura-isa95)): niveles N0–N4 (Proceso → Sensores/actuadores → Control → SCADA → MES → ERP), tecnologías por nivel y flujo de información en ambos sentidos (datos que suben, órdenes y decisiones que bajan). Integración OT/IT.
- [ ] **Modelo físico ISA-88** ([`isa88/modelo-fisico/`](isa88/modelo-fisico)): empresa → sitio → área → celda de proceso → unidad → módulo de equipo → módulo de control, para las tres líneas y los recursos compartidos.
- [ ] **Modelo procedimental ISA-88** ([`isa88/modelo-procedimental/`](isa88/modelo-procedimental)): procedimiento → procedimiento de unidad → operación → fase.
- [ ] **Recetas** ([`isa88/recetas/`](isa88/recetas)): al menos **3 referencias por línea**, que se diferencien de forma no trivial (ingredientes, cantidades, temperaturas, tiempos, envases, calidad).
- [ ] **Instrumentación** ([`instrumentacion/`](instrumentacion)): equipos, sensores, actuadores, variables y comunicaciones. Diagramas P&ID.

## Documentos

| Documento | Contenido |
|:--|:--|
| [P&ID de la empresa base](instrumentacion/PID_Planta_Lactea_Grupo6_Empresa_Base.pdf) | Diagramas de tuberías e instrumentación de las tres líneas y del tronco común, con el nivel de automatización de cada equipo (Pablo Arcila) |
| [Comunicación y datos según ISA-95](arquitectura-isa95/ISA95_Comunicacion_Datos_Empresa_Base.pdf) | Qué se registra hoy en la empresa base, dónde y quién decide, por niveles ISA-95 (Pablo Arcila) |
| [Recetas y procesos de la planta](isa88/Recetas_y_procesos_planta.pdf) | Fórmulas, procedimientos, parámetros, PCC, equipos y códigos de las tres líneas; fuente del modelo ISA-88 |
| [Modelo ISA-88](isa88) | Modelo físico, modelo procedimental y recetas de los nueve productos |
| [Recetas maestras](isa88/recetas-maestras) | Una receta maestra completa por producto, con su diagrama de procedimiento |
| [Diagramas ISA-88](isa88/diagramas) | Modelo físico, modelo procedimental por línea y procedimiento de cada producto |

## Guía de evidencias (enunciado)

> El proyecto debe evidenciar una arquitectura integral de automatización, considerando ISA-95 para estructurar la integración entre proceso, control, supervisión, gestión de producción y gestión empresarial. Asimismo, deberá aplicar conceptos de ISA-88 para estructurar los modelos físicos y procedimentales, así como las recetas y lotes asociados a las líneas de producción.
