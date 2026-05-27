# Overleaf — Compile Instructions

## Files in this folder
- `report.tex` — main LaTeX source (single file, ~30 pages body + ~12-15 pages appendices)
- `references.bib` — BibTeX bibliography (~22 entries)
- `README_OVERLEAF.md` — this file

## Step-by-step on Overleaf

### 1. Create a new project
- Go to https://www.overleaf.com → **New Project** → **Blank Project**
- Name it e.g. `FIFA_WC2026_Report`

### 2. Upload the files
Upload (drag & drop) into the Overleaf project root:
- `report.tex`
- `references.bib`

Delete the default `main.tex` that Overleaf creates.

### 3. Upload the figures
Create a folder named `figures/` in the Overleaf project root and upload all 25 PNG files from `outputs/figures/`:
- `part1_network_architecture.png`
- `part1_stadium_demand.png`
- `part1_network_map.png`
- `part1_cost_donut.png`
- `part1_cost_breakdown.png`
- `part1_setup_comparison.png`
- `part1_feu_efficiency.png`
- `part1_feu_by_class.png`
- `part1_feu_constraint_box.png`
- `part1_sensitivity_tornado.png`
- `part1_flow_matrix.png`
- `part1_port_utilization.png`
- `part1_demand_heatmap.png`
- `part2_two_stage_timeline.png`
- `part2_stage_split.png`
- `part2_feasibility.png`
- `part2_forced_map.png`
- `part2_sensitivity_tornado.png`
- `part2_prod_cost_curve.png`
- `part2_sensitivity_grid.png`
- `part2_waste_curve.png`
- `part2_production_days.png`
- `part2_reactive_sites.png`
- `part2_stage_by_param.png`
- `part2_anticipatory_by_match.png`

Overleaf supports drag & drop of multiple files at once.

### 4. Set compile settings
- Top-right corner → **Menu** → **Settings**
- **Compiler:** `pdfLaTeX`
- **TeX Live version:** 2023 or later (the default current is fine)
- **Main document:** `report.tex`

### 5. Compile
Click **Recompile**. The first compile may take 30-60 seconds because biber (bibliography processor) needs to run twice:
- First pass: collects `\cite{}` references and writes `report.aux`
- Biber pass: processes `references.bib` against `report.bcf`
- Second pass: resolves citation numbers in the PDF
- Third pass: finalises cross-references (figure/table numbers)

Overleaf chains these automatically; just click **Recompile** until references appear correctly (typically twice).

### 6. Fill in author names
On the cover page, replace the three `[Author 1]`, `[Author 2]`, `[Author 3]` placeholders with the actual names of your team. They appear in the `\begin{titlepage}` block near the top of `report.tex`.

## Troubleshooting

### "File not found: part1_xxx.png"
Make sure all PNGs are inside a `figures/` folder at the Overleaf project root. The preamble contains:
```latex
\graphicspath{{../outputs/figures/}{figures/}}
```
which looks first at `../outputs/figures/` (for local builds) and then at `figures/` (for Overleaf).

### "Package biblatex Error: incompatible package"
- Make sure the compiler is **pdfLaTeX** (not XeLaTeX).
- Make sure the TeX Live version is 2022 or later.
- If you still see this, switch the compiler to **XeLaTeX**.

### "Citations show as [?]"
- This happens before biber runs. Click **Recompile** twice more.
- If they still don't appear, click **Logs and output files** → **Clear cached files** → **Recompile**.

### Bibliography style not what I want
The current style is `numeric-comp` (compact numeric citations like `[1, 2, 5]`). To switch to author-year:
- In the preamble, find `\usepackage[...]{biblatex}` and change `style=numeric-comp` to `style=authoryear-comp`.
- Recompile twice.

## Local compilation (optional, requires TeX Live)
```bash
cd report
pdflatex report.tex
biber report
pdflatex report.tex
pdflatex report.tex
```
The PDF is produced as `report.pdf`. If figures don't appear, ensure your `outputs/figures/` directory is one level up (i.e., `../outputs/figures/`), as the preamble expects.

## What's where in the document
| Page range (approx.) | Content |
|---|---|
| i | Title page |
| ii | Executive Summary + headline-result callout |
| iii | Table of Contents |
| 1-3 | Section 1 — Introduction |
| 3-7 | Section 2 — Data foundations |
| 7-15 | Section 3 — Part I LRP (math + results + sensitivity) |
| 15-23 | Section 4 — Part II Stochastic (math + results + sensitivity) |
| 23-26 | Section 5 — Managerial insights & recommendations |
| 26-27 | Section 6 — Limitations & future work |
| 27 | Section 7 — Conclusion |
| 28-29 | References |
| 30+ | Appendices A-F (reconstruction methodology, assumptions registry, data dictionary, sensitivity figures, source registry, reproducibility) |

Total: ~30 pages of body + ~12-15 pages of appendices = ~42-45 pages PDF.

## Last sanity check before submitting
- [ ] Author names filled in on the cover page
- [ ] All 25 figures present in `figures/` folder
- [ ] References render correctly (no `[?]` markers)
- [ ] Cross-references work (e.g., "see Figure 3.1" links to actual figure)
- [ ] Page count is acceptable for the brief (body ≤ 30 pages)
- [ ] No compile errors in the log
