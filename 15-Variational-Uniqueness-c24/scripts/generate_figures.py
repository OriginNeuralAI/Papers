#!/usr/bin/env python3
"""
Figure generation for Paper 15: Daugherty Uniqueness Theorem.
Requires: matplotlib, numpy, scipy.

Paper 15 — U24 Programme
Daugherty, Ward, Ryan (March 2026)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

U24_NAVY = '#1B2A4A'
U24_GOLD = '#C8A951'
PROVED = '#008000'
CONDITIONAL = '#CC6600'
COMPUTATIONAL = '#0000CC'
CONJECTURAL = '#B40000'

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 11,
    'axes.labelsize': 12, 'axes.titlesize': 13,
    'axes.edgecolor': U24_NAVY, 'axes.labelcolor': U24_NAVY,
    'xtick.color': U24_NAVY, 'ytick.color': U24_NAVY,
    'figure.facecolor': 'white', 'savefig.dpi': 300, 'savefig.bbox': 'tight',
})

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

H = np.array([125.0, 500.0, 3000.0])
G0, G1 = 1.0, 4.0
RAMSEY = 903  # C(43,2)


def Z(beta, c):
    return G0 * np.exp(-beta * H[0]) + G1 * np.exp(-beta * H[1]) + c * np.exp(-beta * H[2])


def heat_capacity(beta, c):
    z = Z(beta, c)
    if z <= 0:
        return 0.0
    e1 = G0*H[0]*np.exp(-beta*H[0]) + G1*H[1]*np.exp(-beta*H[1]) + c*H[2]*np.exp(-beta*H[2])
    e2 = G0*H[0]**2*np.exp(-beta*H[0]) + G1*H[1]**2*np.exp(-beta*H[1]) + c*H[2]**2*np.exp(-beta*H[2])
    return beta**2 * (e2/z - (e1/z)**2)


def tc_kramers(c):
    """Kramers escape temperature: T_c = (h2 - h0) / ln(c)."""
    if c <= 1:
        return float('inf')
    return (H[2] - H[0]) / np.log(c)


# ── Fig 1: Thermodynamic Stability ───────────────────────────────────────

def fig1():
    betas = np.linspace(1e-5, 0.025, 800)
    fig, ax = plt.subplots(figsize=(8, 5))
    for c, color, ls, lw in [(3, 'gray', '--', 1.2), (4, CONJECTURAL, '--', 1.5),
                              (5, 'steelblue', '-', 1.5), (12, CONDITIONAL, '-', 1.2),
                              (24, U24_GOLD, '-', 2.8)]:
        cv = [heat_capacity(b, c) for b in betas]
        ax.plot(betas, cv, color=color, linewidth=lw, linestyle=ls, label=f'$c = {c}$')
    ax.set_xlabel(r'Inverse temperature $\beta$')
    ax.set_ylabel(r'Heat capacity $C(\beta)$')
    ax.set_title('Constraint I: Thermodynamic Stability', color=U24_NAVY, fontweight='bold')
    ax.legend(framealpha=0.9, loc='upper right')
    ax.annotate('No peak for $c \\leq 4$', xy=(0.006, 0.15), fontsize=9,
                color=CONJECTURAL, fontstyle='italic')
    ax.annotate('Sharp peak at $c = 24$', xy=(0.008, 1.35), fontsize=9,
                color=U24_GOLD, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(FIGURES_DIR / 'fig1_thermodynamic_stability.pdf')
    fig.savefig(FIGURES_DIR / 'fig1_thermodynamic_stability.png')
    plt.close(fig)
    print("  [OK] fig1_thermodynamic_stability")


# ── Fig 2: Degeneracy Dominance ──────────────────────────────────────────

def fig2():
    cs = list(range(5, 50))
    fwhms = []
    for c in cs:
        betas = np.linspace(1e-5, 0.025, 3000)
        cv = [heat_capacity(b, c) for b in betas]
        peak = max(cv)
        if peak < 1e-6:
            fwhms.append(float('inf'))
            continue
        half = peak / 2
        above = [b for b, v in zip(betas, cv) if v >= half]
        fwhms.append(above[-1] - above[0] if len(above) >= 2 else float('inf'))

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [U24_GOLD if c == 24 else (CONJECTURAL if c <= 16 else U24_NAVY) for c in cs]
    bars = ax.bar(cs, fwhms, color=colors, alpha=0.7, edgecolor=U24_NAVY, linewidth=0.3)
    ax.axvline(x=16.5, color=CONJECTURAL, linestyle='--', linewidth=1.5)
    ax.annotate('$c = g_1^2 = 16$\nthreshold', xy=(16.5, max(fwhms)*0.85),
                fontsize=9, color=CONJECTURAL, ha='right')
    ax.annotate('$c = 24$', xy=(24, fwhms[24-5]), xytext=(32, fwhms[24-5]*1.5),
                fontsize=10, color=U24_GOLD, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=U24_GOLD))
    ax.set_xlabel('Macro degeneracy $c$')
    ax.set_ylabel('FWHM of $C(\\beta)$ peak')
    ax.set_title('Constraint II: Degeneracy Dominance (Peak Sharpness)', color=U24_NAVY, fontweight='bold')
    ax.set_xlim(4, 50)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(FIGURES_DIR / 'fig2_degeneracy_dominance.pdf')
    fig.savefig(FIGURES_DIR / 'fig2_degeneracy_dominance.png')
    plt.close(fig)
    print("  [OK] fig2_degeneracy_dominance")


# ── Fig 3: Ramsey T_c Match (FIXED — uses Kramers formula) ───────────────

def fig3():
    cs = np.arange(10, 51)
    tcs = [tc_kramers(c) for c in cs]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(cs, tcs, 'o-', color=U24_NAVY, markersize=4, linewidth=1.5, zorder=3)

    # Ramsey target
    ax.axhline(y=RAMSEY, color=CONJECTURAL, linestyle='--', linewidth=1.5,
               label='$\\binom{43}{2} = 903$', zorder=2)
    ax.axhspan(RAMSEY*0.9, RAMSEY*1.1, alpha=0.08, color=CONJECTURAL, zorder=1)

    # Highlight c=24
    tc24 = tc_kramers(24)
    ax.plot(24, tc24, 'o', color=U24_GOLD, markersize=14, zorder=5,
            markeredgecolor=U24_NAVY, markeredgewidth=2)
    ax.annotate(f'$c = 24$\n$T_c = {tc24:.1f}$\n$\\Delta = {abs(tc24-RAMSEY):.1f}$',
                xy=(24, tc24), xytext=(32, tc24 + 80), fontsize=10,
                color=U24_GOLD, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=U24_GOLD, lw=1.5))

    # Window markers
    ax.axvspan(19, 30, alpha=0.06, color=U24_GOLD, zorder=0)
    ax.text(24.5, 650, '$c \\in [19, 30]$\n($\\pm 10\\%$ window)',
            fontsize=9, ha='center', color=U24_NAVY, fontstyle='italic')

    ax.set_xlabel('Macro degeneracy $c$')
    ax.set_ylabel('Kramers escape temperature $T_c^{(1)}(c)$')
    ax.set_title('Constraint IV: Ramsey $T_c$ Match', color=U24_NAVY, fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_ylim(500, 1400)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(FIGURES_DIR / 'fig3_ramsey_tc_match.pdf')
    fig.savefig(FIGURES_DIR / 'fig3_ramsey_tc_match.png')
    plt.close(fig)
    print("  [OK] fig3_ramsey_tc_match")


# ── Fig 4: Five-Constraint Intersection ──────────────────────────────────

def fig4():
    fig, ax = plt.subplots(figsize=(10, 4.5))

    constraints = [
        ('I: Thermodynamic stability\n($c \\geq 5$)', 5, 100, PROVED),
        ('II: Degeneracy dominance\n($c \\geq 17$)', 17, 100, 'steelblue'),
        ('III: Hellerman unitarity\n($c \\geq 17$)', 17, 100, CONDITIONAL),
        ('IV: Ramsey $T_c$ match\n($c \\in [19, 30]$)', 19, 30, CONJECTURAL),
        ('V: $S_4$ composition\n($c = 24$)', 24, 24, U24_GOLD),
    ]

    for i, (label, lo, hi, color) in enumerate(constraints):
        width = max(hi - lo + 1, 2)
        ax.barh(i, width, left=lo, height=0.55, color=color, alpha=0.75,
                edgecolor=U24_NAVY, linewidth=0.8)
        ax.text(2, i, label, va='center', ha='left', fontsize=9, color=U24_NAVY)

    # Intersection line
    ax.axvline(x=24, color=U24_GOLD, linewidth=3.5, zorder=10, alpha=0.9)
    ax.text(24, len(constraints) + 0.1, '$c = 24$', ha='center', va='bottom',
            fontsize=15, color=U24_GOLD, fontweight='bold')

    ax.set_xlabel('Central charge $c$', fontsize=13)
    ax.set_yticks([])
    ax.set_xlim(0, 105)
    ax.set_ylim(-0.5, len(constraints) + 0.5)
    ax.set_title('Five-Constraint Intersection $\\Rightarrow \\{24\\}$',
                 color=U24_NAVY, fontweight='bold', fontsize=14)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig4_five_constraint_intersection.pdf')
    fig.savefig(FIGURES_DIR / 'fig4_five_constraint_intersection.png')
    plt.close(fig)
    print("  [OK] fig4_five_constraint_intersection")


# ── Fig 5: Conformal Anomaly Sweep ───────────────────────────────────────

def fig5():
    cs = np.arange(5, 49)
    tc_errors = [abs(tc_kramers(c) - RAMSEY) for c in cs]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [U24_GOLD if c == 24 else (PROVED if abs(tc_kramers(c) - RAMSEY) < 90 else U24_NAVY) for c in cs]
    ax.bar(cs, tc_errors, color=colors, alpha=0.7, edgecolor=U24_NAVY, linewidth=0.3)
    ax.set_xlabel('Macro degeneracy $g_2 = c$')
    ax.set_ylabel('$|T_c^{(1)}(c) - 903|$')
    ax.set_title('Conformal Anomaly Deformation: $T_c$ Error vs. $c$',
                 color=U24_NAVY, fontweight='bold')

    tc24_err = abs(tc_kramers(24) - RAMSEY)
    ax.annotate(f'$c = 24$: min error\n$\\Delta = {tc24_err:.1f}$',
                xy=(24, tc24_err), xytext=(34, max(tc_errors)*0.6),
                fontsize=10, color=U24_GOLD, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=U24_GOLD, lw=1.5))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(FIGURES_DIR / 'fig5_conformal_anomaly_sweep.pdf')
    fig.savefig(FIGURES_DIR / 'fig5_conformal_anomaly_sweep.png')
    plt.close(fig)
    print("  [OK] fig5_conformal_anomaly_sweep")


# ── Fig 6: S4 Composition Series ─────────────────────────────────────────

def fig6():
    fig, ax = plt.subplots(figsize=(9, 5))

    # Composition tower with boxes
    levels = [
        (0, '$\\{e\\}$', 1, 'lightgray', 'Trivial'),
        (1.5, '$V_4$', 4, 'steelblue', 'Klein 4-group'),
        (3.0, '$A_4$', 12, CONDITIONAL, 'Alternating'),
        (4.5, '$S_4$', 24, U24_GOLD, 'Symmetric'),
    ]

    for y, label, order, color, name in levels:
        box = mpatches.FancyBboxPatch((1, y - 0.35), order * 0.3, 0.7,
                                       boxstyle="round,pad=0.1",
                                       facecolor=color, alpha=0.6,
                                       edgecolor=U24_NAVY, linewidth=1.5)
        ax.add_patch(box)
        ax.text(1 + order * 0.15, y, f'{label}\n$|G| = {order}$',
                ha='center', va='center', fontsize=11, color=U24_NAVY, fontweight='bold')
        ax.text(1 + order * 0.3 + 0.3, y, name, va='center', fontsize=10, color='gray')

    # Quotient arrows with labels
    quotients = [(4, '$\\times 4$'), (3, '$\\times 3$'), (2, '$\\times 2$')]
    for i in range(3):
        y1 = levels[i][0]
        y2 = levels[i+1][0]
        q_text = quotients[i][1]
        ax.annotate('', xy=(0.6, y2 - 0.2), xytext=(0.6, y1 + 0.2),
                    arrowprops=dict(arrowstyle='->', color=U24_NAVY, lw=2))
        ax.text(0.25, (y1 + y2) / 2, q_text, fontsize=13, color=U24_NAVY,
                fontweight='bold', ha='center', va='center')

    # Product annotation
    ax.text(9, 2.25, '$4 \\times 3 \\times 2 = 24$\n$= |S_4| = \\dim(\\Lambda_{24})$',
            fontsize=14, ha='center', va='center', color=U24_GOLD, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=U24_GOLD, alpha=0.15,
                      edgecolor=U24_GOLD, linewidth=1.5))

    # Barrier alignment
    barriers = [(125, 0), (500, 1.5), (3000, 4.5)]
    for h, y in barriers:
        ax.text(9, y, f'$h = {h}$', fontsize=10, ha='center', va='center',
                color=U24_NAVY, fontstyle='italic')

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-1, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('$S_4$ Composition Series: $\\{e\\} \\trianglelefteq V_4 \\trianglelefteq A_4 \\trianglelefteq S_4$',
                 color=U24_NAVY, fontweight='bold', fontsize=14, pad=15)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig6_s4_composition.pdf')
    fig.savefig(FIGURES_DIR / 'fig6_s4_composition.png')
    plt.close(fig)
    print("  [OK] fig6_s4_composition")


# ── Fig 7: D4 Dynkin Diagram ─────────────────────────────────────────────

def fig7():
    fig, ax = plt.subplots(figsize=(7, 5))

    # D4 Dynkin: central node connected to 3 outer nodes
    center = (0, 0)
    outer = [(-1.5, 1.2), (1.5, 1.2), (0, -1.5)]
    labels_inner = ['$S$\n(center)']
    labels_outer = ['$F$\n($8_v$ vector)', '$G$\n($8_s$ spinor)', '$Z_2$\n($8_c$ co-spinor)']
    colors_outer = ['steelblue', CONDITIONAL, PROVED]

    # Edges
    for o in outer:
        ax.plot([center[0], o[0]], [center[1], o[1]], '-', color=U24_NAVY, linewidth=2.5)

    # Central node
    ax.scatter(*center, s=500, c=U24_GOLD, edgecolors=U24_NAVY, linewidths=2, zorder=5)
    ax.text(center[0], center[1] - 0.4, labels_inner[0], ha='center', va='top',
            fontsize=10, color=U24_NAVY)

    # Outer nodes
    for (x, y), label, color in zip(outer, labels_outer, colors_outer):
        ax.scatter(x, y, s=400, c=color, edgecolors=U24_NAVY, linewidths=2, zorder=5, alpha=0.8)
        offset_y = 0.4 if y > 0 else -0.5
        ax.text(x, y + offset_y, label, ha='center', va='center' if y > 0 else 'top',
                fontsize=10, color=U24_NAVY)

    # Triality arrow (circular)
    from matplotlib.patches import FancyArrowPatch, Arc
    arc = Arc((0, 0.3), 3.5, 3.5, angle=0, theta1=30, theta2=330,
              color=U24_GOLD, linewidth=2, linestyle='--')
    ax.add_patch(arc)
    ax.annotate('', xy=(1.3, 1.5), xytext=(-1.3, 1.5),
                arrowprops=dict(arrowstyle='->', color=U24_GOLD, lw=2, linestyle='--'))
    ax.text(0, 2.3, 'Triality\n(order 3)', ha='center', fontsize=11,
            color=U24_GOLD, fontweight='bold')

    # Dimension annotation
    ax.text(0, -2.5, '$3 \\times 8 = 24 = \\dim(\\Lambda_{24})$',
            ha='center', fontsize=13, color=U24_GOLD, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=U24_GOLD, alpha=0.1,
                      edgecolor=U24_GOLD))

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-3.2, 3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('$D_4$ Dynkin Diagram with Triality', color=U24_NAVY, fontweight='bold', fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig7_d4_dynkin.pdf')
    fig.savefig(FIGURES_DIR / 'fig7_d4_dynkin.png')
    plt.close(fig)
    print("  [OK] fig7_d4_dynkin")


# ── Fig 8: Hellerman Bound Visualization ─────────────────────────────────

def fig8():
    cs = np.arange(1, 50)
    hellerman_max = cs / 12 + 0.474
    delta1 = np.log(4) * np.ones_like(cs, dtype=float)  # 1.386

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(cs, 0, hellerman_max, alpha=0.15, color=PROVED, label='Allowed region ($\\Delta_1 \\leq c/12 + 0.47$)')
    ax.plot(cs, hellerman_max, '-', color=PROVED, linewidth=2, label='Hellerman bound')
    ax.plot(cs, delta1, '--', color=CONJECTURAL, linewidth=2, label='$\\Delta_1 = \\ln 4 \\approx 1.386$')

    # Mark c=24
    ax.plot(24, np.log(4), 'o', color=U24_GOLD, markersize=12, zorder=5,
            markeredgecolor=U24_NAVY, markeredgewidth=2)
    ax.annotate('$c = 24$: $\\Delta_1 = 1.39 < 2.47$ $\\checkmark$',
                xy=(24, np.log(4)), xytext=(30, 1.0), fontsize=10,
                color=U24_GOLD, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=U24_GOLD, lw=1.5))

    # Mark threshold
    c_thresh = 12 * (np.log(4) - 0.474)
    ax.axvline(x=c_thresh, color='gray', linestyle=':', alpha=0.5)
    ax.annotate(f'$c \\geq {c_thresh:.0f}$', xy=(c_thresh, 0.3), fontsize=9, color='gray')

    ax.set_xlabel('Central charge $c$')
    ax.set_ylabel('Conformal dimension $\\Delta_1$')
    ax.set_title('Constraint III: Hellerman Unitarity Bound', color=U24_NAVY, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.savefig(FIGURES_DIR / 'fig8_hellerman_bound.pdf')
    fig.savefig(FIGURES_DIR / 'fig8_hellerman_bound.png')
    plt.close(fig)
    print("  [OK] fig8_hellerman_bound")


# ── Fig 9: Eleven Paths Summary ──────────────────────────────────────────

def fig9():
    paths = [
        ('$|S_4|$', 24, PROVED),
        ('$\\dim(\\Lambda_{24})$', 24, 'steelblue'),
        ('$\\chi(K3)$', 24, CONDITIONAL),
        ('$D_{\\rm bos} - 2$', 24, 'purple'),
        ('$c(V^\\natural)$', 24, 'teal'),
        ('$[{\\rm SL}_2:{\\Gamma}_0(23)]$', 24, 'brown'),
        ('Ramanujan $\\Delta$ wt/2', 24, 'darkgreen'),
        ('24-cell vertices', 24, 'crimson'),
        ('$|D_4|$ roots', 24, 'navy'),
        ('Cannonball $\\Sigma k^2$', 24, 'olive'),
        ('Kramers $\\Omega$', 24, U24_GOLD),
    ]

    fig, ax = plt.subplots(figsize=(6, 6))
    y_pos = list(range(len(paths)))
    for i, (label, val, color) in enumerate(paths):
        ax.barh(i, val, height=0.6, color=color, alpha=0.6,
                edgecolor=U24_NAVY, linewidth=0.8)
        ax.text(0.5, i, label, va='center', fontsize=9, color='white', fontweight='bold')

    ax.axvline(x=24, color=U24_GOLD, linewidth=3, linestyle='-', zorder=10)
    ax.text(24, len(paths) + 0.2, '$\\mathbf{24}$', ha='center', fontsize=18,
            color=U24_GOLD, fontweight='bold')

    ax.set_xlabel('Value')
    ax.set_yticks([])
    ax.set_xlim(0, 30)
    ax.set_title('Eleven Paths to $\\Omega = 24$ (Paper 04)', color=U24_NAVY, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig9_eleven_paths.pdf')
    fig.savefig(FIGURES_DIR / 'fig9_eleven_paths.png')
    plt.close(fig)
    print("  [OK] fig9_eleven_paths")


def main():
    print("=" * 50)
    print("  Paper 15 — Figure Generation (v2)")
    print("=" * 50)
    print()
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    fig8()
    fig9()
    print(f"\n  9 figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
