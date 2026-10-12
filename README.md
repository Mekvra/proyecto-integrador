<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/">
    <img src=".github/assets/banner.png" alt="Mekvra S.A.S — Automatización e integración industrial" width="100%">
  </a>
</p>

<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/"><img alt="Página web" src="https://img.shields.io/badge/p%C3%A1gina_web-en_l%C3%ADnea-c8ad86?style=flat-square&labelColor=141312"></a>
  <a href="https://github.com/Mekvra/proyecto-integrador/actions/workflows/deploy-web.yml"><img alt="Publicación" src="https://img.shields.io/github/actions/workflow/status/Mekvra/proyecto-integrador/deploy-web.yml?branch=main&label=publicaci%C3%B3n&style=flat-square&labelColor=141312&color=a0ca92"></a>
  <img alt="Curso" src="https://img.shields.io/badge/APM-2026--2S-c8ad86?style=flat-square&labelColor=141312">
  <img alt="Universidad" src="https://img.shields.io/badge/UNAL-Sede_Bogot%C3%A1-c8ad86?style=flat-square&labelColor=141312">
</p>

<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/"><b>Página web</b></a>
  &nbsp;·&nbsp;
  <a href="#estructura">Estructura</a>
  &nbsp;·&nbsp;
  <a href="#equipo">Equipo</a>
  &nbsp;·&nbsp;
  <a href="CONTRIBUTING.md">Cómo aportar</a>
  &nbsp;·&nbsp;
  Video de sustentación <sub>(próximamente)</sub>
</p>

<br>

**Mekvra S.A.S** es una empresa integradora de soluciones de **Transformación Digital Industrial**, formada por ingenieros mecatrónicos. Nuestro cliente es **Lácteos Altos de Teusacá**, una planta de derivados lácteos que recibe 150.000 L de leche al día, y le proponemos una solución que conecta todos sus niveles productivos: del sensor en el tanque a la decisión en la gerencia.

> Proyecto Integrador del curso **Automatización de Procesos de Manufactura 2026-2S** · Universidad Nacional de Colombia · Sede Bogotá.

## Líneas de producción

Tres líneas por lotes que comparten la recepción, la pasteurización y los silos de leche (acta del 9 de octubre de 2026).

| Línea | Leche al día | Productos | Alcance en el proyecto |
|:--|--:|:--|:--|
| **Yogures** | ≈ 57.000 L | Fresa, natural y griego | Línea detallada: recetas ISA-88, simulación, VSM, layout y espagueti |
| **Quesos** | 50.000 L | Mozzarella, quesillo y doble crema | Recetas básicas y simulación de la planta |
| **Leche UHT** | 43.000 L | Entera, descremada y con chocolate | Recetas básicas y simulación de la planta |

## Avances

| Entregable | Contenido |
|:--|:--|
| [**Simulación en Tecnomatix**](02_gestion-produccion/simulacion-tecnomatix) | Planta con las tres líneas y línea de yogures con paletizado manual, en 3D, con 12 semanas simuladas |
| [**VSM**](02_gestion-produccion/vsm) | [Planta completa](02_gestion-produccion/vsm/vsm_planta_3_lineas_clasico.pdf) y [línea de yogures](02_gestion-produccion/vsm/vsm_linea_yogures_clasico.pdf): lead time ≈ 35 h con 30 % de valor agregado |
| [**Distribución en planta**](02_gestion-produccion/distribucion-planta) | [Layout de la planta](02_gestion-produccion/distribucion-planta/layout_planta_3_lineas_clasico.pdf) (edificio de 110 × 60 m) y [layout de la línea de yogures](02_gestion-produccion/distribucion-planta/layout_linea_yogures_actual_clasico.pdf) |
| [**Diagrama de espagueti**](02_gestion-produccion/distribucion-planta/espagueti_linea_yogures_actual_clasico.pdf) | Recorridos diarios de la línea de yogures: ≈ 21 km al día y ≈ 11.600 cajas estibadas a mano |
| [**Recetas ISA-88**](01_transformacion-digital/isa88/recetas) | [Recetas de la línea de yogures](01_transformacion-digital/isa88/recetas/Recetas_linea_yogures_v1.8.pdf) y [recetas básicas de la planta](01_transformacion-digital/isa88/recetas/Recetas_basicas_planta_v1.0.pdf) |

Todas las cifras son valores de diseño o de simulación, no medidas en planta.

<h2 id="estructura">Estructura</h2>

El repositorio sigue los módulos del curso. Cada carpeta tiene su propio `README.md` con los entregables, el responsable y el estado.

| | Módulo | Contenido |
|:--:|:--|:--|
| `00` | [**Gestión del equipo**](00_gestion-equipo) | Actas, roles y evidencias de trabajo colaborativo |
| `01` | [**Transformación digital**](01_transformacion-digital) | Arquitectura ISA-95, modelos y recetas ISA-88, instrumentación |
| `02` | [**Gestión de la producción**](02_gestion-produccion) | Diagramas de proceso, layout, VSM, OEE, Tecnomatix, MES/ERP |
| `03` | [**Planeación del proyecto**](03_planeacion-proyecto) | EDT, cronograma, presupuesto, flujo de caja, propuesta de valor |
| `04` | [**Controladores**](04_controladores) | Grafcet y lógica Ladder en Logix Emulate |
| `05` | [**Gemelo digital**](05_gemelo-digital) | Línea de quesos en Siemens NX |
| `06` | [**Celda robotizada**](06_celda-robotizada) | Diseño, simulación en RobotStudio y análisis de riesgos |
| `07` | [**SCADA**](07_scada) | HMI ISA-101 en Ignition, comunicación OPC |
| `08` | [**Investigación**](08_investigacion) | Proceso lácteo, variables de operación y fuentes |
| `web` | [**Página web**](web) | Sitio en Astro, publicado automáticamente con GitHub Pages |

<h2 id="equipo">Equipo</h2>

| | Integrante | Rol |
|:--:|:--|:--|
| <img src="https://github.com/lmendozar2001.png?size=80" width="40" alt=""> | **Luis Alberto Mendoza**<br><sub>[@lmendozar2001](https://github.com/lmendozar2001)</sub> | Líder de integración OT/IT |
| <img src="https://github.com/Kreiop.png?size=80" width="40" alt=""> | **Pablo de Jesús Arcila**<br><sub>[@Kreiop](https://github.com/Kreiop)</sub> | Líder de arquitectura y modelado técnico |
| <img src="https://github.com/david-pi3141.png?size=80" width="40" alt=""> | **David Steven Pinzón Hernández**<br><sub>[@david-pi3141](https://github.com/david-pi3141)</sub> | Líder de gestión de producción |
| <img src="https://github.com/DanielCastro-02.png?size=80" width="40" alt=""> | **Daniel Felipe Castro**<br><sub>[@DanielCastro-02](https://github.com/DanielCastro-02)</sub> | CFO · Gestión de proyecto |
| <img src="https://github.com/JananLC.png?size=80" width="40" alt=""> | **Janan Libardo Carreño Riaño**<br><sub>[@JananLC](https://github.com/JananLC)</sub> | CTO · Integración digital |

## Cómo aportar

Sube tus archivos a la carpeta de tu módulo, directamente desde GitHub y sin instalar nada. La guía completa, con las reglas de nombres y cómo editar la página web, está en **[CONTRIBUTING.md](CONTRIBUTING.md)**.

<br>

<p align="center">
  <img src=".github/assets/avatar.png" width="44" alt="">
  <br>
  <sub><b>MEKVRA S.A.S</b> · Automatización e integración industrial</sub>
</p>
