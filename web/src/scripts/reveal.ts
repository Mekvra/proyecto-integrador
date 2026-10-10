// Animaciones de entrada al hacer scroll (estilo Factory): los elementos suben,
// pasan de desenfocados a nítidos y entran en cascada cuando llegan a la pantalla.
// La lista de elementos animados vive en global.css (selector de .reveal-ready).

export const REVEAL_SELECTOR = [
  '.stack-strip',
  '.hero-main > :not(script)',
  '.section-head > *',
  '.fact',
  '.cell-stage',
  '.frame',
  '.trunk',
  '.trunk-flow > li',
  '.tablist',
  '.stage',
  '.level',
  '.card',
  '.proposal',
  '.member',
  '.footer > *',
].join(',');

const MAX_STAGGER = 6;
const STEP_MS = 70;

export function initReveal() {
  const root = document.documentElement;
  if (!root.classList.contains('reveal-ready')) return;

  const items = [...document.querySelectorAll<HTMLElement>(REVEAL_SELECTOR)];

  // Cascada: cada elemento espera según su posición entre sus hermanos animados.
  for (const el of items) {
    const siblings = el.parentElement
      ? [...el.parentElement.children].filter((c) => c.matches(REVEAL_SELECTOR))
      : [el];
    const index = Math.min(siblings.indexOf(el), MAX_STAGGER);
    el.style.setProperty('--reveal-delay', `${index * STEP_MS}ms`);
  }

  // 1) Cada elemento aparece la primera vez que entra en pantalla.
  const itemObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.12) {
          entry.target.classList.add('is-in');
        }
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: [0, 0.12] },
  );
  items.forEach((el) => itemObserver.observe(el));

  // 2) Solo cuando TODA la sección sale de la pantalla, sus elementos se reinician
  //    para volver a animarse al regresar (desde arriba si saliste bajando).
  //    Moverse dentro de una misma sección no repite la animación.
  const groups = new Map<Element, HTMLElement[]>();
  for (const el of items) {
    const section = el.closest('section.section, section.hero, footer') ?? document.body;
    if (!groups.has(section)) groups.set(section, []);
    groups.get(section)!.push(el);
  }

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) continue;
        const fromTop = entry.boundingClientRect.top < 0;
        for (const el of groups.get(entry.target) ?? []) {
          el.classList.remove('is-in');
          el.classList.toggle('from-top', fromTop);
        }
      }
    },
    { threshold: 0 },
  );
  groups.forEach((_, section) => section !== document.body && sectionObserver.observe(section));

  root.classList.add('reveal-on');
}
