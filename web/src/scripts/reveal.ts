// Animaciones de entrada al hacer scroll (estilo Factory): los elementos suben,
// pasan de desenfocados a nítidos y entran en cascada cuando llegan a la pantalla.
// La lista de elementos animados vive en global.css (selector de .reveal-ready).

export const REVEAL_SELECTOR = [
  '.hero > :not(script)',
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

  // Se repite cada vez que el elemento entra en pantalla, bajando o subiendo.
  // Si sale por arriba, la próxima entrada es desde arriba (bajando), y viceversa.
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        const el = entry.target;
        if (entry.isIntersecting && entry.intersectionRatio >= 0.12) {
          el.classList.add('is-in');
        } else if (!entry.isIntersecting) {
          el.classList.remove('is-in');
          el.classList.toggle('from-top', entry.boundingClientRect.top < 0);
        }
      }
    },
    { rootMargin: '0px 0px -8% 0px', threshold: [0, 0.12] },
  );

  items.forEach((el) => observer.observe(el));
  root.classList.add('reveal-on');
}
