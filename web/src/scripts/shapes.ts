// Figuras del logo de partículas de Mekvra, dibujadas en un lienzo de 200 × 200.
// Cada figura se rellena en un canvas oculto y luego se muestrea en una retícula:
// cada punto relleno se convierte en el destino de una tesela.

export const SIZE = 200;

// Monograma: una "M" cuyo vértice central es una articulación, como el eje de un brazo robot.
export const MONOGRAM_PATH =
  'M10 190V10h40l50 85 50-85h40v180h-40V80l-38 62H88L50 80v110z';
export const JOINT = { x: 100, y: 128, r: 22, hole: 9 };

type Draw = (ctx: CanvasRenderingContext2D) => void;

export interface Shape {
  id: string;
  label: string;
  draw: Draw;
}

const monogram: Draw = (ctx) => {
  ctx.fill(new Path2D(MONOGRAM_PATH));
  ctx.beginPath();
  ctx.arc(JOINT.x, JOINT.y, JOINT.r, 0, Math.PI * 2);
  ctx.arc(JOINT.x, JOINT.y, JOINT.hole, 0, Math.PI * 2, true);
  ctx.fill('evenodd');
};

const gear: Draw = (ctx) => {
  const cx = 100;
  const cy = 100;
  const teeth = 12;
  ctx.beginPath();
  for (let i = 0; i < teeth; i++) {
    const a = (i / teeth) * Math.PI * 2;
    const w = 0.13;
    const pts = [
      [a - w * 1.4, 62],
      [a - w, 86],
      [a + w, 86],
      [a + w * 1.4, 62],
    ];
    for (const [ang, r] of pts) {
      ctx.lineTo(cx + Math.cos(ang) * r, cy + Math.sin(ang) * r);
    }
    const next = ((i + 1) / teeth) * Math.PI * 2;
    ctx.arc(cx, cy, 62, a + w * 1.4, next - w * 1.4);
  }
  ctx.closePath();
  ctx.moveTo(cx + 26, cy);
  ctx.arc(cx, cy, 26, 0, Math.PI * 2, true);
  ctx.fill('evenodd');
};

const robotArm: Draw = (ctx) => {
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  // base
  ctx.beginPath();
  ctx.moveTo(52, 192);
  ctx.lineTo(148, 192);
  ctx.lineTo(132, 168);
  ctx.lineTo(68, 168);
  ctx.closePath();
  ctx.fill();
  // eslabones
  ctx.lineWidth = 22;
  ctx.beginPath();
  ctx.moveTo(100, 160);
  ctx.lineTo(72, 84);
  ctx.stroke();
  ctx.lineWidth = 17;
  ctx.beginPath();
  ctx.moveTo(72, 84);
  ctx.lineTo(150, 50);
  ctx.stroke();
  // articulaciones
  for (const [x, y, r] of [
    [100, 160, 17],
    [72, 84, 15],
    [150, 50, 11],
  ]) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  // pinza
  ctx.lineWidth = 7;
  ctx.beginPath();
  ctx.moveTo(150, 50);
  ctx.lineTo(166, 78);
  ctx.moveTo(156, 44);
  ctx.lineTo(182, 58);
  ctx.stroke();
};

const pyramid: Draw = (ctx) => {
  // Cinco niveles ISA-95, de campo (abajo) a empresa (arriba).
  const levels = 5;
  const top = 18;
  const bottom = 186;
  const gap = 7;
  const h = (bottom - top - gap * (levels - 1)) / levels;
  const halfW = (y: number) => 18 + ((y - top) / (bottom - top)) * 80;
  for (let i = 0; i < levels; i++) {
    const y0 = top + i * (h + gap);
    const y1 = y0 + h;
    ctx.beginPath();
    ctx.moveTo(100 - halfW(y0), y0);
    ctx.lineTo(100 + halfW(y0), y0);
    ctx.lineTo(100 + halfW(y1), y1);
    ctx.lineTo(100 - halfW(y1), y1);
    ctx.closePath();
    ctx.fill();
  }
};

const milkDrop: Draw = (ctx) => {
  ctx.beginPath();
  ctx.moveTo(100, 10);
  ctx.bezierCurveTo(88, 40, 40, 88, 40, 128);
  ctx.arc(100, 128, 60, Math.PI, 0, true);
  ctx.bezierCurveTo(160, 88, 112, 40, 100, 10);
  ctx.closePath();
  // brillo interior, recortado
  ctx.moveTo(78, 118);
  ctx.arc(72, 118, 6, 0, Math.PI * 2, true);
  ctx.fill('evenodd');
};

export const SHAPES: Shape[] = [
  { id: 'monograma', label: 'Mekvra', draw: monogram },
  { id: 'engranaje', label: 'Mecatrónica', draw: gear },
  { id: 'brazo', label: 'Robótica', draw: robotArm },
  { id: 'isa95', label: 'Integración ISA-95', draw: pyramid },
  { id: 'gota', label: 'Industria láctea', draw: milkDrop },
];

// Muestrea una figura en una retícula y devuelve exactamente `count` puntos (en coordenadas 0–200).
export function samplePoints(shape: Shape, count: number, step = 4): Array<[number, number]> {
  const canvas = document.createElement('canvas');
  canvas.width = SIZE;
  canvas.height = SIZE;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  if (!ctx) return [];
  ctx.fillStyle = '#fff';
  ctx.strokeStyle = '#fff';
  shape.draw(ctx);
  const { data } = ctx.getImageData(0, 0, SIZE, SIZE);

  const cells: Array<[number, number]> = [];
  for (let y = step / 2; y < SIZE; y += step) {
    for (let x = step / 2; x < SIZE; x += step) {
      const alpha = data[(Math.floor(y) * SIZE + Math.floor(x)) * 4 + 3];
      if (alpha > 128) cells.push([x, y]);
    }
  }
  if (cells.length === 0) return [];

  shuffle(cells);
  const out: Array<[number, number]> = [];
  for (let i = 0; i < count; i++) {
    const [x, y] = cells[i % cells.length];
    // Si hay más teselas que celdas, las repetidas se apilan en la misma celda (se ve como tesela más densa).
    out.push([x, y]);
  }
  return out;
}

export function shuffle<T>(arr: T[]): T[] {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
