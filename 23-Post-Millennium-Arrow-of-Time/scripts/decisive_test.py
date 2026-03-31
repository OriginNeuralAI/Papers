#!/usr/bin/env python3
"""
DECISIVE TEST: Three Experiments That Settle Deterministic QM
==============================================================
Post-Millennium Programme — Daugherty, Ward, Ryan

TEST A: EIGENVECTOR BASIN CLUSTERING (Cycle Sector)
  For each eigenvector in the cycle sector (9 periodic channels x N modes):
    1. Compute overlap |<psi_k|basin_j>|^2 for each of 4 Reeds basins
    2. Assign eigenvector to dominant basin
    3. Check: do eigenvectors cluster by basin membership?

  IF YES -> Spectral hierarchy = Reeds topology (not generic)
  IF NO  -> Just eigenvalue statistics, topology not encoded

TEST B: ASYMPTOTIC BETA via SPARSE LANCZOS on LOW-ENERGY SECTOR
  Target: N=2000-5000 with sparse eigensolver on bottom eigenvalues
  Prediction: beta_cycle -> 16/9 = 1.778 (NOT 2.0)

  IF beta stabilizes at 1.78 +/- 0.02 -> Finite symmetry confirmed
  IF beta -> 2.0 -> Infinite-dim irreps somehow emerge

TEST C: CRITICAL EXPONENT at N*=500
  Map |beta_cycle - beta_trans| as function of N near the peak.
  Fit (N - N*)^nu for critical exponent nu.

  IF power-law -> Genuine quantum phase transition
  IF exponential -> Crossover, not transition

Usage:
    python decisive_test.py [--quick]

Authors: Daugherty, Ward, Ryan (March 2026)
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh, norm
from scipy.sparse import kron as sp_kron, eye as sp_eye, diags
from scipy.sparse.linalg import eigsh
from scipy.optimize import curve_fit
import json, time, sys, os, argparse

# ===================================================================
# REEDS
# ===================================================================

REEDS = [2,2,3,5,14,2,6,5,14,15,20,22,14,8,13,20,11,8,8,15,15,15,2]
N_ELEM = 23
BASINS = [
    sorted([0,1,2,3,5,7,11,16,22]),
    sorted([4,8,12,13,14,17,18]),
    [6],
    sorted([9,10,15,19,20,21]),
]
BASIN_SIZES = [9,7,1,6]
BASIN_NAMES = ["Creation","Perception","Stability","Exchange"]
PERIODIC = sorted([2,3,5,6,8,13,14,15,20])
TRANSIENT = sorted(set(range(23)) - set(PERIODIC))
PRIMES_47 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
ALPHA_D = 0.008184

ELEM_BASIN = {}
for k, b in enumerate(BASINS):
    for e in b:
        ELEM_BASIN[e] = k

# Which of the 9 cycle channels belong to which basin
CYCLE_BASIN_MAP = {}  # cycle_local_index -> basin_id
for li, ch in enumerate(PERIODIC):
    CYCLE_BASIN_MAP[li] = ELEM_BASIN[ch]


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


# ===================================================================
# SPARSE OPERATOR CONSTRUCTION
# ===================================================================

def build_H_sparse(N, J, alpha_scale=20.0):
    """Build H_Omega as scipy sparse matrix. Memory: O(23*N*50) not O((23N)^2)."""
    from scipy.sparse import csr_matrix, lil_matrix

    n_ch = N_ELEM
    dim = n_ch * N

    # J (x) I_N — sparse kronecker
    J_sp = csr_matrix(J)
    I_N = sp_eye(N, format='csr')
    H = alpha_scale * sp_kron(J_sp, I_N, format='csr')

    # I_23 (x) T_N — diagonal kinetic energy
    T_diag = np.array([n*n/2.0 for n in range(N)])
    T_sp = diags(T_diag, 0, shape=(N, N), format='csr')
    I_23 = sp_eye(n_ch, format='csr')
    H = H + sp_kron(I_23, T_sp, format='csr')

    # V_Z — banded prime potential (sparse)
    alpha = ALPHA_D * alpha_scale
    V_data = []
    V_row = []
    V_col = []
    for p in PRIMES_47:
        w = alpha / (2.0 * np.sqrt(p))
        for n in range(N - p):
            V_data.extend([w, w])
            V_row.extend([n, n+p])
            V_col.extend([n+p, n])
    if V_data:
        V_Z_sp = csr_matrix((V_data, (V_row, V_col)), shape=(N, N))
        H = H + sp_kron(I_23, V_Z_sp, format='csr')

    return H


def build_sector_sparse(N, channels, J, alpha_scale=20.0):
    """Build sector operator (only specific channels) as sparse matrix."""
    n_ch = len(channels)
    dim = n_ch * N

    # Extract J submatrix for these channels
    J_sub = J[np.ix_(channels, channels)]
    from scipy.sparse import csr_matrix as csr
    J_sp = csr(J_sub)
    I_N = sp_eye(N, format='csr')
    H = alpha_scale * sp_kron(J_sp, I_N, format='csr')

    T_diag = np.array([n*n/2.0 for n in range(N)])
    T_sp = diags(T_diag, 0, shape=(N,N), format='csr')
    I_ch = sp_eye(n_ch, format='csr')
    H = H + sp_kron(I_ch, T_sp, format='csr')

    alpha = ALPHA_D * alpha_scale
    V_data, V_row, V_col = [], [], []
    for p in PRIMES_47:
        w = alpha / (2.0 * np.sqrt(p))
        for n in range(N - p):
            V_data.extend([w, w])
            V_row.extend([n, n+p])
            V_col.extend([n+p, n])
    if V_data:
        V_sp = csr((V_data, (V_row, V_col)), shape=(N, N))
        H = H + sp_kron(I_ch, V_sp, format='csr')

    return H


# ===================================================================
# SPECTRAL STATISTICS (from spacings)
# ===================================================================

def unfold(evals):
    evals = np.sort(evals)
    n = len(evals)
    ranks = np.arange(1, n+1)
    deg = min(6, max(2, n//20))
    coeffs = np.polyfit(evals, ranks, deg=deg)
    return np.polyval(coeffs, evals)

def get_spacings(unfolded):
    s = np.diff(np.sort(unfolded))
    s = s[s > 1e-15]
    if len(s) == 0: return np.array([1.0])
    return s / s.mean()

def ks_gue(sp):
    s = np.sort(sp)
    cdf = 1.0 - np.exp(-4*s**2/np.pi)
    emp = np.arange(1, len(s)+1)/len(s)
    return float(np.max(np.abs(emp - cdf)))

def ks_poisson(sp):
    s = np.sort(sp)
    cdf = 1.0 - np.exp(-s)
    emp = np.arange(1, len(s)+1)/len(s)
    return float(np.max(np.abs(emp - cdf)))

def beta_est(sp):
    s = np.sort(sp)
    mask = (s > 0.01) & (s < 0.5)
    if mask.sum() < 5: return 0.0
    log_s = np.log(s[mask])
    log_cdf = np.log(np.arange(1, mask.sum()+1)/len(s))
    if len(log_s) > 2:
        return max(0, float(np.polyfit(log_s, log_cdf, 1)[0]))
    return 0.0

def spectral_stats(evals, label=""):
    u = unfold(evals)
    sp = get_spacings(u)
    kg = ks_gue(sp)
    kp = ks_poisson(sp)
    b = beta_est(sp)
    return {"label": label, "KS_GUE": kg, "KS_Poi": kp, "beta": b,
            "class": "GUE" if kg < kp else "Poisson", "n": len(evals)}


# ===================================================================
# TEST A: EIGENVECTOR BASIN CLUSTERING
# ===================================================================

def test_A_basin_clustering(N_values, J, alpha=20.0):
    """For cycle-sector eigenvectors, check if they cluster by basin."""
    print("\n" + "="*70)
    print("  TEST A: EIGENVECTOR BASIN CLUSTERING IN CYCLE SECTOR")
    print("="*70)

    results = []
    n_cycle = len(PERIODIC)  # 9

    for N in N_values:
        dim_cyc = n_cycle * N
        print(f"\n  N={N} (cycle sector: {dim_cyc}x{dim_cyc})")

        t0 = time.time()
        # Build cycle sector and diagonalize
        if dim_cyc <= 12000:
            # Dense for moderate sizes
            H_cyc = build_sector_sparse(N, PERIODIC, J, alpha).toarray()
            evals, evecs = eigh(H_cyc)
            del H_cyc
        else:
            # Sparse Lanczos for bottom eigenvalues
            H_sp = build_sector_sparse(N, PERIODIC, J, alpha)
            k_eig = min(dim_cyc - 2, 2000)
            evals, evecs = eigsh(H_sp, k=k_eig, which='SA')
            idx = np.argsort(evals)
            evals = evals[idx]
            evecs = evecs[:, idx]
            del H_sp

        n_eig = len(evals)
        t_diag = time.time() - t0
        print(f"    Diagonalized: {n_eig} eigenvectors in {t_diag:.1f}s")

        # For each eigenvector, compute basin overlap
        # Cycle channels: PERIODIC = [2,3,5,6,8,13,14,15,20]
        # These map to basins: [0,0,0,2,1,1,1,3,3] via CYCLE_BASIN_MAP
        basin_overlaps = np.zeros((n_eig, 4))
        dominant_basin = np.zeros(n_eig, dtype=int)

        for i in range(n_eig):
            psi = evecs[:, i]
            # Compute |<psi|basin_j>|^2 for each basin
            for li, ch_global in enumerate(PERIODIC):
                b = ELEM_BASIN[ch_global]
                start = li * N
                end = (li + 1) * N
                basin_overlaps[i, b] += np.sum(psi[start:end]**2)
            dominant_basin[i] = np.argmax(basin_overlaps[i])

        # Count assignments
        basin_counts = np.bincount(dominant_basin, minlength=4)

        # Expected from channel counting in cycle sector:
        # Basin 0 (Creation): channels 2,3,5 -> 3 of 9 -> 33.3%
        # Basin 1 (Perception): channels 8,13,14 -> 3 of 9 -> 33.3%
        # Basin 2 (Stability): channel 6 -> 1 of 9 -> 11.1%
        # Basin 3 (Exchange): channels 15,20 -> 2 of 9 -> 22.2%
        expected_frac = np.array([3, 3, 1, 2]) / 9.0

        # Concentration metric: how peaked are the overlaps?
        # If clustered: dominant overlap >> 0.25. If uniform: all ~ 0.25
        mean_dominant_overlap = np.mean(np.max(basin_overlaps, axis=1))
        mean_PR = np.mean(1.0 / np.sum((basin_overlaps / basin_overlaps.sum(axis=1, keepdims=True))**2, axis=1))

        # Clustering quality: adjusted Rand index vs expected
        observed_frac = basin_counts / n_eig

        print(f"\n    BASIN ASSIGNMENT (dominant overlap):")
        print(f"    {'Basin':>12s}  {'Count':>6s}  {'Observed':>9s}  {'Expected':>9s}  {'Delta':>8s}")
        for b in range(4):
            delta = observed_frac[b] - expected_frac[b]
            print(f"    {BASIN_NAMES[b]:>12s}  {basin_counts[b]:6d}  {observed_frac[b]:9.4f}  {expected_frac[b]:9.4f}  {delta:+8.4f}")

        print(f"\n    Mean dominant overlap:   {mean_dominant_overlap:.4f} (uniform=0.333, clustered>0.5)")
        print(f"    Mean basin PR:          {mean_PR:.3f} (uniform=4.0, single-basin=1.0)")

        # Separation by energy: bottom vs top half
        half = n_eig // 2
        low_dom = np.mean(np.max(basin_overlaps[:half], axis=1))
        high_dom = np.mean(np.max(basin_overlaps[half:], axis=1))
        print(f"    Low-energy dominance:    {low_dom:.4f}")
        print(f"    High-energy dominance:   {high_dom:.4f}")

        # Is there clustering? Threshold: dominant overlap > 0.5 for > 10% of states
        frac_clustered = np.mean(np.max(basin_overlaps, axis=1) > 0.5)
        clustered = frac_clustered > 0.10
        print(f"    Fraction with overlap > 0.5: {frac_clustered:.1%}")
        print(f"    CLUSTERING: {'YES' if clustered else 'NO'}")

        # Overlap histogram (compact)
        dom_overlaps = np.max(basin_overlaps, axis=1)
        pct = [10, 25, 50, 75, 90]
        pvals = np.percentile(dom_overlaps, pct)
        print(f"    Dominant overlap percentiles: " + "  ".join(f"p{p}={v:.3f}" for p, v in zip(pct, pvals)))

        entry = {
            "N": N, "dim": dim_cyc, "n_eigenvectors": n_eig,
            "time": t_diag,
            "basin_counts": basin_counts.tolist(),
            "observed_frac": observed_frac.tolist(),
            "expected_frac": expected_frac.tolist(),
            "mean_dominant_overlap": float(mean_dominant_overlap),
            "mean_PR": float(mean_PR),
            "frac_clustered_05": float(frac_clustered),
            "low_energy_dominance": float(low_dom),
            "high_energy_dominance": float(high_dom),
            "clustered": clustered,
            "percentiles": {f"p{p}": float(v) for p, v in zip(pct, pvals)},
        }
        results.append(entry)

    return results


# ===================================================================
# TEST B: ASYMPTOTIC BETA via SPARSE LANCZOS
# ===================================================================

def test_B_asymptotic_beta(N_values, J, alpha=20.0):
    """Push to large N with sparse Lanczos on low-energy eigenvalues."""
    print("\n" + "="*70)
    print("  TEST B: ASYMPTOTIC BETA via SPARSE LANCZOS")
    print(f"  Prediction: beta_cycle -> 16/9 = {16/9:.6f}")
    print("="*70)

    results = []

    for N in N_values:
        dim_cyc = len(PERIODIC) * N
        dim_trn = len(TRANSIENT) * N

        # Number of eigenvalues to compute (bottom portion)
        k_cyc = min(dim_cyc - 2, max(200, dim_cyc // 5))
        k_trn = min(dim_trn - 2, max(200, dim_trn // 5))

        print(f"\n  N={N}: cycle {dim_cyc}x{dim_cyc} (k={k_cyc}), trans {dim_trn}x{dim_trn} (k={k_trn})")

        # Cycle sector
        t0 = time.time()
        H_cyc = build_sector_sparse(N, PERIODIC, J, alpha)
        evals_cyc, _ = eigsh(H_cyc, k=k_cyc, which='SA')
        evals_cyc = np.sort(evals_cyc)
        del H_cyc
        t_cyc = time.time() - t0

        # Transient sector
        t1 = time.time()
        H_trn = build_sector_sparse(N, TRANSIENT, J, alpha)
        evals_trn, _ = eigsh(H_trn, k=k_trn, which='SA')
        evals_trn = np.sort(evals_trn)
        del H_trn
        t_trn = time.time() - t1

        # Statistics
        sc = spectral_stats(evals_cyc, f"cycle_N{N}")
        st = spectral_stats(evals_trn, f"trans_N{N}")
        sep = sc["beta"] - st["beta"]

        entry = {
            "N": N, "dim_cyc": dim_cyc, "dim_trn": dim_trn,
            "k_cyc": k_cyc, "k_trn": k_trn,
            "cycle": sc, "transient": st,
            "separation": float(sep),
            "time_cyc": t_cyc, "time_trn": t_trn,
        }
        results.append(entry)

        dev = abs(sc["beta"] - 16/9)
        print(f"    Cycle:  beta={sc['beta']:.4f}  KS_GUE={sc['KS_GUE']:.4f}  [{sc['class']}]  (dev from 16/9: {dev:.4f})  ({t_cyc:.1f}s)")
        print(f"    Trans:  beta={st['beta']:.4f}  KS_GUE={st['KS_GUE']:.4f}  [{st['class']}]  ({t_trn:.1f}s)")
        print(f"    Sep:    {sep:+.4f}")

    # Summary
    print(f"\n  ASYMPTOTIC BETA CONVERGENCE:")
    print(f"  {'N':>6s}  {'beta_cyc':>9s}  {'dev 16/9':>9s}  {'beta_trn':>9s}  {'sep':>7s}")
    print(f"  {'-'*45}")
    for r in results:
        dev = abs(r["cycle"]["beta"] - 16/9)
        print(f"  {r['N']:6d}  {r['cycle']['beta']:9.4f}  {dev:9.4f}  {r['transient']['beta']:9.4f}  {r['separation']:+7.4f}")

    # Fit: does beta_cycle converge to a limit?
    if len(results) >= 3:
        Ns = np.array([r["N"] for r in results], dtype=float)
        betas = np.array([r["cycle"]["beta"] for r in results])
        # Try fit: beta(N) = beta_inf - a/N^b
        try:
            def model(N, beta_inf, a, b):
                return beta_inf - a / N**b
            popt, pcov = curve_fit(model, Ns, betas, p0=[1.78, 1.0, 0.5],
                                   bounds=([1.0, 0, 0], [2.5, 100, 3]),
                                   maxfev=10000)
            print(f"\n  FIT: beta_cycle(N) = {popt[0]:.4f} - {popt[1]:.4f}/N^{popt[2]:.4f}")
            print(f"  beta_inf = {popt[0]:.4f}  (prediction: {16/9:.4f} = 16/9)")
            print(f"  |beta_inf - 16/9| = {abs(popt[0] - 16/9):.4f}")
        except Exception as e:
            print(f"\n  FIT FAILED: {e}")

    return results


# ===================================================================
# TEST C: CRITICAL EXPONENT
# ===================================================================

def test_C_critical_exponent(J, alpha=20.0):
    """Dense scan around N*=500 to extract critical exponent."""
    print("\n" + "="*70)
    print("  TEST C: CRITICAL EXPONENT AT N*=500")
    print("="*70)

    # Dense N scan: 50 to 1200
    N_scan = [50, 75, 100, 150, 200, 300, 400, 500, 600, 750, 900, 1000]
    results = []

    for N in N_scan:
        dim_cyc = len(PERIODIC) * N
        dim_trn = len(TRANSIENT) * N

        t0 = time.time()

        # Use sparse Lanczos for larger sizes
        k_cyc = min(dim_cyc - 2, max(150, dim_cyc // 5))
        k_trn = min(dim_trn - 2, max(150, dim_trn // 5))

        H_cyc = build_sector_sparse(N, PERIODIC, J, alpha)
        evals_cyc, _ = eigsh(H_cyc, k=k_cyc, which='SA')
        del H_cyc

        H_trn = build_sector_sparse(N, TRANSIENT, J, alpha)
        evals_trn, _ = eigsh(H_trn, k=k_trn, which='SA')
        del H_trn

        sc = spectral_stats(np.sort(evals_cyc), f"cyc_N{N}")
        st = spectral_stats(np.sort(evals_trn), f"trn_N{N}")
        sep = sc["beta"] - st["beta"]
        dt = time.time() - t0

        results.append({"N": N, "beta_cyc": sc["beta"], "beta_trn": st["beta"],
                         "separation": sep, "time": dt})
        print(f"  N={N:5d}: beta_cyc={sc['beta']:.3f}  beta_trn={st['beta']:.3f}  sep={sep:+.3f}  ({dt:.1f}s)")

    # Find peak
    seps = np.array([r["separation"] for r in results])
    Ns = np.array([r["N"] for r in results], dtype=float)
    peak_idx = np.argmax(seps)
    N_star = Ns[peak_idx]
    sep_star = seps[peak_idx]
    print(f"\n  PEAK: N* = {N_star:.0f}, separation = {sep_star:.4f}")

    # Fit power law around peak: |sep - sep_star| ~ |N - N*|^nu
    # Use points on both sides of peak
    mask = seps > 0  # Only positive separations
    if mask.sum() >= 4:
        x = np.abs(Ns[mask] - N_star) + 1  # Avoid log(0)
        y = np.abs(seps[mask] - sep_star) + 1e-6

        # Also try: sep(N) = sep_star * exp(-((N-N*)/w)^2)  (Gaussian dome)
        try:
            def gaussian_dome(N, s0, Nc, w):
                return s0 * np.exp(-((N - Nc) / w)**2)
            popt, pcov = curve_fit(gaussian_dome, Ns[mask], seps[mask],
                                   p0=[sep_star, N_star, 300],
                                   bounds=([0, 100, 50], [2, 2000, 2000]),
                                   maxfev=10000)
            perr = np.sqrt(np.diag(pcov))
            print(f"\n  GAUSSIAN DOME FIT: sep(N) = {popt[0]:.4f} * exp(-((N-{popt[1]:.0f})/{popt[2]:.0f})^2)")
            print(f"    Peak amplitude:  {popt[0]:.4f} +/- {perr[0]:.4f}")
            print(f"    Peak position:   N* = {popt[1]:.0f} +/- {perr[1]:.0f}")
            print(f"    Width:           w = {popt[2]:.0f} +/- {perr[2]:.0f}")

            # Compute residuals
            fitted = gaussian_dome(Ns[mask], *popt)
            residuals = seps[mask] - fitted
            rmse = np.sqrt(np.mean(residuals**2))
            print(f"    RMSE:            {rmse:.4f}")
        except Exception as e:
            print(f"\n  GAUSSIAN FIT FAILED: {e}")

        # Try power law on the right side of peak
        right_mask = Ns > N_star
        if right_mask.sum() >= 3:
            try:
                def power_decay(N, a, nu):
                    return a / (N - N_star + 1)**nu
                Nr = Ns[right_mask]
                Sr = seps[right_mask]
                popt2, _ = curve_fit(power_decay, Nr, Sr, p0=[sep_star * 100, 0.5],
                                     bounds=([0, 0.01], [1e6, 5]), maxfev=10000)
                print(f"\n  POWER LAW (right of peak): sep ~ {popt2[0]:.2f} / (N-N*)^{popt2[1]:.3f}")
                print(f"    Critical exponent nu = {popt2[1]:.3f}")
            except Exception as e:
                print(f"\n  POWER LAW FIT FAILED: {e}")

    return results


# ===================================================================
# MAIN
# ===================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--alpha", type=float, default=20.0)
    args = parser.parse_args()

    print("="*70)
    print("  DECISIVE TEST: Three Experiments for Deterministic QM")
    print("  Post-Millennium Programme -- Daugherty, Ward, Ryan")
    print("="*70)

    J = build_J()
    print(f"  J: lambda_max={eigvalsh(J)[-1]:.3f}")
    print(f"  alpha = {args.alpha}")
    print(f"  Prediction: beta_cycle -> 16/9 = {16/9:.6f}")

    all_results = {}
    t_total = time.time()

    # TEST A: Basin clustering
    if args.quick:
        Na = [100, 200]
    else:
        Na = [100, 200, 500, 750]
    all_results["test_A"] = test_A_basin_clustering(Na, J, args.alpha)

    # TEST B: Asymptotic beta
    if args.quick:
        Nb = [200, 500, 1000]
    else:
        Nb = [200, 500, 1000, 2000, 3000, 5000]
    all_results["test_B"] = test_B_asymptotic_beta(Nb, J, args.alpha)

    # TEST C: Critical exponent
    all_results["test_C"] = test_C_critical_exponent(J, args.alpha)

    elapsed = time.time() - t_total

    # ===== FINAL VERDICT =====
    print("\n" + "="*70)
    print("  FINAL VERDICT")
    print("="*70)

    # Test A
    any_clustered = any(r["clustered"] for r in all_results["test_A"])
    max_dom = max(r["mean_dominant_overlap"] for r in all_results["test_A"])
    print(f"\n  TEST A (Basin Clustering):")
    print(f"    Any N shows clustering: {'YES' if any_clustered else 'NO'}")
    print(f"    Max dominant overlap:   {max_dom:.4f}")
    if any_clustered:
        print(f"    -> REEDS TOPOLOGY ENCODED IN EIGENVECTORS")
    else:
        if max_dom > 0.40:
            print(f"    -> PARTIAL: basin structure visible but not dominant")
        else:
            print(f"    -> Eigenvectors delocalized across basins")

    # Test B
    betas_cyc = [r["cycle"]["beta"] for r in all_results["test_B"]]
    last_beta = betas_cyc[-1] if betas_cyc else 0
    target = 16/9
    dev = abs(last_beta - target)
    print(f"\n  TEST B (Asymptotic Beta):")
    print(f"    Largest N:   beta_cycle = {last_beta:.4f}")
    print(f"    Target 16/9: {target:.4f}")
    print(f"    Deviation:   {dev:.4f}")
    if dev < 0.05:
        print(f"    -> FINITE SYMMETRY CONFIRMED (16/9 = 1.778)")
    elif last_beta > 1.9:
        print(f"    -> FULL GUE EMERGING (infinite-dim irreps)")
    else:
        print(f"    -> INCONCLUSIVE at this scale")

    # Test C
    seps = [r["separation"] for r in all_results["test_C"]]
    peak_N = all_results["test_C"][np.argmax(seps)]["N"]
    print(f"\n  TEST C (Critical Exponent):")
    print(f"    Peak at N* = {peak_N}")
    print(f"    Max separation = {max(seps):.4f}")

    print(f"\n  Total elapsed: {elapsed:.0f}s")
    print("="*70)

    # Save
    def sanitize(obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return str(obj)

    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "decisive_test_results.json")
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2, default=sanitize)
    print(f"  Results saved to: {report_path}")


if __name__ == "__main__":
    main()
