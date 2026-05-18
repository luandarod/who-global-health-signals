# Frontend Narrative, Glossary, and Figure Integration Design

Date: 2026-05-18
Project: who-global-health-signals

## Goal

Align the report frontend with the final analytical state of the project:

- TabPFN is the final global benchmark champion on the current dataset.
- The local benchmark remains important context and should still be shown clearly.
- Technical terms must stay readable for non-specialists through a mixed hover/click glossary.
- Generated static figures, including the 3D response surfaces, must appear as narrative evidence in the report instead of staying disconnected from the interactive layer.

## Desired Reading Experience

The page should feel technical and analytical, but still readable for a non-specialist.

The report should tell one consistent story:

1. What question is being asked.
2. What kind of country-year dataset was built.
3. Why data quality matters before model quality.
4. How the benchmark compares local models against the external TabPFN reference.
5. What the residual layer reveals.
6. How the generated figures support the claims.

The page should not feel like a generic dashboard, and it should not overstate causality.

## Content Architecture

The home page remains a single long-form report, organized into five stable sections:

1. Question
   - Introduce the analytical question, unit of analysis, temporal split, and benchmark purpose.

2. Data Foundation
   - Explain dataset breadth, completeness, and indicator coverage before model performance.
   - Use generated figures for static evidence and existing interactive charts for inspection.

3. Model Benchmark
   - Present the final comparison as balanced benchmark evidence.
   - The narrative must say that the local benchmark became strong, but TabPFN still won the final comparison on the current cleaned dataset.

4. Residual Intelligence
   - Position residuals as investigative leads rather than country rankings.
   - Show which regions, years, and countries are harder to model.

5. Sources and Reproducibility
   - Explain public data source, local benchmark stack, optional external reference, runtime notes, and analytical limits.

## Glossary System

Introduce a shared glossary popover component used in text and interactive UI.

Behavior:

- On desktop hover: show a lightweight preview.
- On click: lock the popover open.
- On mobile: click/tap only.
- Keyboard accessible: focusable trigger, Enter/Space to open, Escape to close.
- Click outside closes the popover.

Glossary entries will support:

- short label
- concise explanation
- project-specific meaning

Initial terms:

- MAE
- RMSE
- R2
- residual
- coverage
- completeness
- temporal split
- benchmark
- country-year
- holdout
- predictive signal
- outlier

The glossary should be reusable in:

- narrative text
- metric cards
- benchmark rows/cards
- residual summaries
- chart side panels
- chart labels and captions

## Figure Integration

The frontend must explicitly incorporate the already-generated static figures.

### Data Foundation figures

- 01_variable_coverage_top15.png
- 02_yearly_data_completeness.png
- 03_completeness_by_region.png
- 04_life_expectancy_trend_by_region.png

### Benchmark figures

- 09_tabpfn_actual_vs_predicted.png
- 10_model_comparison_mae.png
- 14_local_model_comparison.png
- 15_local_model_error_by_year.png

### Residual figures

- 11_residuals_by_region.png
- 12_residuals_by_year.png
- 13_top_country_residuals.png

### Response surface figures

- 16_response_surface_<model>.png
- 17_response_surface_<model>.png

These should appear as anchored narrative exhibits, not as a dump of images. Each figure block needs a short caption or framing sentence explaining what it shows and why it matters.

For the response surfaces specifically, the surrounding copy must clarify:

- which model produced the surface
- which two features are on the axes
- that the surface reflects model response, not causal effect

## Component-Level Changes

### MetricCards.svelte

- Replace the fixed TabPFN language with dynamic champion-aware text derived from `summary.best_model`.
- Add glossary triggers for benchmark terms.
- Fix broken character rendering.

### ModelComparison.svelte

- Keep the current comparison layout, but make the side explanation balanced and champion-aware.
- Add glossary triggers for MAE, RMSE, and R2.
- Add keyboard accessibility to selectable model rows.
- Fix encoding issues in labels and tooltips.

### BarInsightChart.svelte

- Add glossary support to coverage, completeness, and residual terminology.
- Preserve the shared structure, but improve the detail panel wording for clarity.
- Ensure keyboard interaction works where rows are selectable.

### LineStressChart.svelte

- Add keyboard accessibility for chart points.
- Improve copy so it describes observed stress/error patterns without over-claiming explanation.
- Fix broken character rendering.

### CountryCaseGrid.svelte

- Make the click interaction real by adding a detail panel or expanded view for the selected country.
- Include region, error summary, residual summary, and year span.
- Add proper keyboard accessibility.

### ResidualFindings.svelte

- Add glossary support for displayed metrics.
- Ensure the selected findings read cleanly after TabPFN becomes champion again.

### format.js

- Normalize formatting helpers and remove mojibake output.
- Keep formatting utilities centralized instead of repeating string fixes in components.

### index.astro

- Rewrite the editorial copy for the final benchmark result.
- Keep the current high-level structure and visual language, but align every paragraph with the final analytical state.
- Add figure blocks in the correct sections.

## Data Contract Assumptions

The frontend will continue reading prebuilt JSON from `web/public/data`.

Expected key inputs:

- report_summary.json
- model_comparison.json
- region_residuals.json
- year_residuals.json
- country_residuals_top.json
- data_completeness_by_region.json
- variable_coverage.json
- model_error_by_year.json
- model_response_surfaces.json

The frontend should treat these as the source of truth for current benchmark state.

## Accessibility Requirements

- All clickable non-button elements must become keyboard-operable.
- Glossary popovers must be screen-reader discoverable and dismissible.
- Hover-only explanations must always have a click/focus path.
- Figure images must have useful alt text or accessible captions.

## Testing and Verification

Implementation should be verified with:

- component-level checks for glossary interaction and keyboard behavior
- a search pass for stale narrative references to outdated winners
- regeneration of web assets from scripts 10-12
- frontend build with `npm run build --prefix web`
- browser validation of interaction behavior after the frontend update

## Out of Scope

- building a full generic glossary CMS
- replacing static 3D images with a full interactive 3D engine in this pass
- redesigning the entire visual identity from scratch
- changing the underlying benchmark outputs again during this frontend pass

## Recommendation

Keep the current editorial shell and component set, but upgrade it into a more precise, consistent, and inspectable technical report:

- one benchmark story
- mixed glossary support everywhere it matters
- real country-card inspection
- static generated figures integrated as narrative evidence
- accessibility and encoding cleanup as part of the same pass
