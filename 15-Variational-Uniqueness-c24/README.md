# Paper 15 — The Daugherty Uniqueness Theorem: Five Constraints Force c = 24

**U24 Programme** | Bryan Daugherty, Gregory Ward, Shawn Ryan | March 2026

---

## Summary

Paper 04 showed that eleven independent mathematical structures all yield Omega = 24. This paper proves the converse: c = 24 is the *only* value consistent with all constraints simultaneously. Five constraints from four independent domains (statistical mechanics, CFT, Ramsey combinatorics, finite group theory) have a singleton intersection at c = 24.

---

## Key Results

| Result | Value | Status |
|--------|-------|--------|
| Uniqueness Theorem | {c : all 5 constraints} = {24} | Proved (exhaustive sweep) |
| Constraint I: Thermodynamic stability | c >= 5 | Proved (analytic) |
| Constraint II: Degeneracy dominance | c >= 17 | Proved (analytic) |
| Constraint III: Hellerman unitarity | c >= 17 | Proved (CFT bound) |
| Constraint IV: Ramsey T_c match | c in [19, 30] | Computational |
| Constraint V: S4 composition series | c = 24 unique | Proved (group theory) |
| Barrier ratio Omega | 3000/125 = 24.00 +/- 0.00 | Computational (670+ instances) |
| D4 triality invariance | Exact | Proved |
| Modular weight of Z-tilde | k = 0.11 +/- 0.10 ~ 0 | Computational |

---

## Verification

**12/12 checks PASS**

```bash
# Full verification (requires NumPy, SciPy)
python scripts/verify_uniqueness.py

# Generate figures (requires matplotlib)
python scripts/generate_figures.py
```

---

## Falsification Criteria

| Claim | Falsified if... |
|-------|-----------------|
| Uniqueness (c = 24 only) | An integer c != 24 satisfying all five constraints is exhibited |
| S4 forcing | A solvable group G with \|G\| != 24 has composition quotients [4, 3, 2] |
| Omega = 24 universality | An optimization family yields tau_macro / tau_micro != 24 |

---

## Citation

```bibtex
@article{DaughertyWardRyan2026uniqueness,
  title   = {The Daugherty Uniqueness Theorem: Five Constraints Force $c = 24$},
  author  = {Daugherty, Bryan and Ward, Gregory and Ryan, Shawn},
  year    = {2026},
  note    = {U24 Programme Paper 15},
  url     = {https://github.com/OriginNeuralAI/Papers}
}
```
