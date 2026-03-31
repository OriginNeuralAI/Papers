#!/usr/bin/env python3
"""
Figure generation for Paper 14: R(8,8) Falsification.

Generates publication-quality figures saved to figures/ directory.
Requires: matplotlib, numpy.

Paper 14 — U24 Programme
Daugherty, Ward, Ryan (March 2026)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from math import comb, log10
from pathlib import Path

# ── Style Configuration ──────────────────────────────────────────────────

U24_NAVY = '#1B2A4A'
U24_GOLD = '#C8A951'
PROVED = '#008000'
CONDITIONAL = '#CC6600'
COMPUTATIONAL = '#0000CC'
CONJECTURAL = '#B40000'

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'axes.edgecolor': U24_NAVY,
    'axes.labelcolor': U24_NAVY,
    'xtick.color': U24_NAVY,
    'ytick.color': U24_NAVY,
    'figure.facecolor': 'white',
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)


# ── Figure 1: Scale Comparison Bar Chart ─────────────────────────────────

def fig_scale_comparison():
    """Log-scale comparison of search space, violations, and samples."""
    categories = [
        'Total 8-cliques\n$\\binom{293}{8}$',
        'Paley(293)\nviolations',
        'Samples\ntested',
        'GPU violations\nfound',
    ]
    values = [
        log10(comb(293, 8)),   # ~14.35
        log10(2_310_012),      # ~6.36
        log10(1_500_000),      # ~6.18
        0.01,                  # placeholder for 0
    ]
    colors = [U24_NAVY, CONJECTURAL, COMPUTATIONAL, PROVED]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(categories, values, color=colors, alpha=0.85, width=0.55,
                  edgecolor=U24_NAVY, linewidth=0.8)

    for bar, val in zip(bars, values):
        if val > 0.1:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f'$10^{{{val:.1f}}}$', ha='center', va='bottom',
                    fontsize=10, color=U24_NAVY, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, 0.5,
                    '0', ha='center', va='bottom',
                    fontsize=12, color=PROVED, fontweight='bold')

    ax.set_ylabel('$\\log_{10}$ (count)', color=U24_NAVY)
    ax.set_title('Search Space vs. Sampling Budget at $k = 8$', color=U24_NAVY,
                 fontweight='bold')
    ax.set_ylim(0, 17)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(FIGURES_DIR / 'fig1_scale_comparison.png')
    fig.savefig(FIGURES_DIR / 'fig1_scale_comparison.pdf')
    plt.close(fig)
    print("  [OK] fig1_scale_comparison")


# ── Figure 2: Paley Landscape ────────────────────────────────────────────

def fig_paley_landscape():
    """Paley violation count by prime for k=8."""
    # Data: primes near the boundary
    primes_clean = [241, 257, 269, 277, 281]
    primes_dirty = [293]
    violations_dirty = [2_310_012]

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.scatter(primes_clean, [0] * len(primes_clean), s=80,
               c=PROVED, zorder=5, label='$K_8$-free (valid)', marker='o',
               edgecolors=U24_NAVY, linewidths=0.5)
    ax.scatter(primes_dirty, violations_dirty, s=100,
               c=CONJECTURAL, zorder=5, label='Violations present', marker='^',
               edgecolors=U24_NAVY, linewidths=0.5)

    # Boundary line
    ax.axvline(x=281, color='gray', linestyle='--', alpha=0.6, linewidth=1.5)
    ax.annotate('$p = 281$\n(last clean)', xy=(281, 500_000), fontsize=9,
                ha='right', color=U24_NAVY, fontstyle='italic')
    ax.annotate('2.31M\nviolations', xy=(293, 2_310_012), fontsize=9,
                ha='left', va='bottom', color=CONJECTURAL, fontweight='bold',
                xytext=(296, 2_400_000))

    ax.set_xlabel('Prime $p$', color=U24_NAVY)
    ax.set_ylabel('Monochromatic $K_8$ count', color=U24_NAVY)
    ax.set_title('Paley Graph $K_8$-Violation Landscape', color=U24_NAVY,
                 fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.set_xlim(230, 310)
    ax.set_ylim(-100_000, 2_700_000)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(FIGURES_DIR / 'fig2_paley_landscape.png')
    fig.savefig(FIGURES_DIR / 'fig2_paley_landscape.pdf')
    plt.close(fig)
    print("  [OK] fig2_paley_landscape")


# ── Figure 3: Search Space Scaling ───────────────────────────────────────

def fig_search_space_scaling():
    """Search space vs sampling budget as k grows."""
    ks = [5, 6, 7, 8, 9, 10]
    # Approximate n values at known lower bounds
    ns = [42, 102, 205, 293, 565, 798]
    log_space = [log10(comb(n, k)) for n, k in zip(ns, ks)]
    log_budget = [log10(1_500_000)] * len(ks)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(ks, log_space, 'o-', color=U24_NAVY, linewidth=2, markersize=8,
            label='$\\binom{n_{\\mathrm{bound}}}{k}$ (search space)', zorder=5)
    ax.plot(ks, log_budget, 's--', color=CONJECTURAL, linewidth=2, markersize=7,
            label='$1.5 \\times 10^6$ samples (budget)', zorder=5)

    # Shade the gap
    ax.fill_between(ks, log_budget, log_space, alpha=0.15, color=CONJECTURAL)
    ax.annotate('Coverage gap\ngrows exponentially',
                xy=(8.5, 10), fontsize=10, ha='center', color=CONJECTURAL,
                fontstyle='italic')

    ax.set_xlabel('Clique size $k$', color=U24_NAVY)
    ax.set_ylabel('$\\log_{10}$ (count)', color=U24_NAVY)
    ax.set_title('Search Space Scaling vs. Fixed Sampling Budget',
                 color=U24_NAVY, fontweight='bold')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.set_xticks(ks)
    ax.set_ylim(3, 22)
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(FIGURES_DIR / 'fig3_search_space_scaling.png')
    fig.savefig(FIGURES_DIR / 'fig3_search_space_scaling.pdf')
    plt.close(fig)
    print("  [OK] fig3_search_space_scaling")


# ── Figure 4: Witness Vertex Spacing ─────────────────────────────────────

def fig_witness_spacing():
    """Red K_8 witness vertex positions on the K_293 ring."""
    vertices = [3, 44, 87, 130, 165, 219, 234, 285]
    n = 293

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # Left: circular layout
    theta = [2 * np.pi * v / n for v in vertices]
    x = [np.cos(t) for t in theta]
    y = [np.sin(t) for t in theta]

    # Draw circle
    circle_theta = np.linspace(0, 2 * np.pi, 200)
    ax1.plot(np.cos(circle_theta), np.sin(circle_theta), '-',
             color='lightgray', linewidth=0.5)

    # Draw clique edges
    for i in range(8):
        for j in range(i + 1, 8):
            ax1.plot([x[i], x[j]], [y[i], y[j]], '-',
                     color='red', alpha=0.3, linewidth=0.8)

    # Draw vertices
    ax1.scatter(x, y, s=60, c='red', zorder=5, edgecolors=U24_NAVY, linewidths=0.8)
    for i, v in enumerate(vertices):
        offset = 0.15
        ax1.annotate(str(v), (x[i] * (1 + offset), y[i] * (1 + offset)),
                     fontsize=8, ha='center', va='center', color=U24_NAVY)

    ax1.set_xlim(-1.4, 1.4)
    ax1.set_ylim(-1.4, 1.4)
    ax1.set_aspect('equal')
    ax1.set_title('Red $K_8$ on $K_{293}$ Ring', color=U24_NAVY, fontweight='bold')
    ax1.axis('off')

    # Right: spacing histogram
    spacings = [vertices[i+1] - vertices[i] for i in range(len(vertices)-1)]
    ax2.bar(range(len(spacings)), spacings, color='red', alpha=0.7,
            edgecolor=U24_NAVY, linewidth=0.8)
    ax2.axhline(y=np.mean(spacings), color=U24_NAVY, linestyle='--',
                linewidth=1.5, label=f'Mean = {np.mean(spacings):.1f}')
    ax2.set_xlabel('Gap index', color=U24_NAVY)
    ax2.set_ylabel('Vertex spacing $\\Delta$', color=U24_NAVY)
    ax2.set_title('Witness Vertex Spacings', color=U24_NAVY, fontweight='bold')
    ax2.legend()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig4_witness_spacing.png')
    fig.savefig(FIGURES_DIR / 'fig4_witness_spacing.pdf')
    plt.close(fig)
    print("  [OK] fig4_witness_spacing")


# ── Figure 5: Detection Probability ─────────────────────────────────────

def fig_detection_probability():
    """P(miss) as a function of violation count V."""
    import math

    N_s = 1_500_000
    total = comb(293, 8)
    V_range = np.logspace(0, 10, 200)
    p_miss = [math.exp(-N_s * V / total) if N_s * V / total < 700 else 0
              for V in V_range]

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.semilogx(V_range, p_miss, '-', color=U24_NAVY, linewidth=2)

    # Mark key points
    ax.axhline(y=0.99, color='gray', linestyle=':', alpha=0.5)
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)

    # V=1
    p1 = math.exp(-N_s / total)
    ax.plot(1, p1, 'o', color=CONJECTURAL, markersize=8, zorder=5)
    ax.annotate(f'$V=1$: $P(\\mathrm{{miss}}) \\approx 1$',
                xy=(1, p1), xytext=(5, 0.85),
                fontsize=9, color=CONJECTURAL,
                arrowprops=dict(arrowstyle='->', color=CONJECTURAL, lw=1.2))

    # V=10^6
    p_1m = math.exp(-N_s * 1e6 / total)
    ax.plot(1e6, p_1m, 's', color=CONJECTURAL, markersize=8, zorder=5)
    ax.annotate(f'$V=10^6$: $P = {p_1m:.3f}$',
                xy=(1e6, p_1m), xytext=(3e6, 0.7),
                fontsize=9, color=CONJECTURAL,
                arrowprops=dict(arrowstyle='->', color=CONJECTURAL, lw=1.2))

    # V where P(miss) = 0.5
    V_half = total * math.log(2) / N_s
    ax.axvline(x=V_half, color=PROVED, linestyle='--', alpha=0.6)
    ax.annotate(f'$P=0.5$ at\n$V \\approx 10^{{{log10(V_half):.1f}}}$',
                xy=(V_half, 0.5), xytext=(V_half * 5, 0.35),
                fontsize=9, color=PROVED,
                arrowprops=dict(arrowstyle='->', color=PROVED, lw=1.2))

    ax.set_xlabel('Number of violations $V$', color=U24_NAVY)
    ax.set_ylabel('$P(\\mathrm{miss})$', color=U24_NAVY)
    ax.set_title('Probability of Missing All Violations ($N_s = 1.5 \\times 10^6$)',
                 color=U24_NAVY, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(1, 1e11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(FIGURES_DIR / 'fig5_detection_probability.png')
    fig.savefig(FIGURES_DIR / 'fig5_detection_probability.pdf')
    plt.close(fig)
    print("  [OK] fig5_detection_probability")


# ── Figure 6: Ramsey Bounds Timeline ────────────────────────────────────

def fig_ramsey_bounds():
    """Historical Ramsey R(k,k) lower bounds."""
    data = {
        '$R(3,3)$': {'exact': 6, 'year_lower': 1930, 'year_exact': 1930},
        '$R(4,4)$': {'exact': 18, 'year_lower': 1955, 'year_exact': 1955},
        '$R(5,5)$': {'lower': 43, 'upper': 48, 'year_lower': 2026},
        '$R(6,6)$': {'lower': 102, 'upper': 165, 'year_lower': 1998},
        '$R(7,7)$': {'lower': 205, 'upper': 298, 'year_lower': 1982},
        '$R(8,8)$': {'lower': 282, 'upper': 1870, 'year_lower': 2026},
    }

    labels = list(data.keys())
    lowers = [d.get('lower', d.get('exact', 0)) for d in data.values()]
    uppers = [d.get('upper', d.get('exact', 0)) for d in data.values()]

    fig, ax = plt.subplots(figsize=(8, 5))

    x = range(len(labels))
    bar_width = 0.35

    # Lower bounds
    bars_lower = ax.bar([i - bar_width/2 for i in x], lowers, bar_width,
                        color=PROVED, alpha=0.7, label='Lower bound',
                        edgecolor=U24_NAVY, linewidth=0.8)
    # Upper bounds (only where different)
    bars_upper = ax.bar([i + bar_width/2 for i in x], uppers, bar_width,
                        color=CONJECTURAL, alpha=0.5, label='Upper bound',
                        edgecolor=U24_NAVY, linewidth=0.8)

    # Highlight R(8,8)
    bars_lower[-1].set_facecolor(U24_GOLD)
    bars_lower[-1].set_alpha(0.9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel('$n$', color=U24_NAVY, fontsize=14)
    ax.set_title('Diagonal Ramsey Number Bounds', color=U24_NAVY,
                 fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_yscale('log')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(FIGURES_DIR / 'fig6_ramsey_bounds.png')
    fig.savefig(FIGURES_DIR / 'fig6_ramsey_bounds.pdf')
    plt.close(fig)
    print("  [OK] fig6_ramsey_bounds")


# ── Figure 7: Zero-Core Schematic ───────────────────────────────────────

def fig_zero_core():
    """Zero-core theorem schematic: distributed constraint network."""
    fig, ax = plt.subplots(figsize=(6, 6))

    # Outer ring of constraints
    n_shown = 24
    angles = np.linspace(0, 2 * np.pi, n_shown, endpoint=False)
    radius = 2.2
    cx = radius * np.cos(angles)
    cy = radius * np.sin(angles)

    # Draw connections to center
    for i in range(n_shown):
        ax.plot([cx[i], 0], [cy[i], 0], '-', color='lightgray',
                alpha=0.4, linewidth=0.8)

    # Constraint nodes
    colors = ['red' if i < 12 else 'blue' for i in range(n_shown)]
    for i in range(n_shown):
        ax.scatter(cx[i], cy[i], s=40, c=colors[i], alpha=0.6,
                   edgecolors=U24_NAVY, linewidths=0.5, zorder=5)

    # Center: empty set
    circle = plt.Circle((0, 0), 0.5, fill=True, facecolor='white',
                        edgecolor=U24_NAVY, linewidth=2.5, zorder=10)
    ax.add_patch(circle)
    ax.text(0, 0.05, '$\\varnothing$', fontsize=24, ha='center', va='center',
            color=U24_NAVY, fontweight='bold', zorder=11)
    ax.text(0, -0.3, 'Essential\nCore', fontsize=7, ha='center', va='center',
            color=U24_NAVY, fontstyle='italic', zorder=11)

    # Labels
    ax.text(0, 3.0, '2,480 constraints', fontsize=11, ha='center',
            color=U24_NAVY, fontweight='bold')
    ax.text(0, -3.0, 'Every removal leaves system infeasible',
            fontsize=9, ha='center', color='gray', fontstyle='italic')

    # Red/Blue labels
    ax.text(-2.5, 2.5, '1,235 red $K_4$', fontsize=9, color='red',
            ha='center')
    ax.text(2.5, -2.5, '1,245 blue $K_4$', fontsize=9, color='blue',
            ha='center')

    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect('equal')
    ax.axis('off')

    fig.savefig(FIGURES_DIR / 'fig7_zero_core.png')
    fig.savefig(FIGURES_DIR / 'fig7_zero_core.pdf')
    plt.close(fig)
    print("  [OK] fig7_zero_core")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Paper 14 — Figure Generation")
    print("=" * 50)
    print()

    fig_scale_comparison()
    fig_paley_landscape()
    fig_search_space_scaling()
    fig_witness_spacing()
    fig_detection_probability()
    fig_ramsey_bounds()
    fig_zero_core()

    print()
    print(f"  All figures saved to {FIGURES_DIR}/")
    print("  Formats: PNG (300 DPI) + PDF (vector)")


if __name__ == "__main__":
    main()
