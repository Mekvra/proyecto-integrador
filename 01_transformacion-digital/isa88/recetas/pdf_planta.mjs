import { chromium } from 'file:///C:/Users/jlcr3/.claude/skills/gstack/node_modules/playwright/index.mjs';
const src = 'file:///C:/Users/jlcr3/Music/Proyecto%20APM/01_transformacion-digital/isa88/recetas/recetas_planta.html';
const out = 'C:/Users/jlcr3/Music/Proyecto APM/01_transformacion-digital/isa88/recetas/Recetas_basicas_planta_v1.0.pdf';
const b = await chromium.launch();
const p = await b.newPage({ colorScheme: 'light' });
await p.goto(src, { waitUntil: 'networkidle' });
await p.addStyleTag({ content: `
  nav.toc, .filter { display: none !important; }
  .wrap { grid-template-columns: minmax(0,1fr) !important; max-width: none !important; padding: 0 !important; }
  .tbl { overflow: visible !important; }
  table { font-size: 11px !important; }
  tr, .prod, .kpis div, .stage { break-inside: avoid; }
  h2, h3, .eyebrow { break-after: avoid; page-break-after: avoid; } .eyebrow { display: block; }
  section { break-inside: auto; display: block !important; margin-bottom: 28px; } section > * + * { margin-top: 14px; } main { display: block !important; } header.head { display: block !important; } header.head > * + * { margin-top: 10px; } .products { grid-template-columns: repeat(3, minmax(0,1fr)) !important; } .kpis { grid-template-columns: repeat(4, minmax(0,1fr)) !important; } .cols2 { grid-template-columns: 1fr 1fr !important; } .recipe { display: block !important; } .recipe > * + * { margin-top: 14px; } html, body, .wrap { background: #ffffff !important; } .prod { break-inside: avoid; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }` });
await p.emulateMedia({ media: 'print', colorScheme: 'light' });
await p.pdf({ path: out, format: 'Letter', printBackground: true, margin: { top: '14mm', bottom: '16mm', left: '12mm', right: '12mm' },
  displayHeaderFooter: true, headerTemplate: '<span></span>',
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#5b6876">Recetas básicas · Planta láctea de 150.000 L/día · Lácteos Altos de Teusacá · v1.0 · página <span class="pageNumber"></span> de <span class="totalPages"></span></div>' });
await b.close();
console.log('ok');




