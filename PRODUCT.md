# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Delegated: Astro (static output) deployed to GitHub Pages via GitHub Actions. Chosen because the user asked for a site that is elegant and interactive yet editable by them and the team "without redoing it": all copy and data live in Markdown/JSON content files separate from components, so content updates never touch layout code.

## Users

- **Primary:** the course professors (UNAL, Automatización de Procesos de Manufactura 2026-2S) evaluating the project as if they were the client — a dairy company modeled on Alpina — receiving a professional engineering proposal.
- **Secondary:** classmates and future cohorts browsing the course's showcase of past projects; the five team members themselves, who use the site to present during the sustentación and the YouTube video.

## Product Purpose

Project website of **Mekvra**, a fictional Industrial Digital Transformation (TDI) integrator formed by five mechatronics students. It presents the company's proposal to modernize a dairy plant: process characterization, ISA-95 architecture and OT/IT information flow, ISA-88 models and recipes, production analysis (VSM, OEE, takt, MLT), simulation evidence, technical-economic evaluation, value proposition, and a required "Proceso de Aprendizaje" section with group and individual reflections. Success = the professors can find every required deliverable quickly and read it as a credible consulting proposal.

## Positioning

A consulting proposal, not a course report: it speaks to the client about their plant, their problem, and measurable before/after improvements. It must cover the whole plant (three batch lines sharing reception, pasteurization, storage, utilities) and zoom into one line (queso) for automation and digital twin.

## Operating Context

- Deliverables: intermediate delivery Mon 2026-10-05 (modules: TDI, Gestión y Evaluación de la Producción, Planeación y Evaluación de Proyectos); final delivery Mon 2026-12-07 (adds Grafcet/Ladder in Logix Emulate, digital twin in Siemens NX, robotic cell in RobotStudio, SCADA in Ignition/Node-RED, Tecnomatix simulation).
- The site grows over the semester: sections for later modules must exist as honest "en desarrollo" states, not fabricated results.
- Companion links: GitHub repository (engineering evidence) and YouTube video (30–45 min sustentación).
- Language: Spanish (Colombia).

## Capabilities and Constraints

- Production lines chosen by the team: queso (detailed line), mantequilla, kéfir. The official brief lists yogur / queso / leche UHT-bebidas lácteas; the team must confirm the mantequilla substitution with professors. Line list must be easy to change in content.
- Company name "Mekvra" confirmed by the team on 2026-09-27 (GitHub org: Mekvra). Name must be a single content value.
- No logo exists yet.

## Brand Commitments

None confirmed beyond the name proposal and a request for an "elegante" and "interactiva" site.

## Evidence on Hand

- Team process analysis with real parameter ranges per stage (recepción, filtrado, normalización, pasteurización, silos, queso fresco, yogur, kéfir; mantequilla only as step list). Source: team doc "Análisis de procesos producción de derivados lácteos".
- Sector figures: Cundinamarca ~5.85 M L/día de leche (Gobernación, oct 2025); Sabanalac ~350 mil L/día; Alpina ~295 mil L/día for its products (team research, source to verify).
- No KPIs, VSM, budget, simulation results, or photos yet. Never fabricate these; show placeholders labeled as pending.

## Product Principles

1. Every required deliverable in the brief has an obvious, findable place.
2. Speak as a consultant to a client: problem → solution → measurable value.
3. Never present invented numbers as results; pending work is labeled pending.
4. Content is data: anyone on the team can update text and figures without touching design code.
5. The process is the hero — the plant, the milk, the flow of information — not generic tech imagery.

## Accessibility & Inclusion

Readable on projector during sustentación and on phones; respects reduced motion; WCAG AA contrast.
