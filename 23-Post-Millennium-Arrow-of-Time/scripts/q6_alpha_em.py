#!/usr/bin/env python3
"""Q6: Derive alpha_EM from Reeds structure."""
import numpy as np
from math import pi, sqrt, log, e
import time

ALPHA_EM_INV = 137.035999177
PHI = (1 + sqrt(5)) / 2
M_ORDER = 2**46 * 3**20 * 5**9 * 7**6 * 11**2 * 13**3 * 17 * 19 * 23 * 29 * 31 * 41 * 47 * 59 * 71
LN_M = log(M_ORDER)
LAMBDA_M = LN_M / (2*pi)

J_EIGS = [5.523, 4.586, 1.322, 0.332, 0.190, 0.123, -0.077, -0.295,
          -0.373, -0.392, -0.470, -0.483, -0.483, -0.483, -0.483, -0.483,
          -0.813, -0.897, -1.076, -1.138, -1.226, -1.364, -1.538]

pool = {
    '9': 9, '7': 7, '1_': 1, '6': 6, '23': 23, '24': 24,
    '125': 125, '3000': 3000, '15': 15, '14': 14,
    'pi': pi, 'phi': PHI, 'e': e,
    'lnM': LN_M, 'lamM': LAMBDA_M,
    'Jmax': 5.523, 'Jgap': 0.937, 'Jrng': 7.061,
    'sqrt6': sqrt(6), '2pi': 2*pi,
}

print("="*70)
print(f"  Q6: ALPHA_EM SEARCH  (target: 1/alpha = {ALPHA_EM_INV:.6f})")
print("="*70)

best = []
keys = list(pool.keys())
vals = list(pool.values())
n = len(keys)

# Two-term combos
for i in range(n):
    for j in range(n):
        if i == j: continue
        a, b = vals[i], vals[j]
        for v in [a*b, a/b if abs(b)>1e-10 else 0, a+b, a-b, a**2/b if abs(b)>1e-10 else 0]:
            if 100 < v < 200:
                err = abs(v - ALPHA_EM_INV) / ALPHA_EM_INV * 100
                if err < 0.5:
                    best.append((f"{keys[i]} op {keys[j]}", v, err))

# Three-term combos (a*b/c, a*b+c, (a+b)*c)
for i in range(n):
    for j in range(n):
        for k in range(n):
            if len({i,j,k}) < 2: continue
            a, b, c = vals[i], vals[j], vals[k]
            tries = []
            if abs(c) > 1e-10: tries.append(a*b/c)
            tries.extend([a*b+c, (a+b)*c, a*b-c, a**2+b*c])
            if abs(b) > 1e-10: tries.append(a**2/b + c)
            for v in tries:
                if 100 < v < 200:
                    err = abs(v - ALPHA_EM_INV) / ALPHA_EM_INV * 100
                    if err < 0.05:
                        best.append((f"{keys[i]},{keys[j]},{keys[k]}", v, err))

best.sort(key=lambda x: x[2])
seen = set()
count = 0
print(f"\n  TOP MATCHES (error < 0.5%):")
for name, v, err in best:
    if count >= 30: break
    key = f"{v:.6f}"
    if key in seen: continue
    seen.add(key)
    print(f"    {v:12.6f}  err={err:.4f}%  from {name}")
    count += 1

# === MANUAL EXPLORATION ===
print(f"\n  === MANUAL EXPLORATION ===")

tests = [
    ("6*23 - 1", 6*23-1),
    ("6*23 - 1 + pi/(24*phi^3)", 137 + pi/(24*PHI**3)),
    ("6*23 - 1 + 1/(24+phi)", 137 + 1/(24+PHI)),
    ("6*23 - 1 + phi^(-7)", 137 + PHI**(-7)),
    ("6*23 - 1 + 9/(7*36)", 137 + 9/(7*36)),
    ("6*23 - 1 + pi^2/(24*23)", 137 + pi**2/(24*23)),
    ("6*23 - 1 + 1/(9*pi)", 137 + 1/(9*pi)),
    ("6*23 - 1 + phi/(24*pi)", 137 + PHI/(24*pi)),
    ("24*pi*phi^2 - 23", 24*pi*PHI**2 - 23),
    ("23*6 - 1 + pi*phi/(24^2)", 137 + pi*PHI/576),
    ("lamM * 7 - 1/phi", LAMBDA_M * 7 - 1/PHI),
    ("9*15 + pi/phi - 1/23", 9*15 + pi/PHI - 1/23),
    ("(24-1)*(6-1) + 12 + pi/(24*phi^2)", 23*5+12+pi/(24*PHI**2)),
    ("3000/23 + 6.68", 3000/23 + 6.68),
    ("125 + 12 + pi/(24*phi^3)", 137 + pi/(24*PHI**3)),
    ("lnM + 12 + pi/(24*phi)", LN_M + 12 + pi/(24*PHI)),
    ("lamM * 7 - phi/pi", LAMBDA_M*7 - PHI/pi),
    ("(9+7)*(6+1) + 24 + 1/phi", 16*7+24+1/PHI),
    ("Jmax*24 + phi", 5.523*24 + PHI),
    ("Jmax*Jrng*pi", 5.523*7.061*pi),
    ("24*pi*phi - 23/phi", 24*pi*PHI - 23/PHI),
]

for name, v in tests:
    err = abs(v - ALPHA_EM_INV) / ALPHA_EM_INV * 100
    marker = " <<<" if err < 0.1 else " <<" if err < 1.0 else ""
    print(f"    {name:40s} = {v:12.6f}  (err = {err:.4f}%){marker}")

# === FRACTIONAL PART ANALYSIS ===
frac = ALPHA_EM_INV - 137
print(f"\n  Fractional part: {frac:.10f}")
print(f"  Candidates for 0.036000:")
for name, v in [
    ("pi^2/(24*phi*23)", pi**2/(24*PHI*23)),
    ("1/(23+phi^2)", 1/(23+PHI**2)),
    ("phi/(24*pi)", PHI/(24*pi)),
    ("1/(9*pi)", 1/(9*pi)),
    ("phi^(-7)", PHI**(-7)),
    ("9/(7*6*6)", 9.0/(7*6*6)),
    ("pi/(24*phi^3)", pi/(24*PHI**3)),
    ("e/(24*pi)", e/(24*pi)),
    ("1/(24+phi+1/phi)", 1/(24+PHI+1/PHI)),
    ("sqrt(6)/(24*phi*pi)", sqrt(6)/(24*PHI*pi)),
]:
    err = abs(v - frac) / frac * 100
    marker = " <<<" if err < 1 else " <<" if err < 5 else ""
    print(f"    {name:30s} = {v:.10f}  (err from 0.036 = {err:.2f}%){marker}")
