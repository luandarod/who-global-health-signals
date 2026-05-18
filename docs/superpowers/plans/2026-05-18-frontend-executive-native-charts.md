# Frontend Executive Native Charts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the public report layer so it opens with an executive business-case summary, replaces all figure PNGs with native charts, and rewrites the README into a long-form results summary.

**Architecture:** Extend the export layer with the remaining chart contracts, replace the current report shell with a narrative-first architecture, and build a small family of focused native chart components that consume only `web/public/data/*.json`. Keep residual and benchmark semantics aligned with the current analytical outputs and remove PNG dependence from the site experience.

**Tech Stack:** Python export scripts, Astro, Svelte, native SVG/CSS charts, Python `unittest`, npm/Astro build.

---

### Task 1: Lock the new data contracts with failing tests

**Files:**
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_report_shell.py`
- Test: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_report_shell.py`

- [ ] **Step 1: Write failing tests for new public assets and no-PNG frontend usage**

Add assertions for:
- `scripts/12_prepare_web_assets.py` required JSON files including a champion scatter payload
- `ReportHome.astro` not referencing `/figures/`
- `ReportHome.astro` containing an executive case section

- [ ] **Step 2: Run the focused frontend contract test to verify it fails**

Run:

```powershell
& 'C:\Users\Luanda Rodrigues\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_frontend_report_shell -v
```

Expected: FAIL because the current export contract and report shell still depend on figure references.

- [ ] **Step 3: Commit after the test-first checkpoint**

```bash
git add tests/test_frontend_report_shell.py
git commit -m "test: lock executive report frontend contracts"
```

### Task 2: Extend the export layer for native charts

**Files:**
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\scripts\11_export_report_assets.py`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\scripts\12_prepare_web_assets.py`
- Test: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_report_shell.py`

- [ ] **Step 1: Export the missing champion scatter payload and any native-only chart data**

Add a public JSON export for the champion model predictions with fields needed for actual-vs-predicted scatter and executive summary support.

- [ ] **Step 2: Stop copying figure PNGs into the web public directory**

Limit `12_prepare_web_assets.py` to the JSON contracts used by the frontend.

- [ ] **Step 3: Run the focused frontend contract test to verify the export layer now passes**

Run:

```powershell
& 'C:\Users\Luanda Rodrigues\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_frontend_report_shell -v
```

Expected: PASS on contract checks once the new JSON list and no-PNG assumption are in place.

- [ ] **Step 4: Commit the export-layer changes**

```bash
git add scripts/11_export_report_assets.py scripts/12_prepare_web_assets.py tests/test_frontend_report_shell.py
git commit -m "feat: export native chart assets for executive report"
```

### Task 3: Build the native chart component system

**Files:**
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ExecutiveSummary.svelte`
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\RankingChart.svelte`
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\MultiSeriesLineChart.svelte`
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ScatterEvidenceChart.svelte`
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ResponseSurfaceHeatmap.svelte`
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ChartFrame.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\presentation.js`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\chartScales.js`

- [ ] **Step 1: Build shared chart framing and formatting helpers**

Create a reusable chart frame/panel wrapper, subtitle and “why this matters” slot pattern, plus any missing formatting helpers.

- [ ] **Step 2: Build ranking and multi-series line components**

Use them for coverage, completeness, benchmark rankings, local model yearly error, residuals by region/year, and life expectancy trends.

- [ ] **Step 3: Build the champion scatter component**

Support the native replacement of `09_tabpfn_actual_vs_predicted.png`.

- [ ] **Step 4: Build the response surface heatmap component**

Use `model_response_surfaces.json` directly and label it as model behavior rather than causal interpretation.

- [ ] **Step 5: Run the Astro build after component creation**

Run:

```powershell
npm.cmd run build --prefix web
```

Expected: PASS or a small compile error list that is resolved before moving on.

- [ ] **Step 6: Commit the new chart system**

```bash
git add web/src/components web/src/lib/presentation.js web/src/lib/chartScales.js
git commit -m "feat: add native chart system for report evidence"
```

### Task 4: Rewrite the report shell around the executive case

**Files:**
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ReportHome.astro`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\pages\index.astro`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\FindingHighlights.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\BenchmarkComparison.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\InsightBarPanel.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ResidualTimeline.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\CountryCaseExplorer.svelte`

- [ ] **Step 1: Add the business-case executive summary at the top of the page**

Use the approved structure:
- question
- what was analyzed
- why it matters
- concrete result metrics
- final conclusion

- [ ] **Step 2: Replace figure exhibits with native chart sections**

Remove `/figures/*` references from the report shell and reorganize the page into:
- Executive case
- Question and method
- What the data says
- Interactive evidence
- Residual intelligence
- Sources and limits

- [ ] **Step 3: Preserve glossary behavior and accessibility while updating the wording**

Keep mixed glossary interactions and keyboard access intact.

- [ ] **Step 4: Run the frontend contract test and Astro build**

Run:

```powershell
& 'C:\Users\Luanda Rodrigues\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_frontend_report_shell -v
npm.cmd run build --prefix web
```

Expected: PASS on both.

- [ ] **Step 5: Commit the narrative-first report shell**

```bash
git add web/src/components web/src/pages/index.astro
git commit -m "feat: rewrite report shell with executive narrative"
```

### Task 5: Rewrite the README as a long-form results summary

**Files:**
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\README.md`

- [ ] **Step 1: Rewrite the README into the mini-paper structure**

Include:
- research question
- why it matters
- data and unit of analysis
- modeling strategy
- main results
- substantive conclusions
- residual interpretation
- limitations
- reproducibility

- [ ] **Step 2: Align the README numbers and narrative with the final TabPFN result**

Keep the benchmark story consistent with the frontend and exported summary.

- [ ] **Step 3: Run a quick text audit for stale ridge-first or PNG-site language**

Run:

```powershell
rg -n "ridge champion|png|figures/|outperform the external TabPFN by a wide margin|simple linear model is the strongest performer" README.md web/src/components/ReportHome.astro
```

Expected: no stale claims from the earlier report state.

- [ ] **Step 4: Commit the README rewrite**

```bash
git add README.md
git commit -m "docs: rewrite readme as long-form analytical summary"
```

### Task 6: Rebuild public assets and run end-to-end verification

**Files:**
- Modify: generated assets under `data/public/` and `web/public/data/`

- [ ] **Step 1: Re-run the report export and web-asset preparation**

Run:

```powershell
& 'C:\Users\Luanda Rodrigues\AppData\Local\Programs\Python\Python312\python.exe' scripts/10_analyze_model_residuals.py
& 'C:\Users\Luanda Rodrigues\AppData\Local\Programs\Python\Python312\python.exe' scripts/11_export_report_assets.py
& 'C:\Users\Luanda Rodrigues\AppData\Local\Programs\Python\Python312\python.exe' scripts/12_prepare_web_assets.py
```

Expected: PASS and only JSON assets copied to the web app.

- [ ] **Step 2: Run the full relevant test suite**

Run:

```powershell
& 'C:\Users\Luanda Rodrigues\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_frontend_report_shell tests.test_benchmarking tests.test_upstream_pipeline tests.test_who_client_tls tests.test_tabpfn_tls tests.test_residual_outputs -v
```

Expected: PASS.

- [ ] **Step 3: Run the final frontend production build**

Run:

```powershell
npm.cmd run build --prefix web
```

Expected: PASS.

- [ ] **Step 4: Commit the rebuilt assets and final polish**

```bash
git add data/public web/public/data docs/superpowers/plans/2026-05-18-frontend-executive-native-charts.md
git commit -m "feat: ship executive report with native charts"
```
