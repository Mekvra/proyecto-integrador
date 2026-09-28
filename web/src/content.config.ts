// Definición del contenido editable de la página.
// Para cambiar textos, edita los archivos .md dentro de src/content/ (no hace falta tocar este archivo).
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Textos largos de la página: empresa, reto, propuesta, aprendizaje...
const textos = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/textos' }),
  schema: z.object({
    titulo: z.string(),
    resumen: z.string().optional(),
    niveles: z
      .array(
        z.object({
          codigo: z.string(),
          nombre: z.string(),
          herramienta: z.string(),
          funcion: z.string(),
          sube: z.array(z.string()).default([]),
          baja: z.array(z.string()).default([]),
        }),
      )
      .optional(),
  }),
});

const etapa = z.object({
  nombre: z.string(),
  tipo: z.string(),
  variables: z.array(z.string()).default([]),
});

// Líneas de producción (una por archivo). El orden define el orden de las pestañas.
const lineas = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/lineas' }),
  schema: z.object({
    nombre: z.string(),
    orden: z.number(),
    detallada: z.boolean().default(false),
    resumen: z.string(),
    etapas: z.array(etapa),
  }),
});

// Módulos del curso con su estado de avance.
const modulos = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/modulos' }),
  schema: z.object({
    numero: z.string(),
    titulo: z.string(),
    estado: z.enum(['pendiente', 'en-desarrollo', 'completado']),
    responsables: z.string(),
    carpeta: z.string(),
    entregables: z.array(z.string()),
  }),
});

// Integrantes del equipo. El cuerpo del archivo es su reflexión individual.
const equipo = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/equipo' }),
  schema: z.object({
    numero: z.number(),
    nombre: z.string(),
    rol: z.string(),
    github: z.string(),
  }),
});

export const collections = { textos, lineas, modulos, equipo };
