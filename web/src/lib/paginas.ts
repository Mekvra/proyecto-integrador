// Páginas del sitio, en el orden del menú. Cada sección de la propuesta tiene su propia página.
export interface Pagina {
  slug: string;
  num: string;
  label: string;
  resumen: string;
}

export const PAGINAS: Pagina[] = [
  { slug: 'inicio', num: '00', label: 'Inicio', resumen: '' },
  { slug: 'empresa', num: '01', label: 'Empresa', resumen: 'Mekvra S.A.S y su cliente, Lácteos Altos de Teusacá: una planta de 150.000 L/día.' },
  { slug: 'automatizacion', num: '02', label: 'Automatización', resumen: 'La celda de paletizado con sensores, PLC y tablero en tiempo real.' },
  { slug: 'proceso', num: '03', label: 'Proceso', resumen: 'Tronco común y tres líneas: yogurts, quesos y leche UHT, con sus variables críticas.' },
  { slug: 'arquitectura', num: '04', label: 'Arquitectura', resumen: 'La pirámide ISA-95: del sensor en planta al ERP de la empresa.' },
  { slug: 'evidencias', num: '05', label: 'Evidencias', resumen: 'Indicadores de la línea de yogurts y uso de cada equipo simulado.' },
  { slug: 'simulacion', num: '06', label: 'Simulación', resumen: 'Modelos de Tecnomatix, VSM, distribución en planta y espagueti.' },
  { slug: 'planeacion', num: '07', label: 'Planeación', resumen: 'EDT y cronograma de doce meses, de la ingeniería a la operación.' },
  { slug: 'modulos', num: '08', label: 'Módulos', resumen: 'Los entregables de cada módulo del curso y la propuesta de valor.' },
  { slug: 'equipo', num: '09', label: 'Equipo', resumen: 'Las cinco personas detrás de Mekvra S.A.S.' },
  { slug: 'mes', num: '10', label: 'MES', resumen: 'Plataforma de la planta: lotes, paros, calidad y archivos compartidos entre equipos.' },
];

const BASE = import.meta.env.BASE_URL.endsWith('/') ? import.meta.env.BASE_URL : `${import.meta.env.BASE_URL}/`;

export function url(slug: string) {
  return slug === 'inicio' ? BASE : `${BASE}${slug}/`;
}
