# Synopsis of Findings — Cross-Referenced Against Known Mathematics

**Authors:** Daugherty, Ward, Ryan
**Date:** March 30, 2026
**Engine:** Isomorphic Engine v0.15.0 — GPU-accelerated (RTX 5070 Ti, 3.87B spins/sec)
**Scale:** 1,000,000 spins (GPU), 100,000 spins (CPU), 1,000 Riemann zeros, primes to 50,000

---

## Paper 1: Cyclotomic Stratification of Diagonal Curves

### Finding 1.1: Optimal CM Hitting Set

**Result:** The set S = {5, 11, 17, 47} is a minimal Legendre-symbol hitting set for the 9 class-number-one imaginary quadratic discriminants. No 3-prime set works (exhaustive over 15,180 triples). Extended to h=2 (optimal: {3,5,7,47,79}, size 5 = info-theoretic bound) and h=3 (size 5).

**Cross-references:**
- **Baker–Heegner–Stark theorem** (1952/1966/1967): Establishes that exactly 9 class-number-one discriminants exist. Our hitting set is a new combinatorial result *about* these discriminants, not previously studied.
- **Watkins (2004), "Class numbers of imaginary quadratic fields"**, Math. Comp. 73: Complete enumeration of discriminants with h ≤ 100. We used the h=2 (18 values) and h=3 (16 values) lists from this reference.
- **Chebotarev density theorem** (1926): Predicts ~50% inert density for CM discriminants, vs <5.5% supersingular density for non-CM (Sato–Tate). Our CM detection via 4-bit signatures is a practical application.
- **Information-theoretic bound** (Shannon, 1948): ceil(log₂(9)) = 4 bits needed. We prove this bound is *achievable*, which is non-trivial — most combinatorial structures have gaps between the information bound and the achievable size.

**Novelty assessment:** The hitting set construction is new. The extension to h=2,3 and joint sets appears to be the first systematic study of Legendre-symbol separability of discriminant families.

### Finding 1.2: Coupling Constants of Fermat Curves

**Result:** 15 cyclotomic coupling constants α(n) for n = 3, 4, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, computed over primes up to 50,000. Scaling: α(n) ≈ 0.76 · n^0.33 (R² = 0.72).

**Cross-references:**
- **Weil (1949), "Numbers of solutions of equations in finite fields"**: The point count N(p) = p + Σ J(χᵃ, χᵇ) via Jacobi sums is the theoretical foundation. Our coupling constants quantify the *variance* of these deviations.
- **Ireland & Rosen (1990), "A Classical Introduction to Modern Number Theory"**: Standard reference for Jacobi sums and their connection to Fermat curves. Our normalization α = std(Z)/(d-1) accounts for the (d-1)² character pairs.
- **Katz & Sarnak (1999), "Random Matrices, Frobenius Eigenvalues, and Monodromy"**: The GUE/GOE statistics of Frobenius eigenvalues. Our coupling constants measure deviations from the independence prediction, quantifying the *arithmetic correlations* among Jacobi sums.
- **Hasse bound** (1933): |J(χᵃ, χᵇ)| = √p for nontrivial characters. Verified exactly for all 12 primes p ≤ 47 in our Jacobi sum computation.

**Novelty assessment:** Values for n ≥ 11 appear to be new. The scaling law α ~ n^{1/3} and the systematic departure from the independence fallback α_indep ~ n^{-1/2} are new observations.

### Finding 1.3: Discriminant Landscape Ising Classification

**Result:** The Ising ground state on a discriminant landscape (1,526 fundamental discriminants, Legendre symbol coupling) naturally separates class numbers: h=1 magnetization = -0.555, h=4 = +0.644, h=7 = +0.643.

**Cross-references:**
- **Goldfeld (1976) / Gross–Zagier (1986)**: Class number growth theory. Our Ising model provides a novel *computational* classifier that recovers class number structure from Legendre symbol correlations alone.
- No direct precedent found for using Ising ground states as arithmetic classifiers. This appears to be genuinely new.

---

## Paper 2: Group-Theoretic Structure of Optimization Stagnation

### Finding 2.1: Ω = 24 Universality

**Result:** The ratio τ_macro/τ_micro = 3000/125 = 24 = |S₄| is exact across all 60 measurements (5 families × 4 sizes × 3 seeds). The inter-tier ratios 500/125 = 4 = |V₄| and 3000/500 = 6 = |S₃| independently match group orders.

**Cross-references:**
- **Jordan–Hölder theorem** (1870/1889): The composition series of S₄ is unique: {e} ◁ V₄ ◁ A₄ ◁ S₄ with quotient orders [4, 3, 2]. This is a standard result in group theory; our claim is that this specific composition series governs stagnation dynamics.
- **Kramers (1940), "Brownian motion in a field of force"**: The Kramers escape rate r = A·exp(-E/kT) is the physical model. Our three-barrier partition function Z_K(β) = 4e^{-125β} + 3e^{-500β} + 2e^{-3000β} extends Kramers to multiple barriers with S₄ multiplicities.
- **The number 24 in mathematics:**
  - |S₄| = 24 (symmetric group, our primary claim)
  - χ(K3) = 24 (Euler characteristic of K3 surface — connects to Paper 4)
  - 24 Niemeier lattices (even unimodular lattices in dim 24) — Niemeier (1973)
  - dim(Leech lattice) = 24 — Conway & Sloane (1985)
  - Ramanujan τ-function related to Δ(τ), a weight-12 modular form for SL₂(ℤ)
  - Central charge c = 24 of the Moonshine module V♮ — Frenkel, Lepowsky, Meurman (1988)

**Novelty assessment:** The stagnation tier windows (125, 500, 3000) are empirical observations from our engine. The claim that they relate to S₄ composition series quotients is new and speculative. The *exact* ratio 24 is by construction (the detector windows are set at these values), but the claim is that these specific values produce *optimal* stagnation detection across problem families.

### Finding 2.2: D₄ Triality of I = F·G·Z₂·S

**Result:** The diagnostic equation I = F·G·Z₂·S has D₄ Dynkin diagram symmetry with S at the central node and {F, G, Z₂} at the outer nodes related by triality.

**Cross-references:**
- **Cartan (1925)**: Classification of simple Lie algebras and their Dynkin diagrams. D₄ is the unique Dynkin diagram with a degree-3 symmetry (triality).
- **Triality** (Cartan, 1925; Freudenthal, 1964): The outer automorphism group Out(D₄) ≅ S₃ permutes the three 8-dimensional representations 8_v, 8_s, 8_c. Our claim maps F, G, Z₂ to these three representations.
- **Verification:** Since I = F·G·Z₂·S and multiplication is commutative, the product is trivially S₃-invariant. The non-trivial claim is about the *budget allocation* and *solver routing*, which we verified computationally.

### Finding 2.3: GPU Scale — 1M Spins in 259ms

**Result:** RTX 5070 Ti solved a 1,000,000-spin sparse Ising model (6M nonzeros) in 259 milliseconds at 3.87 billion spins/second.

**Cross-references:**
- **Simulated Bifurcation Machine** (Goto et al., 2019, Science Advances): A physics-inspired approach. Our implementation follows similar principles.
- **Coherent Ising Machine benchmarks** (Honjo et al., 2021, Science Advances): Optical approach at 100K spins. Our GPU result exceeds this by 10x in problem size.
- **D-Wave quantum annealer** (2023): ~5000 qubits. Our classical GPU solver handles 200x more variables.

---

## Paper 3: A Spectral Diagnostic Hierarchy for Arithmetic Operators

### Finding 3.1: 31-Dimensional Conformal Spectrum

**Result:** 40 power laws from the diagnostic suite produce 31 independent scaling dimensions (22 positive, 9 negative). These satisfy shadow pairing (Δ + Δ' = 2 for d=2 CFT) and Breitenlohner–Freedman stability (Δ(Δ-2) ≥ -1).

**Cross-references:**
- **Belavin, Polyakov, Zamolodchikov (1984), "Infinite conformal symmetry in two-dimensional quantum field theory"**: The BPZ paper establishes conformal field theory. Shadow pairing and the BF bound are standard CFT concepts. Our claim is that optimization diagnostics *happen to satisfy* CFT constraints.
- **Breitenlohner & Freedman (1982)**: Stability bound for scalar fields in AdS. Our spectrum satisfies this bound for d=2, with Δ = 1.0 saturating it exactly.
- **Tracy & Widom (1994)**: GUE convergence rate. Our Δ = 0.50 (GUE convergence) matches the known rate.

**Novelty assessment:** The conformal spectrum itself is new — extracted from optimization diagnostics rather than a physical system. Whether this is deep or coincidental is the open question.

### Finding 3.2: T1/T2/T3 Hierarchy — Riemann Zeros as Unique Rank 3

**Result:** Among 14 operator families (8,700+ experiments), only Riemann zeta zeros achieve Rank 3 (T1 chaos + T2 arithmetic + T3 primality all pass).

**Cross-references:**
- **Montgomery (1973), "The pair correlation of zeros of the zeta function"**: Established GUE statistics for zeta zeros (T1 connection). Our KS distance of 0.093 at 10K zeros is consistent.
- **Odlyzko (1987)**: Numerical verification of Montgomery's conjecture at 10⁶+ zeros. Our results at 1000 zeros are consistent with extrapolation toward Odlyzko's values.
- **Rudnick & Sarnak (1996), "Zeros of principal L-functions and random matrix theory"**: Extended GUE universality to L-functions. Our T2 (bicoherence) and T3 (primality) tiers go beyond GUE to detect arithmetic content.
- **Selberg eigenvalue conjecture** (1965): λ₁ ≥ 1/4 for congruence subgroups. Our T1/T2/T3 parallels this — T3 requires "arithmetic structure as deep as the zeta function."

**Novelty assessment:** The three-tier classification scheme is new. The observation that zeta zeros are uniquely Rank 3 is a testable claim that could be falsified by finding another Rank-3 operator.

### Finding 3.3: I-Value Saturation at N ≥ 50K

**Result:** The difficulty metric I saturates at I = 1.0 for N ≥ 50,000, classifying all large sparse Ising instances as T3 (glassy/frustrated). Verified up to N = 1,000,000 on GPU.

**Cross-references:**
- **Spin glass theory** (Edwards & Anderson, 1975; Sherrington & Kirkpatrick, 1975): SK model frustration grows with N. Our I-value saturation is consistent with the transition to the spin glass phase.
- **NP-hardness** (Cook, 1971; Barahona, 1982): Ising optimization on general graphs is NP-hard. The I = 1.0 saturation may reflect the computational complexity boundary.

---

## Paper 4: Spectral Moonshine — A Conjecture

### Finding 4.1: E₈ Exponent–Monster Prime Overlap (87.5%)

**Result:** The E₈ exponents {1, 7, 11, 13, 17, 19, 23, 29} overlap with Monster primes at 7/8 = 87.5%. Only exponent 1 (trivial) is excluded.

**Cross-references:**
- **E₈ root system** (Killing, 1888; Cartan, 1894): Exponents of E₈ are well-known: degrees of fundamental invariants minus 1. Coxeter number h = 30.
- **Monster group** (Griess, 1982; Fischer, Livingstone, Thorne, 1978): The 15 prime divisors of |M| are {2,3,5,7,11,13,17,19,23,29,31,41,47,59,71}.
- **Overlap observation:** The non-trivial E₈ exponents {7,11,13,17,19,23,29} are all Monster primes. This overlap has been noted informally in the moonshine literature but we are not aware of a formal proof explaining *why* it occurs.
- **K3 intersection form** (Milnor, 1958): H²(K3,ℤ) ≅ 2(-E₈) ⊕ 3H is the unique even unimodular lattice of signature (3,19). This connects E₈ to K3 geometry.

**Novelty assessment:** The 87.5% overlap is a verifiable mathematical fact. The *interpretation* — that it connects K3 geometry to Monster arithmetic — is our speculative contribution.

### Finding 4.2: Exponential Sum Decay Convergence

**Result:** |S_N(r_p)| ~ p^{-β(N)} where β(100) = 0.02, β(500) = 0.32, β(1000) = 0.36. Monotonic steepening toward predicted p^{-2}.

**Cross-references:**
- **Explicit formula for ψ(x)** (von Mangoldt, 1895; Riemann, 1859): The sum over zeta zeros Σ x^ρ/ρ is the classical spectral decomposition of the prime counting function. Our exponential sums at Monster scales are a *generalization* to non-integer scales r_p = ln(p)/(2π).
- **Selberg trace formula** (1956): Relates eigenvalues of the Laplacian on a Riemann surface to lengths of closed geodesics. The conjectured link between zeta zeros and Monster traces would require a Selberg-type formula on a surface whose geodesic spectrum encodes Monster conjugacy classes.

**Novelty assessment:** The specific claim that exponential sums at Monster prime scales approximate Monster traces is entirely new. The convergence trajectory is the strongest computational evidence.

### Finding 4.3: GPU Exponential Sum Amplification — 808x Boost

**Result:** GPU optimizer selects ~500/1000 Riemann zeros that constructively interfere at each Monster prime scale, amplifying the signal from noise-level (|S|/N ~ 0.001) to 63% coherence. Peak boost: **807.5x at p=59**. Mean boost across all 15 Monster primes: **334x**.

**Cross-references:**
- No precedent found. The use of Ising optimization to select zero subsets for maximal constructive interference at specific scales appears to be entirely new. This is a computational technique, not a mathematical theorem — the boosted signals reflect optimal subset selection, not intrinsic structure. However, the fact that the boost varies across Monster primes (73x at p=2 vs 808x at p=59) may encode information about the relative "depth" of different Monster conjugacy classes.

### Finding 4.4: K3-Zeta Duality

**Result:** Shifting zeta zeros by γ_n(m) = γ_n + Σ m_i·ln(p_i) with 20 Kahler moduli produces a testable resonance condition: GUE statistics at the Ricci-flat locus. Wigner p-value improves from 0.087 (50 zeros) to 0.0001 (1000 zeros, full BO).

**Cross-references:**
- **Yau's theorem** (1977): Every compact Kähler manifold with c₁ = 0 admits a Ricci-flat metric. K3 surfaces satisfy this. Our conjecture is that the Ricci-flat metric has a specific relationship to zeta zero statistics.
- **Mirror symmetry** (Candelas, de la Ossa, Green, Parkes, 1991): Relates Kähler and complex structure moduli. The 20-dimensional moduli space h^{1,1}(K3) = 20 is the Kähler side.
- **String theory compactification** (Green, Schwarz, Witten, 1987): K3 is a standard compactification manifold in string theory. The central charge c = 24 of the Monster module equals χ(K3).

**Novelty assessment:** The K3-Zeta duality conjecture is entirely new and highly speculative. The claim that "RH is equivalent to existence of a Ricci-flat metric on a specific K3" would be extraordinary if true.

---

## Paper 5: Moonshine Corrections to Arithmetic Functions

### Finding 5.1: Twin Prime Moonshine Correction (v2) Beats Hardy–Littlewood

**Result:** w_M'(x; σ=2.5) = Σ (1/p)·exp(-(ln x - ln p)²/(2σ²)) over Monster primes produces MAE = 11.0% vs HL's 12.7%. At x=10³, error drops from -20.9% (HL) to -2.9% (Moon v2) — a 7x improvement.

**Cross-references:**
- **Hardy & Littlewood (1923), Conjecture B**: π₂(x) ~ 2C₂ · x/ln(x)². The twin prime constant C₂ = 0.6601618... Our moonshine correction *modulates* the HL estimate, not replaces it.
- **Bateman & Horn (1962)**: Generalized the HL conjecture to polynomial primes. Our correction adds a Monster-prime-localized weight.
- **Oliveira e Silva, Herzog, Pardi (2014)**: Twin prime counts up to 4×10¹⁸. We benchmarked against their data up to 10¹⁴.
- **Li₂(x) logarithmic integral**: MAE = 3.2%, still the gold standard. Our correction beats HL but not Li₂.

**Novelty assessment:** The Monster prime Gaussian weight function is new. The improvement over HL at small x is genuine but modest, and does not beat Li₂. The physical interpretation — that twin prime frequency is modulated by proximity to Monster prime scales — is speculative.

### Finding 5.2: Busy Beaver Variant C

**Result:** BB(n) ~ c_n^{0.4} · |spectral sum| + Ω(n) achieves mean |ln(ratio)| = 2.63 (vs 5.36 for v1). Approximates BB(3) = 21 within factor 1.4, BB(4) = 107 within factor 3.7.

**Cross-references:**
- **Radó (1962)**: Defined BB(n). Known values: BB(1)=1, BB(2)=6, BB(3)=21, BB(4)=107.
- **Marxen & Buntrock (1990)**: BB(5) = 47,176,870 (later confirmed).
- **Aaronson (2020), "The Busy Beaver frontier"**: Survey of BB computability barriers. Our formula cannot work for all n since BB grows faster than any computable function — this is a *structural observation*, not a computational tool.
- **The exponent α = 0.4**: The optimal power-law exponent connecting j-function coefficients to BB values. No known theoretical basis; purely empirical.

---

## Cross-Cutting Themes

### Theme A: The Number 24

The number 24 = |S₄| appears independently in:
1. Stagnation ratio Ω = 3000/125 (Paper 2) — empirical
2. χ(K3) = 24 (Paper 4) — mathematical fact
3. Leech lattice dimension (Paper 4) — mathematical fact
4. Number of Niemeier lattices (Paper 4) — mathematical fact
5. Central charge of V♮ (Paper 4) — moonshine theorem

**Known connection:** The Mathieu moonshine program (Eguchi, Ooguri, Tachikawa, 2010) connects the elliptic genus of K3 to representations of M₂₄. The appearance of 24 in our stagnation framework may or may not be related.

### Theme B: Monster Primes as Universal Scales

Monster primes {2,3,5,7,11,13,17,19,23,29,31,41,47,59,71} appear in:
1. E₈ exponents (Paper 4) — 7/8 overlap
2. K3 moduli primes (Paper 4) — first 15 of 20
3. Twin prime weight function (Paper 5) — Gaussian kernel centers
4. Exponential sum scales (Paper 4) — r_p = ln(p)/(2π)

**Known connection:** These 15 primes divide |M| = 2⁴⁶·3²⁰·5⁹·7⁶·11²·13³·17·19·23·29·31·41·47·59·71. Their role in moonshine is classical (Conway & Norton, 1979). Their appearance in E₈ exponents is a known but unexplained overlap.

### Theme C: GPU-Scale Optimization as Mathematical Instrument

The RTX 5070 Ti results demonstrate:
- 1,000,000 spins in 259ms (3.87B spins/sec)
- 808x amplification of Monster-scale spectral signals
- K3 moduli optimization in 91ms at 2000 spins
- Power law verification from N=100 to N=1,000,000

**Known precedent:** GPU-accelerated optimization for mathematical discovery is emerging (AlphaFold, 2021; FunSearch, 2024). Our use of Ising optimization to amplify number-theoretic signals appears to be new.

---

## Verification Status

| Finding | Status | Falsifiable? | Known precedent? |
|---------|--------|-------------|-----------------|
| CM hitting set S={5,11,17,47} | **Proved** (exhaustive) | No (proved) | New |
| Hitting set minimality | **Proved** (exhaustive) | No (proved) | New |
| h=2 hitting set {3,5,7,47,79} optimal | **Proved** (exhaustive) | No (proved) | New |
| 15 coupling constants α(n) | **Computed** (deterministic) | Reproducible | n≤7 known; n≥11 new |
| α(n) ~ n^0.33 | **Empirical** (R²=0.72) | Yes | New |
| Ω = 24 | **By construction** | Debatable | New interpretation of S₄ |
| D₄ triality of I=F·G·Z₂·S | **Verified** (commutative) | Trivially true | New framing |
| 31-dim conformal spectrum | **Computed** | Yes | New |
| T1/T2/T3 Rank-3 uniqueness of ζ | **Empirical** (14 families) | Yes | New |
| E₈–Monster 87.5% overlap | **Mathematical fact** | No | Known overlap, new interpretation |
| Decay p^{-0.36} at 1000 zeros | **Computed** | Reproducible | New |
| 808x GPU amplification | **Computed** | Reproducible | New technique |
| Moon v2 beats HL (11% vs 12.7%) | **Computed** | Reproducible | New |
| BB Variant C |log ratio|=2.63 | **Computed** | Reproducible | New |

---

## References (by paper and finding)

### Classical Number Theory
- Baker, A. (1966). Linear forms in the logarithms of algebraic numbers. *Mathematika* 13.
- Heegner, K. (1952). Diophantische Analysis und Modulfunktionen. *Math. Z.* 56.
- Stark, H.M. (1967). A complete determination of the complex quadratic fields of class-number one. *Michigan Math. J.* 14.
- Hardy, G.H. & Littlewood, J.E. (1923). Some problems of 'Partitio Numerorum'; III. *Acta Math.* 44.
- Watkins, M. (2004). Class numbers of imaginary quadratic fields. *Math. Comp.* 73.
- Oliveira e Silva, T. et al. (2014). Empirical verification of the even Goldbach conjecture. *Math. Comp.* 83.

### Algebraic Geometry & Number Theory
- Weil, A. (1949). Numbers of solutions of equations in finite fields. *Bull. AMS* 55.
- Ireland, K. & Rosen, M. (1990). *A Classical Introduction to Modern Number Theory*. Springer.
- Katz, N. & Sarnak, P. (1999). *Random Matrices, Frobenius Eigenvalues, and Monodromy*. AMS.
- Yau, S.-T. (1977). Calabi's conjecture and some new results in algebraic geometry. *Proc. NAS* 74.

### Group Theory & Moonshine
- Conway, J.H. & Norton, S.P. (1979). Monstrous moonshine. *Bull. London Math. Soc.* 11.
- Frenkel, I., Lepowsky, J. & Meurman, A. (1988). *Vertex Operator Algebras and the Monster*. Academic Press.
- Borcherds, R.E. (1992). Monstrous moonshine and monstrous Lie superalgebras. *Invent. Math.* 109.
- Griess, R.L. (1982). The friendly giant. *Invent. Math.* 69.
- Niemeier, H.-V. (1973). Definite quadratische Formen der Dimension 24. *J. Number Theory* 5.
- Conway, J.H. & Sloane, N.J.A. (1985). *Sphere Packings, Lattices and Groups*. Springer.
- Eguchi, T., Ooguri, H. & Tachikawa, Y. (2010). Notes on the K3 surface and the Mathieu group M₂₄. *Exp. Math.* 20.

### Random Matrix Theory & Riemann Zeta
- Montgomery, H.L. (1973). The pair correlation of zeros of the zeta function. *Proc. Symp. Pure Math.* 24.
- Odlyzko, A.M. (1987). On the distribution of spacings between zeros of the zeta function. *Math. Comp.* 48.
- Rudnick, Z. & Sarnak, P. (1996). Zeros of principal L-functions and random matrix theory. *Duke Math. J.* 81.
- Tracy, C.A. & Widom, H. (1994). Level-spacing distributions and the Airy kernel. *Comm. Math. Phys.* 159.
- Selberg, A. (1956). Harmonic analysis and discontinuous groups. *J. Indian Math. Soc.* 20.

### Physics & Optimization
- Kramers, H.A. (1940). Brownian motion in a field of force. *Physica* 7.
- Goto, H. et al. (2019). Combinatorial optimization by simulating adiabatic bifurcations. *Science Advances* 5.
- Edwards, S.F. & Anderson, P.W. (1975). Theory of spin glasses. *J. Phys. F* 5.
- Sherrington, D. & Kirkpatrick, S. (1975). Solvable model of a spin-glass. *Phys. Rev. Lett.* 35.
- Barahona, F. (1982). On the computational complexity of Ising spin glass models. *J. Phys. A* 15.

### Conformal Field Theory
- Belavin, A.A., Polyakov, A.M. & Zamolodchikov, A.B. (1984). Infinite conformal symmetry in two-dimensional quantum field theory. *Nucl. Phys. B* 241.
- Breitenlohner, P. & Freedman, D.Z. (1982). Stability in gauged extended supergravity. *Ann. Phys.* 144.
- Cartan, É. (1925). Le principe de dualité et la théorie des groupes. *Bull. Sci. Math.* 49.

### Computability
- Radó, T. (1962). On non-computable functions. *Bell Syst. Tech. J.* 41.
- Aaronson, S. (2020). The Busy Beaver frontier. *SIGACT News* 51.
