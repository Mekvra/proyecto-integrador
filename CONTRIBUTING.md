# Guía para aportar al repositorio

Esta guía es para todo el equipo, incluso si nunca has usado Git.

## Opción A: desde el navegador (sin instalar nada)

1. Entra a la carpeta de tu módulo en GitHub (por ejemplo `02_gestion-produccion/vsm`).
2. Pulsa **Add file → Upload files** y arrastra tus archivos.
3. Abajo, en **Commit changes**, escribe qué subiste. Ejemplo: `VSM estado actual línea de quesos`.
4. Pulsa **Commit changes**. Listo.

Para editar un texto (por ejemplo el README de tu módulo), abre el archivo y pulsa el lápiz ✏️.

## Opción B: con Git en tu computador

```bash
git clone https://github.com/Mekvra/proyecto-integrador.git
cd proyecto-integrador
# ... agregas o editas archivos ...
git add .
git commit -m "Describe aquí lo que hiciste"
git pull --rebase
git push
```

## Reglas del equipo

- **Cada archivo en la carpeta de su módulo.** Si no sabes dónde va, pregunta en el grupo.
- **Nombres de archivo claros, sin espacios ni tildes:** `vsm-actual-quesos.pdf`, no `VSM final (2) versión buena.pdf`.
- **Versiones con fecha, no con "final":** `2026-10-02_presupuesto.xlsx`.
- **Sube también el PDF** de cada documento editable (.docx, .xlsx, .vsdx), para que se pueda ver en GitHub sin descargar.
- **Mensajes de commit que expliquen el cambio:** `Agrega recetas ISA-88 de queso campesino`, no `cambios`.
- **Archivos pesados:** GitHub no acepta archivos de más de 100 MB. Para modelos grandes (Tecnomatix, NX, RobotStudio), comprímelos en .zip. Si aún pasan del límite, súbelos al Drive del equipo y deja el enlace en el README del módulo.
- **Nada de contraseñas ni datos personales** en el repositorio.

## Actualizar la página web

El contenido de la página está en `web/src/content/`, en archivos de texto Markdown (`.md`). Para cambiar un texto de la web, edita ese archivo y la página se actualiza sola en uno o dos minutos. No hace falta tocar el diseño.
