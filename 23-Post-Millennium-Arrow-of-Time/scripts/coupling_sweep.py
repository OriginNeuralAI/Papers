#!/usr/bin/env python3
"""
COUPLING SWEEP: Finding the Deterministic-to-Chaotic Transition
================================================================
Paper I Companion — Post-Millennium Programme

The standard H_Omega = J (x) I + I (x) T + V_Z has alpha_D = 0.008184.
At this coupling, T (kinetic, ~ n^2/2) dominates J (coupling, ~ 5.5),
so eigenvalues are Poisson-like (regular Fourier spacing).

This experiment SWEEPS the coupling strength alpha from 0.001 to 100.0
to find the CRITICAL COUPLING alpha_c where:
  - Cycle sector transitions from Poisson -> GUE (deterministic chaos)
  - Transient sector transitions later or shows different universality

The transition point alpha_c is where quantum chaos emerges from
deterministic Reeds dynamics — the "quantization" of a classical map.

Also analyses eigenvalues in ENERGY WINDOWS to isolate the low-energy
sector where J and T compete.

Experiments:
  1. Coupling sweep: alpha from 0.001 to 100, measure KS_GUE and beta
  2. Energy window analysis: bottom 10%, middle, top 10% of spectrum
  3. N-scaling at optimal coupling: N=100..1500 (up to 34,500 x 34,500)
  4. Cycle vs Transient separation at optimal coupling

Usage:
    python coupling_sweep.py [--max-N 1500] [--quick]

Authors: Daugherty, Ward, Ryan (March 2026)
"""

import numpy as np
from numpy.linalg import eigvalsh, eigh
import json
import time
import sys
import os
import argparse

# ===================================================================
# REEDS (self-contained)
# ===================================================================

REEDS = [2, 2, 3, 5, 14, 2, 6, 5, 14, 15, 20, 22, 14, 8, 13, 20, 11, 8, 8, 15, 15, 15, 2]
N_ELEM = 23
BASINS = [
    {0, 1, 2, 3, 5, 7, 11, 16, 22},
    {4, 8, 12, 13, 14, 17, 18},
    {6},
    {9, 10, 15, 19, 20, 21},
]
PERIODIC = {2, 3, 5, 6, 8, 13, 14, 15, 20}
TRANSIENT = set(range(23)) - PERIODIC
CYCLE_IDX = sorted(PERIODIC)
TRANS_IDX = sorted(TRANSIENT)
PRIMES_47 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def build_J():
    """Build 23x23 enriched coupling matrix."""
    A = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        A[i, REEDS[i]] = 1.0
    elem_basin = {}
    for k, basin in enumerate(BASINS):
        for elem in basin:
            elem_basin[elem] = k
    B = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        for j in range(N_ELEM):
            B[i, j] = 1.0 if elem_basin[i] == elem_basin[j] else -0.5
    O = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        for j in range(N_ELEM):
            xi, xj = i, j
            for _ in range(10):
                xi = REEDS[xi]
                xj = REEDS[xj]
            O[i, j] = np.exp(-(0 if xi == xj else 5) / 5.0)
    J = (A + A.T) / 2.0 + 0.3 * B + 0.2 * O
    eigs = eigvalsh(J)
    J *= 5.52 / eigs[-1]
    J -= np.diag(np.full(N_ELEM, np.trace(J) / N_ELEM))
    return J


def build_H(N, J, alpha_scale=1.0):
    """Build H = alpha_scale * J (x) I + I (x) T + V_Z."""
    alpha = 0.008184 * alpha_scale

    # J (x) I_N, scaled by alpha_scale relative to T
    H = alpha_scale * np.kron(J, np.eye(N))

    # I_23 (x) T_N
    T = np.diag(np.array([n * n / 2.0 for n in range(N)]))
    H += np.kron(np.eye(N_ELEM), T)

    # V_Z (prime potential)
    V_Z = np.zeros((N, N))
    for p in PRIMES_47:
        w = alpha / (2.0 * np.sqrt(p))
        for n in range(N - p):
            V_Z[n, n + p] += w
            V_Z[n + p, n] += w
    H += np.kron(np.eye(N_ELEM), V_Z)

    return (H + H.T) / 2.0


def extract_sector(H, channels, N):
    """Extract submatrix for given channel indices."""
    idx = []
    for ch in channels:
        idx.extend(range(ch * N, (ch + 1) * N))
    idx = np.array(idx)
    return H[np.ix_(idx, idx)]


# ===================================================================
# SPECTRAL STATISTICS
# ===================================================================

def unfold(evals):
    """Unfold eigenvalues to mean spacing 1."""
    evals = np.sort(evals)
    n = len(evals)
    ranks = np.arange(1, n + 1)
    deg = min(6, max(2, n // 20))
    coeffs = np.polyfit(evals, ranks, deg=deg)
    return np.polyval(coeffs, evals)


def spacings(unfolded):
    """Normalized nearest-neighbor spacings."""
    s = np.diff(np.sort(unfolded))
    s = s[s > 1e-15]
    if len(s) == 0:
        return np.array([1.0])
    return s / s.mean()


def ks_gue(sp):
    s = np.sort(sp)
    cdf_gue = 1.0 - np.exp(-4 * s**2 / np.pi)
    cdf_emp = np.arange(1, len(s) + 1) / len(s)
    return float(np.max(np.abs(cdf_emp - cdf_gue)))


def ks_poisson(sp):
    s = np.sort(sp)
    cdf_poi = 1.0 - np.exp(-s)
    cdf_emp = np.arange(1, len(s) + 1) / len(s)
    return float(np.max(np.abs(cdf_emp - cdf_poi)))


def beta_estimate(sp):
    """Level repulsion exponent from small-s CDF."""
    s = np.sort(sp)
    mask = (s > 0.01) & (s < 0.5)
    if mask.sum() < 5:
        return 0.0
    log_s = np.log(s[mask])
    log_cdf = np.log(np.arange(1, mask.sum() + 1) / len(s))
    if len(log_s) > 2:
        return max(0, float(np.polyfit(log_s, log_cdf, 1)[0]))
    return 0.0


def analyze_evals(evals, label=""):
    """Full spectral analysis of eigenvalue array."""
    u = unfold(evals)
    sp = spacings(u)
    kg = ks_gue(sp)
    kp = ks_poisson(sp)
    b = beta_estimate(sp)
    cls = "GUE" if kg < kp else "Poisson"
    return {
        "label": label,
        "n_evals": len(evals),
        "KS_GUE": kg,
        "KS_Poisson": kp,
        "beta": b,
        "class": cls,
        "evals_min": float(evals.min()),
        "evals_max": float(evals.max()),
        "mean_spacing": float(np.mean(np.diff(np.sort(evals)))),
    }


def analyze_windows(evals, label=""):
    """Analyze bottom/middle/top energy windows separately."""
    n = len(evals)
    evals = np.sort(evals)
    w = n // 10  # 10% windows
    results = {}
    for name, sl in [("bottom_10pct", slice(0, w)),
                      ("middle", slice(n//2 - w//2, n//2 + w//2)),
                      ("top_10pct", slice(n - w, n))]:
        window = evals[sl]
        if len(window) > 20:
            results[name] = analyze_evals(window, f"{label}_{name}")
    return results


# ===================================================================
# EXPERIMENT 1: COUPLING SWEEP
# ===================================================================

def exp1_coupling_sweep(N, J):
    """Sweep alpha_scale to find GUE transition."""
    print("\n" + "=" * 70)
    print(f"  EXP 1: COUPLING SWEEP (N={N}, dim={N_ELEM*N})")
    print("=" * 70)

    # Logarithmic sweep from weak to strong coupling
    alpha_values = [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
    results = []

    print(f"\n  {'alpha':>8s}  {'KS_GUE(cyc)':>12s}  {'KS_Poi(cyc)':>12s}  {'beta(cyc)':>10s}  {'class(cyc)':>10s}  {'KS_GUE(trn)':>12s}  {'beta(trn)':>10s}  {'class(trn)':>10s}  {'time':>6s}")
    print("  " + "-" * 110)

    for alpha in alpha_values:
        t0 = time.time()
        H = build_H(N, J, alpha_scale=alpha)
        H_cyc = extract_sector(H, CYCLE_IDX, N)
        H_trn = extract_sector(H, TRANS_IDX, N)
        del H

        evals_cyc = eigvalsh(H_cyc)
        evals_trn = eigvalsh(H_trn)
        del H_cyc, H_trn

        r_cyc = analyze_evals(evals_cyc, f"cycle_a{alpha}")
        r_trn = analyze_evals(evals_trn, f"trans_a{alpha}")

        # Also analyze energy windows
        w_cyc = analyze_windows(evals_cyc, f"cycle_a{alpha}")
        w_trn = analyze_windows(evals_trn, f"trans_a{alpha}")

        dt = time.time() - t0

        entry = {
            "alpha": alpha,
            "cycle": r_cyc,
            "transient": r_trn,
            "cycle_windows": w_cyc,
            "transient_windows": w_trn,
            "time": dt,
        }
        results.append(entry)

        print(f"  {alpha:8.2f}  {r_cyc['KS_GUE']:12.4f}  {r_cyc['KS_Poisson']:12.4f}  {r_cyc['beta']:10.2f}  {r_cyc['class']:>10s}  {r_trn['KS_GUE']:12.4f}  {r_trn['beta']:10.2f}  {r_trn['class']:>10s}  {dt:5.1f}s")

    # Find transition: first alpha where cycle sector is GUE
    gue_alphas = [r["alpha"] for r in results if r["cycle"]["class"] == "GUE"]
    if gue_alphas:
        alpha_c = min(gue_alphas)
        print(f"\n  >> TRANSITION: alpha_c = {alpha_c} (cycle sector enters GUE)")
    else:
        # Check energy windows
        window_gue = []
        for r in results:
            for wname, wdata in r["cycle_windows"].items():
                if wdata["class"] == "GUE":
                    window_gue.append((r["alpha"], wname, wdata["KS_GUE"], wdata["beta"]))
        if window_gue:
            print(f"\n  >> GUE found in energy windows:")
            for a, w, kg, b in window_gue:
                print(f"     alpha={a}, window={w}: KS_GUE={kg:.4f}, beta={b:.2f}")
        else:
            # Find best (lowest KS_GUE)
            best = min(results, key=lambda r: r["cycle"]["KS_GUE"])
            print(f"\n  >> No GUE transition found. Best: alpha={best['alpha']}, KS_GUE={best['cycle']['KS_GUE']:.4f}, beta={best['cycle']['beta']:.2f}")

    return results


# ===================================================================
# EXPERIMENT 2: N-SCALING AT STRONG COUPLING
# ===================================================================

def exp2_scaling(N_values, J, alpha_opt):
    """Test scaling of GUE statistics with N at optimal coupling."""
    print("\n" + "=" * 70)
    print(f"  EXP 2: N-SCALING AT alpha={alpha_opt}")
    print("=" * 70)

    results = []
    print(f"\n  {'N':>6s}  {'dim':>8s}  {'KS_GUE(cyc)':>12s}  {'beta(cyc)':>10s}  {'KS_GUE(trn)':>12s}  {'beta(trn)':>10s}  {'cyc-trn':>8s}  {'time':>6s}")
    print("  " + "-" * 80)

    for N in N_values:
        dim = N_ELEM * N
        t0 = time.time()

        H = build_H(N, J, alpha_scale=alpha_opt)
        H_cyc = extract_sector(H, CYCLE_IDX, N)
        H_trn = extract_sector(H, TRANS_IDX, N)
        del H

        evals_cyc = eigvalsh(H_cyc)
        evals_trn = eigvalsh(H_trn)
        del H_cyc, H_trn

        r_cyc = analyze_evals(evals_cyc, f"cycle_N{N}")
        r_trn = analyze_evals(evals_trn, f"trans_N{N}")
        w_cyc = analyze_windows(evals_cyc, f"cycle_N{N}")

        dt = time.time() - t0

        # Separation: cycle beta - transient beta
        sep = r_cyc["beta"] - r_trn["beta"]

        entry = {
            "N": N, "dim": dim,
            "cycle": r_cyc, "transient": r_trn,
            "cycle_windows": w_cyc,
            "separation": sep, "time": dt,
        }
        results.append(entry)

        print(f"  {N:6d}  {dim:8d}  {r_cyc['KS_GUE']:12.4f}  {r_cyc['beta']:10.2f}  {r_trn['KS_GUE']:12.4f}  {r_trn['beta']:10.2f}  {sep:+8.2f}  {dt:5.1f}s")

    return results


# ===================================================================
# EXPERIMENT 3: PURE COUPLING MATRIX ANALYSIS (J only, no T)
# ===================================================================

def exp3_pure_coupling(J):
    """
    Analyze the coupling-ONLY operator H = J (x) I (no kinetic energy).
    This isolates the Reeds structure from Fourier noise.
    """
    print("\n" + "=" * 70)
    print("  EXP 3: PURE COUPLING ANALYSIS (J only, no kinetic T)")
    print("=" * 70)

    results = []
    for N in [50, 100, 200, 500]:
        dim = N_ELEM * N
        t0 = time.time()

        # H = J (x) I_N only
        H = np.kron(J, np.eye(N))
        H_cyc = extract_sector(H, CYCLE_IDX, N)
        H_trn = extract_sector(H, TRANS_IDX, N)
        del H

        evals_cyc = eigvalsh(H_cyc)
        evals_trn = eigvalsh(H_trn)
        del H_cyc, H_trn

        r_cyc = analyze_evals(evals_cyc, f"pure_cycle_N{N}")
        r_trn = analyze_evals(evals_trn, f"pure_trans_N{N}")

        dt = time.time() - t0
        sep = r_cyc["beta"] - r_trn["beta"]

        entry = {"N": N, "cycle": r_cyc, "transient": r_trn, "separation": sep, "time": dt}
        results.append(entry)

        print(f"  N={N:4d} (dim={dim:6d}): cycle: KS_GUE={r_cyc['KS_GUE']:.4f} beta={r_cyc['beta']:.2f} [{r_cyc['class']}]  trans: KS_GUE={r_trn['KS_GUE']:.4f} beta={r_trn['beta']:.2f} [{r_trn['class']}]  sep={sep:+.2f}  ({dt:.1f}s)")

    return results


# ===================================================================
# EXPERIMENT 4: RANDOMIZED COUPLING TEST
# ===================================================================

def exp4_random_comparison(N, J):
    """
    Compare Reeds-structured J vs random symmetric J.
    If Reeds structure matters, its spectral statistics should differ.
    """
    print("\n" + "=" * 70)
    print(f"  EXP 4: REEDS vs RANDOM COUPLING (N={N})")
    print("=" * 70)

    rng = np.random.default_rng(42)

    # Build with Reeds J
    H_reeds = build_H(N, J, alpha_scale=10.0)
    evals_reeds = eigvalsh(H_reeds)
    del H_reeds

    # Build with random symmetric J (same spectral norm)
    J_rand = rng.standard_normal((N_ELEM, N_ELEM))
    J_rand = (J_rand + J_rand.T) / 2.0
    J_rand *= np.max(np.abs(eigvalsh(J))) / np.max(np.abs(eigvalsh(J_rand)))
    H_rand = 10.0 * np.kron(J_rand, np.eye(N))
    T = np.diag(np.array([n * n / 2.0 for n in range(N)]))
    H_rand += np.kron(np.eye(N_ELEM), T)
    H_rand = (H_rand + H_rand.T) / 2.0
    evals_rand = eigvalsh(H_rand)
    del H_rand

    r_reeds = analyze_evals(evals_reeds, "Reeds")
    r_rand = analyze_evals(evals_rand, "Random")

    # Window analysis
    w_reeds = analyze_windows(evals_reeds, "Reeds")
    w_rand = analyze_windows(evals_rand, "Random")

    print(f"\n  FULL SPECTRUM:")
    print(f"    Reeds:   KS_GUE={r_reeds['KS_GUE']:.4f}  beta={r_reeds['beta']:.2f}  [{r_reeds['class']}]")
    print(f"    Random:  KS_GUE={r_rand['KS_GUE']:.4f}  beta={r_rand['beta']:.2f}  [{r_rand['class']}]")

    print(f"\n  ENERGY WINDOWS:")
    for wname in ["bottom_10pct", "middle", "top_10pct"]:
        if wname in w_reeds and wname in w_rand:
            print(f"    {wname}:")
            print(f"      Reeds:   KS_GUE={w_reeds[wname]['KS_GUE']:.4f}  beta={w_reeds[wname]['beta']:.2f}  [{w_reeds[wname]['class']}]")
            print(f"      Random:  KS_GUE={w_rand[wname]['KS_GUE']:.4f}  beta={w_rand[wname]['beta']:.2f}  [{w_rand[wname]['class']}]")

    return {
        "reeds_full": r_reeds, "random_full": r_rand,
        "reeds_windows": w_reeds, "random_windows": w_rand,
    }


# ===================================================================
# MAIN
# ===================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-N", type=int, default=500)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    print("=" * 70)
    print("  COUPLING SWEEP: Deterministic-to-Chaotic Transition")
    print("  Post-Millennium Programme -- Daugherty, Ward, Ryan")
    print("=" * 70)

    J = build_J()
    J_eigs = eigvalsh(J)
    print(f"  J: lambda_max={J_eigs[-1]:.3f}, lambda_min={J_eigs[0]:.3f}, gap={J_eigs[-1]-J_eigs[-2]:.3f}")

    all_results = {}
    t_total = time.time()

    # EXP 1: Coupling sweep at moderate N
    sweep_N = 100 if args.quick else 200
    all_results["coupling_sweep"] = exp1_coupling_sweep(sweep_N, J)

    # Find optimal alpha (lowest KS_GUE for cycle sector)
    best = min(all_results["coupling_sweep"], key=lambda r: r["cycle"]["KS_GUE"])
    alpha_opt = best["alpha"]
    print(f"\n  Optimal coupling: alpha={alpha_opt} (KS_GUE={best['cycle']['KS_GUE']:.4f})")

    # EXP 2: N-scaling at optimal coupling
    if args.quick:
        N_vals = [50, 100, 200]
    else:
        N_vals = [50, 100, 200, 500]
        if args.max_N >= 1000:
            N_vals.append(1000)
        if args.max_N >= 1500:
            N_vals.append(1500)
    all_results["n_scaling"] = exp2_scaling(N_vals, J, alpha_opt)

    # EXP 3: Pure coupling (no kinetic)
    all_results["pure_coupling"] = exp3_pure_coupling(J)

    # EXP 4: Reeds vs random
    rand_N = 100 if args.quick else 200
    all_results["reeds_vs_random"] = exp4_random_comparison(rand_N, J)

    elapsed = time.time() - t_total
    print(f"\n  Total elapsed: {elapsed:.1f}s")

    # Save
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "coupling_sweep_results.json")
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2, default=lambda o: float(o) if hasattr(o, '__float__') else str(o))
    print(f"  Results saved to: {report_path}")


if __name__ == "__main__":
    main()
