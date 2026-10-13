<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/">
    <img src=".github/assets/banner-mekvra-sas.png" alt="Mekvra S.A.S — Automatización e integración industrial" width="100%">
  </a>
</p>

<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/"><img alt="Página web" src="https://img.shields.io/badge/p%C3%A1gina_web-en_l%C3%ADnea-c8ad86?style=flat-square&labelColor=141312"></a>
  <a href="https://github.com/Mekvra/proyecto-integrador/actions/workflows/deploy-web.yml"><img alt="Publicación" src="https://img.shields.io/github/actions/workflow/status/Mekvra/proyecto-integrador/deploy-web.yml?branch=main&label=publicaci%C3%B3n&style=flat-square&labelColor=141312&color=a0ca92"></a>
  <img alt="APM 2026-2S" src="https://img.shields.io/badge/APM-2026--2S-c8ad86?style=flat-square&labelColor=141312">
  <img alt="UNAL Sede Bogotá" src="https://img.shields.io/badge/UNAL-Sede_Bogot%C3%A1-c8ad86?style=flat-square&labelColor=141312">
</p>

<p align="center">
  <a href="https://mekvra.github.io/proyecto-integrador/"><b>Página web</b></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#la-empresa">La empresa</a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#la-planta">La planta</a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#avances">Avances</a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#equipo">Equipo</a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="#estructura">Estructura</a>
</p>

<br>

<a id="la-empresa"></a>
<img src=".github/assets/secciones/seccion-1.png" alt="01 · La empresa" width="100%">

**Mekvra S.A.S** es una empresa integradora de soluciones de **Transformación Digital Industrial**, formada por ingenieros mecatrónicos. Conectamos el proceso físico con la gestión del negocio: del sensor en el tanque a la decisión en la gerencia.

<table>
  <tr>
    <td width="33%" valign="top">
      <b>Qué hacemos</b><br><br>
      Integramos instrumentación, control, robótica, SCADA, MES y ERP en una sola arquitectura, sobre los estándares ISA-95 e ISA-88.
    </td>
    <td width="33%" valign="top">
      <b>Nuestro cliente</b><br><br>
      Lácteos Altos de Teusacá, planta de derivados lácteos en Zipaquirá, Cundinamarca, con tres líneas de producción por lotes.
    </td>
    <td width="33%" valign="top">
      <b>El proyecto</b><br><br>
      Proyecto Integrador de Automatización de Procesos de Manufactura 2026-2S, Universidad Nacional de Colombia, Sede Bogotá.
    </td>
  </tr>
</table>

<br>

<a id="la-planta"></a>
<img src=".github/assets/secciones/seccion-2.png" alt="02 · La planta" width="100%">

La planta recibe la leche por un tronco común (recepción, pasteurización y silos) y la reparte entre tres líneas por lotes, según el acta del 9 de octubre de 2026.

<img src=".github/assets/produccion-diaria.png" alt="Producción diaria: 150.000 L de leche recibida, 57.600 L en yogurts, 50.000 L en quesos y 43.000 L en leche UHT" width="100%">

| Línea | Productos | Alcance en el proyecto |
|:--|:--|:--|
| **Yogurts** | Fresa, natural y griego | Línea detallada: recetas ISA-88, simulación, VSM, layout y espagueti |
| **Quesos** | Mozzarella, quesillo y doble crema | Recetas básicas y simulación de la planta |
| **Leche UHT** | Entera, descremada y con chocolate | Recetas básicas y simulación de la planta |

<br>

<a id="avances"></a>
<img src=".github/assets/secciones/seccion-3.png" alt="03 · Avances" width="100%">

Análisis de la planta en su estado actual, antes de la propuesta de automatización. Cada imagen abre el documento completo.

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/simulacion-tecnomatix/planta-150k"><img src=".github/assets/avances/avance-1.jpg" alt="Modelo 3D de la planta con tres líneas en Tecnomatix" width="100%"></a>
      <sub>Planta completa en Plant Simulation: tronco común y líneas de yogurts, quesos y leche UHT.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/simulacion-tecnomatix/linea-yogures"><img src=".github/assets/avances/avance-2.jpg" alt="Modelo 3D de la línea de yogurts con paletizado manual" width="100%"></a>
      <sub>Línea de yogurts en seis secciones, de la recepción al despacho, con paletizado manual.</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/vsm/vsm_planta_3_lineas_clasico.pdf"><img src=".github/assets/avances/avance-3.jpg" alt="VSM de la planta con tres líneas" width="100%"></a>
      <sub>Mapa de flujo de valor de las tres líneas sobre el tronco común.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/vsm/vsm_linea_yogures_clasico.pdf"><img src=".github/assets/avances/avance-4.jpg" alt="VSM de la línea de yogurts" width="100%"></a>
      <sub>Mapa de flujo de valor de la línea de yogurts, de la recepción a la cámara.</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/distribucion-planta/layout_planta_3_lineas_clasico.pdf"><img src=".github/assets/avances/avance-5.jpg" alt="Distribución en planta de la nave de 110 por 60 metros" width="100%"></a>
      <sub>Plano de la nave de 110 × 60 m con las tres líneas.</sub>
    </td>
    <td width="50%" valign="top">
      <a href="02_gestion-produccion/distribucion-planta/espagueti_linea_yogures_actual_clasico.pdf"><img src=".github/assets/avances/avance-6.jpg" alt="Diagrama de espagueti de la línea de yogurts" width="100%"></a>
      <sub>Recorridos diarios de personas y montacargas en la línea de yogurts.</sub>
    </td>
  </tr>
</table>

**Documentos**

| Módulo | Documento | Contenido |
|:--|:--|:--|
| Transformación digital | [Recetas y procesos de la planta](01_transformacion-digital/isa88/Recetas_y_procesos_planta.pdf) | Fórmulas, procedimientos, parámetros, PCC y equipos de las tres líneas |
| Transformación digital | [Modelo ISA-88](01_transformacion-digital/isa88) | Modelo físico, modelo procedimental y [recetas maestras](01_transformacion-digital/isa88/recetas-maestras) de los 9 productos, con [diagramas](01_transformacion-digital/isa88/diagramas) |
| Transformación digital | [Recetas de la línea de yogurts](01_transformacion-digital/isa88/recetas/Recetas_linea_yogures_v1.8.pdf) | Fresa, natural y griego, de la recepción al despacho |
| Transformación digital | [Recetas básicas de la planta](01_transformacion-digital/isa88/recetas/Recetas_basicas_planta_v1.0.pdf) | Yogurts, quesos y leche UHT con sus máquinas |
| Transformación digital | [P&ID de la empresa base](01_transformacion-digital/instrumentacion/PID_Planta_Lactea_Grupo6_Empresa_Base.pdf) | Tuberías, instrumentos y nivel de automatización de cada equipo |
| Transformación digital | [Comunicación y datos según ISA-95](01_transformacion-digital/arquitectura-isa95/ISA95_Comunicacion_Datos_Empresa_Base.pdf) | Qué se registra hoy, dónde y quién decide, por niveles |
| Gestión de la producción | [Layout de la línea de yogurts](02_gestion-produccion/distribucion-planta/layout_linea_yogures_actual_clasico.pdf) | La línea de yogurts dentro de la nave, con paletizado manual |
| Planeación del proyecto | [EDT](03_planeacion-proyecto/edt-cronograma/EDT_Completo_v1.0.pdf) y [cronograma](03_planeacion-proyecto/edt-cronograma/Cronograma_Planta_Lactea_v1.0.pdf) | Estructura de desglose del trabajo y plan de 12 meses |
| Planeación del proyecto | [Estado financiero](03_planeacion-proyecto/evaluacion-financiera/Estado_Financiero.pdf) | OPEX, CAPEX, estado gerencial de la línea de yogurts, estado financiero de la planta y evaluación de la propuesta |
| Planeación del proyecto | [Base de cotización](03_planeacion-proyecto/presupuesto/cotizaciones/Mekvra_Base_Cotizacion.pdf) | Costeo de servicios, licencias y equipos, y propuesta económica para el cliente |

<sub>Las cifras son valores de diseño o de simulación, no medidas en planta.</sub>

<br>

<a id="equipo"></a>
<img src=".github/assets/secciones/seccion-4.png" alt="04 · Equipo" width="100%">

<p align="center">
  <a href="https://github.com/lmendozar2001"><img src=".github/assets/equipo/integrante-luis.jpg" width="19%" alt="Luis Alberto Mendoza, líder de automatización"></a>
  <a href="https://github.com/Kreiop"><img src=".github/assets/equipo/integrante-pablo.jpg" width="19%" alt="Pablo de Jesús Arcila Mora, líder de ingeniería"></a>
  <a href="https://github.com/david-pi3141"><img src=".github/assets/equipo/integrante-david.jpg" width="19%" alt="David Steven Pinzón Hernández, líder de gestión y administración"></a>
  <a href="https://github.com/DanielCastro-02"><img src=".github/assets/equipo/integrante-daniel.jpg" width="19%" alt="Daniel Felipe Castro, gerencia, desarrollo y finanzas"></a>
  <a href="https://github.com/JananLC"><img src=".github/assets/equipo/integrante-janan.jpg" width="19%" alt="Janan Libardo Carreño Riaño, líder de instrumentación y software"></a>
</p>

<br>

<a id="estructura"></a>
<img src=".github/assets/secciones/seccion-5.png" alt="05 · Estructura" width="100%">

El repositorio sigue los módulos del curso. Cada carpeta tiene su propio `README.md` con sus entregables.

| | Módulo | Contenido |
|:--:|:--|:--|
| `00` | [**Gestión del equipo**](00_gestion-equipo) | Actas, roles y evidencias de trabajo colaborativo |
| `01` | [**Transformación digital**](01_transformacion-digital) | Modelo y recetas ISA-88, arquitectura ISA-95 e instrumentación |
| `02` | [**Gestión de la producción**](02_gestion-produccion) | Tecnomatix, VSM, layout, espagueti, indicadores y MES/ERP |
| `03` | [**Planeación del proyecto**](03_planeacion-proyecto) | EDT, cronograma, presupuesto, flujo de caja y propuesta de valor |
| `04` | [**Controladores**](04_controladores) | Grafcet y lógica Ladder en Logix Emulate |
| `05` | [**Gemelo digital**](05_gemelo-digital) | Gemelo digital en Siemens NX |
| `06` | [**Celda robotizada**](06_celda-robotizada) | Diseño, simulación en RobotStudio y análisis de riesgos |
| `07` | [**SCADA**](07_scada) | HMI ISA-101 en Ignition y comunicación OPC |
| `08` | [**Investigación**](08_investigacion) | Proceso lácteo, variables de operación y fuentes |
| `web` | [**Página web**](web) | Sitio en Astro, publicado automáticamente con GitHub Pages |


<br>

<p align="center">
  <img src=".github/assets/avatar.png" width="56" alt="">
  <br>
  <b>MEKVRA S.A.S</b>
  <br>
  <sub>Automatización e integración industrial · Bogotá, Colombia</sub>
</p>
