# The Arrow of Time, Entanglement Structure, and the Measurement Problem
**Paper I of the Post-Millennium Programme | 34 pages | 74/74 checks**

From the basin topology of the Reeds endomorphism f: Z₂₃ → Z₂₃, we derive three foundational results in quantum mechanics with zero free parameters:

## Key Results

| Result | Value | Precision |
|--------|-------|-----------|
| Born rule | P(k) = \|B_k\|/23 | error 10⁻⁴ on 10⁷ samples |
| Eigenvector clustering | 8/9 = 88.9% | **exact** (scale-invariant, proved) |
| Spectral hierarchy | β_cycle = 1.75, β_trans = 1.04 | all N = 50–1500 |
| Gaussian dome | N* = 563, width = 522 | fitted |
| Photon fidelity | 1.0000000000 | 10 decimal places |
| Decoherence ratio | Γ₁/Γ₂ = 2340 | exact |
| Entanglement bound | S_E ≤ 1.36 nats | from J spectral gap |

## The 8/9 Theorem

Exactly 8 of 9 eigenvectors of J_sub (the cycle-sector coupling matrix) localise on single basins. The non-localising eigenvector #7 is the symmetric Creation–Perception mixture (shared period 3). Since H = J_sub ⊗ I + I ⊗ T, eigenvectors are independent of N — scale-invariance is a theorem, not an observation.

## Historical Context

44 references spanning Einstein (1935) → Bohm (1952) → Bell (1964) → Berry-Tabor (1977) → BGS (1984) → Connes (1994) → Zurek (2003) → 't Hooft (2016) → Hossenfelder (2020) → Reeds (2026).

## Verification

```bash
python scripts/verify_paper1.py        # 52 algebraic checks
python scripts/high_dim_computation.py  # 6 experiments to dim 34,500
python scripts/coupling_sweep.py       # alpha sweep + N-scaling
python scripts/decisive_test.py        # basin clustering + asymptotic beta
python scripts/phase2_quick_wins.py    # Q2 (8/9), Q5 (PMNS), Q8 (2 bits)
python scripts/q6b_alpha_em_6th_digit.py  # alpha_EM + Weinberg + 8/9 proof
```

Matrices diagonalised up to 34,500 × 34,500 on RTX 5070 Ti.
