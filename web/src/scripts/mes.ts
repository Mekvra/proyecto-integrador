// MES de Lácteos Altos de Teusacá: lógica de la plataforma (Supabase).
// Vistas por nivel de la pirámide ISA-95: piso de planta (operario), operaciones (supervisor, calidad,
// mantenimiento), gestión de planta (jefe) y negocio (gerencia). Todo sale de los registros de la base de datos;
// lo que genera la pasarela simulada viene marcado con origen = 'Simulación' y se muestra con la etiqueta SIM.
// Los textos se pintan con textContent (sin HTML de usuarios).
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
function s(tag: string, attrs: Record<string, any> = {}, ...kids: (Node | string | null | false)[]): SVGElement {
  const el = document.createElementNS(svgNS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, String(v));
  }
  kids.forEach((c) => c && el.append(c));
  return el;
}

const miles = (n: number, d = 0) => (Number.isFinite(n) ? n.toLocaleString('es-CO', { maximumFractionDigits: d, minimumFractionDigits: d }) : '—');
const pct = (x: number | null) => (x == null || !Number.isFinite(x) ? '—' : `${miles(x * 100, 1)} %`);
function cop(n: number | null) {
  if (n == null || !Number.isFinite(n)) return '—';
  const a = Math.abs(n), sg = n < 0 ? '−' : '';
  if (a >= 1e6) return `${sg}$ ${miles(a / 1e6, a >= 1e8 ? 0 : 1)} M`;
  return `${sg}$ ${miles(a)}`;
}
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
const reducido = window.matchMedia('(prefers-reduced-motion: reduce)');

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

// Números que cuentan hasta su valor (recuerdan el último valor de cada indicador).
const ultimos = new Map<string, number>();
function contar(el: HTMLElement, clave: string, valor: number | null, fmt: (n: number) => string) {
  if (valor == null || !Number.isFinite(valor)) { el.textContent = '—'; return; }
  const desde = ultimos.get(clave) ?? 0;
  ultimos.set(clave, valor);
  if (reducido.matches || desde === valor) { el.textContent = fmt(valor); return; }
  const t0 = performance.now(), dura = desde === 0 ? 1100 : 600;
  const paso = (t: number) => {
    const k = Math.min(1, (t - t0) / dura), e = 1 - Math.pow(2, -10 * k);
    el.textContent = fmt(desde + (valor - desde) * (k >= 1 ? 1 : e));
    if (k < 1 && el.isConnected) requestAnimationFrame(paso);
  };
  requestAnimationFrame(paso);
}

// ---------------------------------------------------------------- catálogos
const LINEAS = ['Yogurts', 'Quesos', 'Leche UHT'];
const LINEAS_PLANTA = ['Recepción', ...LINEAS];
const PRODUCTOS: Record<string, string[]> = {
  Yogurts: ['YF · Yogurt con fresa', 'YN · Yogurt natural', 'YG · Yogurt griego'],
  Quesos: ['QM · Mozzarella', 'QQ · Quesillo', 'QD · Doble crema'],
  'Leche UHT': ['LE · Leche entera', 'LD · Leche descremada', 'LC · Leche con chocolate'],
};
const COLOR_LINEA: Record<string, string> = { Yogurts: 'var(--gold)', Quesos: 'var(--green)', 'Leche UHT': 'var(--est-limpieza)' };
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
const NO_PROGRAMADO = new Set(['Sin orden', 'Fin de turno']);
const CAUSAS_PARO = ['Falla', 'Cambio de formato', 'Limpieza CIP', 'Falta de material', 'Mantenimiento', 'Otra'];
const PRUEBAS = ['pH', 'Acidez (% ácido láctico)', 'Grasa (%)', 'Sólidos (%)', 'Temperatura (°C)', 'Peso de llenado (g)', 'Antibióticos', 'Microbiología', 'Sensorial'];
const ESTADOS_ORDEN = ['Planeada', 'Liberada', 'En ejecución', 'Terminada', 'Cerrada'];
const ROLES = ['Operario', 'Supervisor', 'Calidad', 'Mantenimiento', 'Jefe de planta', 'Gerencia', 'Administrador'];
const PLANEAN = ['Supervisor', 'Jefe de planta', 'Administrador'];
const DISPONEN = ['Calidad', 'Jefe de planta', 'Administrador'];
// Puestos que ejecutan órdenes y su capacidad (L/min), la misma que usa la pasarela.
const CUELLOS: Record<string, { linea: string; tasa: number }> = {
  U311: { linea: 'Yogurts', tasa: 25 }, U312: { linea: 'Yogurts', tasa: 15 }, U313: { linea: 'Yogurts', tasa: 10 },
  Q301: { linea: 'Quesos', tasa: 44 }, L311: { linea: 'Leche UHT', tasa: 38 },
};
// Pirámide ISA-95 dentro del MES
const NIVELES = [
  { n: 4, t: 'Negocio', roles: ['Gerencia'], quien: 'Gerencia' },
  { n: 3, t: 'Gestión de planta', roles: ['Jefe de planta'], quien: 'Jefe de planta' },
  { n: 3, t: 'Operaciones', roles: ['Supervisor', 'Calidad', 'Mantenimiento'], quien: 'Supervisión, calidad y mantenimiento' },
  { n: 2, t: 'Piso de planta', roles: ['Operario'], quien: 'Operarios' },
];

const ICONOS: Record<string, string> = {
  planta: 'M3 21V10l5 3V10l5 3V6l8 4v11z',
  turno: 'M12 3a9 9 0 1 0 0 18a9 9 0 0 0 0-18zm0 4v5l3 2',
  ordenes: 'M5 4h14v16H5zM9 9h6M9 13h6M9 17h3',
  lotes: 'M4 8l8-4l8 4l-8 4zM4 8v8l8 4l8-4V8M12 12v8',
  calidad: 'M9 12l2 2l4-4M12 3l7 3v5c0 5-3 8-7 10c-4-2-7-5-7-10V6z',
  mantenimiento: 'M14.5 6.5a4 4 0 0 0-5 5L4 17l3 3l5.5-5.5a4 4 0 0 0 5-5l-2.5 2.5l-2-.5l-.5-2z',
  indicadores: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  negocio: 'M12 2v20M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
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
const simEl = raiz.querySelector<HTMLElement>('[data-sim]')!;
const piramideEl = raiz.querySelector<HTMLElement>('[data-piramide]')!;
const dialogo = raiz.querySelector<HTMLDialogElement>('[data-dialogo]')!;

const url = raiz.dataset.url, key = raiz.dataset.key;
const sb: SupabaseClient | null = url && key ? createClient(url, key) : null;

const TABLAS = ['maquinas', 'eventos_maquina', 'ordenes', 'lotes', 'paros', 'calidad', 'perfiles', 'recepciones', 'lecturas', 'simulacion', 'sim_maquina', 'parametros'];
const D: Record<string, Fila[]> = Object.fromEntries([...TABLAS, 'archivos'].map((t) => [t, []]));
let yo = '';
let miRol = '';
let rolVista = '';
let vista: Vista | null = null;
let trazaPendiente = '';
let montada = '';
const nombre = (id: string | null) => (id ? D.perfiles.find((p) => p.id === id)?.nombre ?? '—' : 'Pasarela');
const puede = (roles: string[]) => roles.includes(miRol);
const esSim = (f: Fila) => f.origen === 'Simulación';
const tagSim = (f: Fila) => (esSim(f) ? h('span', { class: 'sim', title: 'Generado por la pasarela simulada' }, 'SIM') : null);
const P = (k: string) => Number(D.parametros.find((p) => p.clave === k)?.valor ?? 0);
const simActiva = () => Boolean(D.simulacion[0]?.activa);

let avisoT = 0;
function aviso(t: string, error = false) {
  avisoEl.textContent = t;
  avisoEl.toggleAttribute('data-error', error);
  avisoEl.hidden = false;
  clearTimeout(avisoT);
  avisoT = window.setTimeout(() => (avisoEl.hidden = true), error ? 9000 : 3500);
}

// ---------------------------------------------------------------- datos
// Supabase entrega máximo 1.000 filas por consulta: se leen por páginas.
async function paginas(mk: () => any, max = 40000) {
  let out: Fila[] = [];
  for (let i = 0; i < max; i += 1000) {
    const { data, error } = await mk().range(i, i + 999);
    if (error) return { data: null, error };
    out = out.concat(data ?? []);
    if (!data || data.length < 1000) break;
  }
  return { data: out, error: null };
}
async function cargar(t: string) {
  if (!sb) return;
  let q: () => any;
  const hace = (ms: number) => new Date(Date.now() - ms).toISOString();
  if (t === 'maquinas') q = () => sb.from(t).select('*').order('posicion');
  else if (t === 'eventos_maquina') q = () => sb.from(t).select('*').or(`fin.is.null,fin.gte.${hace(31 * 864e5)}`).order('inicio').order('id');
  else if (t === 'ordenes') q = () => sb.from(t).select('*').order('fecha', { ascending: false }).order('id', { ascending: false });
  else if (t === 'perfiles') q = () => sb.from(t).select('*').order('creado');
  else if (t === 'lecturas') q = () => sb.from(t).select('*').gte('ts', hace(3 * 36e5)).order('ts').order('id');
  else if (t === 'simulacion') q = () => sb.from(t).select('*');
  else if (t === 'sim_maquina') q = () => sb.from(t).select('*');
  else if (t === 'parametros') q = () => sb.from(t).select('*').order('orden');
  else if (t === 'archivos') {
    const { data, error } = await sb.storage.from('mes-archivos').list('', { limit: 300, sortBy: { column: 'created_at', order: 'desc' } });
    if (!error) D.archivos = (data ?? []).filter((o) => o.name !== '.emptyFolderPlaceholder') as Fila[];
    return;
  } else q = () => sb.from(t).select('*').order('creado', { ascending: false }).order('id', { ascending: false });
  const { data, error } = await paginas(q, ['lotes', 'calidad', 'paros'].includes(t) ? 8000 : 40000);
  if (error) { if (!['recepciones', 'lecturas', 'simulacion', 'sim_maquina', 'parametros'].includes(t)) aviso(`No se pudo leer ${t}: ${error.message}`, true); return; }
  D[t] = data ?? [];
}

let refrescoT = 0;
function programarRefresco() {
  if (refrescoT) return;
  refrescoT = window.setTimeout(() => {
    refrescoT = 0;
    if (!dialogo.open && vista && montada === vista.id) {
      try { vista.refrescar(); } catch (e) { console.warn(e); }
    }
    pintarSim();
    pulsoVivo();
  }, 700);
}
async function recargar(t: string) {
  await cargar(t);
  if (t === 'perfiles') revisarRol();
  programarRefresco();
}
// Tiempo real: cada cambio llega con la fila nueva y se aplica sin volver a leer la tabla.
const PK: Record<string, string> = { maquinas: 'codigo', sim_maquina: 'codigo', parametros: 'clave' };
const ASC = new Set(['eventos_maquina', 'lecturas', 'maquinas', 'perfiles', 'parametros']);
function aplicar(t: string, pl: any) {
  const pk = PK[t] ?? 'id';
  if (pl.eventType === 'DELETE') {
    const k = pl.old?.[pk];
    D[t] = D[t].filter((r) => r[pk] !== k);
  } else {
    const n = pl.new;
    const i = D[t].findIndex((r) => r[pk] === n[pk]);
    if (i >= 0) D[t][i] = n;
    else if (ASC.has(t)) D[t].push(n);
    else D[t].unshift(n);
  }
  if (t === 'lecturas' && D.lecturas.length > 9000) D.lecturas = D.lecturas.slice(-7000);
  if (t === 'perfiles') revisarRol();
  programarRefresco();
}
function revisarRol() {
  const p = D.perfiles.find((x) => x.id === yo);
  if (p && p.rol !== miRol) { miRol = p.rol; rolVista = p.rol; pintarUsuario(); pintarMenu(); irA(vista?.id ?? ''); }
}

async function guardar(p: PromiseLike<{ error: any }>, ok: string, ...tablas: string[]) {
  const { error } = await p;
  if (error) { aviso(`No se guardó: ${error.message}`, true); return false; }
  aviso(ok);
  tablas.forEach(recargar);
  return true;
}

// ---------------------------------------------------------------- tiempos de máquina
function tiempos(maq: string | null, a: number, b: number) {
  const est: Record<string, number> = {};
  const causa: Record<string, number> = {};
  const fallas: number[] = [];
  let noProg = 0, cips = 0;
  for (const e of D.eventos_maquina) {
    if (maq && e.maquina !== maq) continue;
    const ini = Date.parse(e.inicio);
    const i = Math.max(a, ini);
    const f = Math.min(b, e.fin ? Date.parse(e.fin) : Date.now());
    if (f <= i) continue;
    est[e.estado] = (est[e.estado] ?? 0) + (f - i);
    if (e.estado !== 'En marcha') causa[e.causa || e.estado] = (causa[e.causa || e.estado] ?? 0) + (f - i);
    if (e.estado === 'Parada' && NO_PROGRAMADO.has(e.causa)) noProg += f - i;
    if (ini >= a && ini < b) {
      if (e.estado === 'Falla') fallas.push((e.fin ? Date.parse(e.fin) : Date.now()) - ini);
      if (e.causa === 'Limpieza CIP') cips++;
    }
  }
  const total = Object.values(est).reduce((x, y) => x + y, 0);
  const marcha = est['En marcha'] ?? 0;
  const programado = total - noProg;
  return { est, causa, fallas, cips, total, marcha, programado, disp: programado > 60000 ? marcha / programado : null };
}
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

// ---------------------------------------------------------------- economía (supuestos editables en «parametros»)
function economia(a: number, b: number) {
  const ls = D.lotes.filter((l) => { const t = Date.parse(l.creado); return t >= a && t < b; });
  const pre = (l: Fila) => String(l.producto).slice(0, 2);
  const precio = (l: Fila) => P(`precio_${pre(l)}`);
  const lechePorL = (l: Fila) => (pre(l) === 'YG' ? P('leche_YG') : l.linea === 'Quesos' ? 1 : P('leche_otros'));
  const otrosPorL = (l: Fila) => (pre(l) === 'YF' ? P('otros_YF') : l.linea === 'Yogurts' ? P('otros_Y') : l.linea === 'Quesos' ? P('otros_Q') : P('otros_L'));
  const buenos = ls.filter((l) => l.estado !== 'Retenido');
  const retenidos = ls.filter((l) => l.estado === 'Retenido');
  const litros = ls.reduce((x, l) => x + Number(l.litros), 0);
  const ingresos = buenos.reduce((x, l) => x + Number(l.litros) * precio(l), 0);
  const lecheL = ls.reduce((x, l) => x + Number(l.litros) * lechePorL(l), 0);
  const costoLeche = lecheL * P('leche');
  const costoOtros = ls.reduce((x, l) => x + Number(l.litros) * otrosPorL(l), 0);
  let kwh = 0, kwhReposo = 0, gas = 0, agua = 0, cips = 0;
  for (const m of D.maquinas) {
    const sm = D.sim_maquina.find((x) => x.codigo === m.codigo);
    if (!sm) continue;
    const t = tiempos(m.codigo, a, b);
    const hm = t.marcha / 36e5, hr = (t.total - t.marcha) / 36e5;
    kwh += hm * Number(sm.kw); kwhReposo += hr * Number(sm.kw) * 0.15;
    gas += hm * Number(sm.gas_m3h);
    agua += hm * Number(sm.agua_m3h) + t.cips * 8;
    cips += t.cips;
  }
  const costoEnergia = (kwh + kwhReposo) * P('energia');
  const costoGas = gas * P('gas');
  const costoAgua = agua * P('agua') + cips * P('cip');
  const costos = costoLeche + costoOtros + costoEnergia + costoGas + costoAgua;
  const margen = ingresos - costos;
  // pérdidas en pesos
  const costoVarL = (l: Fila) => lechePorL(l) * P('leche') + otrosPorL(l);
  const perdRetenidos = retenidos.reduce((x, l) => x + Number(l.litros) * costoVarL(l), 0);
  const margenL: Record<string, number> = {};
  for (const ln of LINEAS) {
    const xs = ls.filter((l) => l.linea === ln);
    const lt = xs.reduce((x, l) => x + Number(l.litros), 0);
    margenL[ln] = lt ? xs.reduce((x, l) => x + Number(l.litros) * (precio(l) - costoVarL(l)), 0) / lt : 0;
  }
  const perdCausa: Record<string, number> = {};
  for (const [cod, c] of Object.entries(CUELLOS)) {
    const t = tiempos(cod, a, b);
    for (const [causa, ms] of Object.entries(t.causa)) {
      if (NO_PROGRAMADO.has(causa)) continue;
      perdCausa[causa] = (perdCausa[causa] ?? 0) + (ms / 60000) * c.tasa * Math.max(0, margenL[c.linea]);
    }
  }
  const perdParos = Object.values(perdCausa).reduce((x, y) => x + y, 0);
  const perdReposo = kwhReposo * P('energia');
  const porLinea = LINEAS.map((ln) => {
    const xs = ls.filter((l) => l.linea === ln);
    const ing = xs.filter((l) => l.estado !== 'Retenido').reduce((x, l) => x + Number(l.litros) * precio(l), 0);
    const cv = xs.reduce((x, l) => x + Number(l.litros) * costoVarL(l), 0);
    return { linea: ln, litros: xs.reduce((x, l) => x + Number(l.litros), 0), ingresos: ing, costo: cv, margen: ing - cv };
  });
  return {
    ls, litros, ingresos, lecheL, costoLeche, costoOtros, kwh: kwh + kwhReposo, kwhReposo, gas, agua, cips, costoEnergia, costoGas, costoAgua,
    costos, margen, perdRetenidos, perdParos, perdReposo, perdCausa, perdidas: perdRetenidos + perdParos + perdReposo, porLinea,
    retenidosL: retenidos.reduce((x, l) => x + Number(l.litros), 0),
  };
}

// ---------------------------------------------------------------- piezas de interfaz
const chip = (estado: string, texto = estado) => h('span', { class: `chip ${CLASE[estado] ?? ''}` }, texto);
const chipOrden = (e: string) => h('span', { class: `chip o-${e.toLowerCase().replace(/[^a-z]/g, '')}` }, e);
const chipLote = (e: string) => h('span', { class: `chip l-${e.toLowerCase().replace(/[^a-z]/g, '')}` }, e);
const vivo = (desde: string) => h('span', { class: 'vivo', 'data-desde': desde }, dur(Date.now() - Date.parse(desde)));
const vacio = (t: string) => h('p', { class: 'vacio' }, t);
const tarjeta = (titulo: string | null, ...kids: Kid[]) => h('section', { class: 'm-card' }, titulo ? h('h3', { class: 'm-card-t mono' }, titulo) : null, ...kids);
function kpi(etq: string, valor: string, sub = '', clase = '') {
  return h('div', { class: `kpi ${clase}` }, h('span', { class: 'mono' }, etq), h('b', {}, valor), sub ? h('small', {}, sub) : null);
}
function kpiN(clave: string, etq: string, valor: number | null, fmt: (n: number) => string, sub: Kid = '', clase = '') {
  const b = h('b', {}, '—');
  contar(b, clave, valor, fmt);
  return h('div', { class: `kpi ${clase}` }, h('span', { class: 'mono' }, etq), b, sub ? h('small', {}, sub) : null);
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
function opcionesActualizar(sl: HTMLSelectElement, opciones: (string | [string, string])[]) {
  const v = sl.value;
  sl.replaceChildren(...opciones.map((o) => {
    const [val, t] = Array.isArray(o) ? o : [o, o];
    return h('option', { value: val, selected: val === v }, t);
  }));
}
function tabla(cols: [string, string, ((f: Fila) => Kid)?][], filas: Fila[], extra?: (f: Fila) => Kid, alClic?: (f: Fila, tr: HTMLElement) => void, max = 400) {
  if (!filas.length) return vacio('Sin registros todavía.');
  const vis = filas.slice(0, max);
  return h('div', { class: 'm-tabla' }, h('table', {},
    h('thead', {}, h('tr', {}, cols.map(([, t]) => h('th', {}, t)), extra ? h('th', {}) : null)),
    h('tbody', {}, vis.map((f) => {
      const tr = h('tr', alClic ? { class: 'clic', tabindex: 0 } : {},
        cols.map(([k, , fn]) => h('td', { 'data-k': k }, fn ? fn(f) : String(f[k] ?? ''))),
        extra ? h('td', { class: 'acc' }, extra(f)) : null);
      if (alClic) {
        tr.addEventListener('click', (e) => { if (!(e.target as HTMLElement).closest('button')) alClic(f, tr); });
        tr.addEventListener('keydown', (e) => { if ((e as KeyboardEvent).key === 'Enter') alClic(f, tr); });
      }
      return tr;
    })),
  ), filas.length > max ? h('p', { class: 'sub mono pie-tabla' }, `Mostrando ${max} de ${miles(filas.length)}. Exporta el CSV para verlos todos.`) : null);
}
function csv(nombreArchivo: string, cols: [string, string][], filas: Fila[]) {
  const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const txt = [cols.map(([, n]) => esc(n)).join(';'), ...filas.map((f) => cols.map(([k]) => esc(k === 'autor' ? nombre(f.autor) : f[k])).join(';'))].join('\n');
  const a = h('a', { href: URL.createObjectURL(new Blob(['﻿' + txt], { type: 'text/csv;charset=utf-8' })), download: `${nombreArchivo}_${hoyISO()}.csv` }) as HTMLAnchorElement;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
function borrarPropio(t: string, f: Fila) {
  if (!f.autor || f.autor !== yo) return null;
  return boton('Borrar', async () => {
    if (!confirm('¿Borrar este registro? No se puede deshacer.')) return;
    guardar(sb!.from(t).delete().eq('id', f.id), 'Registro borrado.', t);
  }, 'm-btn mini peligro');
}
function barras(datos: [string, number][], fmt: (n: number) => string, color = 'var(--orange)') {
  if (!datos.length) return vacio('Sin datos en el periodo.');
  const max = Math.max(...datos.map(([, v]) => v));
  const total = datos.reduce((x, [, v]) => x + v, 0);
  let acum = 0;
  return h('ol', { class: 'pareto' }, datos.map(([k, v], i) => {
    acum += v;
    return h('li', { style: `--i:${i}` },
      h('span', { class: 'p-k' }, k),
      h('span', { class: 'p-bar' }, h('i', { style: `width:${(v / max) * 100}%;background:${color}` })),
      h('span', { class: 'p-v mono' }, fmt(v)),
      h('span', { class: 'p-a mono' }, `${Math.round((acum / total) * 100)} %`));
  }));
}
function spark(codigo: string, idx = 0, w = 120, hh = 28) {
  const xs = D.lecturas.filter((l) => l.maquina === codigo);
  const vals = xs.map((l) => Number(l.valores?.[idx]?.v)).filter((v) => Number.isFinite(v));
  if (vals.length < 2) return null;
  const mn = Math.min(...vals), mx = Math.max(...vals), r = mx - mn || 1;
  const pts = vals.map((v, i) => `${((i / (vals.length - 1)) * w).toFixed(1)},${(hh - 3 - ((v - mn) / r) * (hh - 6)).toFixed(1)}`).join(' ');
  return s('svg', { viewBox: `0 0 ${w} ${hh}`, class: 'spark', preserveAspectRatio: 'none', 'aria-hidden': 'true' },
    s('polyline', { points: `0,${hh} ${pts} ${w},${hh}`, class: 'spark-a' }), s('polyline', { points: pts, class: 'spark-l' }));
}
function senalTxt(m: Fila, i = 0) {
  const x = m.senales?.[i];
  if (!x) return '';
  return `${miles(Number(x.v), Math.abs(x.v) >= 100 ? 0 : Math.abs(x.v) >= 10 ? 1 : 2)} ${x.u}`.trim();
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
  const senales = (m.senales ?? []) as Fila[];
  dialogo.replaceChildren(h('form', { method: 'dialog', class: 'dlg' },
    h('header', {},
      h('div', {}, h('span', { class: 'mono gold' }, `${m.codigo} · ${m.linea} · ${m.etapa}`), h('h3', {}, m.nombre)),
      h('button', { type: 'submit', value: 'cancelar', class: 'cerrar', 'aria-label': 'Cerrar' }, '×')),
    h('div', { class: 'dlg-ahora' }, chip(m.estado), h('span', {}, m.causa), h('span', { class: 'mono' }, 'hace ', vivo(m.desde))),
    senales.length ? h('div', { class: 'dlg-senales' }, senales.map((x, i) => h('div', {}, h('span', { class: 'mono' }, x.n), h('b', {}, senalTxt(m, i)), spark(codigo, i, 160, 30)))) : null,
    tira(codigo, hoy0, Date.now(), 'tira grande'),
    h('p', { class: 'dlg-nota mono' }, `Hoy: ${pct(t.disp)} en marcha del tiempo programado · ${t.fallas.length} fallas · ${t.cips} limpiezas CIP`),
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
// ---------- Planta en vivo: sinóptico, líneas, actividad
const POS: Record<string, [number, number]> = {
  U111: [10, 160], U121: [120, 160],
  U201: [250, 40], U202: [350, 40], U211: [450, 40], U215: [550, 40],
  U311: [670, 20], U312: [670, 72], U216: [550, 124], U313: [670, 124], U321: [790, 72], U341: [904, 72],
  Q201: [330, 196], Q202: [330, 246], Q203: [330, 296], Q301: [470, 246], Q311: [610, 246],
  L202: [470, 330], L311: [610, 330],
};
const ARISTAS: [string, string][] = [
  ['U111', 'U121'], ['U121', 'U201'], ['U121', 'Q201'], ['U121', 'Q202'], ['U121', 'Q203'], ['U121', 'L202'],
  ['U201', 'U202'], ['U202', 'U211'], ['U211', 'U215'], ['U215', 'U311'], ['U215', 'U312'], ['U215', 'U216'], ['U216', 'U313'],
  ['U311', 'U321'], ['U312', 'U321'], ['U313', 'U321'], ['U321', 'U341'],
  ['Q201', 'Q301'], ['Q202', 'Q301'], ['Q203', 'Q301'], ['Q301', 'Q311'], ['L202', 'L311'],
];
const NW = 88, NH = 42;
function sinoptico() {
  const est = (c: string) => D.maquinas.find((m) => m.codigo === c);
  const svg = s('svg', { viewBox: '0 0 1000 384', class: 'sinoptico', role: 'img', 'aria-label': 'Sinóptico de la planta en vivo' });
  const fase = `${-((performance.now() % 1200) / 1200) * 1.2}s`;
  [['RECEPCIÓN Y PASTEURIZACIÓN', 10, 150], ['YOGURTS', 250, 30], ['QUESOS', 330, 186], ['LECHE UHT', 470, 320]].forEach(([t, x, y]) =>
    svg.append(s('text', { x, y, class: 'sn-linea' }, t as string)));
  for (const [a, b] of ARISTAS) {
    const pa = POS[a], pb = POS[b];
    if (!pa || !pb) continue;
    const x1 = pa[0] + NW, y1 = pa[1] + NH / 2, x2 = pb[0], y2 = pb[1] + NH / 2, mx = (x1 + x2) / 2;
    const on = est(a)?.estado === 'En marcha' && est(b)?.estado === 'En marcha';
    svg.append(s('path', { d: `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`, class: `sn-tubo${on ? ' on' : ''}`, style: on ? `animation-delay:${fase}` : null }));
  }
  for (const m of D.maquinas) {
    const p = POS[m.codigo];
    if (!p) continue;
    const g = s('g', { class: `sn-nodo ${CLASE[m.estado]}`, transform: `translate(${p[0]},${p[1]})`, tabindex: 0, role: 'button', 'aria-label': `${m.codigo} ${m.nombre}: ${m.estado}`,
      onclick: () => abrirMaquina(m.codigo), onkeydown: (e: KeyboardEvent) => { if (e.key === 'Enter') abrirMaquina(m.codigo); } },
      s('title', {}, `${m.codigo} · ${m.nombre}\n${m.estado} · ${m.causa}${m.orden ? `\nOrden ${m.orden}` : ''}`),
      s('rect', { width: NW, height: NH, rx: 5, class: 'sn-caja' }),
      s('rect', { width: 3, height: NH, rx: 1.5, class: 'sn-barra' }),
      s('circle', { cx: NW - 10, cy: 11, r: 3.5, class: 'sn-luz' }),
      s('text', { x: 10, y: 17, class: 'sn-cod' }, m.codigo),
      s('text', { x: 10, y: 33, class: 'sn-val' }, senalTxt(m) || m.estado));
    svg.append(g);
  }
  return svg;
}
function lineaCard(ln: string) {
  const hoy0 = inicioDia();
  const ords = D.ordenes.filter((o) => o.linea === ln && o.estado === 'En ejecución');
  const ls = D.lotes.filter((l) => l.linea === ln && Date.parse(l.creado) >= hoy0);
  const litros = ls.reduce((x, l) => x + Number(l.litros), 0);
  const ultimo = D.lotes.find((l) => l.linea === ln);
  // producción por hora (hoy)
  const porHora = Array.from({ length: 24 }, (_, i) => ls.filter((l) => new Date(l.creado).getHours() === i).reduce((x, l) => x + Number(l.litros), 0));
  const mx = Math.max(1, ...porHora), ahoraH = new Date().getHours();
  const ms = D.maquinas.filter((m) => m.linea === ln);
  return h('article', { class: 'lin-card', style: `--c:${COLOR_LINEA[ln]}` },
    h('header', {}, h('h3', {}, ln), h('span', { class: 'mono' }, `${ms.filter((m) => m.estado === 'En marcha').length}/${ms.length} en marcha`)),
    h('div', { class: 'lin-num' }, h('b', { 'data-n': `l-${ln}` }, miles(litros)), h('span', { class: 'mono' }, ' L hoy · ', `${ls.length} lotes`)),
    h('div', { class: 'lin-horas', 'aria-label': 'Litros por hora hoy' }, porHora.map((v, i) => h('i', { class: i === ahoraH ? 'ahora' : i > ahoraH ? 'fut' : '', style: `height:${Math.max(2, (v / mx) * 100)}%;--d:${i * 18}ms`, title: `${String(i).padStart(2, '0')}:00 · ${miles(v)} L` }))),
    h('div', { class: 'lin-ords' }, ords.length ? ords.map((o) => {
      const cu = CUELLOS[o.maquina ?? ''];
      const m = D.maquinas.find((x) => x.codigo === o.maquina);
      const corre = m?.estado === 'En marcha' && cu;
      const p = Math.min(1, Number(o.litros_real) / Number(o.litros_plan));
      return h('div', { class: 'lin-ord' },
        h('div', { class: 'lin-ord-top' }, h('b', { class: 'mono' }, o.codigo), tagSim(o), m ? chip(m.estado, `${m.codigo} · ${m.estado}`) : null),
        h('span', { class: 'sub' }, o.producto),
        h('div', { class: 'prog' }, h('i', { style: `width:${p * 100}%`, 'data-prog': '', 'data-base': o.litros_real, 'data-plan': o.litros_plan, 'data-tasa': corre ? cu!.tasa : 0, 'data-t0': D.simulacion[0]?.ultimo ?? '' }),
          h('span', { class: 'mono', 'data-prog-t': '' }, `${miles(o.litros_real)} / ${miles(o.litros_plan)} L`)));
    }) : vacio('Sin orden en ejecución.')),
    ultimo ? h('button', { type: 'button', class: 'lin-lote', onclick: () => { trazaPendiente = ultimo.codigo; location.hash = '#lotes'; } },
      h('span', { class: 'mono' }, 'Último lote'), h('b', { class: 'mono' }, ultimo.codigo), chipLote(ultimo.estado), h('span', { class: 'arrow' }, 'Trazar →')) : null);
}
const vistosFeed = new Set<string>();
function actividad() {
  const it: { k: string; t: number; tipo: string; c: string; x: Kid; sim: boolean }[] = [];
  D.eventos_maquina.slice(-60).forEach((e) => it.push({ k: `e${e.id}`, t: Date.parse(e.inicio), tipo: e.maquina, c: CLASE[e.estado], x: [`${e.estado}`, h('span', { class: 'sub' }, ` · ${e.causa}`)], sim: esSim(e) }));
  D.lotes.slice(0, 20).forEach((l) => it.push({ k: `l${l.id}`, t: Date.parse(l.creado), tipo: 'Lote', c: 'f-lote', x: [h('b', { class: 'mono' }, l.codigo), ` · ${miles(l.litros)} L · `, l.producto.split(' · ')[1] ?? l.producto], sim: esSim(l) }));
  D.calidad.slice(0, 20).filter((q) => q.resultado !== 'Aprobado' || Math.random() < 1).slice(0, 12).forEach((q) => it.push({ k: `q${q.id}`, t: Date.parse(q.creado), tipo: 'Calidad', c: q.resultado === 'Aprobado' ? 'e-marcha' : 'e-falla', x: [h('b', { class: 'mono' }, q.lote), ` · ${q.prueba}: ${q.valor} · ${q.resultado}`], sim: esSim(q) }));
  D.recepciones.slice(0, 8).forEach((r) => it.push({ k: `r${r.id}`, t: Date.parse(r.creado), tipo: 'Leche', c: r.estado === 'Aceptada' ? 'e-limpieza' : 'e-falla', x: [h('b', { class: 'mono' }, r.codigo), ` · ${miles(r.litros)} L · ${r.proveedor}${r.estado === 'Rechazada' ? ' · rechazada' : ''}`], sim: esSim(r) }));
  D.ordenes.slice(0, 15).forEach((o) => it.push({ k: `o${o.id}${o.estado}`, t: Date.parse(o.fin ?? o.inicio ?? o.creado), tipo: 'Orden', c: 'f-orden', x: [h('b', { class: 'mono' }, o.codigo), ` · ${o.estado} · ${o.producto.split(' · ')[1] ?? o.producto}`], sim: esSim(o) }));
  const top = it.filter((x) => Number.isFinite(x.t)).sort((a, b) => b.t - a.t).slice(0, 28);
  const primera = vistosFeed.size === 0;
  const ul = h('ol', { class: 'actividad' }, top.map((x) => {
    const nuevo = !primera && !vistosFeed.has(x.k);
    vistosFeed.add(x.k);
    return h('li', { class: `${x.c}${nuevo ? ' nuevo' : ''}` }, h('span', { class: 'mono a-t' }, hora(x.t)), h('i', {}), h('div', {}, h('span', { class: 'mono a-tipo' }, x.tipo, x.sim ? h('span', { class: 'sim' }, 'SIM') : null), h('div', {}, x.x)));
  }));
  return top.length ? ul : vacio('Sin actividad todavía.');
}
const vPlanta: Vista = {
  id: 'planta', titulo: 'Planta en vivo', grupo: 'Nivel 2 · Piso de planta', roles: ROLES,
  montar(c) {
    c.append(h('div', { 'data-p-kpi': '' }),
      h('div', { class: 'planta-grid' },
        h('section', { class: 'm-card sn-card' }, h('div', { class: 'm-card-cab' }, h('h3', { class: 'm-card-t mono' }, 'Sinóptico de la planta'),
          h('div', { class: 'leyenda mono' }, ESTADOS.map((e) => h('span', { class: CLASE[e] }, h('i', {}), e)))),
          h('div', { class: 'sn-scroll', 'data-p-sn': '' }), h('p', { class: 'nota mono' }, 'Las tuberías se animan cuando las dos máquinas están en marcha. Clic en una máquina para ver sus señales o cambiar su estado.')),
        h('aside', { class: 'm-card act-card' }, h('div', { class: 'm-card-cab' }, h('h3', { class: 'm-card-t mono' }, 'Actividad en vivo'), h('span', { class: 'en-vivo mono' }, h('span', { class: 'pulse', 'data-live': '' }), 'tiempo real')), h('div', { 'data-p-act': '' }))),
      h('div', { class: 'lineas-grid', 'data-p-lin': '' }),
      h('details', { class: 'm-card detalle', open: true }, h('summary', { class: 'm-card-t mono' }, 'Máquinas: estado, señal principal y tendencia de 3 h'), h('div', { 'data-p-maq': '' })));
  },
  refrescar() {
    const c = cont;
    const hoy0 = inicioDia();
    const cuenta = (e: string) => D.maquinas.filter((m) => m.estado === e).length;
    const t = tiempos(null, hoy0, Date.now());
    const lsHoy = D.lotes.filter((l) => Date.parse(l.creado) >= hoy0);
    const litrosHoy = lsHoy.reduce((x, l) => x + Number(l.litros), 0);
    const leche = D.recepciones.filter((r) => Date.parse(r.creado) >= hoy0 && r.estado === 'Aceptada').reduce((x, r) => x + Number(r.litros), 0);
    const disp = lsHoy.filter((l) => ['Liberado', 'Retenido'].includes(l.estado));
    const lib = disp.filter((l) => l.estado === 'Liberado').length;
    const metaHoy = P('meta_dia') * ((Date.now() - hoy0) / 864e5);
    c.querySelector('[data-p-kpi]')!.replaceChildren(h('div', { class: 'kpis' },
      kpiN('p-litros', 'Producción hoy', litrosHoy, (n) => `${miles(n)} L`, metaHoy ? `${pct(litrosHoy / metaHoy)} de la meta a esta hora` : `${lsHoy.length} lotes`, 'k-oee'),
      kpiN('p-marcha', 'En marcha', cuenta('En marcha'), (n) => `${Math.round(n)} / ${D.maquinas.length}`, 'máquinas ahora mismo', 'k-marcha'),
      kpiN('p-disp', 'Disponibilidad hoy', t.disp, (n) => pct(n), 'en marcha / tiempo programado'),
      kpiN('p-falla', 'Fallas abiertas', cuenta('Falla'), (n) => String(Math.round(n)), cuenta('Falla') ? 'mantenimiento avisado' : 'sin fallas', cuenta('Falla') ? 'k-falla' : ''),
      kpiN('p-cal', 'Lotes liberados', disp.length ? lib / disp.length : null, (n) => pct(n), `${lib} de ${disp.length} decididos hoy`),
      kpiN('p-leche', 'Leche recibida hoy', leche, (n) => `${miles(n)} L`, `${D.recepciones.filter((r) => Date.parse(r.creado) >= hoy0).length} cisternas`)));
    c.querySelector('[data-p-sn]')!.replaceChildren(sinoptico());
    c.querySelector('[data-p-act]')!.replaceChildren(actividad());
    c.querySelector('[data-p-lin]')!.replaceChildren(...LINEAS.map(lineaCard));
    c.querySelector('[data-p-maq]')!.replaceChildren(...LINEAS_PLANTA.map((l) => {
      const ms = D.maquinas.filter((m) => m.linea === l);
      return ms.length ? h('section', { class: 'linea' }, h('header', {}, h('h3', {}, l)), h('div', { class: 'maqs' }, ms.map(tileMaquina))) : '';
    }));
  },
};
function tileMaquina(m: Fila) {
  const vel = (m.senales ?? []).find((x: Fila) => x.n === 'Velocidad');
  const porMin = vel ? (vel.u === 'palets/h' ? Number(vel.v) / 60 : Number(vel.v)) : 0;
  return h('button', { type: 'button', class: `maq ${CLASE[m.estado]}`, onclick: () => abrirMaquina(m.codigo) },
    h('span', { class: 'maq-top' }, h('span', { class: 'mono' }, m.codigo), chip(m.estado)),
    h('span', { class: 'maq-n' }, m.nombre),
    h('span', { class: 'maq-c' }, m.causa || '—', m.orden ? h('span', { class: 'mono' }, ` · ${m.orden}`) : null),
    h('span', { class: 'maq-fila' }, h('span', { class: 'maq-t mono' }, vivo(m.desde)), h('span', { class: 'maq-s mono' }, senalTxt(m))),
    spark(m.codigo),
    vel ? h('span', { class: 'maq-cont mono' }, 'Contador ', h('b', { 'data-contador': '', 'data-base': m.contador, 'data-vel': m.estado === 'En marcha' ? porMin : 0, 'data-t0': m.lectura ?? '' }, miles(Number(m.contador))), ` ${String(vel.u).split('/')[0]}`) : null,
    tira(m.codigo, inicioDia(), Date.now()));
}

// ---------- Mi turno (operario)
let miMaquina = (() => { try { return localStorage.getItem('mes-maquina') ?? ''; } catch { return ''; } })();
const vTurno: Vista = {
  id: 'turno', titulo: 'Mi turno', grupo: 'Nivel 2 · Piso de planta', roles: ['Operario', 'Supervisor', 'Jefe de planta', 'Administrador'],
  montar(c) {
    if (!D.maquinas.some((m) => m.codigo === miMaquina)) miMaquina = D.maquinas.find((m) => m.codigo === 'U311')?.codigo ?? D.maquinas[0]?.codigo ?? '';
    const sm = sel('maquina', D.maquinas.map((m) => [m.codigo, `${m.codigo} · ${m.nombre}`] as [string, string]), miMaquina);
    sm.addEventListener('change', () => { miMaquina = sm.value; try { localStorage.setItem('mes-maquina', miMaquina); } catch {} vTurno.refrescar(); });
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
      if (await guardar(sb!.from('lotes').insert({ linea, producto: o?.producto ?? PRODUCTOS[linea][0], codigo: lCodigo.value.trim(), litros: Number(lLitros.value), orden: lOrden.value, estado: 'En proceso', recepcion: D.recepciones.find((r) => r.estado === 'Aceptada')?.codigo ?? '' }), 'Lote registrado.', 'lotes')) fl.reset();
    });
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
    const tt = m ? tiempos(m.codigo, iniT.getTime(), Date.now()) : null;
    c.querySelector('[data-t-turno]')!.replaceChildren(h('div', { class: 'turno-info' },
      h('b', {}, tn.nombre), h('span', { class: 'mono' }, `${String(tn.ini).padStart(2, '0')}:00 – ${String(tn.fin).padStart(2, '0')}:00`),
      h('span', { class: 'mono' }, 'Faltan ', h('span', { 'data-hasta': String(finTurno()) }, dur(finTurno() - Date.now())))),
      m && tt ? h('div', { class: 'kpis mini' },
        kpi('En marcha', dur(tt.marcha)), kpi('Disponibilidad', pct(tt.disp)), kpi('Fallas', String(tt.fallas.length)),
        kpi('Producido', `${miles(Number(m.contador))}`, 'contador de la máquina')) : null);
    if (m) {
      const acc = (t: string, e: string, ca: string, cl: string) => h('button', { type: 'button', class: `accion ${cl}`, disabled: m.estado === e && m.causa === ca, onclick: () => cambiarEstado(m.codigo, e, ca) }, h('i', {}), t);
      c.querySelector('[data-t-maq]')!.replaceChildren(
        h('div', { class: `mi-maq ${CLASE[m.estado]}` },
          h('div', {}, h('span', { class: 'mono' }, `${m.codigo} · ${m.linea}`), h('b', {}, m.estado), h('span', {}, m.causa, m.orden ? ` · ${m.orden}` : '')),
          h('span', { class: 'mi-maq-t mono' }, vivo(m.desde))),
        (m.senales ?? []).length ? h('div', { class: 'dlg-senales' }, (m.senales as Fila[]).map((x, i) => h('div', {}, h('span', { class: 'mono' }, x.n), h('b', {}, senalTxt(m, i)), spark(m.codigo, i, 160, 30)))) : null,
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
      h('div', {}, h('b', { class: 'mono' }, o.codigo), ' ', chipOrden(o.estado), tagSim(o), o.prioridad !== 'Normal' ? h('span', { class: `chip p-${o.prioridad.toLowerCase()}` }, o.prioridad) : null,
        h('div', { class: 'sub' }, `${o.producto} · ${miles(o.litros_plan)} L · ${o.turno}${o.maquina ? ` · ${o.maquina}` : ''}`), progreso(o)),
      h('div', { class: 'btns' }, o.estado === 'Liberada'
        ? boton('Iniciar aquí', async () => {
          if (await guardar(sb!.from('ordenes').update({ estado: 'En ejecución', inicio: new Date().toISOString(), maquina: m!.codigo }).eq('id', o.id), `${o.codigo} en ejecución.`, 'ordenes'))
            cambiarEstado(m!.codigo, 'En marcha', 'Producción', o.codigo);
        }, 'm-btn mini')
        : terminarOrden(o))))) : vacio(linea && LINEAS.includes(linea) ? 'No hay órdenes liberadas para esta línea.' : 'Esta máquina es de recepción: no lleva órdenes de producto.'));
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
  return `${pre}-${d}-${String(n).padStart(3, '0')}`;
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
  id: 'ordenes', titulo: 'Órdenes de producción', grupo: 'Nivel 3 · Operaciones', roles: ['Supervisor', 'Jefe de planta', 'Administrador'],
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
      c.append(h('details', { class: 'm-card' }, h('summary', { class: 'm-card-t mono' }, 'Nueva orden'), f));
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
    const hoy = os.filter((o) => o.fecha === hoyISO());
    c.querySelector('[data-o-kpi]')!.textContent = `Hoy: ${hoy.length} órdenes · ${miles(hoy.reduce((x, o) => x + Number(o.litros_plan), 0))} L planeados · ${miles(hoy.reduce((x, o) => x + Number(o.litros_real), 0))} L producidos`;
    const sig: Record<string, [string, Fila]> = { Planeada: ['Liberar', { estado: 'Liberada' }], Terminada: ['Cerrar', { estado: 'Cerrada' }] };
    c.querySelector('[data-o-kan]')!.replaceChildren(...ESTADOS_ORDEN.map((e) => {
      const lista = os.filter((o) => o.estado === e);
      const visibles = ['Cerrada', 'Terminada'].includes(e) ? lista.slice(0, 8) : lista;
      return h('section', { class: 'col' },
        h('header', {}, chipOrden(e), h('span', { class: 'mono' }, String(lista.length))),
        visibles.length ? visibles.map((o) => h('article', { class: `ord p-${o.prioridad.toLowerCase()}` },
          h('div', { class: 'ord-top' }, h('b', { class: 'mono' }, o.codigo), h('span', {}, tagSim(o), o.prioridad !== 'Normal' ? h('span', { class: `chip p-${o.prioridad.toLowerCase()}` }, o.prioridad) : null)),
          h('span', {}, o.producto),
          h('span', { class: 'sub mono' }, `${o.linea} · ${o.fecha} · ${o.turno}${o.maquina ? ` · ${o.maquina}` : ''}`),
          progreso(o),
          h('div', { class: 'btns' },
            e === 'En ejecución' ? terminarOrden(o) : sig[e] && puede(PLANEAN) ? boton(sig[e][0], () => guardar(sb!.from('ordenes').update(sig[e][1]).eq('id', o.id), `${o.codigo}: ${sig[e][1].estado}.`, 'ordenes'), 'm-btn mini') : null,
            e === 'Planeada' && puede(PLANEAN) ? boton('Borrar', () => confirm(`¿Borrar la orden ${o.codigo}?`) && guardar(sb!.from('ordenes').delete().eq('id', o.id), 'Orden borrada.', 'ordenes'), 'm-btn mini peligro') : null))) : vacio('—'),
        lista.length > visibles.length ? h('p', { class: 'sub mono' }, `y ${lista.length - visibles.length} más`) : null);
    }));
  },
};

// ---------- Lotes y trazabilidad
const vLotes: Vista = {
  id: 'lotes', titulo: 'Lotes y trazabilidad', grupo: 'Nivel 3 · Operaciones', roles: ['Operario', 'Supervisor', 'Calidad', 'Jefe de planta', 'Gerencia', 'Administrador'],
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
        fila.recepcion = D.recepciones.find((r) => r.estado === 'Aceptada')?.codigo ?? '';
        if (await guardar(sb!.from('lotes').insert(fila), `Lote ${fila.codigo} registrado.`, 'lotes')) { (f.querySelector('[name=litros]') as HTMLInputElement).value = ''; setTimeout(() => (codigo.value = sugerirLote(prod.value)), 600); }
      });
      c.append(h('details', { class: 'm-card' }, h('summary', { class: 'm-card-t mono' }, 'Registrar lote a mano'), f));
      (c as any)._orden = orden;
    }
    const buscar = inp('buscar', { type: 'search', placeholder: 'Lote, producto, orden o finca' });
    buscar.addEventListener('input', () => vLotes.refrescar());
    c.append(h('div', { 'data-l-kpi': '' }), h('div', { class: 'barra' }, campo('Buscar', buscar, 'ancho'), boton('Exportar CSV', () => csv('mes_lotes', [['creado', 'Fecha'], ['codigo', 'Lote'], ['linea', 'Línea'], ['producto', 'Producto'], ['orden', 'Orden'], ['recepcion', 'Leche'], ['litros', 'Litros'], ['estado', 'Estado'], ['origen', 'Origen'], ['autor', 'Registró'], ['nota', 'Nota']], D.lotes))),
      h('div', { class: 'lotes-grid' }, h('div', { 'data-l-tabla': '' }), h('aside', { class: 'm-card traza', 'data-l-traza': '' }, vacio('Elige un lote para ver su trazabilidad completa: de la finca al lote liberado.'))));
    (c as any)._buscar = buscar;
  },
  refrescar() {
    const c = cont;
    const o = (c as any)._orden as HTMLSelectElement | undefined;
    if (o) opcionesActualizar(o, [['', '— Sin orden —'], ...D.ordenes.filter((x) => !['Cerrada', 'Planeada'].includes(x.estado)).slice(0, 60).map((x) => [x.codigo, `${x.codigo} · ${x.producto}`] as [string, string])]);
    const hoy0 = inicioDia();
    const est = (e: string) => D.lotes.filter((l) => l.estado === e).length;
    c.querySelector('[data-l-kpi]')!.replaceChildren(h('div', { class: 'kpis' },
      kpiN('l-hoy', 'Lotes hoy', D.lotes.filter((l) => Date.parse(l.creado) >= hoy0).length, (n) => String(Math.round(n))),
      kpiN('l-proc', 'En proceso', est('En proceso') + est('Terminado'), (n) => String(Math.round(n)), 'esperando calidad'),
      kpiN('l-lib', 'Liberados', est('Liberado'), (n) => miles(n), 'en los registros cargados', 'k-marcha'),
      kpiN('l-ret', 'Retenidos', est('Retenido'), (n) => String(Math.round(n)), 'fuera de especificación', est('Retenido') ? 'k-falla' : '')));
    const q = ((c as any)._buscar as HTMLInputElement).value.trim().toLowerCase();
    const finca = (l: Fila) => D.recepciones.find((r) => r.codigo === l.recepcion)?.proveedor ?? '';
    const filas = D.lotes.filter((l) => !q || [l.codigo, l.producto, l.orden, l.linea, l.recepcion, finca(l)].join(' ').toLowerCase().includes(q));
    c.querySelector('[data-l-tabla]')!.replaceChildren(tabla([
      ['creado', 'Fecha', (f) => fecha(f.creado)], ['codigo', 'Lote', (f) => [h('b', { class: 'mono' }, f.codigo), tagSim(f)]], ['producto', 'Producto'],
      ['orden', 'Orden', (f) => h('span', { class: 'mono' }, f.orden || '—')], ['litros', 'Litros', (f) => miles(f.litros)], ['estado', 'Estado', (f) => chipLote(f.estado)],
    ], filas, (f) => [
      puede(DISPONEN) && f.estado !== 'Liberado' ? boton('Liberar', () => disponer(f, 'Liberado'), 'm-btn mini') : null,
      puede(DISPONEN) && f.estado !== 'Retenido' ? boton('Retener', () => disponer(f, 'Retenido'), 'm-btn mini sec') : null,
      borrarPropio('lotes', f),
    ], (f) => trazar(f), 150));
    if (trazaPendiente) {
      const l = D.lotes.find((x) => x.codigo === trazaPendiente);
      trazaPendiente = '';
      if (l) { trazar(l); c.querySelector('[data-l-traza]')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    } else if (!c.querySelector('.traza-cab') && filas[0]) trazar(filas[0]);
  },
};
function disponer(f: Fila, estado: string) {
  return guardar(sb!.from('lotes').update({ estado }).eq('id', f.id), `${f.codigo}: ${estado}.`, 'lotes');
}
function trazar(l: Fila) {
  const o = D.ordenes.find((x) => x.codigo === l.orden);
  const r = D.recepciones.find((x) => x.codigo === l.recepcion);
  const pruebas = D.calidad.filter((x) => x.lote === l.codigo);
  const ev = o ? D.eventos_maquina.filter((e) => e.orden === o.codigo) : [];
  const hermanos = o ? D.lotes.filter((x) => x.orden === o.codigo).length : 0;
  const ok = (b: boolean) => (b ? 'hecho' : '');
  const cadena = h('ol', { class: 'cadena' }, [
    ['Finca', ok(!!r)], ['Recepción', ok(!!r)], ['Pasteurización', ok(!!r)], ['Orden', ok(!!o)], ['Producción', ok(ev.length > 0 || !!o)],
    ['Lote', 'hecho'], ['Calidad', ok(pruebas.length > 0)], [l.estado === 'Retenido' ? 'Retenido' : 'Liberado', l.estado === 'Liberado' ? 'hecho' : l.estado === 'Retenido' ? 'malo' : ''],
  ].map(([t, c], i) => h('li', { class: c, style: `--i:${i}` }, h('i', {}), h('span', { class: 'mono' }, t))));
  const paso = (t: string, ...kids: Kid[]) => h('li', {}, h('span', { class: 'mono gold' }, t), h('div', {}, ...kids));
  cont.querySelector('[data-l-traza]')?.replaceChildren(
    h('h3', { class: 'm-card-t mono' }, 'Trazabilidad del lote'),
    h('div', { class: 'traza-cab' }, h('b', { class: 'mono' }, l.codigo), h('span', {}, tagSim(l), chipLote(l.estado))),
    h('p', { class: 'sub' }, `${l.producto} · ${miles(l.litros)} L · ${fecha(l.creado)}`),
    cadena,
    h('ol', { class: 'traza-pasos' },
      paso('Leche cruda', r ? [h('b', {}, r.codigo), ` · ${r.proveedor}`, h('div', { class: 'sub' }, `${miles(r.litros)} L · ${r.temperatura} °C · acidez ${r.acidez} % · grasa ${r.grasa} % · antibióticos ${r.antibioticos}`)] : 'Sin recepción asociada'),
      paso('Pasteurización', r ? `U121 · HTST 72–75 °C / 15 s (cisterna ${r.codigo})` : '—'),
      paso('Orden de producción', o ? [h('b', {}, o.codigo), ` · ${miles(o.litros_plan)} L plan · `, chipOrden(o.estado), h('div', { class: 'sub' }, `${hermanos} lotes de esta orden · ${o.turno}`)] : 'Sin orden asociada'),
      paso('Máquinas', ev.length ? h('ul', {}, [...new Set(ev.map((e) => e.maquina))].map((mq) => {
        const es = ev.filter((e) => e.maquina === mq);
        const marcha = es.filter((e) => e.estado === 'En marcha').reduce((x, e) => x + ((e.fin ? Date.parse(e.fin) : Date.now()) - Date.parse(e.inicio)), 0);
        const fallas = es.filter((e) => e.estado === 'Falla').length;
        return h('li', {}, `${mq} · ${dur(marcha)} en marcha${fallas ? ` · ${fallas} fallas durante la orden` : ''}`);
      })) : 'Sin eventos de máquina con esta orden'),
      paso('Registro', `${fecha(l.creado)} · ${nombre(l.autor)}`, l.nota ? h('div', { class: 'sub' }, l.nota) : null),
      paso('Controles de calidad', pruebas.length ? h('ul', { class: 'pruebas' }, pruebas.map((p) => h('li', {}, h('span', {}, p.prueba), h('b', { class: 'mono' }, p.valor), chipLote(p.resultado)))) : 'Pendientes')));
}

// ---------- Calidad
const vCalidad: Vista = {
  id: 'calidad', titulo: 'Calidad', grupo: 'Nivel 3 · Operaciones', roles: ['Calidad', 'Supervisor', 'Jefe de planta', 'Administrador'],
  montar(c) {
    const f = h('form', { class: 'm-form' }) as HTMLFormElement;
    const lote = inp('lote', { list: 'mes-lotes', required: true, autocomplete: 'off', placeholder: 'Código del lote' });
    f.append(campo('Lote', lote), h('datalist', { id: 'mes-lotes' }), campo('Prueba', sel('prueba', PRUEBAS)), campo('Valor', inp('valor', { required: true, autocomplete: 'off' })),
      campo('Resultado', sel('resultado', ['Aprobado', 'Rechazado', 'En revisión'])), campo('Nota', inp('nota', { placeholder: 'Opcional' })), h('button', { class: 'm-btn', type: 'submit' }, 'Registrar control'));
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (await guardar(sb!.from('calidad').insert(Object.fromEntries(new FormData(f))), 'Control registrado.', 'calidad')) (f.querySelector('[name=valor]') as HTMLInputElement).value = '';
    });
    c.append(h('div', { 'data-c-kpi': '' }), h('div', { class: 'dos' }, tarjeta('Lotes por disponer', h('div', { 'data-c-pend': '' })), tarjeta('Registrar control', f)),
      tarjeta('Recepción de leche cruda', h('div', { 'data-c-rec': '' })),
      h('div', { class: 'barra' }, h('h3', { class: 'm-card-t mono' }, 'Controles registrados'), boton('Exportar CSV', () => csv('mes_calidad', [['creado', 'Fecha'], ['lote', 'Lote'], ['prueba', 'Prueba'], ['valor', 'Valor'], ['resultado', 'Resultado'], ['origen', 'Origen'], ['autor', 'Registró'], ['nota', 'Nota']], D.calidad))),
      h('div', { 'data-c-tabla': '' }));
  },
  refrescar() {
    const c = cont;
    c.querySelector('#mes-lotes')?.replaceChildren(...D.lotes.slice(0, 200).map((l) => h('option', { value: l.codigo }, l.producto)));
    const d30 = Date.now() - 30 * 864e5;
    const cs = D.calidad.filter((x) => Date.parse(x.creado) >= d30);
    const ap = cs.filter((x) => x.resultado === 'Aprobado').length;
    const pend = D.lotes.filter((l) => ['En proceso', 'Terminado'].includes(l.estado));
    const rec = D.recepciones;
    c.querySelector('[data-c-kpi]')!.replaceChildren(h('div', { class: 'kpis' },
      kpiN('c-hoy', 'Controles hoy', D.calidad.filter((x) => Date.parse(x.creado) >= inicioDia()).length, (n) => String(Math.round(n))),
      kpiN('c-ap', 'Aprobados · 30 días', cs.length ? ap / cs.length : null, pct, `${miles(ap)} de ${miles(cs.length)} controles`, 'k-marcha'),
      kpiN('c-pend', 'Lotes por disponer', pend.length, (n) => String(Math.round(n)), 'en proceso o terminados', pend.length ? 'k-cambio' : ''),
      kpiN('c-rec', 'Leche rechazada', rec.filter((r) => r.estado === 'Rechazada').length, (n) => String(Math.round(n)), `de ${rec.length} cisternas (antibióticos)`)));
    c.querySelector('[data-c-pend]')!.replaceChildren(pend.length ? h('ul', { class: 'lista' }, pend.slice(0, 12).map((l) => {
      const ps = D.calidad.filter((x) => x.lote === l.codigo);
      return h('li', {}, h('div', {}, h('b', { class: 'mono' }, l.codigo), ' ', chipLote(l.estado), tagSim(l), h('div', { class: 'sub' }, `${l.producto} · ${miles(l.litros)} L · ${ps.length} controles${ps.some((p) => p.resultado !== 'Aprobado') ? ' · con desviaciones' : ''}`)),
        puede(DISPONEN) ? h('div', { class: 'btns' }, boton('Liberar', () => disponer(l, 'Liberado'), 'm-btn mini'), boton('Retener', () => disponer(l, 'Retenido'), 'm-btn mini sec')) : null);
    })) : vacio('No hay lotes esperando decisión.'));
    c.querySelector('[data-c-rec]')!.replaceChildren(tabla([
      ['creado', 'Fecha', (r) => fecha(r.creado)], ['codigo', 'Cisterna', (r) => [h('b', { class: 'mono' }, r.codigo), tagSim(r)]], ['proveedor', 'Finca'],
      ['litros', 'Litros', (r) => miles(r.litros)], ['temperatura', 'T (°C)'], ['acidez', 'Acidez (%)'], ['grasa', 'Grasa (%)'],
      ['antibioticos', 'Antibióticos', (r) => chipLote(r.antibioticos === 'Negativo' ? 'Aprobado' : 'Rechazado')], ['estado', 'Estado', (r) => chipLote(r.estado === 'Aceptada' ? 'Liberado' : 'Retenido')],
    ], rec, undefined, undefined, 15));
    c.querySelector('[data-c-tabla]')!.replaceChildren(tabla([
      ['creado', 'Fecha', (f) => fecha(f.creado)], ['lote', 'Lote', (f) => [h('b', { class: 'mono' }, f.lote), tagSim(f)]], ['prueba', 'Prueba'], ['valor', 'Valor'],
      ['resultado', 'Resultado', (f) => chipLote(f.resultado)], ['autor', 'Registró', (f) => nombre(f.autor)], ['nota', 'Nota'],
    ], D.calidad, (f) => borrarPropio('calidad', f), undefined, 120));
  },
};

// ---------- Mantenimiento
const vMant: Vista = {
  id: 'mantenimiento', titulo: 'Mantenimiento', grupo: 'Nivel 3 · Operaciones', roles: ['Mantenimiento', 'Supervisor', 'Jefe de planta', 'Administrador'],
  montar(c) {
    c.append(h('div', { 'data-m-kpi': '' }), tarjeta('Atención inmediata', h('div', { 'data-m-alertas': '' })),
      h('div', { class: 'dos' }, tarjeta('Tiempo perdido por causa · 5 días', h('div', { 'data-m-pareto': '' })), tarjeta('Paros cortos registrados a mano · 14 días', h('div', { 'data-m-paros': '' }))),
      tarjeta('Confiabilidad por máquina · 5 días', h('div', { 'data-m-tabla': '' })));
  },
  refrescar() {
    const c = cont;
    const a = Date.now() - 5 * 864e5, b = Date.now();
    const filas = D.maquinas.map((m) => {
      const t = tiempos(m.codigo, a, b);
      const tf = t.est['Falla'] ?? 0;
      return { m, t, nf: t.fallas.length, tf, mttr: t.fallas.length ? t.fallas.reduce((x, y) => x + y, 0) / t.fallas.length : null, mtbf: t.fallas.length ? t.marcha / t.fallas.length : null };
    });
    const nf = filas.reduce((x, f) => x + f.nf, 0);
    const todas = filas.flatMap((f) => f.t.fallas);
    const marcha = filas.reduce((x, f) => x + f.t.marcha, 0);
    c.querySelector('[data-m-kpi]')!.replaceChildren(h('div', { class: 'kpis' },
      kpiN('m-ab', 'Fallas abiertas', D.maquinas.filter((m) => m.estado === 'Falla').length, (n) => String(Math.round(n)), '', D.maquinas.some((m) => m.estado === 'Falla') ? 'k-falla' : ''),
      kpiN('m-mant', 'En mantenimiento', D.maquinas.filter((m) => m.estado === 'Mantenimiento').length, (n) => String(Math.round(n))),
      kpiN('m-nf', 'Fallas · 5 días', nf, (n) => String(Math.round(n))),
      kpi('MTTR', todas.length ? dur(todas.reduce((x, y) => x + y, 0) / todas.length) : '—', 'tiempo medio para reparar'),
      kpi('MTBF', nf ? dur(marcha / nf) : '—', 'tiempo en marcha entre fallas')));
    const al = D.maquinas.filter((m) => ['Falla', 'Mantenimiento'].includes(m.estado)).sort((x, y) => Date.parse(x.desde) - Date.parse(y.desde));
    c.querySelector('[data-m-alertas]')!.replaceChildren(al.length ? h('ul', { class: 'lista' }, al.map((m) => h('li', { class: `alerta ${CLASE[m.estado]}` },
      h('div', {}, h('b', { class: 'mono' }, m.codigo), ` ${m.nombre} `, chip(m.estado), h('div', { class: 'sub' }, `${m.causa} · ${m.linea} · hace `, vivo(m.desde))),
      h('div', { class: 'btns' },
        m.estado === 'Falla' ? boton('Atender', () => cambiarEstado(m.codigo, 'Mantenimiento', 'Correctivo'), 'm-btn mini sec') : null,
        boton('Reparada · arrancar', () => cambiarEstado(m.codigo, 'En marcha', 'Producción'), 'm-btn mini'))))) : vacio('Ninguna máquina en falla ni en mantenimiento.'));
    const causas: Record<string, number> = {};
    filas.forEach((f) => Object.entries(f.t.causa).forEach(([k, v]) => { if (!NO_PROGRAMADO.has(k)) causas[k] = (causas[k] ?? 0) + v; }));
    c.querySelector('[data-m-pareto]')!.replaceChildren(barras(Object.entries(causas).sort((x, y) => y[1] - x[1]).slice(0, 8), (v) => dur(v)));
    const pc: Record<string, number> = {};
    D.paros.filter((p) => Date.parse(p.creado) >= Date.now() - 14 * 864e5).forEach((p) => (pc[p.causa] = (pc[p.causa] ?? 0) + Number(p.minutos)));
    c.querySelector('[data-m-paros]')!.replaceChildren(barras(Object.entries(pc).sort((x, y) => y[1] - x[1]), (v) => `${miles(v)} min`, 'var(--gold)'));
    c.querySelector('[data-m-tabla]')!.replaceChildren(tabla([
      ['codigo', 'Máquina', (f) => [h('b', { class: 'mono' }, f.m.codigo), ` ${f.m.nombre}`]], ['estado', 'Ahora', (f) => chip(f.m.estado)],
      ['disp', 'Disponibilidad', (f) => pct(f.t.disp)], ['nf', 'Fallas', (f) => String(f.nf)], ['tf', 'Tiempo en falla', (f) => (f.tf ? dur(f.tf) : '—')],
      ['mttr', 'MTTR', (f) => (f.mttr == null ? '—' : dur(f.mttr))], ['mtbf', 'MTBF', (f) => (f.mtbf == null ? '—' : dur(f.mtbf))],
      ['tira', 'Últimos 5 días', (f) => tira(f.m.codigo, a, b)],
    ], filas.sort((x, y) => y.nf - x.nf || y.tf - x.tf) as unknown as Fila[]));
  },
};

// ---------- Indicadores (jefe de planta)
let periodo = 1;
function segmentos(valor: number, cambiar: (d: number) => void) {
  const per = h('div', { class: 'segmentos', role: 'group', 'aria-label': 'Periodo' }, [[1, 'Hoy'], [5, '5 días'], [30, '30 días']].map(([d, t]) =>
    h('button', { type: 'button', 'aria-pressed': String(d === valor), onclick: (e: Event) => { per.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b === e.currentTarget))); cambiar(d as number); } }, t as string)));
  return per;
}
function rangoDe(dias: number) {
  const b = Date.now();
  return { a: dias === 1 ? inicioDia() : inicioDia() - (dias - 1) * 864e5, b };
}
const vInd: Vista = {
  id: 'indicadores', titulo: 'Indicadores de planta', grupo: 'Nivel 3 · Gestión de planta', roles: ['Supervisor', 'Jefe de planta', 'Gerencia', 'Administrador'],
  montar(c) {
    c.append(h('div', { class: 'barra' }, segmentos(periodo, (d) => { periodo = d; vInd.refrescar(); }), h('p', { class: 'nota mono' }, 'OEE = disponibilidad × cumplimiento del plan × calidad, con los registros del MES.')),
      h('div', { 'data-i-kpi': '' }),
      h('div', { class: 'dos' }, tarjeta('Litros por día y línea', h('div', { 'data-i-litros': '' })), tarjeta('Pérdidas de tiempo por causa', h('div', { 'data-i-pareto': '' }))),
      tarjeta('Estados de las máquinas hoy', h('div', { 'data-i-gantt': '' })),
      tarjeta('Resumen por línea', h('div', { 'data-i-lineas': '' })));
  },
  refrescar() {
    const c = cont;
    const { a, b } = rangoDe(periodo);
    const t = tiempos(null, a, b);
    const os = D.ordenes.filter((o) => o.fin && Date.parse(o.fin) >= a);
    const plan = os.reduce((x, o) => x + Number(o.litros_plan), 0), real = os.reduce((x, o) => x + Number(o.litros_real), 0);
    const cumpl = plan ? Math.min(1, real / plan) : null;
    const ls = D.lotes.filter((l) => Date.parse(l.creado) >= a);
    const dispuestos = ls.filter((l) => ['Liberado', 'Retenido'].includes(l.estado));
    const lib = dispuestos.filter((l) => l.estado === 'Liberado').reduce((x, l) => x + Number(l.litros), 0);
    const tot = dispuestos.reduce((x, l) => x + Number(l.litros), 0);
    const cal = tot ? lib / tot : null;
    const oee = t.disp != null && cumpl != null && cal != null ? t.disp * cumpl * cal : null;
    const perd = Object.entries(t.causa).filter(([k]) => !NO_PROGRAMADO.has(k)).reduce((x, [, v]) => x + v, 0);
    c.querySelector('[data-i-kpi]')!.replaceChildren(h('div', { class: 'kpis grandes' },
      kpiN('i-oee', 'OEE', oee, pct, oee == null ? 'faltan datos de algún factor' : 'disponibilidad × cumplimiento × calidad', 'k-oee'),
      kpiN('i-disp', 'Disponibilidad', t.disp, pct, 'en marcha / tiempo programado'),
      kpiN('i-cum', 'Cumplimiento del plan', cumpl, pct, `${miles(real)} de ${miles(plan)} L en órdenes terminadas`),
      kpiN('i-cal', 'Calidad', cal, pct, `${miles(lib)} L liberados de ${miles(tot)} L`),
      kpiN('i-lit', 'Litros registrados', ls.reduce((x, l) => x + Number(l.litros), 0), (n) => miles(n), `${ls.length} lotes`),
      kpi('Tiempo perdido', perd ? dur(perd) : '—', 'fallas, cambios, limpiezas, esperas'),
      kpiN('i-ord', 'Órdenes terminadas', os.length, (n) => String(Math.round(n))),
      kpiN('i-ret', 'Retenidos', ls.filter((l) => l.estado === 'Retenido').length, (n) => String(Math.round(n)), 'lotes del periodo')));
    const dias = Math.max(periodo, 7);
    const d0 = inicioDia() - (dias - 1) * 864e5;
    const porDia = Array.from({ length: dias }, (_, i) => {
      const x0 = d0 + i * 864e5;
      const r: Record<string, number> = {};
      D.lotes.filter((l) => { const tt = Date.parse(l.creado); return tt >= x0 && tt < x0 + 864e5; }).forEach((l) => (r[l.linea] = (r[l.linea] ?? 0) + Number(l.litros)));
      return { x0, r, tot: Object.values(r).reduce((p, q) => p + q, 0) };
    });
    c.querySelector('[data-i-litros]')!.replaceChildren(barrasDia(porDia.map((d) => ({ x0: d.x0, partes: LINEAS.map((l) => [l, d.r[l] ?? 0] as [string, number]) })), (v) => `${miles(v)} L`),
      h('div', { class: 'leyenda mono' }, LINEAS.map((l) => h('span', { style: `--c:${COLOR_LINEA[l]}` }, h('i', {}), l))));
    c.querySelector('[data-i-pareto]')!.replaceChildren(barras(Object.entries(t.causa).filter(([k]) => !NO_PROGRAMADO.has(k)).sort((x, y) => y[1] - x[1]).slice(0, 8), (v) => dur(v)));
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
        ordenes: String(os.filter((o) => o.linea === l).length), cal: pct(lt ? dsp.filter((x) => x.estado === 'Liberado').reduce((x, y) => x + Number(y.litros), 0) / lt : null),
      };
    })));
  },
};
// barras apiladas por día (SVG, crecen al aparecer)
function barrasDia(dias: { x0: number; partes: [string, number][] }[], fmt: (n: number) => string, colores: Record<string, string> = COLOR_LINEA) {
  const max = Math.max(1, ...dias.map((d) => d.partes.reduce((x, [, v]) => x + Math.max(0, v), 0)));
  const W = 640, H = 220, pad = 40, bw = (W - pad - 8) / dias.length;
  const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, class: 'graf crece', role: 'img' });
  [0, 0.5, 1].forEach((k) => {
    const y = H - 24 - k * (H - 40);
    svg.append(s('line', { x1: pad, x2: W, y1: y, y2: y, class: 'g-rej' }), s('text', { x: pad - 6, y: y + 4, 'text-anchor': 'end', class: 'g-txt' }, fmt(max * k).replace(/\$ /, '$')));
  });
  dias.forEach((d, i) => {
    let y = H - 24;
    const g = s('g', { class: 'col-dia', style: `--d:${i * 40}ms` });
    d.partes.forEach(([l, v]) => {
      if (v <= 0) return;
      const hh = (v / max) * (H - 40);
      y -= hh;
      g.append(s('rect', { x: pad + i * bw + bw * 0.18, y, width: bw * 0.64, height: hh, style: `fill:${colores[l] ?? 'var(--gold)'}` }, s('title', {}, `${new Date(d.x0).toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })} · ${l}: ${fmt(v)}`)));
    });
    svg.append(g);
    if (dias.length <= 10 || i % Math.ceil(dias.length / 10) === 0) svg.append(s('text', { x: pad + i * bw + bw / 2, y: H - 6, 'text-anchor': 'middle', class: 'g-txt' }, new Date(d.x0).toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })));
  });
  return svg;
}

// ---------- Negocio (gerencia): pesos, márgenes, pérdidas y consumos
let periodoN = 5;
const vNegocio: Vista = {
  id: 'negocio', titulo: 'Negocio', grupo: 'Nivel 4 · Negocio', roles: ['Gerencia', 'Jefe de planta', 'Administrador'],
  montar(c) {
    c.append(h('div', { class: 'barra' }, segmentos(periodoN, (d) => { periodoN = d; vNegocio.refrescar(); }),
      h('p', { class: 'nota mono' }, 'Pesos colombianos calculados con la producción registrada y los precios supuestos de abajo (editables).')),
      h('div', { 'data-n-resumen': '' }),
      h('div', { 'data-n-kpi': '' }),
      h('div', { class: 'dos' }, tarjeta('De ingresos a margen', h('div', { 'data-n-cascada': '' })), tarjeta('Margen por día', h('div', { 'data-n-dias': '' }))),
      h('div', { class: 'dos' }, tarjeta('Ingresos y margen por línea', h('div', { 'data-n-lineas': '' })), tarjeta('Dónde se pierde la plata', h('div', { 'data-n-perd': '' }))),
      tarjeta('Consumos e intensidad', h('div', { 'data-n-cons': '' })),
      h('details', { class: 'm-card' }, h('summary', { class: 'm-card-t mono' }, 'Supuestos de precios y costos'), h('div', { 'data-n-param': '' })));
  },
  refrescar() {
    const c = cont;
    const { a, b } = rangoDe(periodoN);
    const e = economia(a, b);
    const dias = (b - a) / 864e5;
    const meta = P('meta_dia') * dias;
    const mPct = e.ingresos ? e.margen / e.ingresos : null;
    c.querySelector('[data-n-resumen]')!.replaceChildren(h('div', { class: 'resumen-ej' },
      h('span', { class: 'mono gold' }, periodoN === 1 ? 'Hoy, hasta ahora' : `Últimos ${periodoN} días`),
      h('p', {}, 'La planta produjo ', h('b', {}, `${miles(e.litros)} L`), ` (${pct(meta ? e.litros / meta : null)} de la meta), que valen `, h('b', {}, cop(e.ingresos)),
        '. Después de leche, insumos, energía, gas y agua queda un margen de contribución de ', h('b', { class: e.margen >= 0 ? 'pos' : 'neg' }, cop(e.margen)), ` (${pct(mPct)}).`,
        ' Las pérdidas evitables suman ', h('b', { class: 'neg' }, cop(e.perdidas)), ', sobre todo por ',
        (Object.entries(e.perdCausa).sort((x, y) => y[1] - x[1])[0]?.[0] ?? 'paros').toLowerCase(), '.')));
    c.querySelector('[data-n-kpi]')!.replaceChildren(h('div', { class: 'kpis grandes' },
      kpiN('n-ing', 'Ingresos', e.ingresos, cop, 'producción no retenida × precio', 'k-oee'),
      kpiN('n-cos', 'Costo variable', e.costos, cop, `${cop(e.litros ? e.costos / e.litros : null)} por litro`),
      kpiN('n-mar', 'Margen de contribución', e.margen, cop, `${pct(mPct)} de los ingresos`, e.margen >= 0 ? 'k-marcha' : 'k-falla'),
      kpiN('n-per', 'Pérdidas evitables', e.perdidas, cop, 'paros, retenidos y energía en reposo', 'k-falla'),
      kpiN('n-lit', 'Producción', e.litros, (n) => `${miles(n)} L`, `meta ${miles(meta)} L`),
      kpiN('n-lec', 'Leche consumida', e.lecheL, (n) => `${miles(n)} L`, cop(e.costoLeche)),
      kpiN('n-kwh', 'Energía', e.kwh, (n) => `${miles(n)} kWh`, cop(e.costoEnergia)),
      kpiN('n-agua', 'Agua', e.agua, (n) => `${miles(n, 0)} m³`, `${e.cips} limpiezas CIP`)));
    // cascada
    const pasos: [string, number, string][] = [['Ingresos', e.ingresos, 'ing'], ['Leche', -e.costoLeche, 'cos'], ['Insumos y empaque', -e.costoOtros, 'cos'], ['Energía', -e.costoEnergia, 'cos'], ['Gas', -e.costoGas, 'cos'], ['Agua y CIP', -e.costoAgua, 'cos'], ['Margen', e.margen, e.margen >= 0 ? 'mar' : 'neg']];
    const W = 640, H = 240, top = Math.max(1, e.ingresos), bw = W / pasos.length;
    const y = (v: number) => 20 + (1 - v / top) * (H - 60);
    const svg = s('svg', { viewBox: `0 0 ${W} ${H}`, class: 'graf cascada crece', role: 'img', 'aria-label': 'Cascada de ingresos a margen' });
    let acum = 0;
    pasos.forEach(([t, v, k], i) => {
      const ini = k === 'ing' || k === 'mar' || k === 'neg' ? 0 : acum;
      const fin = k === 'ing' ? v : k === 'mar' || k === 'neg' ? v : acum + v;
      if (k === 'ing') acum = v; else if (k === 'cos') acum += v;
      const y1 = y(Math.max(ini, fin)), y2 = y(Math.min(ini, fin));
      const x = i * bw + bw * 0.16;
      svg.append(s('g', { class: `col-dia c-${k}`, style: `--d:${i * 70}ms` },
        s('rect', { x, y: y1, width: bw * 0.68, height: Math.max(1, y2 - y1), rx: 2 }, s('title', {}, `${t}: ${cop(v)}`)),
        s('text', { x: x + bw * 0.34, y: y1 - 6, 'text-anchor': 'middle', class: 'g-txt g-v' }, cop(v).replace('$ ', '$'))),
        s('text', { x: i * bw + bw / 2, y: H - 22, 'text-anchor': 'middle', class: 'g-txt' }, t.split(' ')[0]));
      if (i < pasos.length - 1 && k !== 'neg') svg.append(s('line', { x1: x + bw * 0.68, x2: (i + 1) * bw + bw * 0.16, y1: y(acum), y2: y(acum), class: 'g-rej punteada' }));
    });
    c.querySelector('[data-n-cascada]')!.replaceChildren(svg);
    // margen por día
    const nd = Math.max(periodoN, 5);
    const d0 = inicioDia() - (nd - 1) * 864e5;
    const porDia = Array.from({ length: nd }, (_, i) => {
      const x0 = d0 + i * 864e5;
      const ed = economia(x0, Math.min(Date.now(), x0 + 864e5));
      return { x0, partes: [['Costo', ed.costos], ['Margen', Math.max(0, ed.margen)]] as [string, number][] };
    });
    c.querySelector('[data-n-dias]')!.replaceChildren(barrasDia(porDia, cop, { Costo: 'var(--cream-16)', Margen: 'var(--gold)' }),
      h('div', { class: 'leyenda mono' }, h('span', { style: '--c:var(--cream-16)' }, h('i', {}), 'Costo variable'), h('span', { style: '--c:var(--gold)' }, h('i', {}), 'Margen'), h('span', { class: 'leyenda-n' }, 'La barra completa son los ingresos del día.')));
    // por línea
    const maxL = Math.max(1, ...e.porLinea.map((x) => x.ingresos));
    c.querySelector('[data-n-lineas]')!.replaceChildren(h('ul', { class: 'neg-lineas' }, e.porLinea.map((x, i) => h('li', { style: `--c:${COLOR_LINEA[x.linea]};--i:${i}` },
      h('div', { class: 'nl-cab' }, h('b', {}, x.linea), h('span', { class: 'mono' }, `${miles(x.litros)} L`)),
      h('div', { class: 'nl-barra' }, h('i', { class: 'nl-ing', style: `width:${(x.ingresos / maxL) * 100}%` }), h('i', { class: 'nl-mar', style: `width:${(Math.max(0, x.margen) / maxL) * 100}%` })),
      h('div', { class: 'nl-num mono' }, h('span', {}, 'Ingresos ', h('b', {}, cop(x.ingresos))), h('span', {}, 'Margen ', h('b', {}, cop(x.margen)), ` · ${pct(x.ingresos ? x.margen / x.ingresos : null)}`))))));
    // pérdidas
    const perd: [string, number][] = [
      ...Object.entries(e.perdCausa).map(([k, v]) => [`Paro: ${k}`, v] as [string, number]),
      ['Lotes retenidos', e.perdRetenidos], ['Energía con máquinas detenidas', e.perdReposo],
    ];
    c.querySelector('[data-n-perd]')!.replaceChildren(barras(perd.filter(([, v]) => v > 0).sort((x, y) => y[1] - x[1]).slice(0, 8), cop),
      h('p', { class: 'nota mono' }, 'Paros: margen que se dejó de ganar en las llenadoras y cuellos de línea. Retenidos: costo de leche e insumos de lotes que no se venden.'));
    // consumos
    const porMil = (v: number) => (e.litros ? (v / e.litros) * 1000 : null);
    c.querySelector('[data-n-cons]')!.replaceChildren(h('div', { class: 'consumos' },
      [['Leche cruda', `${miles(e.lecheL)} L`, `${miles(e.litros ? e.lecheL / e.litros : 0, 2)} L por litro de producto`, cop(e.costoLeche)],
        ['Energía eléctrica', `${miles(e.kwh)} kWh`, `${miles(porMil(e.kwh) ?? 0, 1)} kWh por 1.000 L · ${miles(e.kwhReposo)} kWh en reposo`, cop(e.costoEnergia)],
        ['Gas natural', `${miles(e.gas)} m³`, `${miles(porMil(e.gas) ?? 0, 1)} m³ por 1.000 L`, cop(e.costoGas)],
        ['Agua', `${miles(e.agua)} m³`, `${miles(e.litros ? (e.agua * 1000) / e.litros : 0, 2)} L de agua por litro · ${e.cips} CIP`, cop(e.costoAgua)],
      ].map(([t, v, sub, $]) => h('div', { class: 'consumo' }, h('span', { class: 'mono' }, t), h('b', {}, v), h('small', {}, sub), h('span', { class: 'mono gold' }, $)))));
    // supuestos
    const editable = puede(['Gerencia', 'Jefe de planta', 'Administrador']);
    const grupos = [...new Set(D.parametros.map((p) => p.grupo))];
    c.querySelector('[data-n-param]')!.replaceChildren(D.parametros.length ? h('div', { class: 'params' }, grupos.map((g) => h('fieldset', {}, h('legend', { class: 'mono' }, g),
      D.parametros.filter((p) => p.grupo === g).map((p) => {
        const x = inp(p.clave, { type: 'number', step: 'any', min: 0, value: p.valor, disabled: !editable, 'aria-label': p.nombre });
        x.addEventListener('change', () => guardar(sb!.from('parametros').update({ valor: Number(x.value) }).eq('clave', p.clave), `${p.nombre}: ${x.value} ${p.unidad}`, 'parametros'));
        return h('label', { class: 'param' }, h('span', {}, p.nombre), h('span', { class: 'param-v' }, x, h('small', { class: 'mono' }, p.unidad)));
      })))) : vacio('Faltan los parámetros: ejecuta esquema-4-costos.sql.'));
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

// ---------- Usuarios y pasarela (administrador)
const vUsuarios: Vista = {
  id: 'usuarios', titulo: 'Usuarios y pasarela', grupo: 'General', roles: ['Administrador'],
  montar(c) {
    c.append(tarjeta('Pasarela de datos de planta', h('div', { 'data-u-sim': '' })),
      tarjeta('Usuarios y roles', h('p', { class: 'nota' }, 'Los usuarios se crean en Supabase → Authentication → Users → Add user (con “Auto Confirm User”). Aquí se les pone el nombre y el rol; el rol define el nivel de la pirámide y las ventanas que ve cada persona.'),
        h('div', { 'data-u-tabla': '' })));
  },
  refrescar() {
    const sim = D.simulacion[0];
    cont.querySelector('[data-u-sim]')!.replaceChildren(h('div', { class: 'pasarela' },
      h('ol', { class: 'arquitectura mono' }, ['Pasarela (PLC + Node-RED simulados)', 'Supabase · PostgreSQL', 'Realtime', 'MES en cada portátil'].map((t, i) => h('li', { style: `--i:${i}` }, t))),
      h('div', { class: 'pas-estado' },
        h('span', {}, h('span', { class: 'pulse', 'data-live': sim?.activa ? '' : null }), sim?.activa ? ' Encendida' : ' Apagada'),
        h('span', { class: 'mono sub' }, sim?.ultimo ? `Último ciclo hace ${dur(Date.now() - Date.parse(sim.ultimo))} · cada 30 s con pg_cron` : 'Sin ciclos todavía'),
        boton(sim?.activa ? 'Apagar pasarela' : 'Encender pasarela', async () => {
          const { error } = await sb!.rpc('sim_control', { prender: !sim?.activa });
          if (error) aviso(`No se pudo: ${error.message}`, true); else { aviso(sim?.activa ? 'Pasarela apagada.' : 'Pasarela encendida.'); recargar('simulacion'); }
        }, sim?.activa ? 'm-btn sec' : 'm-btn')),
      h('p', { class: 'nota' }, 'La pasarela corre dentro de la base de datos: cada 30 s mueve los estados de las máquinas, publica sus señales y genera recepciones, órdenes, lotes y controles. Todo lo que crea queda marcado SIM. En la planta real este papel lo cumplen los PLC y Node-RED/OPC UA escribiendo en las mismas tablas.')));
    cont.querySelector('[data-u-tabla]')!.replaceChildren(tabla([
      ['nombre', 'Nombre', (p) => inp('nombre', { value: p.nombre, 'aria-label': 'Nombre' })],
      ['rol', 'Rol', (p) => sel('rol', ROLES, p.rol)],
      ['creado', 'Desde', (p) => fecha(p.creado)],
    ], D.perfiles, (p) => boton('Guardar', (e) => {
      const tr = (e.currentTarget as HTMLElement).closest('tr')!;
      const n = (tr.querySelector('input[name=nombre]') as HTMLInputElement).value.trim();
      const r = (tr.querySelector('select[name=rol]') as HTMLSelectElement).value;
      guardar(sb!.from('perfiles').update({ nombre: n, rol: r }).eq('id', p.id), `${n}: ${r}.`, 'perfiles');
    }, 'm-btn mini')));
  },
};

const VISTAS: Vista[] = [vNegocio, vInd, vPlanta, vTurno, vOrdenes, vLotes, vCalidad, vMant, vArchivos, vUsuarios];
const INICIO: Record<string, string> = { Operario: 'turno', Supervisor: 'planta', Calidad: 'calidad', Mantenimiento: 'mantenimiento', 'Jefe de planta': 'indicadores', Gerencia: 'negocio', Administrador: 'planta' };
const ORDEN_GRUPOS = ['Nivel 4 · Negocio', 'Nivel 3 · Gestión de planta', 'Nivel 3 · Operaciones', 'Nivel 2 · Piso de planta', 'General'];

// ---------------------------------------------------------------- navegación
function visibles() {
  return VISTAS.filter((v) => v.roles.includes(rolVista));
}
function pintarMenu() {
  const grupos = ORDEN_GRUPOS.filter((g) => visibles().some((v) => v.grupo === g));
  menu.replaceChildren(...grupos.map((g) => h('div', { class: 'grupo' }, h('span', { class: 'mono' }, g),
    visibles().filter((v) => v.grupo === g).map((v) => h('a', { href: `#${v.id}`, 'aria-current': vista?.id === v.id ? 'page' : null },
      s('svg', { viewBox: '0 0 24 24', 'aria-hidden': 'true' }, s('path', { d: ICONOS[v.id] })), v.titulo)))));
  pintarPiramide();
}
function pintarPiramide() {
  piramideEl.replaceChildren(h('span', { class: 'mono' }, 'Pirámide ISA-95'),
    h('ol', {}, NIVELES.map((n, i) => {
      const activo = rolVista === 'Administrador' || n.roles.includes(rolVista);
      const li = h('li', { class: activo ? 'activo' : '', style: `--i:${i}`, title: n.quien },
        h('button', { type: 'button', disabled: miRol !== 'Administrador', onclick: () => verComo(n.roles[0]) }, h('b', { class: 'mono' }, `N${n.n}`), h('span', {}, n.t)));
      return li;
    })));
}
function verComo(rol: string) {
  rolVista = rol;
  const s2 = raiz.querySelector<HTMLSelectElement>('[data-como] select');
  if (s2) s2.value = rol;
  pintarMenu();
  irA(INICIO[rolVista] ?? 'planta');
  aviso(rolVista === miRol ? 'Vista normal.' : `Viendo el MES como ${rolVista}. Los permisos reales siguen siendo los tuyos.`);
}
function irA(id: string) {
  const v = visibles().find((x) => x.id === id) ?? visibles().find((x) => x.id === (INICIO[rolVista] ?? 'planta')) ?? visibles()[0];
  vista = v;
  tituloEl.textContent = v.titulo;
  grupoEl.textContent = v.grupo;
  menu.querySelectorAll('a').forEach((a) => (a.getAttribute('href') === `#${v.id}` ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
  cont.replaceChildren();
  cont.classList.remove('entra');
  void cont.offsetWidth;
  cont.classList.add('entra');
  montada = '';
  v.montar(cont);
  montada = v.id;
  v.refrescar();
  if (location.hash !== `#${v.id}`) history.replaceState(null, '', `#${v.id}`);
}
window.addEventListener('hashchange', () => { if (!pantallaApp.hidden) irA(location.hash.slice(1)); });

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
raiz.querySelector<HTMLSelectElement>('[data-como] select')!.addEventListener('change', (e) => verComo((e.target as HTMLSelectElement).value));
function pintarSim() {
  const sim = D.simulacion[0];
  simEl.hidden = !sim?.activa;
  if (sim?.activa) simEl.querySelector('[data-sim-t]')!.textContent = sim.ultimo ? `último ciclo hace ${dur(Date.now() - Date.parse(sim.ultimo))}` : '';
}

// ---------------------------------------------------------------- reloj y tiempo real
function pulsoVivo() {
  const p = raiz.querySelector('.top-estado [data-live]');
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
  // contadores y órdenes avanzan entre lecturas (máximo 90 s de extrapolación)
  raiz.querySelectorAll<HTMLElement>('[data-contador]').forEach((e) => {
    const t0 = Date.parse(e.dataset.t0 || '');
    const dt = Number.isFinite(t0) ? Math.min(1.5, Math.max(0, (n - t0) / 60000)) : 0;
    e.textContent = miles(Math.floor(Number(e.dataset.base) + Number(e.dataset.vel) * dt));
  });
  raiz.querySelectorAll<HTMLElement>('[data-prog]').forEach((e) => {
    const t0 = Date.parse(e.dataset.t0 || '');
    const dt = Number.isFinite(t0) ? Math.min(1.5, Math.max(0, (n - t0) / 60000)) : 0;
    const v = Math.min(Number(e.dataset.plan), Number(e.dataset.base) + Number(e.dataset.tasa) * dt);
    e.style.width = `${(v / Number(e.dataset.plan)) * 100}%`;
    const t = e.parentElement?.querySelector('[data-prog-t]');
    if (t) t.textContent = `${miles(v)} / ${miles(Number(e.dataset.plan))} L`;
  });
  const reloj = raiz.querySelector('[data-reloj]');
  if (reloj) reloj.textContent = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const tn = raiz.querySelector('[data-turno]');
  if (tn) tn.textContent = `Turno ${turnoDe().nombre}`;
  if (++seg % 10 === 0) pintarSim();
  if (seg % 60 === 0 && vista && montada === vista.id && ['planta', 'indicadores', 'mantenimiento', 'negocio'].includes(vista.id) && !dialogo.open) vista.refrescar();
}, 1000);

async function entrar(uid: string) {
  yo = uid;
  pantallaLogin.hidden = true;
  pantallaApp.hidden = false;
  cont.replaceChildren(h('div', { class: 'cargando' }, h('span', { class: 'pulse', 'data-live': '' }), h('span', { class: 'mono' }, 'Conectando con la planta…')));
  await Promise.all([...TABLAS, 'archivos'].map(cargar));
  miRol = D.perfiles.find((p) => p.id === yo)?.rol ?? 'Operario';
  rolVista = miRol;
  pintarUsuario();
  pintarMenu();
  pintarSim();
  irA(location.hash.slice(1));
  const canal = sb!.channel('mes-planta');
  TABLAS.forEach((t) => canal.on('postgres_changes', { event: '*', schema: 'public', table: t }, (pl) => aplicar(t, pl)));
  canal.subscribe((estado) => {
    const p = raiz.querySelector<HTMLElement>('.top-estado [data-live]');
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
    history.replaceState(null, '', location.pathname);
    location.reload();
  });
}
