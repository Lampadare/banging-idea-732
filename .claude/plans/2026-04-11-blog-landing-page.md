# Blog Landing Page — VNS for Cows

## Overview
Single-page static site for presenting the hackathon project. Dark theme matching
existing figures. Mobile-first, single column, vertical scroll. Deployable as
static files to home server.

## Tech Stack
- **Plain HTML + CSS + JS** — no framework, no build step
- **Three.js** via CDN — for interactive 3D nerve/electrode visualization
- **CSS custom properties** — for theming, responsive breakpoints
- Dark background (#1a1a2e or similar) to match figure aesthetics

## Page Structure (top → bottom)

1. **Hero** — Project title, one-liner tagline, subtle animated background
2. **Problem** — Why selective VNS matters for livestock welfare
3. **Approach** — The simulation pipeline (geometry → potentials → thresholds)
4. **Interactive 3D** — Three.js nerve cross-section with fascicles + electrode cuff
   - Rotate/zoom, hover fascicles for info
   - Toggle electrode activation
5. **Results** — The three existing figures with captions:
   - Nerve cross-section anatomy
   - Monopolar threshold heatmaps
   - Recruitment curves
6. **Process / Timeline** — Blog-style writeup (placeholder, user will supply content)
7. **Footer** — Team, hackathon credit, repo link

## File Layout
```
blog/
├── index.html
├── css/
│   └── style.css
├── js/
│   ├── main.js          # scroll animations, nav
│   └── nerve-viewer.js  # three.js 3D visualization
├── assets/
│   └── figures/         # copies/symlinks of output PNGs
└── data/
    └── nerve-geometry.json  # exported fascicle + electrode coords for three.js
```

## Build Steps

- [ ] 1. Scaffold `blog/` directory and file structure
- [ ] 2. Build HTML skeleton with semantic sections
- [ ] 3. Write CSS — dark theme, mobile-first responsive, typography, scroll layout
- [ ] 4. Copy figures into `blog/assets/figures/`
- [ ] 5. Export nerve geometry to JSON for three.js consumption
- [ ] 6. Build three.js interactive nerve cross-section viewer
- [ ] 7. Add scroll animations and section transitions
- [ ] 8. Add placeholder sections for blog content (user will fill)
- [ ] 9. Test on mobile viewport + desktop
- [ ] 10. Commit on `blog` branch

## Design Notes
- Figures already use dark backgrounds — page should complement, not clash
- Keep typography clean: system font stack or one Google Font (Inter/Space Grotesk)
- Subtle scroll-reveal animations, nothing flashy
- Three.js scene should be lightweight — simple geometry, no heavy textures
- Content sections are placeholder until user provides hackathon narrative
