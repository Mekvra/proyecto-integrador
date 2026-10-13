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
  <img alt="Tecnomatix" src="https://img.shields.io/badge/Tecnomatix-Plant_Simulation-8a8380?style=flat-square&labelColor=141312">
  <img alt="ISA-88 e ISA-95" src="https://img.shields.io/badge/ISA--88_·_ISA--95-est%C3%A1ndares-8a8380?style=flat-square&labelColor=141312">
</p>

<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/"><b>Página web</b></a>
  &nbsp;·&nbsp;
  <a href="#la-planta">La planta</a>
  &nbsp;·&nbsp;
  <a href="#avances">Avances</a>
  &nbsp;·&nbsp;
  <a href="#equipo">Equipo</a>
  &nbsp;·&nbsp;
  <a href="#estructura">Estructura</a>
  &nbsp;·&nbsp;
  <a href="CONTRIBUTING.md">Cómo aportar</a>
</p>

<br>

<p align="center">
  <b>Mekvra S.A.S</b> es una empresa integradora de soluciones de <b>Transformación Digital Industrial</b>, formada por ingenieros mecatrónicos.<br>
  Conectamos el proceso físico con la gestión del negocio: del sensor en el tanque a la decisión en la gerencia.
</p>

<p align="center"><sub>Proyecto Integrador · Automatización de Procesos de Manufactura 2026-2S · Universidad Nacional de Colombia · Sede Bogotá</sub></p>

<br>

<h2 id="la-planta">La planta</h2>

Nuestro cliente es **Lácteos Altos de Teusacá**, una planta de derivados lácteos que recibe **150.000 L de leche al día**. Tres líneas por lotes comparten la recepción, la pasteurización y los silos (acta del 9 de octubre de 2026).

| | Línea | Productos | Alcance en el proyecto |
|:--:|:--|:--|:--|
| <img src="https://img.shields.io/badge/-%20%20-e87090?style=flat-square" alt=""> | **Yogures** | Fresa, natural y griego | Línea detallada: recetas ISA-88, simulación, VSM, layout y espagueti |
| <img src="https://img.shields.io/badge/-%20%20-e6c25a?style=flat-square" alt=""> | **Quesos** | Mozzarella, quesillo y doble crema | Recetas básicas y simulación de la planta |
| <img src="https://img.shields.io/badge/-%20%20-6fae78?style=flat-square" alt=""> | **Leche UHT** | Entera, descremada y con chocolate | Recetas básicas y simulación de la planta |

<p align="center">
  <img src=".github/assets/cifras.png" alt="Producción diaria: 150.000 L de leche recibida, 57.600 L en yogures, 50.000 L en quesos y 43.000 L en leche UHT" width="100%">
</p>

<br>

<h2 id="avances">Avances</h2>

Estado actual de la planta, antes de la propuesta de automatización. Cada imagen abre el documento completo.

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/simulacion-tecnomatix/planta-150k"><img src=".github/assets/avances/d1.jpg" alt="Modelo 3D de la planta con tres líneas en Tecnomatix" width="100%"></a>
      <sub>Planta completa en Plant Simulation: tronco común y líneas de yogures, quesos y leche UHT.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/simulacion-tecnomatix/linea-yogures"><img src=".github/assets/avances/d2.jpg" alt="Modelo 3D de la línea de yogures con paletizado manual" width="100%"></a>
      <sub>Línea de yogures en seis secciones, de la recepción al despacho, con paletizado manual.</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/vsm/vsm_planta_3_lineas_clasico.pdf"><img src=".github/assets/avances/d3.jpg" alt="VSM de la planta con tres líneas" width="100%"></a>
      <sub>Mapa de flujo de valor de las tres líneas sobre el tronco común.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/vsm/vsm_linea_yogures_clasico.pdf"><img src=".github/assets/avances/d4.jpg" alt="VSM de la línea de yogures" width="100%"></a>
      <sub>Mapa de flujo de valor de la línea de yogures, de la recepción a la cámara.</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/distribucion-planta/layout_planta_3_lineas_clasico.pdf"><img src=".github/assets/avances/d5.jpg" alt="Distribución en planta de la nave de 110 por 60 metros" width="100%"></a>
      <sub>Plano de la nave de 110 × 60 m con las tres líneas. También el <a href="02_gestion-produccion/distribucion-planta/layout_linea_yogures_actual_clasico.pdf">layout de la línea de yogures</a>.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/distribucion-planta/espagueti_linea_yogures_actual_clasico.pdf"><img src=".github/assets/avances/d6.jpg" alt="Diagrama de espagueti de la línea de yogures" width="100%"></a>
      <sub>Recorridos diarios de personas y montacargas en la línea de yogures.</sub>
    </td>
  </tr>
</table>

**Recetas ISA-88:** [modelo físico, procedimental y 9 recetas maestras](01_transformacion-digital/isa88) · [recetas de la línea de yogures](01_transformacion-digital/isa88/recetas/Recetas_linea_yogures_v1.8.pdf) · [recetas básicas de la planta](01_transformacion-digital/isa88/recetas/Recetas_basicas_planta_v1.0.pdf)
<br>
**Planeación:** [EDT](03_planeacion-proyecto/edt-cronograma/EDT_Completo_v1.0.pdf) · [cronograma](03_planeacion-proyecto/edt-cronograma/Cronograma_Planta_Lactea_v1.0.pdf)

<sub>Todas las cifras son valores de diseño o de simulación, no medidas en planta.</sub>

<br>

<h2 id="equipo">Equipo</h2>

<p align="center">
  <a href="https://github.com/lmendozar2001"><img src=".github/assets/equipo/tarjeta_luis.jpg" width="19%" alt="Luis Alberto Mendoza, líder de automatización"></a>
  <a href="https://github.com/Kreiop"><img src=".github/assets/equipo/tarjeta_pablo.jpg" width="19%" alt="Pablo de Jesús Arcila Mora, líder de ingeniería"></a>
  <a href="https://github.com/david-pi3141"><img src=".github/assets/equipo/tarjeta_david.jpg" width="19%" alt="David Steven Pinzón Hernández, líder de gestión y administración"></a>
  <a href="https://github.com/DanielCastro-02"><img src=".github/assets/equipo/tarjeta_daniel.jpg" width="19%" alt="Daniel Felipe Castro, gerencia, desarrollo y finanzas"></a>
  <a href="https://github.com/JananLC"><img src=".github/assets/equipo/tarjeta_janan.jpg" width="19%" alt="Janan Libardo Carreño Riaño, líder de instrumentación y software"></a>
</p>

<br>

<h2 id="estructura">Estructura</h2>

El repositorio sigue los módulos del curso. Cada carpeta tiene su propio `README.md` con sus entregables.

| | Módulo | Contenido | Estado |
|:--:|:--|:--|:--:|
| `00` | [**Gestión del equipo**](00_gestion-equipo) | Actas, roles y evidencias de trabajo colaborativo | ![](https://img.shields.io/badge/-en_curso-c8ad86?style=flat-square) |
| `01` | [**Transformación digital**](01_transformacion-digital) | Modelos y recetas ISA-88, arquitectura ISA-95, instrumentación | ![](https://img.shields.io/badge/-en_desarrollo-c8ad86?style=flat-square) |
| `02` | [**Gestión de la producción**](02_gestion-produccion) | Tecnomatix, VSM, layout, espagueti, indicadores, MES/ERP | ![](https://img.shields.io/badge/-en_desarrollo-c8ad86?style=flat-square) |
| `03` | [**Planeación del proyecto**](03_planeacion-proyecto) | EDT, cronograma, presupuesto, flujo de caja, propuesta de valor | ![](https://img.shields.io/badge/-en_desarrollo-c8ad86?style=flat-square) |
| `04` | [**Controladores**](04_controladores) | Grafcet y lógica Ladder en Logix Emulate | ![](https://img.shields.io/badge/-pendiente-8a8380?style=flat-square) |
| `05` | [**Gemelo digital**](05_gemelo-digital) | Gemelo digital en Siemens NX | ![](https://img.shields.io/badge/-pendiente-8a8380?style=flat-square) |
| `06` | [**Celda robotizada**](06_celda-robotizada) | Diseño, simulación en RobotStudio y análisis de riesgos | ![](https://img.shields.io/badge/-pendiente-8a8380?style=flat-square) |
| `07` | [**SCADA**](07_scada) | HMI ISA-101 en Ignition, comunicación OPC | ![](https://img.shields.io/badge/-pendiente-8a8380?style=flat-square) |
| `08` | [**Investigación**](08_investigacion) | Proceso lácteo, variables de operación y fuentes | ![](https://img.shields.io/badge/-en_curso-c8ad86?style=flat-square) |
| `web` | [**Página web**](web) | Sitio en Astro, publicado automáticamente con GitHub Pages | ![](https://img.shields.io/badge/-en_l%C3%ADnea-a0ca92?style=flat-square) |

## Cómo aportar

Sube tus archivos a la carpeta de tu módulo, directamente desde GitHub y sin instalar nada. La guía completa, con las reglas de nombres y cómo editar la página web, está en **[CONTRIBUTING.md](CONTRIBUTING.md)**.

<br>

<p align="center">
  <img src=".github/assets/avatar.png" width="56" alt="">
  <br>
  <b>MEKVRA S.A.S</b>
  <br>
  <sub>Automatización e integración industrial · Bogotá, Colombia</sub>
</p>
