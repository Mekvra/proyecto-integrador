// MES de Lácteos Altos de Teusacá: lógica de la plataforma (Supabase).
// Vistas por rol, del operario a la gerencia. Todo lo que se muestra sale de los registros de la base de datos:
// no hay cifras inventadas. Los textos se pintan con textContent (sin HTML de usuarios).
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

type Fila = Record<string, any>;
type Kid = Node | string | number | null | undefined | false | Kid[];

// ---------------------------------------------------------------- utilidades
function h(tag: string, p: Record<string, any> = {}, ...kids: Kid[]): HTMLElement {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(p)) {
    if (v == null || v === false) continue;
    if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
    else if (k === 'class') el.className = v;
    else if (k === 'style') el.setAttribute('style', v);
    else if (k === 'value' || k === 'checked' || k === 'disabled' || k === 'required' || k === 'hidden' || k === 'selected') (el as any)[k] = v;
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  const add = (c: Kid) => {
    if (c == null || c === false) return;
    if (Array.isArray(c)) c.forEach(add);
    else el.append(c instanceof Node ? c : String(c));
  };
  kids.forEach(add);
  return el;
}
const svgNS = 'http://www.w3.org/2000/svg';
function s(tag: string, attrs: Record<string, any> = {}, ...kids: (SVGElement | string)[]): SVGElement {
  const el = document.createElementNS(svgNS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) el.setAttribute(k, String(v));
  kids.forEach((c) => el.append(c));
  return el;
}

const miles = (n: number, d = 0) => (Number.isFinite(n) ? n.toLocaleString('es-CO', { maximumFractionDigits: d, minimumFractionDigits: d }) : '—');
const pct = (x: number | null) => (x == null || !Number.isFinite(x) ? '—' : `${miles(x * 100, 1)} %`);
const fecha = (iso: string) => new Date(iso).toLocaleString('es-CO', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
const hora = (iso: string | number) => new Date(iso).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
const hoyISO = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};
function dur(ms: number) {
  const m = Math.max(0, Math.floor(ms / 60000));
  if (ms < 60000) return `${Math.max(0, Math.floor(ms / 1000))} s`;
  if (m < 60) return `${m} min`;
  const hh = Math.floor(m / 60);
  if (hh < 24) return `${hh} h ${String(m % 60).padStart(2, '0')} min`;
  return `${Math.floor(hh / 24)} d ${hh % 24} h`;
}
const inicioDia = (d = new Date()) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();

function turnoDe(d = new Date()) {
  const hh = d.getHours();
  if (hh >= 6 && hh < 14) return { nombre: 'Mañana', ini: 6, fin: 14 };
  if (hh >= 14 && hh < 22) return { nombre: 'Tarde', ini: 14, fin: 22 };
  return { nombre: 'Noche', ini: 22, fin: 6 };
}
function finTurno(d = new Date()) {
  const t = turnoDe(d);
  const f = new Date(d);
  f.setHours(t.fin, 0, 0, 0);
  if (f.getTime() <= d.getTime()) f.setDate(f.getDate() + 1);
  return f.getTime();
}

// ---------------------------------------------------------------- catálogos
const LINEAS = ['Yogurts', 'Quesos', 'Leche UHT'];
const LINEAS_PLANTA = ['Recepción', ...LINEAS];
const PRODUCTOS: Record<string, string[]> = {
  Yogurts: ['YF · Yogurt con fresa', 'YN · Yogurt natural', 'YG · Yogurt griego'],
  Quesos: ['QM · Mozzarella', 'QQ · Quesillo', 'QD · Doble crema'],
  'Leche UHT': ['LE · Leche entera', 'LD · Leche descremada', 'LC · Leche con chocolate'],
};
const ESTADOS = ['En marcha', 'Parada', 'Cambio', 'Limpieza', 'Falla', 'Mantenimiento'] as const;
const CLASE: Record<string, string> = {
  'En marcha': 'e-marcha', Parada: 'e-parada', Cambio: 'e-cambio', Limpieza: 'e-limpieza', Falla: 'e-falla', Mantenimiento: 'e-mant',
};
const CAUSAS_ESTADO: Record<string, string[]> = {
  'En marcha': ['Producción'],
  Parada: ['Sin orden', 'Fin de turno', 'Falta de material', 'Falta de personal', 'Espera de calidad'],
  Cambio: ['Cambio de formato', 'Cambio de producto'],
  Limpieza: ['Limpieza CIP', 'Limpieza manual'],
  Falla: ['Falla mecánica', 'Falla eléctrica', 'Falla de instrumentación', 'Atasco'],
  Mantenimiento: ['Preventivo', 'Correctivo', 'Calibración'],
};
// Tiempo que no cuenta como pérdida: la máquina no tenía producción programada.
const NO_PROGRAMADO = new Set(['Sin orden', 'Fin de turno']);
const CAUSAS_PARO = ['Falla', 'Cambio de formato', 'Limpieza CIP', 'Falta de material', 'Mantenimiento', 'Otra'];
const PRUEBAS = ['pH', 'Acidez (% ácido láctico)', 'Grasa (%)', 'Sólidos (%)', 'Temperatura (°C)', 'Peso de llenado (g)', 'Antibióticos', 'Microbiología', 'Sensorial'];
const ESTADOS_ORDEN = ['Planeada', 'Liberada', 'En ejecución', 'Terminada', 'Cerrada'];
const ROLES = ['Operario', 'Supervisor', 'Calidad', 'Mantenimiento', 'Jefe de planta', 'Gerencia', 'Administrador'];
const PLANEAN = ['Supervisor', 'Jefe de planta', 'Administrador'];
const DISPONEN = ['Calidad', 'Jefe de planta', 'Administrador'];

const ICONOS: Record<string, string> = {
  planta: 'M3 21V10l5 3V10l5 3V6l8 4v11z',
  turno: 'M12 3a9 9 0 1 0 0 18a9 9 0 0 0 0-18zm0 4v5l3 2',
  ordenes: 'M5 4h14v16H5zM9 9h6M9 13h6M9 17h3',
  lotes: 'M4 8l8-4l8 4l-8 4zM4 8v8l8 4l8-4V8M12 12v8',
  calidad: 'M9 12l2 2l4-4M12 3l7 3v5c0 5-3 8-7 10c-4-2-7-5-7-10V6z',
  mantenimiento: 'M14.5 6.5a4 4 0 0 0-5 5L4 17l3 3l5.5-5.5a4 4 0 0 0 5-5l-2.5 2.5l-2-.5l-.5-2z',
  indicadores: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  archivos: 'M4 4h6l2 2h8v14H4zM12 10v6M9 13l3 3l3-3',
  usuarios: 'M9 11a4 4 0 1 0 0-8a4 4 0 0 0 0 8zM2 21c0-4 3-6 7-6s7 2 7 6M16 3.5a4 4 0 0 1 0 7.5M22 21c0-3-1.5-5-4-5.7',
};

interface Vista { id: string; titulo: string; grupo: string; roles: string[]; montar: (c: HTMLElement) => void; refrescar: () => void }

// ---------------------------------------------------------------- arranque
const raiz = document.querySelector<HTMLElement>('[data-mes]')!;
const pantallaLogin = raiz.querySelector<HTMLElement>('[data-vista="login"]')!;
const pantallaApp = raiz.querySelector<HTMLElement>('[data-vista="app"]')!;
const loginMsg = raiz.querySelector<HTMLElement>('[data-login-msg]')!;
const cont = raiz.querySelector<HTMLElement>('[data-cont]')!;
const menu = raiz.querySelector<HTMLElement>('[data-menu]')!;
const tituloEl = raiz.querySelector<HTMLElement>('[data-titulo]')!;
const grupoEl = raiz.querySelector<HTMLElement>('[data-grupo]')!;
const avisoEl = raiz.querySelector<HTMLElement>('[data-aviso]')!;
const dialogo = raiz.querySelector<HTMLDialogElement>('[data-dialogo]')!;

const url = raiz.dataset.url, key = raiz.dataset.key;
const sb: SupabaseClient | null = url && key ? createClient(url, key) : null;

const D: Record<string, Fila[]> = { maquinas: [], eventos_maquina: [], ordenes: [], lotes: [], paros: [], calidad: [], perfiles: [], archivos: [] };
let yo = '';
let miRol = '';
let rolVista = '';
let vista: Vista | null = null;
const nombre = (id: string) => D.perfiles.find((p) => p.id === id)?.nombre ?? '—';
const puede = (roles: string[]) => roles.includes(miRol);

let avisoT = 0;
function aviso(t: string, error = false) {
  avisoEl.textContent = t;
  avisoEl.toggleAttribute('data-error', error);
  avisoEl.hidden = false;
  clearTimeout(avisoT);
  avisoT = window.setTimeout(() => (avisoEl.hidden = true), error ? 9000 : 3500);
}

// ---------------------------------------------------------------- datos
async function cargar(t: string) {
  if (!sb) return;
  let q;
  if (t === 'maquinas') q = sb.from(t).select('*').order('posicion');
  else if (t === 'eventos_maquina') {
    const desde = new Date(Date.now() - 31 * 864e5).toISOString();
    q = sb.from(t).select('*').or(`fin.is.null,fin.gte.${desde}`).order('inicio').limit(10000);
  } else if (t === 'ordenes') q = sb.from(t).select('*').order('fecha', { ascending: false }).order('id', { ascending: false }).limit(500);
  else if (t === 'perfiles') q = sb.from(t).select('*').order('creado');
  else if (t === 'archivos') {
    const { data, error } = await sb.storage.from('mes-archivos').list('', { limit: 300, sortBy: { column: 'created_at', order: 'desc' } });
    if (!error) D.archivos = (data ?? []).filter((o) => o.name !== '.emptyFolderPlaceholder') as Fila[];
    return;
  } else q = sb.from(t).select('*').order('creado', { ascending: false }).limit(1000);
  const { data, error } = await q;
  if (error) return aviso(`No se pudo leer ${t}: ${error.message}`, true);
  D[t] = data ?? [];
}

const pendientes = new Set<string>();
let recargaT = 0;
function recargar(t: string) {
  pendientes.add(t);
  clearTimeout(recargaT);
  recargaT = window.setTimeout(async () => {
    const ts = [...pendientes];
    pendientes.clear();
    await Promise.all(ts.map(cargar));
    if (ts.includes('perfiles')) {
      const p = D.perfiles.find((x) => x.id === yo);
      if (p && p.rol !== miRol) { miRol = p.rol; rolVista = p.rol; pintarUsuario(); pintarMenu(); }
    }
    vista?.refrescar();
    pulsoVivo();
  }, 250);
}

async function guardar(p: PromiseLike<{ error: any }>, ok: string, ...tablas: string[]) {
  const { error } = await p;
  if (error) { aviso(`No se guardó: ${error.message}`, true); return false; }
  aviso(ok);
  tablas.forEach(recargar);
  return true;
}

// ---------------------------------------------------------------- tiempos de máquina
/** Milisegundos de cada estado y causa de una máquina entre a y b (según el historial de eventos). */
function tiempos(maq: string | null, a: number, b: number) {
  const est: Record<string, number> = {};
  const causa: Record<string, number> = {};
  const fallas: number[] = [];
  for (const e of D.eventos_maquina) {
    if (maq && e.maquina !== maq) continue;
    const i = Math.max(a, Date.parse(e.inicio));
    const f = Math.min(b, e.fin ? Date.parse(e.fin) : Date.now());
    if (f <= i) continue;
    est[e.estado] = (est[e.estado] ?? 0) + (f - i);
    if (e.estado !== 'En marcha') causa[e.causa || e.estado] = (causa[e.causa || e.estado] ?? 0) + (f - i);
    if (e.estado === 'Falla' && Date.parse(e.inicio) >= a) fallas.push((e.fin ? Date.parse(e.fin) : Date.now()) - Date.parse(e.inicio));
  }
  let noProg = 0;
  for (const e of D.eventos_maquina) {
    if ((maq && e.maquina !== maq) || e.estado !== 'Parada' || !NO_PROGRAMADO.has(e.causa)) continue;
    const i = Math.max(a, Date.parse(e.inicio));
    const f = Math.min(b, e.fin ? Date.parse(e.fin) : Date.now());
    if (f > i) noProg += f - i;
  }
  const total = Object.values(est).reduce((x, y) => x + y, 0);
  const marcha = est['En marcha'] ?? 0;
  const programado = total - noProg;
  return { est, causa, fallas, total, marcha, programado, disp: programado > 60000 ? marcha / programado : null };
}

/** Tira de estados de una máquina entre a y b. */
function tira(maq: string, a: number, b: number, clase = 'tira') {
  const el = h('div', { class: clase, role: 'img', 'aria-label': `Historial de estados de ${maq}` });
  for (const e of D.eventos_maquina) {
    if (e.maquina !== maq) continue;
    const i = Math.max(a, Date.parse(e.inicio));
    const f = Math.min(b, e.fin ? Date.parse(e.fin) : Date.now());
    if (f <= i) continue;
    el.append(h('i', {
      class: CLASE[e.estado],
      style: `left:${((i - a) / (b - a)) * 100}%;width:${Math.max(0.15, ((f - i) / (b - a)) * 100)}%`,
      title: `${e.estado}${e.causa ? ` · ${e.causa}` : ''} · ${hora(i)}–${hora(f)} (${dur(f - i)})`,
    }));
  }
  return el;
}

// ---------------------------------------------------------------- piezas de interfaz
const chip = (estado: string, texto = estado) => h('span', { class: `chip ${CLASE[estado] ?? 'e-' + estado.toLowerCase().replace(/[^a-z]/g, '')}` }, texto);
const chipOrden = (e: string) => h('span', { class: `chip o-${e.toLowerCase().replace(/[^a-z]/g, '')}` }, e);
const chipLote = (e: string) => h('span', { class: `chip l-${e.toLowerCase().replace(/[^a-z]/g, '')}` }, e);
const vivo = (desde: string) => h('span', { class: 'vivo', 'data-desde': desde }, dur(Date.now() - Date.parse(desde)));
const vacio = (t: string) => h('p', { class: 'vacio' }, t);
const tarjeta = (titulo: string | null, ...kids: Kid[]) => h('section', { class: 'm-card' }, titulo ? h('h3', { class: 'm-card-t mono' }, titulo) : null, ...kids);
function kpi(etq: string, valor: string, sub = '', clase = '') {
  return h('div', { class: `kpi ${clase}` }, h('span', { class: 'mono' }, etq), h('b', {}, valor), sub ? h('small', {}, sub) : null);
}
function campo(etq: string, control: HTMLElement, ancho = '') {
  return h('label', { class: `campo ${ancho}` }, h('span', { class: 'mono' }, etq), control);
}
function sel(name: string, opciones: (string | [string, string])[], valor?: string) {
  return h('select', { name }, opciones.map((o) => {
    const [v, t] = Array.isArray(o) ? o : [o, o];
    return h('option', { value: v, selected: v === valor }, t);
  })) as HTMLSelectElement;
}
const inp = (name: string, p: Record<string, any> = {}) => h('input', { name, ...p }) as HTMLInputElement;
const boton = (t: string, onclick: (e: Event) => void, clase = 'm-btn sec') => h('button', { type: 'button', class: clase, onclick }, t);
function opcionesActualizar(s: HTMLSelectElement, opciones: (string | [string, string])[]) {
  const v = s.value;
  s.replaceChildren(...opciones.map((o) => {
    const [val, t] = Array.isArray(o) ? o : [o, o];
    return h('option', { value: val, selected: val === v }, t);
  }));
}
function tabla(cols: [string, string, ((f: Fila) => Kid)?][], filas: Fila[], extra?: (f: Fila) => Kid, alClic?: (f: Fila, tr: HTMLElement) => void) {
  if (!filas.length) return vacio('Sin registros todavía.');
  return h('div', { class: 'm-tabla' }, h('table', {},
    h('thead', {}, h('tr', {}, cols.map(([, t]) => h('th', {}, t)), extra ? h('th', {}) : null)),
    h('tbody', {}, filas.map((f) => {
      const tr = h('tr', alClic ? { class: 'clic', tabindex: 0 } : {},
        cols.map(([k, , fn]) => h('td', { 'data-k': k }, fn ? fn(f) : String(f[k] ?? ''))),
        extra ? h('td', { class: 'acc' }, extra(f)) : null);
      if (alClic) {
        tr.addEventListener('click', (e) => { if (!(e.target as HTMLElement).closest('button')) alClic(f, tr); });
        tr.addEventListener('keydown', (e) => { if ((e as KeyboardEvent).key === 'Enter') alClic(f, tr); });
      }
      return tr;
    })),
  ));
}
function csv(nombreArchivo: string, cols: [string, string][], filas: Fila[]) {
  const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const txt = [cols.map(([, n]) => esc(n)).join(';'), ...filas.map((f) => cols.map(([k]) => esc(k === 'autor' ? nombre(f.autor) : f[k])).join(';'))].join('\n');
  const a = h('a', { href: URL.createObjectURL(new Blob(['﻿' + txt], { type: 'text/csv;charset=utf-8' })), download: `${nombreArchivo}_${hoyISO()}.csv` }) as HTMLAnchorElement;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
function borrarPropio(t: string, f: Fila) {
  if (f.autor !== yo) return null;
  return boton('Borrar', async () => {
    if (!confirm('¿Borrar este registro? No se puede deshacer.')) return;
    guardar(sb!.from(t).delete().eq('id', f.id), 'Registro borrado.', t);
  }, 'm-btn mini peligro');
}

// Barras horizontales (Pareto)
function barras(datos: [string, number][], fmt: (n: number) => string, color = 'var(--orange)') {
  if (!datos.length) return vacio('Sin datos en el periodo.');
  const max = Math.max(...datos.map(([, v]) => v));
  const total = datos.reduce((x, [, v]) => x + v, 0);
  let acum = 0;
  return h('ol', { class: 'pareto' }, datos.map(([k, v]) => {
    acum += v;
    return h('li', {},
      h('span', { class: 'p-k' }, k),
      h('span', { class: 'p-bar' }, h('i', { style: `width:${(v / max) * 100}%;background:${color}` })),
      h('span', { class: 'p-v mono' }, fmt(v)),
      h('span', { class: 'p-a mono' }, `${Math.round((acum / total) * 100)} %`));
  }));
}

// ---------------------------------------------------------------- diálogo de estado de máquina
function abrirMaquina(codigo: string) {
  const m = D.maquinas.find((x) => x.codigo === codigo);
  if (!m) return;
  let estado: string = m.estado;
  const causa = sel('causa', CAUSAS_ESTADO[estado], m.causa);
  const ordenesLinea = () => [['', '— Sin orden —'] as [string, string], ...D.ordenes
    .filter((o) => o.linea === m.linea && ['Liberada', 'En ejecución'].includes(o.estado))
    .map((o) => [o.codigo, `${o.codigo} · ${o.producto} · ${miles(o.litros_plan)} L`] as [string, string])];
  const orden = sel('orden', ordenesLinea(), m.orden);
  const botones = h('div', { class: 'estados-btn' }, ESTADOS.map((e) => h('button', {
    type: 'button', class: `est-btn ${CLASE[e]}`, 'aria-pressed': String(e === estado),
    onclick: (ev: Event) => {
      estado = e;
      botones.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b === ev.currentTarget)));
      opcionesActualizar(causa, CAUSAS_ESTADO[e]);
      causa.value = CAUSAS_ESTADO[e][0];
    },
  }, h('i', {}), e)));
  const hoy0 = inicioDia();
  const t = tiempos(codigo, hoy0, Date.now());
  dialogo.replaceChildren(h('form', { method: 'dialog', class: 'dlg' },
    h('header', {},
      h('div', {}, h('span', { class: 'mono gold' }, `${m.codigo} · ${m.linea} · ${m.etapa}`), h('h3', {}, m.nombre)),
      h('button', { type: 'submit', value: 'cancelar', class: 'cerrar', 'aria-label': 'Cerrar' }, '×')),
    h('div', { class: 'dlg-ahora' }, chip(m.estado), h('span', {}, m.causa), h('span', { class: 'mono' }, 'hace ', vivo(m.desde))),
    tira(codigo, hoy0, Date.now(), 'tira grande'),
    h('p', { class: 'dlg-nota mono' }, `Hoy: ${pct(t.disp)} en marcha del tiempo programado · ${t.fallas.length} fallas`),
    h('span', { class: 'mono etq' }, 'Nuevo estado'),
    botones,
    h('div', { class: 'm-form' }, campo('Causa', causa), campo('Orden en la máquina', orden)),
    h('footer', {},
      h('button', { type: 'submit', value: 'cancelar', class: 'm-btn sec' }, 'Cancelar'),
      h('button', { type: 'button', class: 'm-btn', onclick: async () => {
        const ok = await guardar(sb!.from('maquinas').update({ estado, causa: causa.value, orden: orden.value }).eq('codigo', codigo),
          `${codigo}: ${estado} · ${causa.value}`, 'maquinas', 'eventos_maquina');
        if (ok) dialogo.close();
      } }, 'Registrar cambio'))));
  dialogo.showModal();
}

async function cambiarEstado(codigo: string, estado: string, causa: string, orden?: string) {
  const cambio: Fila = { estado, causa };
  if (orden !== undefined) cambio.orden = orden;
  return guardar(sb!.from('maquinas').update(cambio).eq('codigo', codigo), `${codigo}: ${estado} · ${causa}`, 'maquinas', 'eventos_maquina');
}

// ================================================================= VISTAS
// ---------- Planta en vivo
function tileMaquina(m: Fila) {
  return h('button', { type: 'button', class: `maq ${CLASE[m.estado]}`, onclick: () => abrirMaquina(m.codigo) },
    h('span', { class: 'maq-top' }, h('span', { class: 'mono' }, m.codigo), chip(m.estado)),
    h('span', { class: 'maq-n' }, m.nombre),
    h('span', { class: 'maq-c' }, m.causa || '—', m.orden ? h('span', { class: 'mono' }, ` · ${m.orden}`) : null),
    h('span', { class: 'maq-t mono' }, vivo(m.desde)),
    tira(m.codigo, inicioDia(), Date.now()));
}
const vPlanta: Vista = {
  id: 'planta', titulo: 'Planta en vivo', grupo: 'Operación', roles: ROLES,
  montar(c) {
    c.append(h('div', { 'data-p-resumen': '' }), h('div', { class: 'leyenda mono' },
      ESTADOS.map((e) => h('span', { class: CLASE[e] }, h('i', {}), e)), h('span', { class: 'leyenda-n' }, 'Clic en una máquina para cambiar su estado. Las tiras muestran el día desde las 00:00.')),
    h('div', { 'data-p-lineas': '' }));
  },
  refrescar() {
    const c = cont;
    const cuenta = (e: string) => D.maquinas.filter((m) => m.estado === e).length;
    const t = tiempos(null, inicioDia(), Date.now());
    c.querySelector('[data-p-resumen]')!.replaceChildren(h('div', { class: 'kpis' },
      kpi('Máquinas en marcha', `${cuenta('En marcha')} / ${D.maquinas.length}`, 'ahora mismo', 'k-marcha'),
      kpi('En falla', String(cuenta('Falla')), cuenta('Falla') ? 'requieren mantenimiento' : 'sin fallas abiertas', cuenta('Falla') ? 'k-falla' : ''),
      kpi('Cambio o limpieza', String(cuenta('Cambio') + cuenta('Limpieza')), 'alistamientos en curso'),
      kpi('Disponibilidad hoy', pct(t.disp), 'tiempo en marcha / tiempo programado'),
      kpi('Órdenes en ejecución', String(D.ordenes.filter((o) => o.estado === 'En ejecución').length), `${D.ordenes.filter((o) => o.estado === 'Liberada').length} liberadas en espera`)));
    c.querySelector('[data-p-lineas]')!.replaceChildren(...LINEAS_PLANTA.map((l) => {
      const ms = D.maquinas.filter((m) => m.linea === l);
      if (!ms.length) return '';
      const tl = ms.map((m) => tiempos(m.codigo, inicioDia(), Date.now()));
      const marcha = tl.reduce((x, y) => x + y.marcha, 0), prog = tl.reduce((x, y) => x + y.programado, 0);
      return h('section', { class: 'linea' },
        h('header', {}, h('h3', {}, l), h('span', { class: 'mono' }, `${ms.filter((m) => m.estado === 'En marcha').length} de ${ms.length} en marcha · disponibilidad hoy ${pct(prog > 60000 ? marcha / prog : null)}`)),
        h('div', { class: 'maqs' }, ms.map(tileMaquina)));
    }));
  },
};

// ---------- Mi turno (operario)
let miMaquina = (() => { try { return localStorage.getItem('mes-maquina') ?? ''; } catch { return ''; } })();
const vTurno: Vista = {
  id: 'turno', titulo: 'Mi turno', grupo: 'Operación', roles: ['Operario', 'Supervisor', 'Jefe de planta', 'Administrador'],
  montar(c) {
    if (!D.maquinas.some((m) => m.codigo === miMaquina)) miMaquina = D.maquinas[0]?.codigo ?? '';
    const sm = sel('maquina', D.maquinas.map((m) => [m.codigo, `${m.codigo} · ${m.nombre}`] as [string, string]), miMaquina);
    sm.addEventListener('change', () => { miMaquina = sm.value; try { localStorage.setItem('mes-maquina', miMaquina); } catch {} vTurno.refrescar(); });

    // registrar lote rápido
    const fl = h('form', { class: 'm-form' }) as HTMLFormElement;
    const lOrden = sel('orden', []);
    const lLitros = inp('litros', { type: 'number', min: 1, step: 'any', required: true, inputmode: 'decimal' });
    const lCodigo = inp('codigo', { required: true, autocomplete: 'off' });
    fl.append(campo('Orden', lOrden), campo('Lote', lCodigo), campo('Litros', lLitros), h('button', { class: 'm-btn', type: 'submit' }, 'Registrar lote'));
    fl.addEventListener('submit', async (e) => {
      e.preventDefault();
      const o = D.ordenes.find((x) => x.codigo === lOrden.value);
      const m = D.maquinas.find((x) => x.codigo === miMaquina);
      const linea = o?.linea ?? (LINEAS.includes(m?.linea) ? m!.linea : 'Yogurts');
      if (await guardar(sb!.from('lotes').insert({ linea, producto: o?.producto ?? PRODUCTOS[linea][0], codigo: lCodigo.value.trim(), litros: Number(lLitros.value), orden: lOrden.value, estado: 'En proceso' }), 'Lote registrado.', 'lotes')) {
        fl.reset();
      }
    });

    // paro manual
    const fp = h('form', { class: 'm-form' }) as HTMLFormElement;
    const pCausa = sel('causa', CAUSAS_PARO), pMin = inp('minutos', { type: 'number', min: 1, step: 'any', required: true, inputmode: 'decimal' }), pNota = inp('nota', { placeholder: 'Opcional' });
    fp.append(campo('Causa', pCausa), campo('Minutos', pMin), campo('Nota', pNota), h('button', { class: 'm-btn sec', type: 'submit' }, 'Registrar paro'));
    fp.addEventListener('submit', async (e) => {
      e.preventDefault();
      const m = D.maquinas.find((x) => x.codigo === miMaquina);
      if (await guardar(sb!.from('paros').insert({ linea: m?.linea ?? '', equipo: `${m?.codigo} ${m?.nombre}`, causa: pCausa.value, minutos: Number(pMin.value), nota: pNota.value }), 'Paro registrado.', 'paros')) fp.reset();
    });

    c.append(h('div', { class: 'turno-grid' },
      h('div', { class: 'turno-col' },
        tarjeta('Mi equipo', campo('Máquina a cargo', sm), h('div', { 'data-t-maq': '' })),
        tarjeta('Órdenes de mi línea', h('div', { 'data-t-ord': '' }))),
      h('div', { class: 'turno-col' },
        tarjeta('Turno', h('div', { 'data-t-turno': '' })),
        tarjeta('Registrar lote', fl, h('p', { class: 'nota mono' }, 'El lote queda “En proceso” hasta que Calidad lo libere.')),
        tarjeta('Registrar paro corto', fp, h('p', { class: 'nota mono' }, 'Para paros que no se marcaron en la máquina (microparos, esperas).')),
        tarjeta('Mis registros de hoy', h('div', { 'data-t-mios': '' })))));
    (c as any)._lOrden = lOrden;
    (c as any)._lCodigo = lCodigo;
  },
  refrescar() {
    const c = cont;
    const m = D.maquinas.find((x) => x.codigo === miMaquina);
    const tn = turnoDe();
    const iniT = new Date(); if (tn.nombre === 'Noche' && iniT.getHours() < 6) iniT.setDate(iniT.getDate() - 1); iniT.setHours(tn.ini, 0, 0, 0);
    c.querySelector('[data-t-turno]')!.replaceChildren(h('div', { class: 'turno-info' },
      h('b', {}, tn.nombre), h('span', { class: 'mono' }, `${String(tn.ini).padStart(2, '0')}:00 – ${String(tn.fin).padStart(2, '0')}:00`),
      h('span', { class: 'mono' }, 'Faltan ', h('span', { 'data-hasta': String(finTurno()) }, dur(finTurno() - Date.now())))),
      m ? h('p', { class: 'mono nota' }, `En este turno ${m.codigo} lleva ${dur(tiempos(m.codigo, iniT.getTime(), Date.now()).marcha)} en marcha.`) : null);
    if (m) {
      const acc = (t: string, e: string, ca: string, cl: string) => h('button', { type: 'button', class: `accion ${cl}`, disabled: m.estado === e && m.causa === ca, onclick: () => cambiarEstado(m.codigo, e, ca) }, h('i', {}), t);
      c.querySelector('[data-t-maq]')!.replaceChildren(
        h('div', { class: `mi-maq ${CLASE[m.estado]}` },
          h('div', {}, h('span', { class: 'mono' }, `${m.codigo} · ${m.linea}`), h('b', {}, m.estado), h('span', {}, m.causa, m.orden ? ` · ${m.orden}` : '')),
          h('span', { class: 'mi-maq-t mono' }, vivo(m.desde))),
        tira(m.codigo, inicioDia(), Date.now(), 'tira grande'),
        h('div', { class: 'acciones' },
          acc('Arrancar', 'En marcha', 'Producción', 'e-marcha'),
          acc('Parar', 'Parada', 'Fin de turno', 'e-parada'),
          acc('Cambio de formato', 'Cambio', 'Cambio de formato', 'e-cambio'),
          acc('Limpieza CIP', 'Limpieza', 'Limpieza CIP', 'e-limpieza'),
          acc('Reportar falla', 'Falla', 'Falla mecánica', 'e-falla'),
          h('button', { type: 'button', class: 'accion otra', onclick: () => abrirMaquina(m.codigo) }, 'Otro…')));
    }
    const linea = m?.linea;
    const ords = D.ordenes.filter((o) => o.linea === linea && ['Liberada', 'En ejecución'].includes(o.estado));
    c.querySelector('[data-t-ord]')!.replaceChildren(ords.length ? h('ul', { class: 'lista' }, ords.map((o) => h('li', {},
      h('div', {}, h('b', { class: 'mono' }, o.codigo), ' ', chipOrden(o.estado), o.prioridad !== 'Normal' ? h('span', { class: `chip p-${o.prioridad.toLowerCase()}` }, o.prioridad) : null,
        h('div', { class: 'sub' }, `${o.producto} · ${miles(o.litros_plan)} L · ${o.turno}`), progreso(o)),
      h('div', { class: 'btns' }, o.estado === 'Liberada'
        ? boton('Iniciar aquí', async () => {
          if (await guardar(sb!.from('ordenes').update({ estado: 'En ejecución', inicio: new Date().toISOString(), maquina: m!.codigo }).eq('id', o.id), `${o.codigo} en ejecución.`, 'ordenes'))
            cambiarEstado(m!.codigo, 'En marcha', 'Producción', o.codigo);
        }, 'm-btn mini')
        : terminarOrden(o))))) : vacio(linea && LINEAS.includes(linea) ? 'No hay órdenes liberadas para esta línea. El supervisor las libera en Órdenes.' : 'Esta máquina es de recepción: no lleva órdenes de producto.'));
    const lo = (c as any)._lOrden as HTMLSelectElement;
    opcionesActualizar(lo, [['', '— Sin orden —'], ...D.ordenes.filter((o) => ['En ejecución', 'Liberada', 'Terminada'].includes(o.estado)).map((o) => [o.codigo, `${o.codigo} · ${o.producto}`] as [string, string])]);
    const lc = (c as any)._lCodigo as HTMLInputElement;
    if (!lc.value) lc.placeholder = sugerirLote(D.ordenes.find((o) => o.codigo === lo.value)?.producto ?? '');
    lo.onchange = () => { lc.placeholder = sugerirLote(D.ordenes.find((o) => o.codigo === lo.value)?.producto ?? ''); lc.value = lc.placeholder; };
    const hoy0 = inicioDia();
    const mios = [
      ...D.lotes.filter((f) => f.autor === yo && Date.parse(f.creado) >= hoy0).map((f) => ({ t: Date.parse(f.creado), x: `Lote ${f.codigo} · ${miles(f.litros)} L` })),
      ...D.paros.filter((f) => f.autor === yo && Date.parse(f.creado) >= hoy0).map((f) => ({ t: Date.parse(f.creado), x: `Paro ${f.equipo} · ${f.causa} · ${f.minutos} min` })),
      ...D.eventos_maquina.filter((f) => f.autor === yo && Date.parse(f.inicio) >= hoy0).map((f) => ({ t: Date.parse(f.inicio), x: `${f.maquina} → ${f.estado} · ${f.causa}` })),
    ].sort((a, b) => b.t - a.t);
    c.querySelector('[data-t-mios]')!.replaceChildren(mios.length ? h('ul', { class: 'feed' }, mios.slice(0, 15).map((r) => h('li', {}, h('span', { class: 'mono' }, hora(r.t)), h('span', {}, r.x)))) : vacio('Aún no has registrado nada hoy.'));
  },
};
function sugerirLote(producto: string) {
  const pre = producto.slice(0, 2) || 'LT';
  const d = hoyISO().slice(2).replace(/-/g, '');
  const n = D.lotes.filter((l) => String(l.codigo).startsWith(`${pre}-${d}`)).length + 1;
  return `${pre}-${d}-${String(n).padStart(2, '0')}`;
}
function progreso(o: Fila) {
  const p = Math.min(1, Number(o.litros_real) / Number(o.litros_plan));
  return h('div', { class: 'prog', title: `${miles(o.litros_real)} de ${miles(o.litros_plan)} L` }, h('i', { style: `width:${p * 100}%` }), h('span', { class: 'mono' }, `${miles(o.litros_real)} / ${miles(o.litros_plan)} L`));
}
function terminarOrden(o: Fila) {
  const lit = D.lotes.filter((l) => l.orden === o.codigo).reduce((x, l) => x + Number(l.litros), 0);
  return boton('Terminar', async () => {
    const v = prompt(`Litros producidos en ${o.codigo} (lotes registrados: ${miles(lit)} L)`, String(lit || o.litros_plan));
    if (v == null) return;
    const n = Number(v.replace(',', '.'));
    if (!(n >= 0)) return aviso('Cantidad no válida.', true);
    await guardar(sb!.from('ordenes').update({ estado: 'Terminada', litros_real: n, fin: new Date().toISOString() }).eq('id', o.id), `${o.codigo} terminada.`, 'ordenes');
    if (o.maquina) {
      const m = D.maquinas.find((x) => x.codigo === o.maquina);
      if (m && m.orden === o.codigo) cambiarEstado(m.codigo, 'Parada', 'Sin orden', '');
    }
  }, 'm-btn mini');
}

// ---------- Órdenes
const vOrdenes: Vista = {
  id: 'ordenes', titulo: 'Órdenes de producción', grupo: 'Producción', roles: ['Supervisor', 'Jefe de planta', 'Gerencia', 'Administrador'],
  montar(c) {
    if (puede(PLANEAN)) {
      const f = h('form', { class: 'm-form' }) as HTMLFormElement;
      const linea = sel('linea', LINEAS), prod = sel('producto', PRODUCTOS.Yogurts);
      linea.addEventListener('change', () => { opcionesActualizar(prod, PRODUCTOS[linea.value]); prod.value = PRODUCTOS[linea.value][0]; });
      const codigo = inp('codigo', { required: true, autocomplete: 'off' });
      const sugerir = () => { const d = hoyISO().slice(2).replace(/-/g, ''); codigo.value = `OP-${d}-${String(D.ordenes.filter((o) => String(o.codigo).startsWith(`OP-${d}`)).length + 1).padStart(2, '0')}`; };
      sugerir();
      f.append(campo('Código', codigo), campo('Línea', linea), campo('Producto', prod),
        campo('Litros plan', inp('litros_plan', { type: 'number', min: 1, step: 'any', required: true, inputmode: 'decimal' })),
        campo('Fecha', inp('fecha', { type: 'date', value: hoyISO(), required: true })),
        campo('Turno', sel('turno', ['Mañana', 'Tarde', 'Noche'], turnoDe().nombre)),
        campo('Prioridad', sel('prioridad', ['Normal', 'Alta', 'Urgente'])),
        campo('Nota', inp('nota', { placeholder: 'Opcional' })),
        h('button', { class: 'm-btn', type: 'submit' }, 'Crear orden'));
      f.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fila = Object.fromEntries(new FormData(f)) as Fila;
        fila.litros_plan = Number(fila.litros_plan);
        if (await guardar(sb!.from('ordenes').insert(fila), `Orden ${fila.codigo} creada.`, 'ordenes')) { (f.querySelector('[name=litros_plan]') as HTMLInputElement).value = ''; setTimeout(sugerir, 600); }
      });
      c.append(tarjeta('Nueva orden', f));
    }
    const filtro = sel('linea', [['', 'Todas las líneas'], ...LINEAS.map((l) => [l, l] as [string, string])]);
    filtro.addEventListener('change', () => vOrdenes.refrescar());
    c.append(h('div', { class: 'barra' }, campo('Línea', filtro), h('div', { 'data-o-kpi': '', class: 'barra-kpi mono' })), h('div', { class: 'kanban', 'data-o-kan': '' }));
    (c as any)._filtro = filtro;
  },
  refrescar() {
    const c = cont;
    const l = ((c as any)._filtro as HTMLSelectElement).value;
    const os = D.ordenes.filter((o) => !l || o.linea === l);
    const plan = os.filter((o) => o.fecha === hoyISO()).reduce((x, o) => x + Number(o.litros_plan), 0);
    c.querySelector('[data-o-kpi]')!.textContent = `Hoy: ${os.filter((o) => o.fecha === hoyISO()).length} órdenes · ${miles(plan)} L planeados`;
    const sig: Record<string, [string, Fila]> = {
      Planeada: ['Liberar', { estado: 'Liberada' }], 'En ejecución': ['', {}], Terminada: ['Cerrar', { estado: 'Cerrada' }],
    };
    c.querySelector('[data-o-kan]')!.replaceChildren(...ESTADOS_ORDEN.map((e) => {
      const lista = os.filter((o) => o.estado === e);
      const visibles = e === 'Cerrada' ? lista.slice(0, 8) : lista;
      return h('section', { class: 'col' },
        h('header', {}, chipOrden(e), h('span', { class: 'mono' }, String(lista.length))),
        visibles.length ? visibles.map((o) => h('article', { class: `ord p-${o.prioridad.toLowerCase()}` },
          h('div', { class: 'ord-top' }, h('b', { class: 'mono' }, o.codigo), o.prioridad !== 'Normal' ? h('span', { class: `chip p-${o.prioridad.toLowerCase()}` }, o.prioridad) : null),
          h('span', {}, o.producto),
          h('span', { class: 'sub mono' }, `${o.linea} · ${o.fecha} · ${o.turno}${o.maquina ? ` · ${o.maquina}` : ''}`),
          progreso(o),
          h('div', { class: 'btns' },
            e === 'En ejecución' ? terminarOrden(o) : sig[e] && puede(PLANEAN) ? boton(sig[e][0], () => guardar(sb!.from('ordenes').update(sig[e][1]).eq('id', o.id), `${o.codigo}: ${sig[e][1].estado}.`, 'ordenes'), 'm-btn mini') : null,
            e === 'Liberada' ? h('span', { class: 'sub' }, 'La inicia el operario en Mi turno') : null,
            e === 'Planeada' && puede(PLANEAN) ? boton('Borrar', () => confirm(`¿Borrar la orden ${o.codigo}?`) && guardar(sb!.from('ordenes').delete().eq('id', o.id), 'Orden borrada.', 'ordenes'), 'm-btn mini peligro') : null))) : vacio('—'),
        lista.length > visibles.length ? h('p', { class: 'sub mono' }, `y ${lista.length - visibles.length} más`) : null);
    }));
  },
};

// ---------- Lotes y trazabilidad
const vLotes: Vista = {
  id: 'lotes', titulo: 'Lotes y trazabilidad', grupo: 'Producción', roles: ['Operario', 'Supervisor', 'Calidad', 'Jefe de planta', 'Gerencia', 'Administrador'],
  montar(c) {
    if (miRol !== 'Gerencia') {
      const f = h('form', { class: 'm-form' }) as HTMLFormElement;
      const linea = sel('linea', LINEAS), prod = sel('producto', PRODUCTOS.Yogurts), orden = sel('orden', []);
      const codigo = inp('codigo', { required: true, autocomplete: 'off' });
      linea.addEventListener('change', () => { opcionesActualizar(prod, PRODUCTOS[linea.value]); prod.value = PRODUCTOS[linea.value][0]; codigo.value = sugerirLote(prod.value); });
      prod.addEventListener('change', () => (codigo.value = sugerirLote(prod.value)));
      orden.addEventListener('change', () => {
        const o = D.ordenes.find((x) => x.codigo === orden.value);
        if (o) { linea.value = o.linea; opcionesActualizar(prod, PRODUCTOS[o.linea]); prod.value = o.producto; codigo.value = sugerirLote(o.producto); }
      });
      codigo.value = sugerirLote(prod.value);
      f.append(campo('Orden', orden), campo('Línea', linea), campo('Producto', prod), campo('Lote', codigo),
        campo('Litros', inp('litros', { type: 'number', min: 1, step: 'any', required: true, inputmode: 'decimal' })),
        campo('Nota', inp('nota', { placeholder: 'Opcional' })), h('button', { class: 'm-btn', type: 'submit' }, 'Registrar lote'));
      f.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fila = Object.fromEntries(new FormData(f)) as Fila;
        fila.litros = Number(fila.litros);
        if (await guardar(sb!.from('lotes').insert(fila), `Lote ${fila.codigo} registrado.`, 'lotes')) { (f.querySelector('[name=litros]') as HTMLInputElement).value = ''; setTimeout(() => (codigo.value = sugerirLote(prod.value)), 600); }
      });
      c.append(tarjeta('Registrar lote', f));
      (c as any)._orden = orden;
    }
    const buscar = inp('buscar', { type: 'search', placeholder: 'Buscar lote, producto u orden' });
    buscar.addEventListener('input', () => vLotes.refrescar());
    c.append(h('div', { class: 'barra' }, campo('Buscar', buscar, 'ancho'), boton('Exportar CSV', () => csv('mes_lotes', [['creado', 'Fecha'], ['codigo', 'Lote'], ['linea', 'Línea'], ['producto', 'Producto'], ['orden', 'Orden'], ['litros', 'Litros'], ['estado', 'Estado'], ['autor', 'Registró'], ['nota', 'Nota']], D.lotes))),
      h('div', { class: 'lotes-grid' }, h('div', { 'data-l-tabla': '' }), h('aside', { class: 'm-card traza', 'data-l-traza': '' }, vacio('Elige un lote para ver su trazabilidad: orden, máquina, controles de calidad y quién lo registró.'))));
    (c as any)._buscar = buscar;
  },
  refrescar() {
    const c = cont;
    const o = (c as any)._orden as HTMLSelectElement | undefined;
    if (o) opcionesActualizar(o, [['', '— Sin orden —'], ...D.ordenes.filter((x) => x.estado !== 'Cerrada').map((x) => [x.codigo, `${x.codigo} · ${x.producto}`] as [string, string])]);
    const q = ((c as any)._buscar as HTMLInputElement).value.trim().toLowerCase();
    const filas = D.lotes.filter((l) => !q || [l.codigo, l.producto, l.orden, l.linea].join(' ').toLowerCase().includes(q));
    c.querySelector('[data-l-tabla]')!.replaceChildren(tabla([
      ['creado', 'Fecha', (f) => fecha(f.creado)], ['codigo', 'Lote', (f) => h('b', { class: 'mono' }, f.codigo)], ['producto', 'Producto'],
      ['orden', 'Orden', (f) => h('span', { class: 'mono' }, f.orden || '—')], ['litros', 'Litros', (f) => miles(f.litros)], ['estado', 'Estado', (f) => chipLote(f.estado)],
      ['autor', 'Registró', (f) => nombre(f.autor)],
    ], filas, (f) => [
      puede(DISPONEN) && f.estado !== 'Liberado' ? boton('Liberar', () => disponer(f, 'Liberado'), 'm-btn mini') : null,
      puede(DISPONEN) && f.estado !== 'Retenido' ? boton('Retener', () => disponer(f, 'Retenido'), 'm-btn mini sec') : null,
      f.autor === yo && f.estado === 'En proceso' ? boton('Terminado', () => guardar(sb!.from('lotes').update({ estado: 'Terminado' }).eq('id', f.id), `${f.codigo} terminado.`, 'lotes'), 'm-btn mini sec') : null,
      borrarPropio('lotes', f),
    ], (f) => trazar(f)));
  },
};
function disponer(f: Fila, estado: string) {
  return guardar(sb!.from('lotes').update({ estado }).eq('id', f.id), `${f.codigo}: ${estado}.`, 'lotes');
}
function trazar(l: Fila) {
  const o = D.ordenes.find((x) => x.codigo === l.orden);
  const pruebas = D.calidad.filter((x) => x.lote === l.codigo);
  const ev = o ? D.eventos_maquina.filter((e) => e.orden === o.codigo) : [];
  const paso = (t: string, ...kids: Kid[]) => h('li', {}, h('span', { class: 'mono gold' }, t), h('div', {}, ...kids));
  cont.querySelector('[data-l-traza]')?.replaceChildren(
    h('h3', { class: 'm-card-t mono' }, 'Trazabilidad'),
    h('div', { class: 'traza-cab' }, h('b', { class: 'mono' }, l.codigo), chipLote(l.estado)),
    h('ol', { class: 'traza-pasos' },
      paso('Orden', o ? [h('b', {}, o.codigo), ` · ${o.producto} · ${miles(o.litros_plan)} L plan · `, chipOrden(o.estado)] : 'Sin orden asociada'),
      paso('Máquinas', ev.length ? h('ul', {}, [...new Set(ev.map((e) => e.maquina))].map((mq) => {
        const es = ev.filter((e) => e.maquina === mq);
        const marcha = es.filter((e) => e.estado === 'En marcha').reduce((x, e) => x + ((e.fin ? Date.parse(e.fin) : Date.now()) - Date.parse(e.inicio)), 0);
        return h('li', {}, `${mq} · ${dur(marcha)} en marcha · ${es.filter((e) => e.estado !== 'En marcha').length} eventos`);
      })) : 'Sin eventos de máquina con esta orden'),
      paso('Registro', `${fecha(l.creado)} · ${nombre(l.autor)} · ${miles(l.litros)} L · ${l.linea}`, l.nota ? h('div', { class: 'sub' }, l.nota) : null),
      paso('Calidad', pruebas.length ? h('ul', {}, pruebas.map((p) => h('li', {}, `${p.prueba}: ${p.valor} `, chipLote(p.resultado), h('span', { class: 'sub' }, ` · ${nombre(p.autor)}`)))) : 'Sin controles registrados')));
}

// ---------- Calidad
const vCalidad: Vista = {
  id: 'calidad', titulo: 'Calidad', grupo: 'Producción', roles: ['Calidad', 'Supervisor', 'Jefe de planta', 'Administrador'],
  montar(c) {
    const f = h('form', { class: 'm-form' }) as HTMLFormElement;
    const lote = inp('lote', { list: 'mes-lotes', required: true, autocomplete: 'off', placeholder: 'Código del lote' });
    f.append(campo('Lote', lote), h('datalist', { id: 'mes-lotes' }), campo('Prueba', sel('prueba', PRUEBAS)), campo('Valor', inp('valor', { required: true, autocomplete: 'off' })),
      campo('Resultado', sel('resultado', ['Aprobado', 'Rechazado', 'En revisión'])), campo('Nota', inp('nota', { placeholder: 'Opcional' })), h('button', { class: 'm-btn', type: 'submit' }, 'Registrar control'));
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (await guardar(sb!.from('calidad').insert(Object.fromEntries(new FormData(f))), 'Control registrado.', 'calidad')) { (f.querySelector('[name=valor]') as HTMLInputElement).value = ''; }
    });
    c.append(h('div', { 'data-c-kpi': '' }), h('div', { class: 'dos' }, tarjeta('Lotes por disponer', h('div', { 'data-c-pend': '' })), tarjeta('Registrar control', f)),
      h('div', { class: 'barra' }, h('h3', { class: 'm-card-t mono' }, 'Controles registrados'), boton('Exportar CSV', () => csv('mes_calidad', [['creado', 'Fecha'], ['lote', 'Lote'], ['prueba', 'Prueba'], ['valor', 'Valor'], ['resultado', 'Resultado'], ['autor', 'Registró'], ['nota', 'Nota']], D.calidad))),
      h('div', { 'data-c-tabla': '' }));
  },
  refrescar() {
    const c = cont;
    c.querySelector('#mes-lotes')?.replaceChildren(...D.lotes.slice(0, 200).map((l) => h('option', { value: l.codigo }, l.producto)));
    const d30 = Date.now() - 30 * 864e5;
    const cs = D.calidad.filter((x) => Date.parse(x.creado) >= d30);
    const ap = cs.filter((x) => x.resultado === 'Aprobado').length;
    const pend = D.lotes.filter((l) => ['En proceso', 'Terminado'].includes(l.estado));
    c.querySelector('[data-c-kpi]')!.replaceChildren(h('div', { class: 'kpis' },
      kpi('Controles hoy', String(D.calidad.filter((x) => Date.parse(x.creado) >= inicioDia()).length)),
      kpi('Aprobados · 30 días', cs.length ? pct(ap / cs.length) : '—', `${ap} de ${cs.length} controles`),
      kpi('Lotes por disponer', String(pend.length), 'en proceso o terminados', pend.length ? 'k-cambio' : ''),
      kpi('Retenidos', String(D.lotes.filter((l) => l.estado === 'Retenido').length), '', D.lotes.some((l) => l.estado === 'Retenido') ? 'k-falla' : '')));
    c.querySelector('[data-c-pend]')!.replaceChildren(pend.length ? h('ul', { class: 'lista' }, pend.slice(0, 20).map((l) => {
      const ps = D.calidad.filter((x) => x.lote === l.codigo);
      return h('li', {}, h('div', {}, h('b', { class: 'mono' }, l.codigo), ' ', chipLote(l.estado), h('div', { class: 'sub' }, `${l.producto} · ${miles(l.litros)} L · ${ps.length} controles${ps.some((p) => p.resultado === 'Rechazado') ? ' · con rechazos' : ''}`)),
        puede(DISPONEN) ? h('div', { class: 'btns' }, boton('Liberar', () => disponer(l, 'Liberado'), 'm-btn mini'), boton('Retener', () => disponer(l, 'Retenido'), 'm-btn mini sec')) : null);
    })) : vacio('No hay lotes esperando decisión.'));
    c.querySelector('[data-c-tabla]')!.replaceChildren(tabla([
      ['creado', 'Fecha', (f) => fecha(f.creado)], ['lote', 'Lote', (f) => h('b', { class: 'mono' }, f.lote)], ['prueba', 'Prueba'], ['valor', 'Valor'],
      ['resultado', 'Resultado', (f) => chipLote(f.resultado)], ['autor', 'Registró', (f) => nombre(f.autor)], ['nota', 'Nota'],
    ], D.calidad, (f) => borrarPropio('calidad', f)));
  },
};

// ---------- Mantenimiento
const vMant: Vista = {
  id: 'mantenimiento', titulo: 'Mantenimiento', grupo: 'Activos', roles: ['Mantenimiento', 'Supervisor', 'Jefe de planta', 'Administrador'],
  montar(c) {
    c.append(h('div', { 'data-m-kpi': '' }), tarjeta('Atención inmediata', h('div', { 'data-m-alertas': '' })),
      h('div', { class: 'dos' }, tarjeta('Tiempo perdido por causa · 14 días', h('div', { 'data-m-pareto': '' })), tarjeta('Paros cortos registrados a mano · 14 días', h('div', { 'data-m-paros': '' }))),
      tarjeta('Confiabilidad por máquina · 14 días', h('div', { 'data-m-tabla': '' })));
  },
  refrescar() {
    const c = cont;
    const a = Date.now() - 14 * 864e5, b = Date.now();
    const filas = D.maquinas.map((m) => {
      const t = tiempos(m.codigo, a, b);
      const tf = t.est['Falla'] ?? 0;
      return { m, t, nf: t.fallas.length, tf, mttr: t.fallas.length ? t.fallas.reduce((x, y) => x + y, 0) / t.fallas.length : null, mtbf: t.fallas.length ? t.marcha / t.fallas.length : null };
    });
    const nf = filas.reduce((x, f) => x + f.nf, 0);
    const todas = filas.flatMap((f) => f.t.fallas);
    const marcha = filas.reduce((x, f) => x + f.t.marcha, 0);
    c.querySelector('[data-m-kpi]')!.replaceChildren(h('div', { class: 'kpis' },
      kpi('Fallas abiertas', String(D.maquinas.filter((m) => m.estado === 'Falla').length), '', D.maquinas.some((m) => m.estado === 'Falla') ? 'k-falla' : ''),
      kpi('En mantenimiento', String(D.maquinas.filter((m) => m.estado === 'Mantenimiento').length)),
      kpi('Fallas · 14 días', String(nf)),
      kpi('MTTR', todas.length ? dur(todas.reduce((x, y) => x + y, 0) / todas.length) : '—', 'tiempo medio para reparar'),
      kpi('MTBF', nf ? dur(marcha / nf) : '—', 'tiempo en marcha entre fallas')));
    const al = D.maquinas.filter((m) => ['Falla', 'Mantenimiento'].includes(m.estado)).sort((x, y) => Date.parse(x.desde) - Date.parse(y.desde));
    c.querySelector('[data-m-alertas]')!.replaceChildren(al.length ? h('ul', { class: 'lista' }, al.map((m) => h('li', { class: `alerta ${CLASE[m.estado]}` },
      h('div', {}, h('b', { class: 'mono' }, m.codigo), ` ${m.nombre} `, chip(m.estado), h('div', { class: 'sub' }, `${m.causa} · ${m.linea} · hace `, vivo(m.desde))),
      h('div', { class: 'btns' },
        m.estado === 'Falla' ? boton('Atender', () => cambiarEstado(m.codigo, 'Mantenimiento', 'Correctivo'), 'm-btn mini sec') : null,
        boton('Reparada · arrancar', () => cambiarEstado(m.codigo, 'En marcha', 'Producción'), 'm-btn mini'),
        boton('Reparada · dejar parada', () => cambiarEstado(m.codigo, 'Parada', 'Sin orden'), 'm-btn mini sec'))))) : vacio('Ninguna máquina en falla ni en mantenimiento.'));
    const causas: Record<string, number> = {};
    filas.forEach((f) => Object.entries(f.t.causa).forEach(([k, v]) => { if (!NO_PROGRAMADO.has(k)) causas[k] = (causas[k] ?? 0) + v; }));
    c.querySelector('[data-m-pareto]')!.replaceChildren(barras(Object.entries(causas).sort((x, y) => y[1] - x[1]).slice(0, 8), (v) => dur(v)));
    const pc: Record<string, number> = {};
    D.paros.filter((p) => Date.parse(p.creado) >= a).forEach((p) => (pc[p.causa] = (pc[p.causa] ?? 0) + Number(p.minutos)));
    c.querySelector('[data-m-paros]')!.replaceChildren(barras(Object.entries(pc).sort((x, y) => y[1] - x[1]), (v) => `${miles(v)} min`, 'var(--gold)'));
    c.querySelector('[data-m-tabla]')!.replaceChildren(tabla([
      ['codigo', 'Máquina', (f) => [h('b', { class: 'mono' }, f.m.codigo), ` ${f.m.nombre}`]], ['estado', 'Ahora', (f) => chip(f.m.estado)],
      ['disp', 'Disponibilidad', (f) => pct(f.t.disp)], ['nf', 'Fallas', (f) => String(f.nf)], ['tf', 'Tiempo en falla', (f) => (f.tf ? dur(f.tf) : '—')],
      ['mttr', 'MTTR', (f) => (f.mttr == null ? '—' : dur(f.mttr))], ['mtbf', 'MTBF', (f) => (f.mtbf == null ? '—' : dur(f.mtbf))],
      ['tira', 'Últimos 14 días', (f) => tira(f.m.codigo, a, b)],
    ], filas.sort((x, y) => y.nf - x.nf || y.tf - x.tf) as unknown as Fila[]));
  },
};

// ---------- Indicadores (jefe de planta y gerencia)
let periodo = 1;
const vInd: Vista = {
  id: 'indicadores', titulo: 'Indicadores de planta', grupo: 'Gestión', roles: ['Supervisor', 'Jefe de planta', 'Gerencia', 'Administrador'],
  montar(c) {
    const per = h('div', { class: 'segmentos', role: 'group', 'aria-label': 'Periodo' }, [[1, 'Hoy'], [7, '7 días'], [30, '30 días']].map(([d, t]) =>
      h('button', { type: 'button', 'aria-pressed': String(d === periodo), onclick: (e: Event) => { periodo = d as number; per.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b === e.currentTarget))); vInd.refrescar(); } }, t as string)));
    c.append(h('div', { class: 'barra' }, per, h('p', { class: 'nota mono' }, 'Calculado con los registros del MES. OEE = disponibilidad × cumplimiento del plan × calidad.')),
      h('div', { 'data-i-kpi': '' }),
      h('div', { class: 'dos' }, tarjeta('Litros registrados por día y línea', h('div', { 'data-i-litros': '' })), tarjeta('Pérdidas de tiempo por causa', h('div', { 'data-i-pareto': '' }))),
      tarjeta('Estados de las máquinas hoy', h('div', { 'data-i-gantt': '' })),
      tarjeta('Resumen por línea', h('div', { 'data-i-lineas': '' })));
  },
  refrescar() {
    const c = cont;
    const b = Date.now(), a = periodo === 1 ? inicioDia() : inicioDia() - (periodo - 1) * 864e5;
    const t = tiempos(null, a, b);
    const os = D.ordenes.filter((o) => Date.parse(o.fecha + 'T12:00') >= a - 864e5 / 2);
    const term = os.filter((o) => ['Terminada', 'Cerrada'].includes(o.estado));
    const plan = term.reduce((x, o) => x + Number(o.litros_plan), 0), real = term.reduce((x, o) => x + Number(o.litros_real), 0);
    const cumpl = plan ? Math.min(1, real / plan) : null;
    const ls = D.lotes.filter((l) => Date.parse(l.creado) >= a);
    const dispuestos = ls.filter((l) => ['Liberado', 'Retenido'].includes(l.estado));
    const lib = dispuestos.filter((l) => l.estado === 'Liberado').reduce((x, l) => x + Number(l.litros), 0);
    const tot = dispuestos.reduce((x, l) => x + Number(l.litros), 0);
    const cal = tot ? lib / tot : null;
    const oee = t.disp != null && cumpl != null && cal != null ? t.disp * cumpl * cal : null;
    const perd = Object.entries(t.causa).filter(([k]) => !NO_PROGRAMADO.has(k)).reduce((x, [, v]) => x + v, 0);
    c.querySelector('[data-i-kpi]')!.replaceChildren(h('div', { class: 'kpis grandes' },
      kpi('OEE', pct(oee), oee == null ? 'faltan datos de algún factor' : 'disponibilidad × cumplimiento × calidad', 'k-oee'),
      kpi('Disponibilidad', pct(t.disp), 'en marcha / tiempo programado'),
      kpi('Cumplimiento del plan', pct(cumpl), `${miles(real)} de ${miles(plan)} L en órdenes terminadas`),
      kpi('Calidad', pct(cal), `${miles(lib)} L liberados de ${miles(tot)} L dispuestos`),
      kpi('Litros registrados', miles(ls.reduce((x, l) => x + Number(l.litros), 0)), `${ls.length} lotes`),
      kpi('Tiempo perdido', perd ? dur(perd) : '—', 'fallas, cambios, limpiezas, esperas'),
      kpi('Órdenes terminadas', String(term.length), `de ${os.length} en el periodo`),
      kpi('Retenidos', String(ls.filter((l) => l.estado === 'Retenido').length), 'lotes del periodo')));

    // litros por día (barras apiladas)
    const dias = Math.max(periodo, 7);
    const d0 = inicioDia() - (dias - 1) * 864e5;
    const col: Record<string, string> = { Yogurts: 'var(--gold)', Quesos: 'var(--green)', 'Leche UHT': 'var(--est-limpieza)' };
    const porDia = Array.from({ length: dias }, (_, i) => {
      const x0 = d0 + i * 864e5;
      const r: Record<string, number> = {};
      D.lotes.filter((l) => { const tt = Date.parse(l.creado); return tt >= x0 && tt < x0 + 864e5; }).forEach((l) => (r[l.linea] = (r[l.linea] ?? 0) + Number(l.litros)));
      return { x0, r, tot: Object.values(r).reduce((p, q) => p + q, 0) };
    });
    const max = Math.max(1, ...porDia.map((d) => d.tot));
    const W = 640, H = 220, pad = 34, bw = (W - pad - 8) / dias;
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, class: 'graf', role: 'img', 'aria-label': 'Litros registrados por día y línea' });
    [0, 0.5, 1].forEach((k) => {
      const y = H - 24 - k * (H - 40);
      svg.append(s('line', { x1: pad, x2: W, y1: y, y2: y, class: 'g-rej' }), s('text', { x: pad - 6, y: y + 4, 'text-anchor': 'end', class: 'g-txt' }, miles(max * k / 1000, 0) + 'k'));
    });
    porDia.forEach((d, i) => {
      let y = H - 24;
      LINEAS.forEach((l) => {
        const v = d.r[l] ?? 0;
        if (!v) return;
        const hh = (v / max) * (H - 40);
        y -= hh;
        const r = s('rect', { x: pad + i * bw + bw * 0.18, y, width: bw * 0.64, height: hh, style: `fill:${col[l]}` });
        r.append(s('title', {}, `${new Date(d.x0).toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })} · ${l}: ${miles(v)} L`));
        svg.append(r);
      });
      if (dias <= 10 || i % Math.ceil(dias / 10) === 0) svg.append(s('text', { x: pad + i * bw + bw / 2, y: H - 6, 'text-anchor': 'middle', class: 'g-txt' }, new Date(d.x0).toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })));
    });
    c.querySelector('[data-i-litros]')!.replaceChildren(svg, h('div', { class: 'leyenda mono' }, LINEAS.map((l) => h('span', { style: `--c:${col[l]}` }, h('i', {}), l))),
      porDia.every((d) => !d.tot) ? vacio('Aún no hay lotes registrados en estos días.') : '');

    c.querySelector('[data-i-pareto]')!.replaceChildren(barras(Object.entries(t.causa).filter(([k]) => !NO_PROGRAMADO.has(k)).sort((x, y) => y[1] - x[1]).slice(0, 8), (v) => dur(v)));

    // Gantt del día
    const h0 = inicioDia(), h1 = h0 + 864e5;
    const ahora = ((Date.now() - h0) / 864e5) * 100;
    c.querySelector('[data-i-gantt]')!.replaceChildren(h('div', { class: 'gantt' },
      h('div', { class: 'g-horas mono' }, h('span', {}), h('div', {}, [0, 3, 6, 9, 12, 15, 18, 21].map((x) => h('span', { style: `left:${(x / 24) * 100}%` }, `${String(x).padStart(2, '0')}h`)))),
      D.maquinas.map((m) => h('div', { class: 'g-fila' }, h('span', { class: 'mono', title: m.nombre }, m.codigo),
        h('div', { class: 'g-pista' }, tira(m.codigo, h0, h1, 'tira g'), h('b', { class: 'g-ahora', style: `left:${ahora}%` }))))),
    h('div', { class: 'leyenda mono' }, ESTADOS.map((e) => h('span', { class: CLASE[e] }, h('i', {}), e))));

    c.querySelector('[data-i-lineas]')!.replaceChildren(tabla([
      ['linea', 'Línea'], ['disp', 'Disponibilidad'], ['litros', 'Litros'], ['lotes', 'Lotes'], ['ordenes', 'Órdenes terminadas'], ['cal', 'Calidad'],
    ], LINEAS.map((l) => {
      const ms = D.maquinas.filter((m) => m.linea === l).map((m) => tiempos(m.codigo, a, b));
      const mar = ms.reduce((x, y) => x + y.marcha, 0), pr = ms.reduce((x, y) => x + y.programado, 0);
      const lsl = ls.filter((x) => x.linea === l), dsp = lsl.filter((x) => ['Liberado', 'Retenido'].includes(x.estado));
      const lt = dsp.reduce((x, y) => x + Number(y.litros), 0);
      return {
        linea: l, disp: pct(pr > 60000 ? mar / pr : null), litros: miles(lsl.reduce((x, y) => x + Number(y.litros), 0)), lotes: String(lsl.length),
        ordenes: String(term.filter((o) => o.linea === l).length), cal: pct(lt ? dsp.filter((x) => x.estado === 'Liberado').reduce((x, y) => x + Number(y.litros), 0) / lt : null),
      };
    })));
  },
};

// ---------- Archivos
const vArchivos: Vista = {
  id: 'archivos', titulo: 'Archivos compartidos', grupo: 'General', roles: ROLES,
  montar(c) {
    const f = h('form', { class: 'subir' }) as HTMLFormElement;
    const file = inp('archivo', { type: 'file', multiple: true, required: true });
    f.append(h('label', { class: 'soltar' }, file, h('b', {}, 'Elegir archivos'), h('span', { class: 'mono' }, 'Planos, actas, recetas, reportes · hasta 50 MB')), h('button', { class: 'm-btn', type: 'submit' }, 'Subir'));
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      for (const x of Array.from(file.files ?? [])) {
        const n = `${Date.now()}_${x.name.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^\w.\- ]/g, '_')}`;
        const { error } = await sb!.storage.from('mes-archivos').upload(n, x);
        aviso(error ? `No se subió ${x.name}: ${error.message}` : `Subido: ${x.name}`, !!error);
      }
      f.reset();
      recargar('archivos');
    });
    c.append(tarjeta('Subir', f), h('div', { 'data-a-lista': '' }));
  },
  refrescar() {
    cont.querySelector('[data-a-lista]')!.replaceChildren(tabla([
      ['name', 'Archivo', (o) => h('b', {}, String(o.name).replace(/^\d+_/, ''))],
      ['created_at', 'Subido', (o) => (o.created_at ? fecha(o.created_at) : '')],
      ['size', 'Tamaño', (o) => (o.metadata?.size ? `${miles(Math.max(1, o.metadata.size / 1024))} KB` : '')],
    ], D.archivos, (o) => [
      boton('Descargar', async () => {
        const { data, error } = await sb!.storage.from('mes-archivos').createSignedUrl(o.name, 120, { download: String(o.name).replace(/^\d+_/, '') });
        if (error) return aviso(`No se pudo descargar: ${error.message}`, true);
        location.href = data.signedUrl;
      }, 'm-btn mini sec'),
      boton('Borrar', async () => {
        if (!confirm('¿Borrar este archivo? Solo puedes borrar los que subiste tú.')) return;
        const { data, error } = await sb!.storage.from('mes-archivos').remove([o.name]);
        if (error || !data?.length) return aviso('No se pudo borrar: solo quien lo subió puede hacerlo.', true);
        aviso('Archivo borrado.'); recargar('archivos');
      }, 'm-btn mini peligro'),
    ]));
  },
};

// ---------- Usuarios (administrador)
const vUsuarios: Vista = {
  id: 'usuarios', titulo: 'Usuarios y roles', grupo: 'General', roles: ['Administrador'],
  montar(c) {
    c.append(h('p', { class: 'nota' }, 'Los usuarios se crean en Supabase → Authentication → Users → Add user (con “Auto Confirm User”). Aquí se les pone el nombre y el rol; el rol define qué ventanas ve cada persona.'),
      h('div', { 'data-u-tabla': '' }));
  },
  refrescar() {
    cont.querySelector('[data-u-tabla]')!.replaceChildren(tabla([
      ['nombre', 'Nombre', (p) => inp('nombre', { value: p.nombre, 'data-id': p.id, 'aria-label': 'Nombre' })],
      ['rol', 'Rol', (p) => { const x = sel('rol', ROLES, p.rol); x.dataset.id = p.id; return x; }],
      ['creado', 'Desde', (p) => fecha(p.creado)],
    ], D.perfiles, (p) => boton('Guardar', (e) => {
      const tr = (e.currentTarget as HTMLElement).closest('tr')!;
      const n = (tr.querySelector('input[name=nombre]') as HTMLInputElement).value.trim();
      const r = (tr.querySelector('select[name=rol]') as HTMLSelectElement).value;
      guardar(sb!.from('perfiles').update({ nombre: n, rol: r }).eq('id', p.id), `${n}: ${r}.`, 'perfiles');
    }, 'm-btn mini')));
  },
};

const VISTAS: Vista[] = [vPlanta, vTurno, vOrdenes, vLotes, vCalidad, vMant, vInd, vArchivos, vUsuarios];
const INICIO: Record<string, string> = { Operario: 'turno', Calidad: 'calidad', Mantenimiento: 'mantenimiento', Gerencia: 'indicadores' };

// ---------------------------------------------------------------- navegación
function visibles() {
  return VISTAS.filter((v) => v.roles.includes(rolVista));
}
function pintarMenu() {
  const grupos = [...new Set(visibles().map((v) => v.grupo))];
  menu.replaceChildren(...grupos.map((g) => h('div', { class: 'grupo' }, h('span', { class: 'mono' }, g),
    visibles().filter((v) => v.grupo === g).map((v) => h('a', { href: `#${v.id}`, 'aria-current': vista?.id === v.id ? 'page' : null },
      s('svg', { viewBox: '0 0 24 24', 'aria-hidden': 'true' }, s('path', { d: ICONOS[v.id] })), v.titulo)))));
}
function irA(id: string) {
  const v = visibles().find((x) => x.id === id) ?? visibles().find((x) => x.id === (INICIO[rolVista] ?? 'planta')) ?? visibles()[0];
  vista = v;
  tituloEl.textContent = v.titulo;
  grupoEl.textContent = v.grupo;
  menu.querySelectorAll('a').forEach((a) => a.toggleAttribute('aria-current', a.getAttribute('href') === `#${v.id}`));
  menu.querySelectorAll('a[aria-current]').forEach((a) => a.setAttribute('aria-current', 'page'));
  cont.replaceChildren();
  v.montar(cont);
  v.refrescar();
  if (location.hash !== `#${v.id}`) history.replaceState(null, '', `#${v.id}`);
}
window.addEventListener('hashchange', () => irA(location.hash.slice(1)));

function pintarUsuario() {
  const p = D.perfiles.find((x) => x.id === yo);
  raiz.querySelector('[data-u-nombre]')!.textContent = p?.nombre ?? '';
  raiz.querySelector('[data-u-rol]')!.textContent = miRol;
  raiz.querySelector('[data-u-ini]')!.textContent = (p?.nombre ?? '?').slice(0, 1).toUpperCase();
  const como = raiz.querySelector<HTMLElement>('[data-como]')!;
  como.hidden = miRol !== 'Administrador';
  if (!como.hidden) {
    const s2 = como.querySelector('select')!;
    opcionesActualizar(s2, ROLES);
    s2.value = rolVista;
  }
}
raiz.querySelector<HTMLSelectElement>('[data-como] select')!.addEventListener('change', (e) => {
  rolVista = (e.target as HTMLSelectElement).value;
  pintarMenu();
  irA(INICIO[rolVista] ?? 'planta');
  aviso(rolVista === miRol ? 'Vista normal.' : `Viendo el MES como ${rolVista}. Los permisos reales siguen siendo los tuyos.`);
});

// ---------------------------------------------------------------- reloj y tiempo real
function pulsoVivo() {
  const p = raiz.querySelector('[data-live]');
  p?.classList.remove('latido');
  void (p as HTMLElement | null)?.offsetWidth;
  p?.classList.add('latido');
}
let seg = 0;
setInterval(() => {
  if (pantallaApp.hidden) return;
  const n = Date.now();
  raiz.querySelectorAll<HTMLElement>('[data-desde]').forEach((e) => (e.textContent = dur(n - Date.parse(e.dataset.desde!))));
  raiz.querySelectorAll<HTMLElement>('[data-hasta]').forEach((e) => (e.textContent = dur(Number(e.dataset.hasta) - n)));
  const reloj = raiz.querySelector('[data-reloj]');
  if (reloj) reloj.textContent = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const tn = raiz.querySelector('[data-turno]');
  if (tn) tn.textContent = `Turno ${turnoDe().nombre}`;
  // las tiras y los acumulados avanzan cada minuto (sin tocar formularios)
  if (++seg % 60 === 0 && vista && ['planta', 'indicadores', 'mantenimiento'].includes(vista.id) && !dialogo.open) vista.refrescar();
}, 1000);

const TABLAS = ['maquinas', 'eventos_maquina', 'ordenes', 'lotes', 'paros', 'calidad', 'perfiles'];
async function entrar(uid: string) {
  yo = uid;
  pantallaLogin.hidden = true;
  pantallaApp.hidden = false;
  document.documentElement.classList.add('mes-dentro');
  cont.replaceChildren(h('p', { class: 'vacio' }, 'Cargando la planta…'));
  await Promise.all([...TABLAS, 'archivos'].map(cargar));
  miRol = D.perfiles.find((p) => p.id === yo)?.rol ?? 'Operario';
  rolVista = miRol;
  pintarUsuario();
  pintarMenu();
  irA(location.hash.slice(1));
  const canal = sb!.channel('mes-planta');
  TABLAS.forEach((t) => canal.on('postgres_changes', { event: '*', schema: 'public', table: t }, () => recargar(t)));
  canal.subscribe((estado) => {
    const p = raiz.querySelector<HTMLElement>('[data-live]');
    p?.toggleAttribute('data-off', estado !== 'SUBSCRIBED');
    raiz.querySelector('[data-live-t]')!.textContent = estado === 'SUBSCRIBED' ? 'En vivo' : 'Reconectando…';
  });
}

if (sb) {
  sb.auth.getSession().then(({ data }) => { if (data.session) entrar(data.session.user.id); });
  raiz.querySelector<HTMLFormElement>('[data-login]')!.addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget as HTMLFormElement);
    loginMsg.textContent = 'Entrando…';
    const { data, error } = await sb.auth.signInWithPassword({ email: String(f.get('correo')), password: String(f.get('clave')) });
    if (error) { loginMsg.textContent = 'Correo o contraseña incorrectos.'; return; }
    loginMsg.textContent = '';
    entrar(data.user.id);
  });
  raiz.querySelector('[data-salir]')!.addEventListener('click', async () => {
    await sb.auth.signOut();
    location.hash = '';
    location.reload();
  });
}
