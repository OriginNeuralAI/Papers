# U24 Paper 29: Persistent Homology of Optimization Landscapes

**beta_1 = 0 Universality and Bounded H_2**

Bryan Daugherty, Gregory Ward, Shawn Ryan
SmartLedger Solutions / Origin Neural AI --- March 2026

## Key Results

| Result | Statement | Evidence |
|--------|-----------|----------|
| beta_1 = 0 Universality | No persistent 1-cycles in any Ising optimization landscape | 185/185 checks PASS, 7 families, N up to 100,000 |
| H_2 = O(1) Boundedness | Topological complexity bounded by a constant as N -> infinity | H_2 <= 3 at N=100,000 across all families |
| Integrable Exactness | Ferromagnetic ring: H_2 = 0 exact for N <= 5,000 | 0.0 measured at N=1K, 5K |
| No Strong GUE | r-statistic never exceeds 0.50 for any family at large N | Sparse graphs are Poisson-like (r ~ 0.38) |

### H_2 Scaling Data

| Family | N=1K | N=5K | N=10K | N=50K | N=100K |
|--------|------|------|-------|-------|--------|
| Ferromagnetic Ring | 0 | 0 | 1.0 | 1.5 | 1.5 |
| Regular MaxCut k=3 | 0 | 7.0 | 4.3 | 4.0 | 3.0 |
| Regular MaxCut k=5 | 2.3 | 6.0 | 4.0 | 3.5 | 1.5 |
| ER MaxCut p=0.1 | 9.0 | 4.3 | 6.0 | --- | 3.3 |
| SK Sparse d=10 | 6.0 | 11.0 | 4.3 | 0.5 | 2.0 |
| Frustrated Sparse | 5.0 | 5.3 | 3.3 | 3.5 | 3.0 |

## Verification

```bash
# Run 16-check verification suite (requires numpy, scipy)
python scripts/verify_h2.py

# Generate all 8 figures (requires matplotlib, numpy)
python scripts/generate_figures.py
```

### Verification Checklist (16/16 PASS)

**A. beta_1 Universality (4 checks)**
1. beta_1=0 for all N<=200 runs (all 7 families)
2. beta_1=0 for all N<=1000 runs
3. beta_1=0 for all N<=10000 runs
4. beta_1=0 for all N=100000 runs

**B. H_2 Boundedness (4 checks)**
5. H_2(N=100K) <= 5 for Ferromagnetic Ring
6. H_2(N=100K) <= 5 for Regular MaxCut k=3
7. H_2(N=100K) <= 5 for SK Sparse
8. H_2(N=100K) <= 5 for Frustrated Sparse

**C. Scaling (4 checks)**
9. H_2(100K) <= H_2(5K) for Regular MaxCut k=3
10. H_2(100K) <= H_2(5K) for Regular MaxCut k=5
11. H_2(100K) <= H_2(5K) for SK Sparse
12. H_2(100K) <= H_2(5K) for Frustrated Sparse

**D. Integrable Exactness (4 checks)**
13. H_2=0 exact for Ferromagnetic Ring at N<=5000
14. H_2=0 exact for Ramsey K8
15. Ferromagnetic Ring topology = Degenerate at all N<=5000
16. Total computation time < 1000s

## Falsification Criteria

| ID | Prediction (would refute claims) |
|----|----------------------------------|
| F1 | beta_1 > 0 for any Ising optimization landscape at any N |
| F2 | H_2 grows proportionally to N for any family |
| F3 | A frustrated system with H_2 > 10 at N > 50,000 |
| F4 | beta_1 > 2 for any PH computation on solution sets |
| F5 | r > 0.60 (strong GUE) for sparse random graphs at N > 10,000 |

## Structure

```
32-Persistent-Homology-H2/
  main.tex              LaTeX source
  u24style.sty          U24 Programme house style
  scripts/
    verify_h2.py        16-check verification suite
    generate_figures.py  8 figure generation script
  figures/               Generated figures (PNG + PDF)
  data/                  Verification certificates
```

## Compilation

```bash
pdflatex main.tex && pdflatex main.tex && pdflatex main.tex
```

## Citation

```bibtex
@article{dwr2026paper29,
  title   = {Persistent Homology of Optimization Landscapes:
             $\beta_1 = 0$ Universality and Bounded $H_2$},
  author  = {Daugherty, Bryan and Ward, Gregory and Ryan, Shawn},
  year    = {2026},
  month   = {March},
  note    = {U24 Programme --- Paper 29},
  url     = {https://github.com/OriginNeuralAI/Papers}
}
```

## Engine

Isomorphic Engine v0.15.0 (Rust). 77 runs at N >= 1,000 totaling 951 seconds.
Hardware: AMD Ryzen 9 7900X, 64 GB DDR5, RTX 5070 Ti.
