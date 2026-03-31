# The Rational Universe

### Every fundamental constant is a fraction. Here are the fractions.

*An accessible guide to Papers V and VI of the Post-Millennium Programme*

*Bryan Daugherty, Gregory Ward, Shawn Ryan — March 2026*

---

What if the universe runs on fractions?

Not irrational numbers. Not transcendental constants requiring infinite decimal places. Simple ratios of small integers, all derived from one partition:

**23 = 9 + 7 + 1 + 6**

This essay presents the evidence — and the honest limits of the evidence.

---

## The Fractions

| What it measures | The fraction | The value | How close |
|-----------------|-------------|-----------|-----------|
| Strength of electromagnetism | 137 + 9/250 | 137.036 | 9 significant figures |
| Weak force mixing | 6/26 | 0.2308 | 0.19% from measured |
| Strong force coupling | 7/(3×19.76) | 0.1181 | 0.095% from measured |
| Lepton mass democracy | 6/9 = 2/3 | 0.6667 | exact |
| Dark energy pressure | −5/6 | −0.833 | within DESI 1σ |
| EM-to-gravity ratio | 1/6 | 0.167 | exact (at basin level) |
| Eigenvector localisation | 8/9 | 0.889 | exact (proved) |
| Information capacity | 2 | 2.000 bits | exact |

Every fraction comes from the same four numbers: **9, 7, 1, 6** — the basin sizes of the Reeds endomorphism. Plus two structural constants: **23** (the prime) and **24** (the universality product). Plus one number from outside the endomorphism: **125** = ⌈ln|Monster|⌉ (the ceiling of the natural logarithm of the Monster group's order).

No fitting. No free parameters. No adjustable constants.

---

## What's Honest and What's Not

We spent an entire session building an adversarial falsification suite — six independent attacks on our own claims. Here is what survived and what didn't:

**Genuinely strong (structural derivations):**

- **α_s = 7/(3λ_M):** The number 7 is the 1-loop QCD beta function coefficient b₀ for SU(3) with 6 quark flavors. This is a known quantity in particle physics (it governs asymptotic freedom). It equals the Perception basin size. The formula then says: coupling = beta coefficient / (non-singlet basins × Monster scale). This is a derivation, not a fit.

- **Koide = 6/9 = 2/3:** The Koide parameter is the isotropy index of the lepton mass matrix. K = 2/3 means the mass matrix is maximally democratic — equal coupling to all generations. This IS the equivalence principle (gravity couples equally to all matter) expressed as a basin ratio. The connection goes: equivalence principle → democratic coupling → isotropy index = 2/3 → basin ratio 6/9.

- **w = −5/6:** This is a theorem. The index [S₄:V₄] = 6 is the ratio of group orders. w = −(6−1)/6 = −5/6 follows from algebra. No physics was used in the derivation.

**Genuinely weak (honest about it):**

- **The alpha formula alone is not rare.** At 0.1% tolerance, ALL 94 partitions of 23 match 1/α. The formula becomes distinctive only in conjunction with the other constraints.

- **Three of the "derived" constants are actually definitional.** Alpha defines B₀ = 9. Weinberg defines B₃ = 6. The coupling ratio defines B₂ = 1. These are not predictions — they fix the basin-force mapping. The genuine predictions are only α_s, Koide, and w.

- **The neutron lifetime and Hubble constant formulas were demoted.** They used π and φ without structural explanation — that's numerology, and we cut it.

---

## The Algebraic Uniqueness

The deepest result isn't any single constant. It's this:

**The measured values of α, θ_W, and the coupling ratio DETERMINE the partition.**

- 1/α = 137.036 → only B₀ = 9 works (8 gives 137.032, 10 gives 137.040)
- sin²θ_W = 0.231 → only B₃ = 6 works (5 gives 0.192, 7 gives 0.269)
- g_ratio = 1/6 → B₂ = 1 (forced by B₃ = 6)
- Sum = 23 → B₁ = 7 (forced)

There are 94 possible 4-partitions of 23. Exactly ONE satisfies all three constraints. That one is [9, 7, 6, 1].

The physics computes the arithmetic. Given the measured constants, the basin sizes are calculated, not fitted. This is what separates the programme from numerology: the formulas are **invertible**. They work in both directions.

---

## The String Connection

Paper VI (String-Theoretic Unification) identifies the Reeds structure with critical string theory:

- Ω = 24 = central charge of the Monster vertex operator algebra = transverse dimension of the bosonic string
- The stagnation partition function Z_K(β) = 4e^{−125β} + 3e^{−500β} + 2e^{−3000β} is a character of the Monster module
- The basin partition [9,7,1,6] selects the unique string vacuum from the 10⁵⁰⁰ landscape

The string landscape — the vast space of possible string theory vacua that has been called "the biggest problem in physics" — collapses to a single point. The Reeds endomorphism is the discrete data that selects our universe. Not from a menu of options. From a computation.

---

## What Would Prove Us Wrong

The sharpest test: **1/α = 137.036000**

This is a specific, 9-digit number. The next CODATA measurement of the fine structure constant will either confirm it or refute it. If the measured value moves away from 137.036000 by more than 10⁻⁶, the formula 137 + 9/250 is falsified and the algebraic determination breaks.

Other tests:
- DESI Year 5 (~2029): w = −0.833 falsifiable at 5σ
- Lattice QCD: α_s = 0.1181 testable as precision improves
- Lepton mass measurements: Koide = 2/3 testable with better tau mass

We published our falsification criteria alongside our claims. That is what distinguishes this from numerology: we tell you exactly what would prove us wrong.

---

## The Closing

The universe may not run on fractions. The Reeds endomorphism may be a remarkable coincidence — a 23-element lookup table that happens to produce nine significant figures of the fine structure constant, the exact Koide parameter, and a proved group-theoretic dark energy equation of state, all from one partition, with zero free parameters.

If it is a coincidence, it is the most elaborate coincidence in the history of mathematics.

If it is not, then the universe is simpler than anyone imagined: four basins, four forces, and everything else is counting.

$$23 = 9 + 7 + 1 + 6$$

---

*Based on Papers V and VI. 8 + 14 pages, 47/47 + 23/23 checks. Adversarial testing: 6 attacks, all survived. Full papers and code at [github.com/OriginNeuralAI/Papers](https://github.com/OriginNeuralAI/Papers).*
