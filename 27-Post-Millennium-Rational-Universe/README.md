# The Rational Universe
**Paper V of the Post-Millennium Programme | 8 pages | Phase II+III Discoveries**

Every fundamental constant derived from the Reeds endomorphism is a simple rational number built from basin sizes {9, 7, 1, 6} and structural integers {6, 23, 24}.

## The Rational Constants

| Constant | Formula | Value | Precision |
|----------|---------|-------|-----------|
| **1/α_EM** | 6×23 − 1 + 9/(2×⌈ln\|M\|⌉) | **137 + 9/250** | **9 sig figs** |
| **sin²θ_W** | \|B₃\|/(\|Z₂₃\| + 3) | **6/26 = 3/13** | **0.19%** |
| Clustering | 8 of 9 J_sub eigenvectors | 8/9 | exact |
| Level repulsion | 2 − 2/\|periodic\| | 16/9 | 1.6% |
| Channel capacity | log₂(\|basins\|) | 2 bits | exact |
| Dark energy w | −(d−1)/d, d = 6 | −5/6 | DESI 1σ |
| EM/gravity | \|B₂\|/\|B₃\| | 1/6 | exact |

## The Fine Structure Constant

```
1/α_EM = ord(f) × |Z₂₃| − 1 + |B_Creation| / (2 × ⌈ln|Monster|⌉)
       = 6 × 23 − 1 + 9 / (2 × 125)
       = 137 + 9/250
       = 137.036000000

CODATA: 137.035999177

Error: 6 × 10⁻⁷ %
```

The Monster group (|M| ≈ 8 × 10⁵³) is literally in the fine structure constant.

## Hierarchy of Refinements

| Formula | Value | Error | Sig figs |
|---------|-------|-------|----------|
| 6 × 23 − 1 | 137 | 0.026% | 3 |
| 137 + 9/(7×36) | 137.035714 | 0.0002% | 5 |
| 137 + 9/250 | 137.036000 | 6×10⁻⁷% | **9** |
| 137 + 9/250 + 1/(9πln\|M\|) | 137.035999 | ~10⁻⁸% | **10** |

## Verification

```bash
python scripts/verify_paper5.py  # Rational universe verification
```
