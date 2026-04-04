[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19414435.svg)](https://doi.org/10.5281/zenodo.19414435)

# Paper 14 — Falsification of R(8,8) > 293

**U24 Programme** | Bryan Daugherty, Gregory Ward, Shawn Ryan | March 2026

---

## Summary

We falsify the claim R(8,8) > 293 by exhaustive max-clique verification, confirm R(8,8) > 281 via Paley construction, and verify the Zero-Core Theorem for R(5,5).  The central methodological finding is that stochastic sampling becomes unreliable for Ramsey verification at k = 8, where random sampling covers only ~6.6 x 10^-9 of the search space.

---

## Key Results

| Result | Value | Status |
|--------|-------|--------|
| R(8,8) > 293 claim | **Falsified** | Proved (exhaustive Bron-Kerbosch) |
| Red max-clique in K_293 | omega = 8 (monochromatic K_8) | Proved |
| Blue max-clique in K_293 | omega = 11 (monochromatic K_11) | Proved |
| Red K_8 witness | {3, 44, 87, 130, 165, 219, 234, 285} | Proved (28 edges verified) |
| Stochastic sampling coverage | 6.6 x 10^-9 | Computational |
| Detection probability P(miss\|V=1) | ~1.0 | Computational |
| R(8,8) > 281 (Paley) | **Confirmed** | Proved (exhaustive K_8 enumeration) |
| Paley(293) violations | 2,310,012 monochromatic K_8 | Computational (31.1s) |
| Zero-Core Theorem (R(5,5)) | Essential core = empty set | Proved (2,480 DPLL proofs) |
| Confirmed bound | 282 <= R(8,8) <= 1,870 | Proved |

---

## Verification

**12/12 checks PASS**

Run the verification suite:

```bash
# R(8,8) falsification + Paley confirmation (requires NumPy)
python scripts/verify_r88.py

# Zero-Core Theorem verification (~4 min)
python scripts/verify_zerocore.py

# Generate all figures (requires matplotlib)
python scripts/generate_figures.py
```

### Prerequisites
- Python 3.10+
- NumPy
- matplotlib (for figures only)

### Data Files

| File | Description |
|------|-------------|
| `data/K293_best_20260315_101534.npy` | GPU-optimized K_293 coloring (42,778 spins) |
| `data/verification_certificate_r88.json` | Falsification certificate |
| `data/k8_landscape.json` | Paley(281) K_8-free proof |
| `data/paley_293_k8.json` | Paley(293) 2.31M violations |
| `data/r88_gpu_sparse_20260315_101534.json` | GPU campaign results |
| `data/r88_gpu_log.txt` | GPU campaign log |
| `data/zerocore_certificate.json` | Zero-Core verification certificate |

---

## Falsification Criteria

| Claim | Falsified if... |
|-------|-----------------|
| R(8,8) > 293 is false (for this coloring) | Independent verifier shows omega(red) <= 7 AND omega(blue) <= 7 in the coloring file |
| R(8,8) > 281 | A monochromatic K_8 is found in either color of Paley(281) |
| Zero-Core Theorem | A constraint index i is found where S \ {c_i} is feasible |
| Stochastic sampling unreliable | A poly-time sampler detects K_8 cliques with high probability at n=293 |

---

## Figures

| Figure | Description |
|--------|-------------|
| `fig1_scale_comparison` | Log-scale: search space vs sampling budget |
| `fig2_paley_landscape` | Paley K_8 violation count by prime |
| `fig3_search_space_scaling` | Coverage gap grows super-exponentially with k |
| `fig4_witness_spacing` | Red K_8 witness vertices on K_293 ring + spacing analysis |
| `fig5_detection_probability` | P(miss) as function of violation count |
| `fig6_ramsey_bounds` | Diagonal Ramsey number bounds overview |
| `fig7_zero_core` | Zero-Core Theorem schematic |

---

## Connection to U24 Programme

This paper extends the Ramsey theory campaign from Papers 02 and 03 (R(5,5) bounds) to k = 8, demonstrating the methodological boundary where stochastic optimization fails.  The Zero-Core Theorem connects to the S_4 stagnation structure (Paper 17): the distributed constraint obstruction mirrors permutation-invariant energy barriers in |S_4| = 24-dimensional landscapes.

---

## Citation

```bibtex
@article{DaughertyWardRyan2026r88,
  title   = {Falsification of {R}(8,8) > 293: Exhaustive Max-Clique
             Verification and the Structural Limits of Stochastic Sampling},
  author  = {Daugherty, Bryan and Ward, Gregory and Ryan, Shawn},
  year    = {2026},
  note    = {U24 Programme Paper 14},
  url     = {https://github.com/OriginNeuralAI/Papers}
}
```
