# Frontend Executive Narrative And Native Charts Design

Date: 2026-05-18
Project: `who-global-health-signals`
Scope: Final redesign of the public report layer after the benchmark and TabPFN comparison were stabilized

## Goal

Turn the current report into a clearer executive-facing analytical product that:

1. answers the target question in plain language at the top of the page
2. keeps the analytical rigor and benchmark transparency intact
3. replaces all report PNG figures with native frontend visualizations
4. moves the long-form analytical summary into the repository README, with a mini-paper structure

This is not a cosmetic polish task. It is a narrative and evidence architecture change.

## Problem statement

The current site is visually strong but still too centered on technical method before conclusion. A non-technical stakeholder can understand that the benchmark is sophisticated, but still leave without a crisp answer to the project question:

> Can public health indicators from the WHO Global Health Observatory explain observable variation and predict differences in life expectancy across countries?

The current site also still treats much of the generated evidence as external figure attachments. The PNG-based figures are valid analytical artifacts, but inside the report they behave more like inserted exhibits than first-class visual arguments.

The next version should therefore do two things simultaneously:

1. promote the substantive conclusions to the top of the experience
2. absorb the generated evidence into the design system as native charts

## User-facing outcomes

After this redesign:

1. the top of the site should read like a business case or executive summary
2. a broad audience should understand the answer to the target question before reaching the technical sections
3. all major figures should appear as native report graphics instead of static PNG embeds
4. the report should still preserve methodological honesty, benchmark comparison, and residual interpretation
5. the README should become a long-form results summary suitable for GitHub readers, closer to a mini-paper than a setup note

## Final narrative stance

The report should tell a balanced story:

1. the WHO public indicator panel contains a very strong predictive signal for life expectancy
2. local trainable models perform very well on the temporal holdout
3. the final global comparison is still won by TabPFN
4. residuals remain important because strong prediction does not eliminate regional stress, year-level shocks, or country-level divergence from the modeled pattern

The site should not frame the result as “TabPFN won, end of story.” It should frame the result as:

> the benchmark is strong, the signal is real, the external reference wins the final comparison, and the remaining error is analytically meaningful

## Information architecture

### 1. Executive case

This becomes the new top section of the home page.

Purpose:

1. answer the target question immediately
2. explain why the analysis matters
3. summarize what was analyzed
4. state the main results with concrete numbers

Content structure:

1. target question
2. business relevance / analytical value
3. what data was used
4. key findings
5. final comparative result

Expected tone:

1. executive
2. direct
3. evidence-based
4. accessible to non-specialists

This section should include data-backed claims such as:

1. size of the analytical panel
2. number of countries/entities
3. temporal range
4. final champion MAE/RMSE/R2
5. best local model and its relative position

### 2. Question and method

This section remains, but is demoted from “main story” to “method framing.”

Purpose:

1. explain the analytical unit
2. explain the target variable
3. explain the temporal holdout
4. explain the benchmark structure

This section should be shorter than in the current version because the top of the page will already have answered the “why” and “what we concluded” questions.

### 3. What the data says

This is a new narrative layer distinct from raw benchmark comparison.

Purpose:

1. interpret the target question substantively
2. make clear that public WHO indicators explain life expectancy very well
3. connect predictive strength back to real indicator families

This section should answer, in plain language:

1. what kinds of signals are most informative
2. what the model performance implies about the relationship between indicators and life expectancy
3. where the data still has structural limitations

### 4. Interactive evidence

This is where the old figure gallery becomes native report graphics.

Purpose:

1. show the evidence supporting the executive summary
2. keep all visual logic inside the report’s own design language
3. replace static PNG dependence

### 5. Residual intelligence

This remains a major section, but should become easier to understand for non-technical readers.

Purpose:

1. explain where the model remains less certain
2. highlight region, year and country-level outliers
3. show that residuals are investigative leads, not success/failure labels

### 6. Sources, limits, reproducibility

This remains the closing section.

Purpose:

1. preserve transparency
2. state methodological limits
3. avoid causal overclaiming

## Native chart system

All major `outputs/figures/*` artifacts should stop appearing as embedded PNGs in the final site.

Instead, they should be re-expressed as native frontend charts grouped into four families.

### Family A: data quality charts

Replaces:

1. `01_variable_coverage_top15.png`
2. `02_yearly_data_completeness.png`
3. `03_completeness_by_region.png`
4. `04_life_expectancy_trend_by_region.png`

Target chart forms:

1. coverage ranking: horizontal bar chart
2. yearly completeness: line or area chart
3. completeness by region: ordered bar chart
4. life expectancy trend by region: multi-series line chart

Interpretive role:

1. show where the panel is strongest
2. show why some comparisons are better supported than others
3. show that the dataset structure itself matters to model performance

### Family B: benchmark charts

Replaces:

1. `09_tabpfn_actual_vs_predicted.png`
2. `10_model_comparison_mae.png`
3. `14_local_model_comparison.png`
4. `15_local_model_error_by_year.png`

Target chart forms:

1. final comparison ranking
2. local-only comparison ranking
3. actual vs predicted scatter for the champion
4. model error over time

Interpretive role:

1. show final winner and local benchmark strength
2. distinguish external reference from local trainable models
3. make the benchmark story legible without forcing the reader into raw tables

### Family C: residual charts

Replaces:

1. `11_residuals_by_region.png`
2. `12_residuals_by_year.png`
3. `13_top_country_residuals.png`

Target chart forms:

1. residual difficulty by region
2. residual stress by year
3. top country error ranking with linked detail panel

Interpretive role:

1. identify where prediction remains hardest
2. surface temporal stress periods
3. show country cases that merit qualitative follow-up

### Family D: model behavior charts

Replaces:

1. `16_response_surface_<model>.png`
2. `17_response_surface_<model>.png`

Initial target representation:

1. native heatmap views rather than immediate heavy 3D recreation

Reasoning:

1. heatmaps are easier to read in-report
2. they are more robust on mobile
3. they preserve analytical value without introducing unnecessary rendering complexity

Future-friendly extension:

1. the architecture should leave room for later pseudo-3D or WebGL rendering if desired

Interpretive constraint:

These views must be explicitly labeled as model response surfaces, not causal landscapes.

## Native chart design rules

Every native chart should include:

1. an executive title
2. a one-sentence interpretive subtitle
3. a tooltip that uses the glossary system where relevant
4. a short reason why this chart matters to the target question

Every native chart should feel like part of one visual family:

1. same spacing rhythm
2. same panel treatment
3. same typography
4. same tooltip language
5. same interaction affordances

## Glossary behavior

The mixed glossary interaction remains valid and should be reused:

1. hover preview on desktop
2. click to pin
3. click-only on mobile
4. keyboard accessible open/close behavior

Glossary should remain embedded:

1. in editorial text
2. in metric cards
3. in benchmark labels
4. in chart annotations and tooltips

## Executive summary content requirements

The new top section should contain a business-case style summary with these elements:

1. what was analyzed
2. why it matters
3. what the data volume and scope were
4. what the benchmark found
5. what the main conclusion is

The summary must explicitly cite concrete values from the current build, such as:

1. `13,785` full analytical rows
2. `4,048` modeling-ready rows
3. `218` countries/entities
4. the `2015+` temporal holdout structure
5. `tabpfn_priorlabs` as final champion
6. `0.110` test MAE for TabPFN
7. `ridge` as strongest local baseline at `0.243` MAE

The summary should read like:

1. a concise analytical business case
2. not like a methods section
3. not like marketing copy

## README redesign

The README should be rewritten into a long-form summary that behaves more like a mini-paper.

### Required sections

1. research question
2. why the question matters
3. data and unit of analysis
4. modeling strategy
5. main results
6. substantive conclusions
7. residual interpretation
8. limitations
9. reproducibility

### README narrative stance

The README should make explicit that:

1. the signal is very strong
2. local models are competitive
3. TabPFN wins the final comparison
4. predictive accuracy does not imply causality
5. residuals help identify cases for follow-up

### README role relative to the site

The site:

1. more narrative
2. more executive
3. more interactive

The README:

1. denser
2. more complete
3. more paper-like
4. more suitable for GitHub readers and repository evaluation

## Affected files and systems

### Frontend architecture

Likely affected:

1. `web/src/components/ReportHome.astro`
2. current report components under `web/src/components/`
3. shared formatting and glossary helpers
4. new chart components and possible chart-specific helpers

### Data contracts

May require expanded or reshaped JSON exports for:

1. benchmark time-series
2. regional completeness and trend series
3. line and scatter inputs
4. response surface heatmap payloads

If a chart cannot be expressed cleanly from the current compact JSON exports, the export layer should be extended rather than hacking around missing structure in the frontend.

### Documentation

Affected:

1. `README.md`
2. possibly report-facing wording in exported summaries if the executive copy benefits from upstream fields

## Non-goals

This redesign does not aim to:

1. change the underlying modeling results
2. add new models
3. rerun the scientific pipeline unless needed for chart contracts
4. claim causal inference
5. keep PNG figures in the final web experience

PNG artifacts may continue to exist in repo outputs, but they should no longer be part of the site experience.

## Risks and mitigations

### Risk 1: clearer narrative becomes oversimplified

Mitigation:

1. keep the executive layer at the top
2. preserve method, benchmark and residual sections below
3. keep hard numbers visible

### Risk 2: native chart rewrite drifts away from actual analytical artifacts

Mitigation:

1. use the exported data directly
2. preserve chart semantics from the analytical pipeline
3. verify that frontend views still match the quantitative outputs

### Risk 3: 3D response surfaces become ornamental

Mitigation:

1. start with heatmap-style native rendering
2. explicitly label them as model behavior surfaces
3. attach interpretive guidance in the UI

### Risk 4: README and site diverge again

Mitigation:

1. rewrite them in the same implementation cycle
2. use the final benchmark numbers consistently
3. reverify exported summary fields before closing the work

## Recommended implementation order

1. rewrite the report architecture so the executive summary leads the experience
2. build the native chart system by visual family
3. remove PNG dependence from the site
4. rewrite the README as the long-form analytical summary
5. verify chart-data consistency and rebuild the frontend

## Acceptance criteria

This redesign is complete when:

1. the top of the site contains a business-case style executive summary with data-backed conclusions
2. the answer to the target question is understandable before the technical sections
3. all current figure-driven report sections are rendered natively in the frontend
4. PNG figures are no longer used in the final site experience
5. the README reads like a substantial long-form summary of findings
6. the final site and README tell the same benchmark story
7. the report remains technically honest about limitations and non-causal interpretation
