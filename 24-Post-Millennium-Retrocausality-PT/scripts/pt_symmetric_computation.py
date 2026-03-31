#!/usr/bin/env python3
"""
PT-SYMMETRIC COMPUTATION: Non-Hermitian Reeds Operator
========================================================
Paper II — Post-Millennium Programme

Constructs H_Omega^PT = alpha*J (x) I + I (x) T + V_Z + i*gamma*G (x) I
where G is the anti-symmetric part of the Reeds adjacency matrix.

Experiments:
  1. PT Phase Diagram: sweep gamma to find gamma_c (PT symmetry breaking)
  2. Ginibre Statistics: compute complex eigenvalue spacings in PT-broken phase
  3. Cycle vs Transient in non-Hermitian regime
  4. Exceptional point detection

Authors: Daugherty, Ward, Ryan (March 2026)
"""

import numpy as np
from numpy.linalg import eigvalsh, eigvals, eigh, norm
from scipy.sparse.linalg import eigs
import json, time, sys, os, argparse

# === REEDS ===
REEDS = [2,2,3,5,14,2,6,5,14,15,20,22,14,8,13,20,11,8,8,15,15,15,2]
N_ELEM = 23
BASINS = [sorted([0,1,2,3,5,7,11,16,22]), sorted([4,8,12,13,14,17,18]), [6], sorted([9,10,15,19,20,21])]
PERIODIC = sorted([2,3,5,6,8,13,14,15,20])
TRANSIENT = sorted(set(range(23)) - set(PERIODIC))
PRIMES_47 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
ALPHA_D = 0.008184

ELEM_BASIN = {}
for k, b in enumerate(BASINS):
    for e in b:
        ELEM_BASIN[e] = k


def build_J():
    A = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        A[i, REEDS[i]] = 1.0
    B = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        for j in range(N_ELEM):
            B[i,j] = 1.0 if ELEM_BASIN[i] == ELEM_BASIN[j] else -0.5
    O = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        for j in range(N_ELEM):
            xi, xj = i, j
            for _ in range(10):
                xi = REEDS[xi]; xj = REEDS[xj]
            O[i,j] = np.exp(-(0 if xi==xj else 5)/5.0)
    J = (A+A.T)/2.0 + 0.3*B + 0.2*O
    eigs = eigvalsh(J)
    J *= 5.52/eigs[-1]
    J -= np.diag(np.full(N_ELEM, np.trace(J)/N_ELEM))
    return J


def build_G():
    """Anti-symmetric part of Reeds adjacency: G = (A - A^T)/2."""
    A = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        A[i, REEDS[i]] = 1.0
    G = (A - A.T) / 2.0
    return G


def build_H_PT(N, J, G, alpha=20.0, gamma=0.0):
    """Build H_PT = alpha*J(x)I + I(x)T + V_Z + i*gamma*G(x)I."""
    dim = N_ELEM * N

    # Hermitian part
    H = alpha * np.kron(J, np.eye(N))
    T = np.diag(np.array([n*n/2.0 for n in range(N)]))
    H += np.kron(np.eye(N_ELEM), T)

    # Prime potential
    a = ALPHA_D * alpha
    V_Z = np.zeros((N, N))
    for p in PRIMES_47:
        w = a / (2.0*np.sqrt(p))
        for n in range(N-p):
            V_Z[n, n+p] += w
            V_Z[n+p, n] += w
    H += np.kron(np.eye(N_ELEM), V_Z)

    # Non-Hermitian part: i*gamma*G(x)I
    if gamma > 0:
        H = H.astype(complex)
        H += 1j * gamma * np.kron(G, np.eye(N))

    return H


def complex_nn_spacings(evals):
    """Nearest-neighbor spacings for complex eigenvalues."""
    n = len(evals)
    if n < 3:
        return np.array([1.0])
    # For each eigenvalue, find distance to nearest neighbor
    spacings = []
    for i in range(n):
        dists = np.abs(evals - evals[i])
        dists[i] = np.inf  # exclude self
        spacings.append(np.min(dists))
    s = np.array(spacings)
    s = s[s > 1e-15]
    return s / s.mean()


def ginibre_ks(spacings):
    """KS test against Ginibre surmise P(s) = c*s*exp(-c*s^2/2) (Rayleigh)."""
    s = np.sort(spacings)
    # Ginibre nearest-neighbor CDF: P(s) ~ 1 - exp(-pi*s^2/4) (Wigner surmise for complex)
    cdf_gin = 1.0 - np.exp(-np.pi * s**2 / 4)
    cdf_emp = np.arange(1, len(s)+1) / len(s)
    return float(np.max(np.abs(cdf_emp - cdf_gin)))


def count_complex_evals(evals, tol=1e-10):
    """Count eigenvalues with |Im| > tol."""
    return int(np.sum(np.abs(evals.imag) > tol))


# === EXPERIMENT 1: PT PHASE DIAGRAM ===

def exp1_pt_phase(N, J, G, alpha=20.0):
    """Sweep gamma to find PT symmetry breaking point."""
    print(f"\n{'='*70}")
    print(f"  EXP 1: PT PHASE DIAGRAM (N={N}, dim={N_ELEM*N})")
    print(f"{'='*70}")

    gammas = [0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 5000.0]
    results = []

    print(f"\n  {'gamma':>8s}  {'n_complex':>10s}  {'frac_complex':>13s}  {'max_Im':>10s}  {'mean_Im':>10s}  {'time':>6s}")
    print(f"  {'-'*62}")

    for gamma in gammas:
        t0 = time.time()
        H = build_H_PT(N, J, G, alpha=alpha, gamma=gamma)
        evals = eigvals(H)
        dt = time.time() - t0

        n_complex = count_complex_evals(evals)
        frac = n_complex / len(evals)
        max_im = float(np.max(np.abs(evals.imag)))
        mean_im = float(np.mean(np.abs(evals.imag)))

        entry = {
            "gamma": gamma, "n_complex": n_complex, "frac_complex": frac,
            "max_Im": max_im, "mean_Im": mean_im, "time": dt,
        }
        results.append(entry)
        print(f"  {gamma:8.2f}  {n_complex:10d}  {frac:13.4f}  {max_im:10.4f}  {mean_im:10.4f}  {dt:5.1f}s")

    # Find gamma_c: first gamma where frac_complex > 0.01
    for r in results:
        if r["frac_complex"] > 0.01:
            print(f"\n  PT BREAKING: gamma_c ~ {r['gamma']} (frac_complex = {r['frac_complex']:.3f})")
            break

    return results


# === EXPERIMENT 2: GINIBRE STATISTICS IN PT-BROKEN PHASE ===

def exp2_ginibre(N, J, G, alpha=20.0, gamma=10.0):
    """Compute complex spacing statistics in PT-broken phase."""
    print(f"\n{'='*70}")
    print(f"  EXP 2: GINIBRE STATISTICS (N={N}, gamma={gamma})")
    print(f"{'='*70}")

    t0 = time.time()
    H = build_H_PT(N, J, G, alpha=alpha, gamma=gamma)
    evals = eigvals(H)
    dt = time.time() - t0

    # Complex spacings
    sp = complex_nn_spacings(evals)
    ks_gin = ginibre_ks(sp)

    # Real-part spacings (for comparison)
    real_parts = np.sort(evals.real)
    def quick_beta(sp):
        s = np.sort(sp)
        mask = (s > 0.01) & (s < 0.5)
        if mask.sum() < 5: return 0.0
        log_s = np.log(s[mask])
        log_cdf = np.log(np.arange(1, mask.sum()+1)/len(s))
        if len(log_s) > 2:
            return max(0, float(np.polyfit(log_s, log_cdf, 1)[0]))
        return 0.0

    beta_complex = quick_beta(sp)

    n_complex = count_complex_evals(evals)
    frac = n_complex / len(evals)

    print(f"  Dimension:         {len(evals)}")
    print(f"  gamma:             {gamma}")
    print(f"  Complex evals:     {n_complex} ({frac:.1%})")
    print(f"  KS (Ginibre):      {ks_gin:.4f}")
    print(f"  beta (complex NN): {beta_complex:.2f}")
    print(f"  max |Im|:          {np.max(np.abs(evals.imag)):.4f}")
    print(f"  mean |Im|:         {np.mean(np.abs(evals.imag)):.4f}")
    print(f"  Time:              {dt:.1f}s")

    return {
        "N": N, "gamma": gamma, "dim": len(evals),
        "n_complex": n_complex, "frac_complex": frac,
        "KS_Ginibre": ks_gin, "beta_complex": beta_complex,
        "max_Im": float(np.max(np.abs(evals.imag))),
        "mean_Im": float(np.mean(np.abs(evals.imag))),
        "time": dt,
    }


# === EXPERIMENT 3: EXCEPTIONAL POINTS ===

def exp3_exceptional_points(N, J, G, alpha=20.0):
    """Find exceptional points: gamma values where eigenvalues coalesce."""
    print(f"\n{'='*70}")
    print(f"  EXP 3: EXCEPTIONAL POINT DETECTION (N={N})")
    print(f"{'='*70}")

    # Fine gamma scan
    gammas = np.linspace(0, 5.0, 100)
    min_gaps = []

    for gamma in gammas:
        H = build_H_PT(N, J, G, alpha=alpha, gamma=gamma)
        evals = eigvals(H)
        evals_sorted = np.sort(evals.real)
        # Minimum gap between consecutive real eigenvalues
        gaps = np.diff(evals_sorted)
        min_gap = np.min(np.abs(gaps[gaps != 0])) if len(gaps[gaps != 0]) > 0 else 0
        min_gaps.append(float(min_gap))

    min_gaps = np.array(min_gaps)
    # Exceptional point: where min_gap is minimized
    ep_idx = np.argmin(min_gaps)
    gamma_ep = gammas[ep_idx]

    print(f"  Scan range:        gamma in [0, 5.0], 100 points")
    print(f"  Exceptional point: gamma_EP = {gamma_ep:.3f}")
    print(f"  Min gap at EP:     {min_gaps[ep_idx]:.6f}")
    print(f"  Min gap at gamma=0: {min_gaps[0]:.6f}")

    return {
        "gamma_EP": float(gamma_ep),
        "min_gap_EP": float(min_gaps[ep_idx]),
        "min_gap_hermitian": float(min_gaps[0]),
    }


# === MAIN ===

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-N", type=int, default=200)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    print("="*70)
    print("  PT-SYMMETRIC COMPUTATION: Non-Hermitian Reeds Operator")
    print("  Paper II -- Post-Millennium Programme")
    print("="*70)

    J = build_J()
    G = build_G()
    print(f"  J: lambda_max={eigvalsh(J)[-1]:.3f}")
    print(f"  G: ||G||_F = {norm(G):.3f}, rank = {np.linalg.matrix_rank(G)}")

    all_results = {}
    t_total = time.time()

    N = 50 if args.quick else 100

    # EXP 1: PT Phase Diagram
    all_results["pt_phase"] = exp1_pt_phase(N, J, G, alpha=20.0)

    # EXP 2: Ginibre statistics at several gamma values
    ginibre_results = []
    for gamma in [1.0, 5.0, 10.0, 20.0]:
        ginibre_results.append(exp2_ginibre(N, J, G, alpha=20.0, gamma=gamma))
    all_results["ginibre"] = ginibre_results

    # EXP 3: Exceptional points
    all_results["exceptional"] = exp3_exceptional_points(N, J, G, alpha=20.0)

    # Scale test
    if not args.quick:
        print(f"\n{'='*70}")
        print(f"  SCALING: PT-broken Ginibre at N=50,100,200")
        print(f"{'='*70}")
        for Ns in [50, 100, 200]:
            r = exp2_ginibre(Ns, J, G, alpha=20.0, gamma=10.0)
            print()

    elapsed = time.time() - t_total
    print(f"\n  Total: {elapsed:.0f}s")

    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "pt_symmetric_results.json")
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2,
                  default=lambda o: float(o) if hasattr(o, '__float__') else str(o))
    print(f"  Results: {report_path}")


if __name__ == "__main__":
    main()
