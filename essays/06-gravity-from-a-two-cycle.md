# Gravity from a Two-Cycle

### How elements 15 and 20 of a cipher table encode the graviton.

*An accessible guide to Paper III of the Post-Millennium Programme*

*Bryan Daugherty, Gregory Ward, Shawn Ryan — March 2026*

---

On November 25, 1915, Albert Einstein presented the field equations of general relativity to the Prussian Academy of Sciences in Berlin. The equations were beautiful — ten coupled partial differential equations relating the curvature of spacetime to the distribution of matter and energy. They explained the anomalous precession of Mercury's orbit, predicted the bending of light by the Sun (confirmed by Eddington's 1919 eclipse expedition, making Einstein a global celebrity), and implied the existence of gravitational waves (detected by LIGO a century later, in 2015, earning Weiss, Barish, and Thorne the 2017 Nobel Prize).

But general relativity has a problem. It is a *classical* theory. It treats spacetime as a smooth manifold, not a quantum object. Every attempt to quantise it — to describe gravity using quantum mechanics, the way QED describes electromagnetism — has failed. The infinities that appear are not the gentle, removable infinities of QED (which Feynman, Schwinger, and Tomonaga tamed in the 1940s). They are violent, uncontrollable infinities that devour the theory.

String theory was supposed to solve this. Loop quantum gravity was supposed to solve this. Neither has produced a single testable prediction in forty years.

We found gravity in a two-cycle.

---

## The Four Basins, Four Forces

The Reeds endomorphism f: Z₂₃ → Z₂₃ has four basins:

| Basin | Name | Size | Cycle | Force |
|-------|------|------|-------|-------|
| 0 | Creation | 9 | 2→3→5→2 (period 3) | Strong (SU(3)) |
| 1 | Perception | 7 | 14→13→8→14 (period 3) | Weak (SU(2)) |
| 2 | Stability | 1 | 6→6 (fixed point) | Electromagnetic (U(1)) |
| 3 | Exchange | 6 | 15↔20 (period 2) | **Gravity** |

This mapping — basin sizes to forces — was not assumed. It was determined by matching the formulas: the fine structure constant fixes B₀ = 9 to the strong force sector, the Weinberg angle fixes B₃ = 6 to the gravitational sector, and the coupling ratio B₂/B₃ = 1/6 fixes B₂ = 1 to electromagnetism. The assignment is unique: no other permutation works.

---

## Why Basin 3 Is Gravity

The Exchange basin has three properties that match gravity precisely:

**1. Spin 2.** The graviton — the hypothetical quantum of gravity — has spin 2. This means it has two polarisation states. The Exchange cycle has period 2: element 15 maps to 20, and 20 maps back to 15. Two states, cycling between each other. The cycle period IS the spin.

Compare: the photon (Basin 2) has spin 1 and cycle period 1 (fixed point). The strong and weak forces have spin 1 but more complex cycle structures (period 3). The correspondence between cycle period and boson spin is exact.

**2. Self-duality.** In general relativity, the graviton field is symmetric: h_μν = h_νμ. The graviton is its own dual. In Z₂₃ arithmetic: 15 × 20 = 300 = 13 × 23 + 1, so 15 × 20 ≡ 1 (mod 23). Elements 15 and 20 are *multiplicative inverses*. Each is the "reverse" of the other. This is the discrete analogue of self-duality.

**3. Masslessness.** The graviton is massless — gravity propagates at the speed of light. In the Reeds structure, both elements 15 and 20 are *periodic* (they sit on the cycle, not in the transient tree). Transient elements have finite lifetime — they "decay" toward the cycle. Periodic elements are eternal. A massless particle IS an element with zero decay rate — a permanent resident of the cycle.

---

## The Coupling Ratio

How strong is gravity compared to electromagnetism? In everyday experience, EM is about 10³⁶ times stronger. But at the fundamental level — in natural units where the Planck mass is 1 — the ratio of coupling strengths is much simpler:

**g²_EM / g²_grav = |Basin 2| / |Basin 3| = 1/6**

This is the ratio of basin sizes: 1 element (the photon's basin) to 6 elements (gravity's basin). The enormous hierarchy in everyday units (10³⁶) arises from dimensional transmutation — the conversion from natural to SI units through the Planck mass. But at the basin level, gravity is simply 6 times the unit coupling.

---

## Dark Energy: A Theorem, Not a Fit

The dark energy equation of state w tells you how dark energy behaves. If w = −1, it's a cosmological constant (Einstein's Λ). If w > −1, it's "quintessence" — dynamic, evolving. DESI's 2024 measurements hint at w ≈ −0.83, suggesting dark energy is NOT a constant.

Our prediction: **w = −5/6 = −0.8333...**

This is not a fit to data. It is a **proved theorem** of group theory:

The symmetric group S₄ has a composition series {e} ◁ V₄ ◁ A₄ ◁ S₄. The index of V₄ in S₄ is [S₄:V₄] = 24/4 = 6. This gives the effective dimension d = 6 (matching the 6 compactified dimensions in string theory). Then:

w = −(d−1)/d = −(6−1)/6 = **−5/6**

No fitting. No free parameters. No physics input beyond the S₄ group structure. The dark energy equation of state is determined by the index of the Klein four-group in the symmetric group on four elements.

DESI Year 5 (~2029) will test this to < 3% precision. If w is confirmed at −0.833, it will be the first cosmological parameter derived from pure mathematics.

The history of dark energy is worth recounting. In 1998, two teams — the Supernova Cosmology Project (led by Saul Perlmutter at Berkeley) and the High-Z Supernova Search Team (led by Brian Schmidt and Adam Riess) — independently discovered that the expansion of the universe is *accelerating*. Distant supernovae were dimmer than expected, meaning they were farther away, meaning the expansion was speeding up. This was supposed to be impossible. Einstein had introduced a "cosmological constant" Λ in 1917 to keep the universe static, then called it "my greatest blunder" when Hubble showed the universe was expanding. Perlmutter, Schmidt, and Riess shared the 2011 Nobel Prize for showing that Einstein's "blunder" was actually real — but they couldn't say what Λ *is*.

DESI's 2024 data hints that dark energy is not constant (w ≠ −1) but evolving. Our w = −5/6 is consistent with this: it's quintessence, not Λ. If confirmed, it would mean dark energy is not a mysterious substance but a group-theoretic index.

---

## Black Holes and the Monster

The conformal central charge c = 24 is proved unique by the intersection of three constraints (Hellerman unitarity, T_c matching, S₄ compatibility). Via the Cardy formula:

**S = 2π√(cE₀/6) = 4π√E₀**

this gives the Bekenstein-Hawking entropy of a black hole. The same c = 24 that appears in the Monster group's vertex operator algebra governs the thermodynamics of black holes. Witten conjectured this connection in 2007. Our work provides independent confirmation: c = 24 is not assumed but forced.

---

## The Non-Polynomial Gap

A striking numerical identity with no known explanation:

**24 − 9 = 15 = number of supersingular primes**

The universality product Ω = 24. The best polynomial approximation to the Reeds map gives Ω_poly = 9. The gap is 15 — which happens to equal the number of primes that divide the Monster group's order.

This connects three independent mathematical domains (finite maps, polynomial approximation, sporadic group theory) through a single integer. Nobody has proved *why* these are equal. The identity is verified computationally but remains one of the deepest open questions in the programme.

---

## Why It Matters

For a century, quantum gravity has been the holy grail of theoretical physics. Every approach — string theory, loop quantum gravity, causal set theory — requires additional structure beyond the Standard Model.

The Reeds endomorphism provides gravity from the SAME structure that gives the other three forces. No extra dimensions (they're implicit in d = 6). No extra particles. No extra fields. Just Basin 3, with its 2-cycle, its self-duality, and its coupling ratio 1/6.

Whether this is a deep truth or a remarkable coincidence is for experiment to decide. The predictions are specific and falsifiable. The w = −5/6 test comes first — in approximately three years.

---

*Based on Paper III. 15 pages, 56/56 checks. Full paper and code at [github.com/OriginNeuralAI/Papers](https://github.com/OriginNeuralAI/Papers).*
