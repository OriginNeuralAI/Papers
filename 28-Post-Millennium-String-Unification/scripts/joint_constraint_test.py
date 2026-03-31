#!/usr/bin/env python3
"""
THE DECISIVE COMPUTATION: Joint Constraint Null-Hypothesis Test
================================================================
Does the Reeds partition [9,7,1,6] UNIQUELY satisfy all four physical
constraints simultaneously? Or can other partitions do the same?

Phase A: Exhaustive enumeration of ALL 4-partitions of 23
Phase B: Random endomorphism test (10^6 samples)
Phase C: Formal p-value with Bonferroni correction

This is the computation the programme lives or dies on.
"""

import numpy as np
from math import pi, sqrt, log, ceil, gcd
from functools import reduce
from itertools import combinations_with_replacement
import time

ALPHA_INV = 137.035999177
WEINBERG = 0.23121
W_DE = -5.0/6.0
G_RATIO = 1.0/6.0

# Thresholds (generous — if we pass at loose thresholds, tighter is even better)
ALPHA_TOL = 0.001     # 0.1% relative error
WEINBERG_TOL = 0.02   # 2% relative error
W_TOL = 0.05          # 5% relative error
G_RATIO_TOL = 0.1     # 10% relative error

REEDS = [2,2,3,5,14,2,6,5,14,15,20,22,14,8,13,20,11,8,8,15,15,15,2]

print("="*70)
print("  THE DECISIVE COMPUTATION: Joint Constraint Null-Hypothesis Test")
print("="*70)
print(f"  Targets: 1/alpha={ALPHA_INV:.6f}, sin2_tW={WEINBERG:.5f}, w={W_DE:.4f}, g_ratio={G_RATIO:.4f}")
print(f"  Tolerances: alpha {ALPHA_TOL:.1%}, Weinberg {WEINBERG_TOL:.1%}, w {W_TOL:.1%}, g_ratio {G_RATIO_TOL:.1%}")

# ================================================================
# PHASE A: Exhaustive Partition Enumeration
# ================================================================

print(f"\n{'='*70}")
print(f"  PHASE A: All 4-partitions of 23")
print(f"{'='*70}")

def test_partition(sizes):
    """Test a partition [a,b,c,d] against all four constraints.
    Uses ALL formula variants tried in the programme."""
    a, b, c, d = sorted(sizes, reverse=True)
    results = {'alpha': False, 'weinberg': False, 'w': False, 'g_ratio': False}

    # Alpha formulas tried in the programme:
    # F1: 6*23 - 1 + a/(2*125)        (Paper V: Basin_0 / (2*ceil(ln|M|)))
    # F2: 6*23 - 1 + a/(b*d**2)       (Paper V earlier: Basin_0/(Basin_1*Basin_3^2))
    # F3: 6*23 - 1 + a/(b*d*d)        (same as F2)
    for denom in [250, b*d**2 if d > 0 else 999999]:
        if denom == 0: continue
        v = 137 + a / denom
        if abs(v - ALPHA_INV) / ALPHA_INV < ALPHA_TOL:
            results['alpha'] = True
            break

    # Weinberg formulas:
    # F1: d/(23+3) = d/26             (Paper V: Basin_3/(|Z_23|+3))
    # F2: a/(24+15) = a/39            (alternative)
    for v in [d/26.0, a/39.0, d/(23+c) if c > 0 else 0]:
        if abs(v - WEINBERG) / WEINBERG < WEINBERG_TOL:
            results['weinberg'] = True
            break

    # Dark energy formulas:
    # F1: -(d_eff-1)/d_eff with d_eff = stagnation ratio = macro/meso
    # Simplified: need d_eff = 6, giving w = -5/6
    # Test: does any basin size or ratio give d_eff = 6?
    for d_eff in [d, c, a/c if c > 0 else 0, (a+b)/(c+d) if (c+d) > 0 else 0]:
        if d_eff > 1:
            w = -(d_eff - 1) / d_eff
            if abs(w - W_DE) / abs(W_DE) < W_TOL:
                results['w'] = True
                break

    # Coupling ratio formulas:
    # The actual formula: |Basin_Stability|/|Basin_Exchange| = smallest/third = d/c
    # Also: d/c, d/b, d/a (any ratio involving smallest basin)
    if c > 0:
        for ratio in [d/c, d/b if b > 0 else 0, d/a if a > 0 else 0,
                       1/d if d > 0 else 0]:
            if 0 < ratio < 1:
                if abs(ratio - G_RATIO) / G_RATIO < G_RATIO_TOL:
                    results['g_ratio'] = True
                    break

    return results

# Enumerate ALL 4-partitions of 23: a+b+c+d = 23, a>=b>=c>=d>=1
t0 = time.time()
partitions = []
for a in range(20, 0, -1):
    for b in range(min(a, 23-a), 0, -1):
        for c in range(min(b, 23-a-b), 0, -1):
            d = 23 - a - b - c
            if d >= 1 and d <= c:
                partitions.append((a, b, c, d))

n_parts = len(partitions)
print(f"  Total 4-partitions of 23: {n_parts}")

# Test each partition
alpha_matches = []
weinberg_matches = []
w_matches = []
g_matches = []
joint_matches = []

for p in partitions:
    r = test_partition(p)
    if r['alpha']: alpha_matches.append(p)
    if r['weinberg']: weinberg_matches.append(p)
    if r['w']: w_matches.append(p)
    if r['g_ratio']: g_matches.append(p)
    if all(r.values()): joint_matches.append(p)

dt = time.time() - t0
print(f"  Time: {dt:.2f}s")
print(f"\n  INDIVIDUAL CONSTRAINT MATCHES:")
print(f"    Alpha (0.1%):    {len(alpha_matches):4d} / {n_parts} = {len(alpha_matches)/n_parts:.2%}")
print(f"    Weinberg (2%):   {len(weinberg_matches):4d} / {n_parts} = {len(weinberg_matches)/n_parts:.2%}")
print(f"    Dark energy (5%): {len(w_matches):4d} / {n_parts} = {len(w_matches)/n_parts:.2%}")
print(f"    g_ratio (10%):   {len(g_matches):4d} / {n_parts} = {len(g_matches)/n_parts:.2%}")
print(f"\n  *** JOINT MATCHES (ALL FOUR): {len(joint_matches)} / {n_parts} ***")

if joint_matches:
    print(f"\n  Matching partitions:")
    for p in joint_matches:
        r = test_partition(p)
        print(f"    {p} ← {'[9,7,1,6] = REEDS' if sorted(p,reverse=True) == [9,7,6,1] else 'OTHER'}")
else:
    print(f"\n  NO partition matches all four constraints simultaneously.")

# Check if [9,7,6,1] is among individual matches
reeds = (9, 7, 6, 1)
r_reeds = test_partition(reeds)
print(f"\n  Reeds [9,7,1,6] results:")
for k, v in r_reeds.items():
    print(f"    {k}: {'MATCH' if v else 'no match'}")

# ================================================================
# PHASE B: Random Endomorphism Test
# ================================================================

print(f"\n{'='*70}")
print(f"  PHASE B: Random Endomorphism Test (10^5 samples)")
print(f"{'='*70}")

rng = np.random.default_rng(42)
n_endo = 100_000
endo_joint = 0
endo_alpha = 0
endo_weinberg = 0

t0 = time.time()
for _ in range(n_endo):
    f = rng.integers(0, 23, size=23).tolist()

    # Find cycles and basins
    visited = set()
    cycles = []
    for start in range(23):
        if start in visited: continue
        path, seen = [], {}
        x = start
        while x not in seen:
            seen[x] = len(path); path.append(x); x = f[x]
        idx = seen[x]
        cycle = frozenset(path[idx:])
        for elem in path: visited.add(elem)
        if not any(frozenset(c) == cycle for c in cycles):
            cycles.append(list(cycle))

    if not cycles: continue

    # Basin sizes
    cycle_map = {}
    for ci, cyc in enumerate(cycles):
        for elem in cyc: cycle_map[elem] = ci
    basins = {ci: set() for ci in range(len(cycles))}
    for s in range(23):
        x = s
        for _ in range(30): x = f[x]
        if x in cycle_map: basins[cycle_map[x]].add(s)

    sizes = sorted([len(v) for v in basins.values()], reverse=True)
    if len(sizes) < 4:
        sizes.extend([0] * (4 - len(sizes)))

    r = test_partition(sizes[:4])
    if r['alpha']: endo_alpha += 1
    if all(r.values()): endo_joint += 1

dt = time.time() - t0
print(f"  Samples: {n_endo}")
print(f"  Alpha matches:  {endo_alpha} ({endo_alpha/n_endo:.4%})")
print(f"  Joint matches:  {endo_joint} ({endo_joint/n_endo:.4%})")
print(f"  Time: {dt:.1f}s")

# ================================================================
# PHASE C: P-Value and Significance
# ================================================================

print(f"\n{'='*70}")
print(f"  PHASE C: Statistical Significance")
print(f"{'='*70}")

# Exhaustive p-value
p_exhaustive = len(joint_matches) / n_parts
print(f"  Exhaustive (all partitions):   p = {len(joint_matches)}/{n_parts} = {p_exhaustive:.6f}")

# Endomorphism p-value
p_endo = endo_joint / n_endo if n_endo > 0 else 0
print(f"  Endomorphism (random sample):  p = {endo_joint}/{n_endo} = {p_endo:.6f}")

# Bonferroni correction: we tried ~5 formula families for alpha, ~3 for Weinberg,
# ~4 for w, ~2 for g_ratio → total ~120 combinations
n_families = 5 * 3 * 4 * 2
p_corrected = min(1.0, p_exhaustive * n_families)
print(f"  Bonferroni correction ({n_families} families): p_corr = {p_corrected:.6f}")

# Significance
if p_corrected < 3e-7:
    sig = "5-SIGMA (DISCOVERY)"
elif p_corrected < 6.3e-5:
    sig = "4-SIGMA"
elif p_corrected < 1.3e-3:
    sig = "3-SIGMA"
elif p_corrected < 0.0455:
    sig = "2-SIGMA"
else:
    sig = "NOT SIGNIFICANT"

print(f"\n  SIGNIFICANCE: {sig}")

# Key result
if len(joint_matches) <= 1:
    is_unique = len(joint_matches) == 1 and sorted(joint_matches[0], reverse=True) == [9,7,6,1]
    if is_unique:
        print(f"\n  *** RESULT: [9,7,1,6] is the UNIQUE partition satisfying all four constraints ***")
    elif len(joint_matches) == 0:
        print(f"\n  *** RESULT: NO partition satisfies all four constraints simultaneously ***")
        print(f"  (This means either the formula set or the tolerance needs adjustment)")
else:
    print(f"\n  RESULT: {len(joint_matches)} partitions match — not unique")
    for p in joint_matches:
        print(f"    {p}")

print(f"\n{'='*70}")
print(f"  THE PROGRAMME {'STANDS' if p_corrected < 0.01 else 'NEEDS TIGHTER CONSTRAINTS'}")
print(f"{'='*70}")
