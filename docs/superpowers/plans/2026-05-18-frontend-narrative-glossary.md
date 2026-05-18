# Frontend Narrative, Glossary, and Figure Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the report frontend with the final TabPFN-winning benchmark, add a reusable mixed-interaction glossary, integrate generated figures into the narrative, and fix frontend accessibility and consistency issues.

**Architecture:** Keep the current single-page Astro shell and Svelte component structure, but introduce one shared glossary/popover layer plus a small set of formatting helpers that all components can use. Update components in place instead of redesigning the whole app, then wire the page copy and static figure exhibits to the already-generated JSON and PNG outputs.

**Tech Stack:** Astro, Svelte 5, plain JS utilities, static JSON assets, generated PNG figures, Node build via `npm.cmd run build --prefix web`

---

## File Map

### Create

- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\glossary.js`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\GlossaryTerm.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\FigureExhibit.svelte`

### Modify

- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\format.js`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\chartScales.js`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\MetricCards.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ModelComparison.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\BarInsightChart.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\LineStressChart.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\CountryCaseGrid.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ResidualFindings.svelte`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\pages\index.astro`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\scripts\11_export_report_assets.py`

### Verify With

- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\public\data\report_summary.json`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\web\public\data\model_comparison.json`
- `C:\Users\Luanda Rodrigues\who-global-health-signals\outputs\figures\*.png`

---

### Task 1: Fix the shared data/story foundation

**Files:**
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\scripts\11_export_report_assets.py`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\format.js`
- Test: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_exports.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import json
import unittest


class FrontendExportContractTests(unittest.TestCase):
    def test_report_summary_best_model_matches_champion_finding(self):
        root = Path(r"C:\Users\Luanda Rodrigues\who-global-health-signals")
        payload = json.loads((root / "data" / "public" / "report_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["best_model"]["name"], payload["executive_findings"][0]["metric"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_frontend_exports.py -v`
Expected: FAIL because `best_model.name` is `tabpfn_priorlabs` while the first executive finding still reports `ridge`.

- [ ] **Step 3: Write minimal implementation**

Implement these fixes:

- ensure `scripts/11_export_report_assets.py` always exports the freshest executive findings after `scripts/10`
- add a champion-consistency normalization step in `build_report_summary(...)` so the `best_model` and `executive_findings` agree if stale data slips through
- update `web/src/lib/format.js` to remove mojibake and standardize:

```js
export function fallbackDash() {
  return '-';
}

export function formatNumber(value, digits = 2) {
  const number = Number(value);
  if (!Number.isFinite(number)) return fallbackDash();
  return number.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits
  });
}

export function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return fallbackDash();
  return `${Math.round(number * 100)}%`;
}

export function formatYearRange(start, end) {
  return `${start ?? fallbackDash()}-${end ?? fallbackDash()}`;
}

export function labelName(value) {
  return String(value ?? '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function compactLabel(value, max = 58) {
  const label = labelName(value);
  if (label.length <= max) return label;
  return `${label.slice(0, max - 1).trim()}...`;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_frontend_exports.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_frontend_exports.py scripts/11_export_report_assets.py web/src/lib/format.js
git commit -m "fix: align exported frontend summary with final champion"
```

### Task 2: Add the glossary foundation

**Files:**
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\glossary.js`
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\GlossaryTerm.svelte`
- Test: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_strings.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import unittest


class FrontendGlossaryTests(unittest.TestCase):
    def test_glossary_contains_core_metric_terms(self):
        root = Path(r"C:\Users\Luanda Rodrigues\who-global-health-signals")
        glossary = (root / "web" / "src" / "lib" / "glossary.js").read_text(encoding="utf-8")
        for term in ["MAE", "RMSE", "R2", "residual", "coverage", "completeness"]:
            self.assertIn(term, glossary)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_frontend_strings.py::FrontendGlossaryTests -v`
Expected: FAIL because the glossary module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `web/src/lib/glossary.js` with:

```js
export const glossary = {
  MAE: {
    label: 'MAE',
    short: 'Average absolute prediction error.',
    body: 'Mean Absolute Error is the average distance between predicted and observed life expectancy. Lower values mean predictions stay closer to the observed outcome.'
  },
  RMSE: {
    label: 'RMSE',
    short: 'Error metric that penalizes larger misses more strongly.',
    body: 'Root Mean Squared Error increases faster when the model makes a few large mistakes. It complements MAE by showing whether the error distribution has heavier tails.'
  },
  R2: {
    label: 'R2',
    short: 'Share of variation explained by the model.',
    body: 'R2 measures how much of the observed variation in life expectancy is captured by the model on the test set. Higher values indicate a tighter fit, but do not imply causality.'
  },
  residual: {
    label: 'Residual',
    short: 'Observed minus predicted outcome.',
    body: 'A residual is the difference between observed and predicted life expectancy. Positive values mean the observed outcome was higher than expected, and negative values mean it was lower.'
  },
  coverage: {
    label: 'Coverage',
    short: 'How often a variable appears in the country-year table.',
    body: 'Coverage describes the share of country-year rows in which a variable is available. Higher coverage makes cross-country comparison and model training more stable.'
  },
  completeness: {
    label: 'Completeness',
    short: 'How much of the expected feature set is present for a row or group.',
    body: 'Completeness summarizes how many indicators are available for a country-year record or aggregate slice. It is a data quality signal, not a performance score.'
  },
  temporal_split: {
    label: 'Temporal split',
    short: 'Train on earlier years, test on later years.',
    body: 'The benchmark trains on pre-2015 records and evaluates on 2015 onward. This is stricter than a random split because it tests forward-looking generalization.'
  },
  benchmark: {
    label: 'Benchmark',
    short: 'Structured comparison across multiple models.',
    body: 'A benchmark compares several models on the same data split and metrics so that any performance gain can be interpreted against a common baseline.'
  }
};
```

Create `GlossaryTerm.svelte` with focusable trigger, mixed hover/click behavior, `Escape` close, and click-outside dismissal.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_frontend_strings.py::FrontendGlossaryTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/lib/glossary.js web/src/components/GlossaryTerm.svelte tests/test_frontend_strings.py
git commit -m "feat: add shared frontend glossary system"
```

### Task 3: Upgrade interactive components

**Files:**
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\MetricCards.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ModelComparison.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\BarInsightChart.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\LineStressChart.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\CountryCaseGrid.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\ResidualFindings.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\lib\chartScales.js`
- Test: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_strings.py`

- [ ] **Step 1: Write the failing test**

```python
class FrontendNarrativeTests(unittest.TestCase):
    def test_metric_cards_and_model_comparison_do_not_hardcode_tabpfn_label(self):
        root = Path(r"C:\Users\Luanda Rodrigues\who-global-health-signals")
        metric_cards = (root / "web" / "src" / "components" / "MetricCards.svelte").read_text(encoding="utf-8")
        model_comparison = (root / "web" / "src" / "components" / "ModelComparison.svelte").read_text(encoding="utf-8")
        self.assertNotIn("TabPFN MAE years", metric_cards)
        self.assertIn("GlossaryTerm", model_comparison)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_frontend_strings.py::FrontendNarrativeTests -v`
Expected: FAIL because the old hardcoded label and missing glossary integration are still present.

- [ ] **Step 3: Write minimal implementation**

Apply these component changes:

- `MetricCards.svelte`
  - derive the champion label from `summary.best_model.name`
  - replace fixed `TabPFN MAE years` with champion-aware wording such as `best-model MAE`
  - use `formatYearRange(...)`
  - add glossary trigger on the benchmark metric label

- `ModelComparison.svelte`
  - replace mojibake strings
  - add keyboard support: `role="button"`, `tabindex="0"`, `on:keydown`
  - use `GlossaryTerm` for MAE, RMSE, and R2
  - keep narrative balanced: strong local benchmark, TabPFN final winner

- `BarInsightChart.svelte`
  - add `role`, `tabindex`, and Enter/Space handling for selectable rows
  - use glossary terms in the detail panel where `coverage`, `completeness`, or `mean absolute error` are explained

- `LineStressChart.svelte`
  - add keyboard support to the point group or replace it with focusable wrappers
  - fix labels and tooltip text

- `CountryCaseGrid.svelte`
  - add a real selected-country detail panel below the grid
  - include region, mean error, mean residual, and year span
  - make cards keyboard accessible

- `ResidualFindings.svelte`
  - support glossary for metrics shown in findings
  - keep selected findings aligned with current champion state

- `chartScales.js`
  - make `valueExtent(...)` safe for empty arrays:

```js
export function valueExtent(data, accessor) {
  const values = data.map(accessor).map(Number).filter(Number.isFinite);
  if (!values.length) return [0, 1];
  return [Math.min(...values), Math.max(...values)];
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_frontend_strings.py::FrontendNarrativeTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/components/MetricCards.svelte web/src/components/ModelComparison.svelte web/src/components/BarInsightChart.svelte web/src/components/LineStressChart.svelte web/src/components/CountryCaseGrid.svelte web/src/components/ResidualFindings.svelte web/src/lib/chartScales.js tests/test_frontend_strings.py
git commit -m "feat: upgrade interactive report components and glossary hooks"
```

### Task 4: Integrate generated figures and rewrite the report shell

**Files:**
- Create: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\components\FigureExhibit.svelte`
- Modify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\src\pages\index.astro`
- Test: `C:\Users\Luanda Rodrigues\who-global-health-signals\tests\test_frontend_strings.py`

- [ ] **Step 1: Write the failing test**

```python
class FrontendPageNarrativeTests(unittest.TestCase):
    def test_homepage_mentions_generated_figures_and_balanced_benchmark_story(self):
        root = Path(r"C:\Users\Luanda Rodrigues\who-global-health-signals")
        page = (root / "web" / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
        self.assertIn("FigureExhibit", page)
        self.assertIn("TabPFN", page)
        self.assertIn("local benchmark", page)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_frontend_strings.py::FrontendPageNarrativeTests -v`
Expected: FAIL because the page does not yet use a shared figure exhibit component and the copy is not fully aligned with the final narrative.

- [ ] **Step 3: Write minimal implementation**

Create `FigureExhibit.svelte` with:

- image source
- title
- caption
- optional glossary terms in title/caption
- accessible `img` and caption layout

Rewrite `index.astro` so it:

- imports `FigureExhibit`
- uses `summary.best_model.name` story as source of truth
- includes figure exhibits in the correct sections:
  - data foundation: `01` to `04`
  - benchmark: `09`, `10`, `14`, `15`
  - residual intelligence: `11`, `12`, `13`
  - model response chapter: two strongest 3D surfaces
- keeps the narrative balanced:
  - local benchmark is strong
  - TabPFN wins final comparison
  - residuals remain the interpretation layer

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_frontend_strings.py::FrontendPageNarrativeTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/components/FigureExhibit.svelte web/src/pages/index.astro tests/test_frontend_strings.py
git commit -m "feat: integrate generated figures into final report narrative"
```

### Task 5: Regenerate assets and verify the final frontend

**Files:**
- Verify: `C:\Users\Luanda Rodrigues\who-global-health-signals\data\public\report_summary.json`
- Verify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\public\data\report_summary.json`
- Verify: `C:\Users\Luanda Rodrigues\who-global-health-signals\web\dist\index.html`

- [ ] **Step 1: Rebuild report JSON in correct order**

Run:

```bash
python scripts/10_analyze_model_residuals.py
python scripts/11_export_report_assets.py
python scripts/12_prepare_web_assets.py
```

Expected:

- `report_summary.json` shows `tabpfn_priorlabs` in `best_model.name`
- `report_summary.json` executive findings start with `tabpfn_priorlabs`

- [ ] **Step 2: Run the full verification suite**

Run:

```bash
python -m unittest tests/test_benchmarking.py tests/test_upstream_pipeline.py tests/test_who_client_tls.py tests/test_tabpfn_tls.py tests/test_residual_outputs.py tests/test_frontend_exports.py tests/test_frontend_strings.py -v
```

Expected: all tests pass

- [ ] **Step 3: Build the frontend**

Run:

```bash
npm.cmd run build --prefix web
```

Expected: Astro build exits 0 and emits `web/dist/index.html`

- [ ] **Step 4: Search for stale narrative strings**

Run:

```bash
rg -n "TabPFN MAE years|TabPFN is the only model below one year|Compare Ridge, Random Forest and TabPFN|RÂ²|â€”|â€¦" web/src README.md
```

Expected: no stale or mojibake strings remain

- [ ] **Step 5: Commit**

```bash
git add data/public web/public/data web/src README.md tests
git commit -m "feat: finalize report frontend narrative and glossary"
```

## Self-Review

- Spec coverage:
  - balanced technical-analytical narrative: covered in Tasks 3 and 4
  - mixed glossary system: covered in Task 2 and integrated in Task 3
  - generated PNG figures embedded in the page: covered in Task 4
  - accessibility and keyboard interaction: covered in Task 3
  - final asset regeneration and verification: covered in Task 5

- Placeholder scan:
  - no TBD/TODO placeholders left
  - each task contains concrete files, tests, and commands

- Type consistency:
  - `GlossaryTerm` and `glossary` names are consistent across tasks
  - `FigureExhibit` naming is consistent across page integration tasks

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-18-frontend-narrative-glossary.md`.

User has already asked to proceed, so execute inline in this session using the plan structure above.
