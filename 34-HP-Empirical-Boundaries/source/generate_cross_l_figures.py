#!/usr/bin/env python3
"""Generate new cross-L figures for the unified paper."""
import os, sys, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.format'] = 'pdf'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

OUT = Path(__file__).parent / 'figures'
OUT.mkdir(exist_ok=True)

# Load cross-L analysis results
CROSS_L = json.loads(Path('C:/Users/ripva/rh_blackwell_campaign/cross_l_full_analysis.json').read_text())

# --- Figure 1: 15-pair cross-correlation heatmap ---
def fig_cross_correlation_matrix():
    L_names = ['ζ', 'L(χ_5)', 'L(χ_7)', 'L(χ_{11})', 'L(χ_{13})', 'L(χ_{23})']
    # Build matrix of near-zero mean / far mean ratio per pair
    ratio = np.ones((6, 6))  # diagonal = 1 (self-correlation, trivial)
    pair_lookup = {c['pair']: c for c in CROSS_L['cross_correlations']}
    label_map = {
        'zeta': 'ζ',
        'L_chi_mod5_ord2': 'L(χ_5)',
        'L_chi_mod7_ord2': 'L(χ_7)',
        'L_chi_mod11_ord2': 'L(χ_{11})',
        'L_chi_mod13_ord2': 'L(χ_{13})',
        'L_chi_mod23_ord2': 'L(χ_{23})',
    }
    labels_inv = {v: k for k, v in label_map.items()}
    for i, a in enumerate(L_names):
        for j, b in enumerate(L_names):
            if i >= j: continue
            key = f"{labels_inv[a]} × {labels_inv[b]}"
            if key in pair_lookup:
                c = pair_lookup[key]
                r = c['near_zero_mean'] / c['far_mean'] if c['far_mean'] > 0 else 1
                ratio[i, j] = ratio[j, i] = r
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(ratio, cmap='RdYlGn_r', vmin=0.85, vmax=1.1)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{ratio[i,j]:.2f}", ha='center', va='center',
                     fontsize=9,
                     color='black' if 0.9 < ratio[i,j] < 1.05 else 'white')
    ax.set_xticks(range(6)); ax.set_yticks(range(6))
    ax.set_xticklabels(L_names, rotation=45, ha='right')
    ax.set_yticklabels(L_names)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label(r'$R_2^{A \times B}(|r|<0.5) / R_2^{A \times B}(|r|>1.5)$')
    ax.set_title(r'Cross-pair correlation ratio (1.0 = independent)')
    fig.tight_layout()
    fig.savefig(OUT / 'fig_cross_correlation_matrix.pdf')
    plt.close(fig)

fig_cross_correlation_matrix()
print("  fig_cross_correlation_matrix OK")

# --- Figure 2: union spacing histograms ---
def fig_union_spacings():
    # Get zeros
    zeta = np.loadtxt(r'C:/Users/ripva/Desktop/Physics_Research/Part-VIII_Data-Results/_archive/spectral-data/zeros_1_100000.txt')
    zero_dir = Path('C:/Users/ripva/rh_blackwell_campaign/l_function_zeros')
    dirichlet = {}
    for f in sorted(zero_dir.glob('L_chi_*.json')):
        d = json.loads(f.read_text())
        dirichlet[f'q{d["q"]}'] = np.array(d['zeros'])
    # Zeta alone
    sp_zeta = np.diff(np.sort(zeta[:5000])); sp_zeta = sp_zeta[sp_zeta > 0]; sp_zeta /= np.mean(sp_zeta)
    # Union of 5 Dirichlet
    combined = np.concatenate([arr[:400] for arr in dirichlet.values()])
    combined.sort()
    sp_union = np.diff(combined); sp_union = sp_union[sp_union > 0]; sp_union /= np.mean(sp_union)
    # zeta + dirichlet
    all_z = np.concatenate([zeta[:2000]] + [arr[:400] for arr in dirichlet.values()])
    all_z.sort()
    sp_all = np.diff(all_z); sp_all = sp_all[sp_all > 0]; sp_all /= np.mean(sp_all)

    # Reference: Wigner surmise p(s) = (π/2)s exp(-π s²/4), Poisson p(s) = exp(-s)
    s_grid = np.linspace(0, 4, 200)
    wigner = (np.pi/2) * s_grid * np.exp(-np.pi * s_grid**2 / 4)
    poisson = np.exp(-s_grid)

    fig, axs = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, sp, label in zip(axs, [sp_zeta, sp_union, sp_all],
                              [r'$\zeta$ alone (5000 zeros)',
                               'Union 5 Dirichlet (2000 zeros)',
                               r'$\zeta$(2000) + Dirichlet union']):
        ax.hist(sp, bins=40, range=(0, 4), density=True, alpha=0.7,
                 color='C0', edgecolor='black', linewidth=0.5)
        ax.plot(s_grid, wigner, 'r-', lw=2, label='Wigner (GUE)')
        ax.plot(s_grid, poisson, 'g--', lw=2, label='Poisson')
        ax.set_xlim(0, 4)
        ax.set_xlabel(r'normalised spacing $s$')
        ax.set_title(label, fontsize=10)
        ax.legend(fontsize=8)
    axs[0].set_ylabel(r'density $p(s)$')
    fig.tight_layout()
    fig.savefig(OUT / 'fig_union_spacings.pdf')
    plt.close(fig)

fig_union_spacings()
print("  fig_union_spacings OK")

# --- Figure 3: Full quadrant map with all 13 families ---
def fig_quadrant_full():
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.axvline(0.05, ls='--', color='gray', alpha=0.5)
    ax.axhline(2.0, ls='--', color='gray', alpha=0.5)
    ax.fill_betweenx([2, 5], 0, 0.05, color='C2', alpha=0.15)
    ax.fill_betweenx([0, 2], 0, 0.05, color='C0', alpha=0.15)
    ax.fill_betweenx([2, 5], 0.05, 1.0, color='C1', alpha=0.15)
    ax.fill_betweenx([0, 2], 0.05, 1.0, color='gray', alpha=0.15)

    pts = [
        ('Riemann ζ n=10K', 0.080, 4.91, 'C3', '*', 150),
        ('Riemann ζ n=5K', 0.080, 3.66, 'C3', '*', 100),
        ('Riemann ζ n=2K', 0.092, 2.48, 'C3', '*', 80),
        ('x55+Peierls n=5K', 0.086, 1.66, 'C0', 'o', 100),
        ('x55+Peierls n=2K', 0.086, 1.58, 'C0', 'o', 80),
        ('x55 no flux', 0.506, 1.52, 'C0', 's', 80),
        ('BSD+fixes', 0.765, 1.37, 'C4', 'D', 80),
        ('BSD baseline', 0.946, 1.36, 'C4', 'X', 80),
        ('Mayer transfer', 0.309, 1.00, 'C5', 'v', 80),
        ('Bost-Connes dim 100K', 0.269, 1.08, 'C6', '^', 100),
        ('Hodge K3³', 0.413, 0.75, 'C7', 'p', 80),
        ('Connes S-adelic', 0.321, 1.24, 'C8', 'h', 80),
        ('YM-analog+P', 0.104, 1.00, 'C2', 'P', 80),
        ('YM SU(3) L=5', 0.055, 0.01, 'C2', '^', 80),
        ('log(p)·k synth', 0.30, 2.29, 'C9', 'H', 100),
    ]
    for label, t1, t3, color, marker, size in pts:
        ax.scatter([t1], [t3], s=size, color=color, marker=marker,
                   edgecolor='black', linewidth=0.5, zorder=5)
    # Key labels only
    for label, t1, t3 in [
        ('ζ zeros', 0.085, 3.66),
        ('x55+Peierls', 0.086, 1.62),
        ('BSD', 0.76, 1.37),
        ('Bost-Connes', 0.269, 1.08),
        ('log(p)·k', 0.30, 2.29),
    ]:
        ax.annotate(label, (t1, t3), xytext=(5, 5), textcoords='offset points',
                    fontsize=9, fontweight='bold')

    ax.set_xlim(0.03, 1.0); ax.set_ylim(0, 5.2)
    ax.set_xscale('log')
    ax.set_xlabel(r'$T_1$ KS distance (lower = better)')
    ax.set_ylabel(r'$T_3$ prime-triad ratio (higher = better)')
    ax.set_title(r'Hilbert--P\'olya quadrant map, 13 operator families')
    ax.text(0.035, 4.8, 'C: L-functions', fontsize=11, color='C2', fontweight='bold')
    ax.text(0.3,  4.8, 'B: synth log(p)·k', fontsize=10, color='C1', fontweight='bold')
    ax.text(0.035, 0.2, 'A/D: chaos, no T3', fontsize=10, color='C0', fontweight='bold')
    ax.text(0.3, 0.2, r'$\varnothing$: neither', fontsize=10, color='gray', fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'fig_quadrant_full.pdf')
    plt.close(fig)

fig_quadrant_full()
print("  fig_quadrant_full OK")
print(f"\nGenerated 3 figures in {OUT}")
