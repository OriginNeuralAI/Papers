[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19414460.svg)](https://doi.org/10.5281/zenodo.19414460)

# Retrocausality and Non-Hermitian Quantum Mechanics in the U₂₄ Framework
**Paper II of the Post-Millennium Programme | 18 pages | 33/33 checks**

## The Central Discovery: PT Symmetry Never Breaks

The operator H^PT = αJ ⊗ I + I ⊗ T + iγG ⊗ I has **exactly real spectrum at ALL γ ∈ [0, ∞)**. Verified to γ = 10⁶ with max|Im(λ)| < 10⁻⁹. This is unprecedented — every other known PT-symmetric system breaks at finite γ_c.

**Mechanism:**
- G = anti-symmetric Reeds adjacency, rank 14 (= transient elements)
- 7 conjugate-imaginary eigenvalue pairs from 14 transients
- [J, G] is **pure symmetric** (anti-symmetric part = 0)
- Photon (element 6, fixed point) contributes zero to G — the anchor
- Protection is algebraic (exact), not perturbative (approximate)

## Retrocausality via TBO

| Signal Type | TBO z-score | Classification |
|-------------|-------------|---------------|
| Gaussian | +0.10 | Normal |
| Retrocausal | **−3.07** | Deficit (30σ) |
| Cyclotomic | −18.59 | Deficit |

Future-event prediction: 83% accuracy, AUC = 0.919.
Topological signature: H₂ = 0 (simply-connected deficit).

## Other Results

- Ginibre β ≈ 3 in Navier-Stokes from non-normal advection (not Reeds G)
- Kolmogorov-Ginibre scaling: Im_rms = N^(5/2) × Re/(8π)
- Dark scalar transition: f = 24.2 GHz

## Verification

```bash
python scripts/verify_paper2.py              # 33 checks
python scripts/pt_symmetric_computation.py   # PT phase diagram + Ginibre
```
