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
| **Ridgeway Health Walk Podcast** | GP-guided walking podcast for health education at conversational pace. |
| **Bridge Four** | Online bridge against Claude-powered AI partner and opponents. |
| **DL Invoice Generator** | Voice- or text-input invoice creator with PDF export. |
| **Family Corkboard** | Passcode-protected family board for photos, notes, weekly diary. |
| **We Take Blood** | Preview of a community phlebotomy service (private, password-gated). |

## How it's made

- Every app lives in its own GitHub repo under `davidlloyd73-cell`.
- Pushed to main → auto-deploys (Netlify for most, Cloudflare Pages for WTB, Render for Bridge Four, GitHub Pages for the simulator).
- The portfolio is itself a single-page Netlify site that auto-deploys the same way.
