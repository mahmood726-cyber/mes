# MES — Multiverse Evidence Synthesis

**Evidence Landscapes, Not Point Estimates**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-126%20passing-brightgreen.svg)]()

MES is a next-generation meta-analysis framework that replaces single point estimates with robustness-classified evidence landscapes. Instead of asking "what is the effect?", MES asks "how much of the evidence landscape supports an effect, and what does that landscape look like?"

## The Problem

Traditional meta-analysis produces a single pooled estimate (e.g., OR = 0.73, p = 0.02), hiding the fact that the conclusion often depends on arbitrary analytical choices. Our empirical validation on **403 Cochrane systematic reviews** found:

- **~40% of conclusions are Fragile or Unstable** when the full multiverse of defensible choices is explored
- **Bias correction alone** drives 99% of conclusion variance
- **93% of prediction intervals** cross the null (BCG vaccine example)

## How MES Works

MES uses a three-phase pipeline: **ASSESS → EXPLORE → MAP**

1. **ASSESS**: Annotate each study with design type, risk of bias, and bias indicators — without subjective weighting
2. **EXPLORE**: Execute all defensible analytical specifications (648+ combinations of estimator, CI method, bias correction, quality filter, design filter, and leave-one-out sensitivity)
3. **MAP**: Classify robustness (Robust/Moderate/Fragile/Unstable), decompose what drives fragility, and certify the evidence package

### Key Innovation

Evidence quality and study design are **first-class multiverse dimensions**, not subjective weights. MES answers: *"Does the conclusion survive when you demand better evidence?"*

## Quick Start

### Python Engine (batch research)

```bash
pip install .
```

```python
from mes_core.pipeline import run_mes

studies = [
    {"study_id": "Study1", "yi": -0.5, "vi": 0.04, "measure": "logOR"},
    {"study_id": "Study2", "yi": -0.3, "vi": 0.06, "measure": "logOR"},
    {"study_id": "Study3", "yi": -0.8, "vi": 0.03, "measure": "logOR"},
]

verdict = run_mes(studies)
print(f"Classification: {verdict.overall_class}")
print(f"Concordance: {verdict.overall_c_sig:.1%}")
print(f"Dominant driver: {verdict.dominant_dimension} (eta2={verdict.dominant_eta2:.3f})")
```

### Browser App (interactive)

Open `app/mes-app.html` in any modern browser. No installation required.

## Robustness Classification

| Class | C_sig | Interpretation |
|-------|-------|---------------|
| **ROBUST** | >= 90% | Conclusion stable across all defensible specifications |
| **MODERATE** | 70-89% | Mostly stable, note caveats |
| **FRAGILE** | 50-69% | Conclusion depends on analytical choices |
| **UNSTABLE** | < 50% | No defensible single conclusion |

## Validation

- **R parity**: All 6 estimators validated against `metafor::rma()` (tolerance < 1e-4)
- **126 Python tests** + browser Selenium tests
- **403 Cochrane reviews** processed with zero errors

## Citation

If you use MES in your research, please cite:

> Ahmad M. Multiverse Evidence Synthesis: A Framework for Robust Meta-Analysis Applied to 403 Cochrane Reviews. *BMJ*. 2026.

## License

[MIT](LICENSE)
