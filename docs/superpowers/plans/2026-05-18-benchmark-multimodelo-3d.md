# Benchmark Multi-Modelo e Superfícies 3D Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expandir o benchmark local para múltiplos modelos fortes com tuning temporal pesado, benchmark opcional de TabPFN e figuras 3D estáticas para os melhores modelos locais.

**Architecture:** Extrair a lógica compartilhada de modelagem para `src/models/`, usar `scripts/08` como benchmark local principal, manter `scripts/09` como benchmark externo opcional e atualizar os scripts posteriores para consumir um esquema global de métricas, predições e resíduos. As superfícies 3D serão geradas a partir do modelo campeão local e de um segundo modelo local competitivo usando duas features relevantes e demais variáveis fixadas.

**Tech Stack:** pandas, numpy, scikit-learn, scipy, matplotlib, requests/httpx, bibliotecas opcionais xgboost/lightgbm/catboost.

---

### Task 1: Shared benchmark module

**Files:**
- Create: `src/models/benchmarking.py`
- Create: `tests/test_benchmarking.py`

- [ ] Step 1: Write failing tests for temporal folds and surface feature selection.
- [ ] Step 2: Run the tests and confirm failure.
- [ ] Step 3: Implement shared helpers for feature sets, temporal CV, optional model registry and surface feature selection.
- [ ] Step 4: Run the focused tests and confirm pass.

### Task 2: Local heavy benchmark script

**Files:**
- Modify: `scripts/08_train_baseline_models.py`

- [ ] Step 1: Add a failing test or script-level assertion path for benchmark outputs.
- [ ] Step 2: Refactor `scripts/08` to train multiple local models, tune them on temporal CV and export richer outputs.
- [ ] Step 3: Generate updated comparison figures and 3D response surface figures for the top local models.
- [ ] Step 4: Run the benchmark entrypoint on the available environment or, if dependencies are missing, run a focused smoke command.

### Task 3: Optional TabPFN integration

**Files:**
- Modify: `scripts/09_train_tabpfn_priorlabs.py`

- [ ] Step 1: Refactor feature preparation to reuse the shared benchmark layer.
- [ ] Step 2: Append TabPFN outputs into the global comparison artifacts without breaking local-only execution.
- [ ] Step 3: Run a non-credential smoke validation path if the API key is absent.

### Task 4: Residual and asset generalization

**Files:**
- Modify: `scripts/10_analyze_model_residuals.py`
- Modify: `scripts/11_export_report_assets.py`
- Modify: `scripts/12_prepare_web_assets.py`

- [ ] Step 1: Generalize residual analysis to choose the champion model from the global metrics table.
- [ ] Step 2: Export model-level summaries and new assets for the expanded benchmark.
- [ ] Step 3: Update the web asset copy list to include any new JSON outputs.
- [ ] Step 4: Run the downstream export scripts or focused smoke validations.

### Task 5: Docs and dependency updates

**Files:**
- Modify: `README.md`
- Modify: `requirements.txt`

- [ ] Step 1: Document the new benchmark behavior, optional libraries and 3D outputs.
- [ ] Step 2: Add optional heavy local model libraries to requirements with clear comments.
- [ ] Step 3: Re-run the key verification commands and capture final status.
