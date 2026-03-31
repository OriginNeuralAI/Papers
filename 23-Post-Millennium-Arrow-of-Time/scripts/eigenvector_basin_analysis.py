#!/usr/bin/env python3
"""
EIGENVECTOR BASIN ANALYSIS: Extracting Reeds Topology from Spectral Data
=========================================================================
Paper I — Post-Millennium Programme

The decisive test: can we RECOVER the Reeds endomorphism's 4-basin partition
[9,7,1,6] directly from the eigenvectors of H_Omega?

If the eigenvectors cluster by basin membership, it proves the spectral
hierarchy is not generic but carries the SPECIFIC Reeds topology.

Experiments:
  1. BASIN PROJECTION: For each eigenvector |psi_k>, compute the probability
     weight on each basin's channels. Do low-energy eigenvectors concentrate
     on specific basins?

  2. PARTICIPATION RATIO: How many channels does each eigenvector occupy?
     Basin-localized states have PR ~ basin_size/23.
     Delocalized states have PR ~ 1.

  3. INVERSE PROBLEM: Given ONLY the eigenvectors, can we reconstruct the
     basin partition [9,7,1,6] without knowing the Reeds table?

  4. CYCLE vs TRANSIENT EIGENVECTOR STRUCTURE: Do cycle-sector eigenvectors
     have different channel-occupation patterns than transient-sector ones?

  5. SPECTRAL FLOW: Track how basin projections change across the eigenvalue
     spectrum (low-energy to high-energy).

  6. ENTANGLEMENT ENTROPY PER EIGENSTATE: Compute S_E for each eigenstate
     across the basin bipartition.

Scales: N = 100, 200, 500, 750, 1000 at alpha = 20.

Usage:
    python eigenvector_basin_analysis.py [--max-N 1000] [--quick]

Authors: Daugherty, Ward, Ryan (March 2026)
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh, norm
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
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
    sorted([0, 1, 2, 3, 5, 7, 11, 16, 22]),  # Basin 0: Creation, size 9
    sorted([4, 8, 12, 13, 14, 17, 18]),        # Basin 1: Perception, size 7
    [6],                                         # Basin 2: Stability, size 1
    sorted([9, 10, 15, 19, 20, 21]),            # Basin 3: Exchange, size 6
]
BASIN_SIZES = [9, 7, 1, 6]
BASIN_NAMES = ["Creation", "Perception", "Stability", "Exchange"]
PERIODIC = sorted([2, 3, 5, 6, 8, 13, 14, 15, 20])
TRANSIENT = sorted(set(range(23)) - set(PERIODIC))
PRIMES_47 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
ALPHA_D = 0.008184

# Element-to-basin map
ELEM_BASIN = {}
for k, basin in enumerate(BASINS):
    for elem in basin:
        ELEM_BASIN[elem] = k


def build_J():
    """Build 23x23 enriched coupling matrix."""
    A = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        A[i, REEDS[i]] = 1.0
    B = np.zeros((N_ELEM, N_ELEM))
    for i in range(N_ELEM):
        for j in range(N_ELEM):
            B[i, j] = 1.0 if ELEM_BASIN[i] == ELEM_BASIN[j] else -0.5
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
    """Build H = alpha * J (x) I + I (x) T + V_Z."""
    H = alpha_scale * np.kron(J, np.eye(N))
    T = np.diag(np.array([n * n / 2.0 for n in range(N)]))
    H += np.kron(np.eye(N_ELEM), T)
    alpha = ALPHA_D * alpha_scale
    V_Z = np.zeros((N, N))
    for p in PRIMES_47:
        w = alpha / (2.0 * np.sqrt(p))
        for n in range(N - p):
            V_Z[n, n + p] += w
            V_Z[n + p, n] += w
    H += np.kron(np.eye(N_ELEM), V_Z)
    return (H + H.T) / 2.0


# ===================================================================
# BASIN PROJECTION
# ===================================================================

def basin_weights(psi, N):
    """
    For eigenvector psi (length 23*N), compute probability weight on each basin.
    Returns array of shape (4,) summing to ~1.
    """
    weights = np.zeros(4)
    for k, basin in enumerate(BASINS):
        for ch in basin:
            start = ch * N
            end = (ch + 1) * N
            weights[k] += np.sum(psi[start:end]**2)
    return weights


def channel_weights(psi, N):
    """
    For eigenvector psi, compute probability per channel (23 values).
    """
    w = np.zeros(N_ELEM)
    for ch in range(N_ELEM):
        start = ch * N
        end = (ch + 1) * N
        w[ch] = np.sum(psi[start:end]**2)
    return w


def participation_ratio(weights):
    """
    Participation ratio: PR = 1 / sum(w_k^2).
    PR = 1 means localized on one basin, PR = 4 means uniform.
    """
    w = weights / weights.sum()
    return 1.0 / np.sum(w**2)


def channel_participation_ratio(cw):
    """PR over 23 channels. PR=1 = single channel, PR=23 = uniform."""
    w = cw / cw.sum()
    return 1.0 / np.sum(w**2)


def shannon_entropy(weights):
    """Shannon entropy of basin weights."""
    w = weights / weights.sum()
    w = w[w > 1e-30]
    return -np.sum(w * np.log(w))


# ===================================================================
# EXPERIMENT 1: BASIN PROJECTION ACROSS SPECTRUM
# ===================================================================

def exp1_basin_projection(N, J, alpha=20.0):
    """Compute basin weights for all eigenvectors."""
    print(f"\n  === EXP 1: BASIN PROJECTION (N={N}, dim={N_ELEM*N}, alpha={alpha}) ===")

    t0 = time.time()
    H = build_H(N, J, alpha_scale=alpha)
    t_build = time.time() - t0
    print(f"  Build: {t_build:.1f}s", flush=True)

    t1 = time.time()
    evals, evecs = eigh(H)
    t_diag = time.time() - t1
    del H
    print(f"  Diag:  {t_diag:.1f}s ({len(evals)} eigenvalues)", flush=True)

    n_evals = len(evals)

    # Compute basin weights for all eigenvectors
    all_bw = np.zeros((n_evals, 4))
    all_cw = np.zeros((n_evals, N_ELEM))
    all_pr = np.zeros(n_evals)
    all_cpr = np.zeros(n_evals)
    all_se = np.zeros(n_evals)

    for i in range(n_evals):
        psi = evecs[:, i]
        bw = basin_weights(psi, N)
        cw = channel_weights(psi, N)
        all_bw[i] = bw
        all_cw[i] = cw
        all_pr[i] = participation_ratio(bw)
        all_cpr[i] = channel_participation_ratio(cw)
        all_se[i] = shannon_entropy(bw)

    # Summary by energy quartile
    q_size = n_evals // 4
    quartile_names = ["Bottom 25%", "Q2 (25-50%)", "Q3 (50-75%)", "Top 25%"]

    print(f"\n  BASIN WEIGHTS BY ENERGY QUARTILE:")
    print(f"  {'Quartile':>14s}  {'Creation':>9s}  {'Perception':>11s}  {'Stability':>10s}  {'Exchange':>9s}  {'PR':>5s}  {'S_H':>5s}")
    print(f"  {'-'*70}")

    quartile_data = []
    for q in range(4):
        start = q * q_size
        end = (q + 1) * q_size if q < 3 else n_evals
        mean_bw = all_bw[start:end].mean(axis=0)
        mean_pr = all_pr[start:end].mean()
        mean_se = all_se[start:end].mean()
        print(f"  {quartile_names[q]:>14s}  {mean_bw[0]:9.4f}  {mean_bw[1]:11.4f}  {mean_bw[2]:10.4f}  {mean_bw[3]:9.4f}  {mean_pr:5.2f}  {mean_se:5.3f}")
        quartile_data.append({
            "quartile": quartile_names[q],
            "mean_basin_weights": mean_bw.tolist(),
            "mean_PR": float(mean_pr),
            "mean_Shannon": float(mean_se),
        })

    # Expected uniform weights
    uniform = np.array(BASIN_SIZES) / N_ELEM
    print(f"  {'Uniform':>14s}  {uniform[0]:9.4f}  {uniform[1]:11.4f}  {uniform[2]:10.4f}  {uniform[3]:9.4f}  {4.00:5.2f}  {1.279:5.3f}")

    # Find most basin-localized eigenstates
    print(f"\n  MOST BASIN-LOCALIZED EIGENSTATES (lowest PR):")
    sorted_by_pr = np.argsort(all_pr)
    for rank in range(min(10, n_evals)):
        idx = sorted_by_pr[rank]
        dom_basin = np.argmax(all_bw[idx])
        print(f"    #{rank+1}: eigenvalue={evals[idx]:+10.4f}  PR={all_pr[idx]:.3f}  dominant={BASIN_NAMES[dom_basin]} ({all_bw[idx, dom_basin]:.3f})  S_H={all_se[idx]:.3f}")

    # Find most Stability-concentrated (photon-like)
    stab_weights = all_bw[:, 2]  # Basin 2 = Stability
    top_stab = np.argsort(stab_weights)[::-1][:5]
    print(f"\n  MOST STABILITY-CONCENTRATED (photon-like):")
    for idx in top_stab:
        print(f"    eigenvalue={evals[idx]:+10.4f}  Stability_weight={stab_weights[idx]:.4f}  PR={all_pr[idx]:.3f}")

    return {
        "N": N, "dim": N_ELEM * N, "alpha": alpha,
        "n_eigenvalues": n_evals,
        "quartile_data": quartile_data,
        "build_time": t_build, "diag_time": t_diag,
        "mean_PR": float(all_pr.mean()),
        "min_PR": float(all_pr.min()),
        "mean_channel_PR": float(all_cpr.mean()),
        "all_basin_weights": all_bw,  # for further analysis
        "all_channel_weights": all_cw,
        "all_PR": all_pr,
        "eigenvalues": evals,
    }


# ===================================================================
# EXPERIMENT 2: INVERSE PROBLEM — RECOVER BASINS FROM EIGENVECTORS
# ===================================================================

def exp2_inverse_problem(result):
    """
    Given ONLY eigenvector channel weights, reconstruct basin partition.
    Uses hierarchical clustering on channel correlation matrix.
    """
    N = result["N"]
    all_cw = result["all_channel_weights"]
    n_evals = all_cw.shape[0]

    print(f"\n  === EXP 2: INVERSE PROBLEM — RECOVER BASINS FROM EIGENVECTORS (N={N}) ===")

    # Build channel-channel correlation matrix from eigenvectors
    # C[i,j] = correlation of channel weights across all eigenstates
    C = np.corrcoef(all_cw.T)  # 23 x 23 correlation matrix

    print(f"  Channel correlation matrix: {C.shape}")
    print(f"  Mean intra-basin correlation vs inter-basin:")

    # Ground truth: compute mean correlation within vs between basins
    intra_corrs = []
    inter_corrs = []
    for i in range(N_ELEM):
        for j in range(i + 1, N_ELEM):
            if ELEM_BASIN[i] == ELEM_BASIN[j]:
                intra_corrs.append(C[i, j])
            else:
                inter_corrs.append(C[i, j])

    mean_intra = np.mean(intra_corrs) if intra_corrs else 0
    mean_inter = np.mean(inter_corrs) if inter_corrs else 0
    print(f"    Intra-basin mean correlation: {mean_intra:.4f} (n={len(intra_corrs)})")
    print(f"    Inter-basin mean correlation: {mean_inter:.4f} (n={len(inter_corrs)})")
    print(f"    Separation ratio: {mean_intra / max(abs(mean_inter), 1e-10):.2f}x")

    # Hierarchical clustering to recover basins
    dist = 1.0 - C  # Convert correlation to distance
    np.fill_diagonal(dist, 0)
    dist = np.maximum(dist, 0)  # Ensure non-negative
    dist_condensed = pdist(dist)  # Condensed distance matrix

    Z = linkage(dist_condensed, method='ward')
    clusters_4 = fcluster(Z, t=4, criterion='maxclust')
    clusters_4 = clusters_4 - 1  # 0-indexed

    print(f"\n  CLUSTERING RESULT (4 clusters):")
    recovered_basins = {}
    for ch in range(N_ELEM):
        cl = clusters_4[ch]
        if cl not in recovered_basins:
            recovered_basins[cl] = []
        recovered_basins[cl].append(ch)

    # Match recovered clusters to true basins
    # Try all permutations of cluster labels
    from itertools import permutations
    true_basins = [set(b) for b in BASINS]
    best_match = 0
    best_perm = None

    for perm in permutations(range(4)):
        match = 0
        for k in range(4):
            recovered_set = set(recovered_basins.get(perm[k], []))
            match += len(recovered_set & true_basins[k])
        if match > best_match:
            best_match = match
            best_perm = perm

    accuracy = best_match / N_ELEM
    print(f"  Best permutation match: {best_match}/{N_ELEM} = {accuracy:.1%}")

    print(f"\n  RECOVERED vs TRUE BASINS (best permutation):")
    for k in range(4):
        rec = sorted(recovered_basins.get(best_perm[k], []))
        true = sorted(BASINS[k])
        match = set(rec) & set(true)
        extra = set(rec) - set(true)
        missing = set(true) - set(rec)
        status = "EXACT" if rec == true else f"+{sorted(extra)} -{sorted(missing)}"
        print(f"    {BASIN_NAMES[k]:>12s}: recovered={rec}  true={true}  [{status}]")

    print(f"\n  Basin recovery accuracy: {accuracy:.1%}")
    print(f"  Status: {'PASS (>=90%)' if accuracy >= 0.90 else 'PARTIAL' if accuracy >= 0.70 else 'FAIL'}")

    return {
        "N": N,
        "mean_intra_corr": float(mean_intra),
        "mean_inter_corr": float(mean_inter),
        "separation_ratio": float(mean_intra / max(abs(mean_inter), 1e-10)),
        "accuracy": float(accuracy),
        "best_match": best_match,
        "recovered_basins": {str(k): sorted(v) for k, v in recovered_basins.items()},
        "passed": accuracy >= 0.90,
    }


# ===================================================================
# EXPERIMENT 3: CYCLE vs TRANSIENT EIGENVECTOR STRUCTURE
# ===================================================================

def exp3_cycle_vs_transient(result):
    """Compare eigenvector properties for cycle vs transient channels."""
    N = result["N"]
    all_cw = result["all_channel_weights"]
    evals = result["eigenvalues"]
    n_evals = len(evals)

    print(f"\n  === EXP 3: CYCLE vs TRANSIENT EIGENVECTOR STRUCTURE (N={N}) ===")

    # For each eigenstate: fraction of weight on cycle channels vs transient
    cycle_set = set(PERIODIC)
    trans_set = set(TRANSIENT)

    cycle_frac = np.zeros(n_evals)
    trans_frac = np.zeros(n_evals)
    for i in range(n_evals):
        cw = all_cw[i]
        cycle_frac[i] = sum(cw[ch] for ch in cycle_set)
        trans_frac[i] = sum(cw[ch] for ch in trans_set)

    # Expected from counting: cycle = 9/23 = 0.391, trans = 14/23 = 0.609
    expected_cycle = 9.0 / 23.0
    expected_trans = 14.0 / 23.0

    # By energy quartile
    q_size = n_evals // 4
    print(f"\n  {'Quartile':>14s}  {'Cycle frac':>11s}  {'Trans frac':>11s}  {'Excess cycle':>13s}")
    print(f"  {'-'*55}")

    quartile_results = []
    for q in range(4):
        s = q * q_size
        e = (q + 1) * q_size if q < 3 else n_evals
        mc = cycle_frac[s:e].mean()
        mt = trans_frac[s:e].mean()
        excess = mc - expected_cycle
        names = ["Bottom 25%", "Q2 (25-50%)", "Q3 (50-75%)", "Top 25%"]
        print(f"  {names[q]:>14s}  {mc:11.4f}  {mt:11.4f}  {excess:+13.4f}")
        quartile_results.append({
            "quartile": names[q],
            "mean_cycle_frac": float(mc),
            "mean_trans_frac": float(mt),
            "excess_cycle": float(excess),
        })

    print(f"  {'Expected':>14s}  {expected_cycle:11.4f}  {expected_trans:11.4f}  {0.0:+13.4f}")

    # Find eigenstates most concentrated on cycle channels
    sorted_by_cycle = np.argsort(cycle_frac)[::-1]
    print(f"\n  TOP 5 CYCLE-CONCENTRATED EIGENSTATES:")
    for rank in range(5):
        idx = sorted_by_cycle[rank]
        print(f"    eigenvalue={evals[idx]:+10.4f}  cycle_frac={cycle_frac[idx]:.4f}  trans_frac={trans_frac[idx]:.4f}")

    # Find eigenstates most concentrated on transient channels
    sorted_by_trans = np.argsort(trans_frac)[::-1]
    print(f"\n  TOP 5 TRANSIENT-CONCENTRATED EIGENSTATES:")
    for rank in range(5):
        idx = sorted_by_trans[rank]
        print(f"    eigenvalue={evals[idx]:+10.4f}  cycle_frac={cycle_frac[idx]:.4f}  trans_frac={trans_frac[idx]:.4f}")

    # Statistics
    mean_excess = cycle_frac.mean() - expected_cycle
    std_cycle = cycle_frac.std()
    max_cycle = cycle_frac.max()
    max_trans = trans_frac.max()

    print(f"\n  GLOBAL STATISTICS:")
    print(f"    Mean cycle excess:     {mean_excess:+.6f}")
    print(f"    Std of cycle fraction: {std_cycle:.6f}")
    print(f"    Max cycle fraction:    {max_cycle:.4f} (expected: {expected_cycle:.4f})")
    print(f"    Max trans fraction:    {max_trans:.4f} (expected: {expected_trans:.4f})")

    return {
        "N": N,
        "expected_cycle": expected_cycle,
        "expected_trans": expected_trans,
        "mean_excess_cycle": float(mean_excess),
        "std_cycle_frac": float(std_cycle),
        "max_cycle_frac": float(max_cycle),
        "max_trans_frac": float(max_trans),
        "quartile_results": quartile_results,
    }


# ===================================================================
# EXPERIMENT 4: ENTANGLEMENT ENTROPY PER EIGENSTATE
# ===================================================================

def exp4_eigenstate_entanglement(result):
    """Compute entanglement entropy for each eigenstate across basin bipartition."""
    N = result["N"]
    all_bw = result["all_basin_weights"]
    evals = result["eigenvalues"]
    n_evals = len(evals)

    print(f"\n  === EXP 4: EIGENSTATE ENTANGLEMENT ENTROPY (N={N}) ===")

    # Basin Shannon entropy as proxy for entanglement
    entropies = np.zeros(n_evals)
    for i in range(n_evals):
        bw = all_bw[i]
        bw = bw / bw.sum()
        bw = bw[bw > 1e-30]
        entropies[i] = -np.sum(bw * np.log(bw))

    max_entropy = np.log(4)  # Uniform over 4 basins

    # By energy quartile
    q_size = n_evals // 4
    print(f"\n  {'Quartile':>14s}  {'Mean S_H':>9s}  {'Min S_H':>9s}  {'Max S_H':>9s}  {'Frac < 1.0':>11s}")
    print(f"  {'-'*60}")
    names = ["Bottom 25%", "Q2 (25-50%)", "Q3 (50-75%)", "Top 25%"]

    for q in range(4):
        s = q * q_size
        e = (q + 1) * q_size if q < 3 else n_evals
        ent_q = entropies[s:e]
        frac_low = np.mean(ent_q < 1.0)
        print(f"  {names[q]:>14s}  {ent_q.mean():9.4f}  {ent_q.min():9.4f}  {ent_q.max():9.4f}  {frac_low:11.1%}")

    print(f"  {'Max possible':>14s}  {max_entropy:9.4f}")
    print(f"\n  Overall: mean={entropies.mean():.4f}, std={entropies.std():.4f}, min={entropies.min():.4f}")

    # Correlation between eigenvalue and entanglement
    corr = np.corrcoef(evals, entropies)[0, 1]
    print(f"  Correlation(eigenvalue, entropy): r = {corr:.4f}")

    return {
        "N": N,
        "mean_entropy": float(entropies.mean()),
        "std_entropy": float(entropies.std()),
        "min_entropy": float(entropies.min()),
        "max_entropy_observed": float(entropies.max()),
        "max_entropy_possible": float(max_entropy),
        "eigenvalue_entropy_correlation": float(corr),
    }


# ===================================================================
# EXPERIMENT 5: SCALING STUDY
# ===================================================================

def exp5_scaling(N_values, J, alpha=20.0):
    """Run basin projection + inverse problem at multiple scales."""
    print(f"\n{'='*70}")
    print(f"  EXP 5: SCALING STUDY (alpha={alpha})")
    print(f"{'='*70}")

    scaling_results = []

    for N in N_values:
        print(f"\n{'='*70}")
        print(f"  N = {N} (dim = {N_ELEM * N})")
        print(f"{'='*70}")

        t0 = time.time()

        # Full eigenvector analysis
        r1 = exp1_basin_projection(N, J, alpha=alpha)

        # Inverse problem
        r2 = exp2_inverse_problem(r1)

        # Cycle vs transient
        r3 = exp3_cycle_vs_transient(r1)

        # Entanglement
        r4 = exp4_eigenstate_entanglement(r1)

        # Clean up large arrays before storing
        entry = {
            "N": N,
            "dim": N_ELEM * N,
            "total_time": time.time() - t0,
            "basin_projection": {
                "mean_PR": r1["mean_PR"],
                "min_PR": r1["min_PR"],
                "quartile_data": r1["quartile_data"],
            },
            "inverse_problem": {
                "accuracy": r2["accuracy"],
                "intra_corr": r2["mean_intra_corr"],
                "inter_corr": r2["mean_inter_corr"],
                "separation_ratio": r2["separation_ratio"],
                "passed": r2["passed"],
            },
            "cycle_vs_transient": {
                "mean_excess_cycle": r3["mean_excess_cycle"],
                "max_cycle_frac": r3["max_cycle_frac"],
                "quartile_results": r3["quartile_results"],
            },
            "entanglement": {
                "mean_entropy": r4["mean_entropy"],
                "min_entropy": r4["min_entropy"],
                "eigenvalue_entropy_corr": r4["eigenvalue_entropy_correlation"],
            },
        }
        scaling_results.append(entry)

        # Free memory
        del r1["all_basin_weights"], r1["all_channel_weights"], r1["all_PR"], r1["eigenvalues"]

    # Summary table
    print(f"\n{'='*70}")
    print(f"  SCALING SUMMARY")
    print(f"{'='*70}")
    print(f"  {'N':>6s}  {'dim':>8s}  {'Accuracy':>9s}  {'Intra/Inter':>12s}  {'Min PR':>7s}  {'Mean S_H':>9s}  {'Time':>6s}")
    print(f"  {'-'*65}")
    for r in scaling_results:
        ip = r["inverse_problem"]
        bp = r["basin_projection"]
        ent = r["entanglement"]
        print(f"  {r['N']:6d}  {r['dim']:8d}  {ip['accuracy']:9.1%}  {ip['separation_ratio']:12.2f}x  {bp['min_PR']:7.3f}  {ent['mean_entropy']:9.4f}  {r['total_time']:5.0f}s")

    return scaling_results


# ===================================================================
# MAIN
# ===================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-N", type=int, default=500)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--alpha", type=float, default=20.0)
    args = parser.parse_args()

    print("=" * 70)
    print("  EIGENVECTOR BASIN ANALYSIS")
    print("  Extracting Reeds Topology from Spectral Data")
    print("  Post-Millennium Programme -- Daugherty, Ward, Ryan")
    print("=" * 70)

    J = build_J()
    J_eigs = eigvalsh(J)
    print(f"  J: lambda_max={J_eigs[-1]:.3f}, gap={J_eigs[-1]-J_eigs[-2]:.3f}")
    print(f"  alpha = {args.alpha}")

    if args.quick:
        N_values = [50, 100]
    else:
        N_values = [100, 200, 500]
        if args.max_N >= 750:
            N_values.append(750)
        if args.max_N >= 1000:
            N_values.append(1000)

    t_total = time.time()
    results = exp5_scaling(N_values, J, alpha=args.alpha)
    elapsed = time.time() - t_total

    print(f"\n  Total elapsed: {elapsed:.0f}s")

    # Save results
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "eigenvector_analysis_results.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2,
                  default=lambda o: float(o) if hasattr(o, '__float__') else str(o))
    print(f"  Results saved to: {report_path}")


if __name__ == "__main__":
    main()
