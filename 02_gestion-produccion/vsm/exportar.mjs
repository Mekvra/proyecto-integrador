// Exporta un HTML a PNG y PDF con Playwright. Uso: node exportar.mjs <archivo.html> <ancho> <alto>
import { chromium } from 'file:///C:/Users/jlcr3/.claude/skills/gstack/node_modules/playwright/index.mjs';
import { pathToFileURL } from 'node:url';
const [, , html, w, h] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
await page.goto(pathToFileURL(html).href, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: html.replace(/\.html$/, '.png') });
await page.pdf({ path: html.replace(/\.html$/, '.pdf'), width: `${w}px`, height: `${h}px`, printBackground: true });
await browser.close();
console.log('exportado');
