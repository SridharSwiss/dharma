# ధర్మ ప్రచార వేదిక – 6 నెలల బ్లూప్రింట్ సైట్

Live: https://sridharswiss.github.io/dharma/

A static GitHub Pages site for the Telugu devotional YouTube channel family (ధర్మ దీపం, స్తోత్ర సుధ, పూజా మందిరం, వేద వాణి), Vijayadashami 2026 → Chaitra Pournami 2027.

## Pages

| File | Telugu name | Contents |
|---|---|---|
| `index.html` | అవలోకనం | Interactive dashboard: channels, 26-week plan, festival calendar, series & texts, chapter maps, budget, rules |
| `karthika.html` | కార్తీక పురాణం ప్యాక్ | 30-episode production calendar, workflow, description/thumbnail/tag templates |
| `production.html` | నిర్మాణ మార్గదర్శి | Technical specs, per-format specs, BGM/raga guide, visual identity, QC checklist, publish times |
| `homams.html` | హోమాలు & వ్రతాలు | 9 homam darshan shoots, cost plan, 13 vratams/pujas, on-set etiquette |
| `team.html` | బృందం & నియామకం | 7 roles at ₹20,000/month, RACI, weekly rhythm, hiring timeline |
| `growth.html` | వృద్ధి & ఆదాయం | YPP path to 31 Jan 2027, monthly targets, growth tactics, revenue streams, weekly metrics |
| `library.html` | గ్రంథాలయం | Searchable links to Vedas, Upanishads, Gita, Puranas, Shankara works, stotrams, puja/homam texts |

## Structure

- `assets/site.css`, `assets/site.js` – shared navigation and a section renderer (types: `kpis`, `cards`, `table`, `steps`, `links`, `prose`, `note`).
- `data/page-<id>.js` – each detail page's content as `window.PAGE = {...}`.
- `data/*.json` – dashboard datasets (also embedded inside `index.html`).
- `.nojekyll` – serve files as-is (no Jekyll processing).

## Adding a page

1. Add `['<id>', 'Telugu name', '<id>.html']` to `NAV` in `assets/site.js`.
2. Create `data/page-<id>.js` with `window.PAGE = {id, title, lede, sections:[...]}`.
3. Copy any detail page's HTML shell to `<id>.html` and change the two `<id>` references.

Works offline (open the files directly) and in light/dark mode. Dates marked "సందేహం" must be checked against a printed Telugu panchangam; costs and targets are planning estimates.
