# Paper 30 — R(5,5) >= 43: Computational Proof via GF(p) Polynomial Seeding and Multi-Track Optimization

**U24 Programme** | Bryan Daugherty, Gregory Ward, Shawn Ryan | March 2026

---

## Summary

We present a computational proof that R(5,5) >= 43 via a novel GF(p) polynomial seeding construction. A zero-violation 2-coloring of K42 is constructed using f(x) = x^2 + 2x + 11 over GF(43), producing only 10 raw violations -- a 138x improvement over the classical Paley construction's 1,380 violations. All 850,668 five-cliques of K42 are verified to be non-monochromatic.

On the K43 frontier, a 2-violation coloring is obtained via f(x) = x^2 + 30x + 41, representing a stable local minimum that survives GPU descent, iterated local search, population crossover, and all other tested optimization methods. IIS analysis identifies a 6-constraint essential core, and the obstruction to R(5,5) >= 44 is shown to be fundamentally 3-body in nature.

---

## Key Results

| Result | Value | Status |
|--------|-------|--------|
| R(5,5) >= 43 | Zero-violation K42 coloring | Certified |
| GF(43) raw violations | 10 (vs Paley's 1,380) | Computational |
| Improvement factor | 138x over Paley | Computational |
| K43 frontier | 2 violations (99.9998% K5-free) | Computational |
| Violating cliques | Share 4 of 5 vertices | Computational |
| Frustration index | 0.0 (strict local minimum) | Computational |
| IIS essential core | 6 constraints, 3 critical vertices | Computational |
| K44 extension | Infeasible for all 4 basin representatives | Computational |
| Obstruction type | 3-body (singles 0%, pairs 0%, triples 9.3%) | Computational |

---

## Verification

**14/14 checks PASS**

```bash
# Full verification (requires NumPy)
python scripts/verify_r55.py

# Generate figures (requires matplotlib, numpy)
python scripts/generate_figures.py
```

---

## Figures

| Figure | Description |
|--------|-------------|
| fig1 | GF(p) prime comparison -- violations by prime |
| fig2 | K42 coloring adjacency matrix heatmap |
| fig3 | K43 violating clique structure |
| fig4 | Multi-track optimization convergence |
| fig5 | Basin structure of K43 violation landscape |
| fig6 | IIS essential core network diagram |
| fig7 | Paley-GF phase transition interpolation |
| fig8 | Ramsey bounds staircase (k=3 to k=8) |

---

## Falsification Criteria

| Claim | Falsified if... |
|-------|-----------------|
| K42 zero-violation | Any 5-element subset of {0,...,41} induces a monochromatic K5 |
| GF(43) = 10 violations | Independent re-evaluation of f(x) = x^2 + 2x + 11 over GF(43) yields a different count |
| Paley(43) = 1,380 | Standard Paley construction on 43 vertices yields a different count |
| 2-violation stability | Any method reduces the K43 coloring below 2 violations |
| 3-body obstruction | A 2-vertex edge-fixing renders K44 extension infeasible |
| IIS core size = 6 | Under the same edge-fixing regime, a smaller IIS is extracted |

---

## Citation

```bibtex
@article{DaughertyWardRyan2026r55,
  title   = {$R(5,5) \ge 43$: Computational Proof via GF$(p)$ Polynomial Seeding and Multi-Track Optimization},
  author  = {Daugherty, Bryan and Ward, Gregory and Ryan, Shawn},
  year    = {2026},
  note    = {U24 Programme Paper 30},
  url     = {https://github.com/OriginNeuralAI/Papers}
}
```
