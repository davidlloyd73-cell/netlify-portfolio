# Things We've Built

A small collection of web apps for clinical, family, and business use — all live, all built quickly with Claude.

**Portfolio:** [things-we-have-built.netlify.app](https://things-we-have-built.netlify.app)

Every app links back to the portfolio (top-left pill) when opened from there. If you share an app URL directly, the back-link stays hidden — so each one is standalone.

## What's in it

| Project | What it does |
|---|---|
| **Post-EMIS Mockup** | Animated walkthrough of a clinically-governed shared record with on-premise AI. |
| **Ridgeway AI Tools** | RefGP (notes → referral letter) and RateConsult (RCGP-style consultation grading). |
| **Diagnostic Teammate** | Clinician and AI form independent diagnoses, then reconcile, with patient-friendly summary. |
| **GP Population Simulator** | Models a 10,000-patient practice — change demographics and interventions, see the impact on mortality and equity. |
| **GP Surgery Simulator** | Discrete-event model of a practice's appointment book over a year — set staffing, triage model and AI adoption, see the continuity-vs-access trade-off. |
| **Ridgeway Health Walk Podcast** | GP-guided walking podcast for health education at conversational pace. |
| **Bridge Four** | Online bridge against Claude-powered AI partner and opponents. |
| **DL Invoice Generator** | Voice- or text-input invoice creator with PDF export. |
| **Family Corkboard** | Passcode-protected family board for photos, notes, weekly diary. |
| **We Take Blood** | Preview of a community phlebotomy service (private, password-gated). |

## Tools & MCPs

| Tool | What it does |
|---|---|
| **uk-evidence MCP** | A Model Context Protocol server giving Claude live, point-of-care access to UK clinical evidence — NICE guidance and quality standards, NICE CKS summaries, MHRA drug-safety articles, and PubMed. So Claude answers from the current guideline, not its training data. |

## Adding to the site

Two helper scripts live in this repo. Both are interactive (just run them and
answer the questions), commit for you, and offer to push so Netlify redeploys.

**Add an app to the Apps page:**

```bash
python3 add-app.py
```

Asks for the app's name, live URL, description, category, and what it's built
with — then screenshots the app, adds a card to `index.html` + a row above,
commits, optionally pushes, and prints the exact "← All projects" back-button
snippet to paste into the new app so it links home when opened from here.

**Add a NotebookLM (or a new topic) to the Research Topics page:**

```bash
python3 add-notebook.py
```

Either adds a NotebookLM under an existing topic (you pick from the list; it's
slotted in by source count to match the layout), or creates a whole new topic
(name, description, Drive URL, and an optional first notebook). Commits and
offers to push.
| **David's AI Daily Brief** | Self-updating daily distillation of The AI Daily Brief podcast — readable page, three-minute spoken edition with podcast feed, an opposing-source synthesis from Ed Zitron's Better Offline, and a GP's Corner for the NHS. Rebuilds itself every morning at 7. |

## How it's made

- Every app lives in its own GitHub repo under `davidlloyd73-cell`.
- Pushed to main → auto-deploys (Netlify for most, Cloudflare Pages for WTB, Render for Bridge Four, GitHub Pages for the simulator).
- The portfolio is itself a single-page Netlify site that auto-deploys the same way.
