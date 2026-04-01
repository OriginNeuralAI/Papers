//! Chromosome Dynamics Correlation: Reeds vs Collatz vs COSMIC
//!
//! Three dynamical systems applied to chromosome numbers 1-23:
//! 1. REEDS: f: Z₂₃ → Z₂₃ (Book of Soyga lookup table, 1583)
//! 2. COLLATZ: n → n/2 (even) or 3n+1 (odd), count steps to reach 1
//! 3. COSMIC: actual cancer mutation frequency data (TCGA Pan-Cancer Atlas)
//!
//! Question: Which dynamical system's transient length better predicts
//! cancer mutation frequency? Compute Pearson r and Spearman ρ for both.

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  CHROMOSOME DYNAMICS CORRELATION                                ║");
    println!("║  Reeds f(x) vs Collatz 3n+1 vs COSMIC mutation frequency        ║");
    println!("║  Which dynamical system predicts cancer?                         ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    // ═══════════════════════════════════════════════════════════════
    // DATA: Three measurements per chromosome
    // ═══════════════════════════════════════════════════════════════

    // Reeds endomorphism f: Z₂₃ → Z₂₃
    let soyga_f: [usize; 23] = [2,2,3,5,14,2,6,5,14,15,20,22,14,8,13,20,11,8,8,15,15,15,2];
    let cycle_elements: [usize; 9] = [2,3,5,6,8,13,14,15,20];

    // Compute Reeds transient for each chromosome (chr n → element n-1)
    let reeds_tau: Vec<usize> = (0..23).map(|x| {
        if cycle_elements.contains(&x) { return 0; }
        let mut current = x;
        let mut steps = 0;
        while !cycle_elements.contains(&current) && steps < 100 {
            current = soyga_f[current];
            steps += 1;
        }
        steps
    }).collect();

    // Compute Collatz orbit length for each chromosome number
    let collatz_tau: Vec<usize> = (1..=23).map(|n| collatz_steps(n)).collect();

    // COSMIC/TCGA Pan-Cancer mutation frequency per chromosome
    // Sources: Bailey et al. 2018 (TCGA), Sondka et al. 2018 (COSMIC CGC)
    // Values = approximate % of cancer patients with driver mutations on this chromosome
    // Aggregated from top driver genes per chromosome
    let cosmic_freq: Vec<f64> = vec![
        13.5,  // Chr 1:  ARID1A(8.0), NRAS(5.5)
        10.0,  // Chr 2:  IDH1(5.0), NFE2L2(3.0), ALK(2.0)
        25.5,  // Chr 3:  PIK3CA(14.0), CTNNB1(4.5), VHL(4.5), SETD2(2.5)
         9.2,  // Chr 4:  FBXW7(5.0), FGFR3(2.0), KIT(1.2), PDGFRA(1.0)
        11.0,  // Chr 5:  APC(10.0), NPM1(1.0)
         1.5,  // Chr 6:  ROS1(1.5)
        19.5,  // Chr 7:  BRAF(8.0), EGFR(6.0), KMT2C(3.5), EZH2(1.0), MET(1.0)
         3.6,  // Chr 8:  MYC(2.8), RAD21(0.8)
        15.3,  // Chr 9:  CDKN2A(7.0), NOTCH1(3.0), JAK2(2.0), PTCH1(1.8), ABL1(1.5)
        11.3,  // Chr 10: PTEN(9.0), RET(1.5), GATA3(0.8)
         6.7,  // Chr 11: ATM(4.0), HRAS(1.5), WT1(1.2)
        19.5,  // Chr 12: KRAS(12.0), KMT2D(7.5)
        10.0,  // Chr 13: RB1(6.0), BRCA2(4.0)
         0.0,  // Chr 14: immunoglobulin (translocations, not point mutations)
         0.0,  // Chr 15: (no major pan-cancer drivers)
         4.5,  // Chr 16: CREBBP(2.5), CDH1(2.0)
        47.0,  // Chr 17: TP53(36.0), NF1(4.5), BRCA1(3.5), ERBB2(3.0)
         6.0,  // Chr 18: SMAD4(3.5), BCL2(2.5)
         3.0,  // Chr 19: STK11(3.0)
         0.0,  // Chr 20: (growth hormone, no major drivers)
         1.0,  // Chr 21: RUNX1(0.8), SOD1(0.2)
         1.5,  // Chr 22: BCR(1.5)
         0.0,  // Chr X/Y: (sex-linked, excluded from pan-cancer)
    ];

    // ═══════════════════════════════════════════════════════════════
    // TABLE: All three measurements side by side
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Full Data Table ━━━\n");
    println!("  Chr | Reeds τ | Collatz τ | COSMIC freq% | Reeds orbit          | Collatz orbit");
    println!("  ----|---------|----------|-------------|----------------------|---------------------------");

    for chr in 1..=23 {
        let i = chr - 1;
        let r_tau = reeds_tau[i];
        let c_tau = collatz_tau[i];

        // Show Reeds orbit
        let mut reeds_orbit = vec![i];
        let mut x = i;
        for _ in 0..r_tau {
            x = soyga_f[x];
            reeds_orbit.push(x);
        }
        let reeds_str: String = reeds_orbit.iter().map(|x| x.to_string()).collect::<Vec<_>>().join("→");

        // Show Collatz orbit (abbreviated)
        let collatz_str = collatz_orbit_str(chr, 8);

        println!("  {:3} | {:7} | {:8} | {:11.1} | {:20} | {}",
            chr, r_tau, c_tau, cosmic_freq[i], reeds_str, collatz_str);
    }

    // ═══════════════════════════════════════════════════════════════
    // CORRELATION ANALYSIS
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Correlation Analysis ━━━\n");

    let reeds_f64: Vec<f64> = reeds_tau.iter().map(|&t| t as f64).collect();
    let collatz_f64: Vec<f64> = collatz_tau.iter().map(|&t| t as f64).collect();

    // Pearson correlations
    let r_reeds = pearson(&reeds_f64, &cosmic_freq);
    let r_collatz = pearson(&collatz_f64, &cosmic_freq);

    // Spearman rank correlations
    let rho_reeds = spearman(&reeds_f64, &cosmic_freq);
    let rho_collatz = spearman(&collatz_f64, &cosmic_freq);

    println!("  Correlation with COSMIC mutation frequency:\n");
    println!("  Dynamical system | Pearson r | Spearman ρ | p-value (approx)");
    println!("  ─────────────────|───────────|────────────|─────────────────");
    println!("  Reeds f: Z₂₃     | {:+9.4}  | {:+10.4}  | {:.4}",
        r_reeds, rho_reeds, p_value_approx(r_reeds, 23));
    println!("  Collatz 3n+1     | {:+9.4}  | {:+10.4}  | {:.4}",
        r_collatz, rho_collatz, p_value_approx(r_collatz, 23));
    println!();

    // ═══════════════════════════════════════════════════════════════
    // WEIGHTED ANALYSIS: τ² weighting (longer transient = more exposure)
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Weighted Analysis: τ² (exposure ∝ τ²) ━━━\n");

    let reeds_sq: Vec<f64> = reeds_f64.iter().map(|t| t * t).collect();
    let collatz_sq: Vec<f64> = collatz_f64.iter().map(|t| t * t).collect();

    let r_reeds_sq = pearson(&reeds_sq, &cosmic_freq);
    let r_collatz_sq = pearson(&collatz_sq, &cosmic_freq);
    let rho_reeds_sq = spearman(&reeds_sq, &cosmic_freq);
    let rho_collatz_sq = spearman(&collatz_sq, &cosmic_freq);

    println!("  With τ² weighting (mutation exposure scales as window²):\n");
    println!("  Dynamical system | Pearson r | Spearman ρ | Improvement");
    println!("  ─────────────────|───────────|────────────|────────────");
    println!("  Reeds τ²         | {:+9.4}  | {:+10.4}  | {:+.4} from linear",
        r_reeds_sq, rho_reeds_sq, r_reeds_sq - r_reeds);
    println!("  Collatz τ²       | {:+9.4}  | {:+10.4}  | {:+.4} from linear",
        r_collatz_sq, rho_collatz_sq, r_collatz_sq - r_collatz);
    println!();

    // ═══════════════════════════════════════════════════════════════
    // BASIN-AWARE ANALYSIS: Reeds basin + τ combined
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Basin-Aware Analysis: Combined basin + transient predictor ━━━\n");

    // Composite predictor: basin_weight × (1 + τ)²
    // Creation basin gets highest weight (most "open" to mutation)
    let basin_weights = [1.0_f64, 0.7, 2.0, 0.5]; // Creation, Perception, Stability(fixed), Exchange
    let composite: Vec<f64> = (0..23).map(|x| {
        let basin = match x {
            0|1|4|9|10|11|16|17|21 => 0,
            3|7|12|18|19|22|14     => 1,
            6                      => 2,
            _                      => 3,
        };
        basin_weights[basin] * (1.0 + reeds_tau[x] as f64).powi(2)
    }).collect();

    let r_composite = pearson(&composite, &cosmic_freq);
    let rho_composite = spearman(&composite, &cosmic_freq);

    println!("  Composite predictor: basin_weight × (1 + τ)²");
    println!("  Basin weights: Creation=1.0, Perception=0.7, Stability=2.0, Exchange=0.5");
    println!();
    println!("  Pearson r  = {:+.4}", r_composite);
    println!("  Spearman ρ = {:+.4}", rho_composite);
    println!("  p-value    ≈ {:.4}", p_value_approx(r_composite, 23));
    println!();

    // ═══════════════════════════════════════════════════════════════
    // CHROMOSOME SIZE CONTROL
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Control: Chromosome Size (genes per chromosome) ━━━\n");

    // Approximate gene counts per chromosome (GRCh38)
    let gene_counts: Vec<f64> = vec![
        2058.0, 1309.0, 1078.0, 752.0, 876.0, 1048.0, 989.0, 677.0, 786.0,
        733.0, 1298.0, 1034.0, 327.0, 830.0, 613.0, 873.0, 1197.0, 270.0,
        1472.0, 544.0, 234.0, 488.0, 842.0, // X treated as 23
    ];

    let r_size = pearson(&gene_counts, &cosmic_freq);
    let rho_size = spearman(&gene_counts, &cosmic_freq);

    println!("  Does chromosome SIZE explain mutation frequency?");
    println!("  (Null hypothesis: more genes = more mutations)\n");
    println!("  Size vs COSMIC: Pearson r = {:+.4}, Spearman ρ = {:+.4}", r_size, rho_size);
    println!();

    // Partial correlation: Reeds τ controlling for size
    let r_reeds_partial = partial_correlation(&reeds_sq, &cosmic_freq, &gene_counts);
    println!("  Partial correlation (Reeds τ² | controlling for chr size):");
    println!("  r_partial = {:+.4}", r_reeds_partial);
    println!();

    // ═══════════════════════════════════════════════════════════════
    // SUMMARY
    // ═══════════════════════════════════════════════════════════════
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  CORRELATION SUMMARY                                            ║");
    println!("╠══════════════════════════════════════════════════════════════════╣");
    println!("║                                                                 ║");
    println!("║  Predictor          │ Pearson r │ Spearman ρ │ p-value          ║");
    println!("║  ──────────────────-┼───────────┼────────────┼────────────────  ║");
    println!("║  Reeds τ (linear)   │ {:+7.4}   │ {:+8.4}   │ {:.4}            ║", r_reeds, rho_reeds, p_value_approx(r_reeds, 23));
    println!("║  Reeds τ²           │ {:+7.4}   │ {:+8.4}   │ {:.4}            ║", r_reeds_sq, rho_reeds_sq, p_value_approx(r_reeds_sq, 23));
    println!("║  Composite (basin×τ²)│ {:+7.4}   │ {:+8.4}   │ {:.4}            ║", r_composite, rho_composite, p_value_approx(r_composite, 23));
    println!("║  Collatz τ          │ {:+7.4}   │ {:+8.4}   │ {:.4}            ║", r_collatz, rho_collatz, p_value_approx(r_collatz, 23));
    println!("║  Collatz τ²         │ {:+7.4}   │ {:+8.4}   │ {:.4}            ║", r_collatz_sq, rho_collatz_sq, p_value_approx(r_collatz_sq, 23));
    println!("║  Chr size (genes)   │ {:+7.4}   │ {:+8.4}   │ {:.4}            ║", r_size, rho_size, p_value_approx(r_size, 23));
    println!("║  Reeds τ²|size      │ {:+7.4}   │    —       │  (partial)       ║", r_reeds_partial);
    println!("║                                                                 ║");

    let best_predictor = if r_reeds_sq.abs() > r_collatz_sq.abs() && r_reeds_sq.abs() > r_size.abs() {
        "Reeds τ²"
    } else if r_collatz_sq.abs() > r_size.abs() {
        "Collatz τ²"
    } else {
        "Chromosome size"
    };
    println!("║  Best predictor: {}                                        ║", best_predictor);
    println!("║                                                                 ║");

    if r_reeds_sq.abs() > r_collatz_sq.abs() {
        println!("║  ✓ Reeds endomorphism OUTPERFORMS Collatz                       ║");
        println!("║    The specific Z₂₃ structure of the Book of Soyga matters.     ║");
    } else {
        println!("║  ✗ Collatz outperforms Reeds — generic dynamics, not Soyga-specific║");
    }

    if r_reeds_partial.abs() > 0.3 {
        println!("║  ✓ Reeds τ² effect PERSISTS after controlling for chromosome size║");
        println!("║    Not just a size artifact — genuine structural prediction.     ║");
    }
    println!("╚══════════════════════════════════════════════════════════════════╝");
}

// ═══════════════════════════════════════════════════════════════
// Statistical functions
// ═══════════════════════════════════════════════════════════════

fn collatz_steps(mut n: usize) -> usize {
    let mut steps = 0;
    while n != 1 && steps < 1000 {
        n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
        steps += 1;
    }
    steps
}

fn collatz_orbit_str(mut n: usize, max_show: usize) -> String {
    let mut orbit = vec![n];
    while n != 1 && orbit.len() < max_show {
        n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
        orbit.push(n);
    }
    let s: String = orbit.iter().map(|x| x.to_string()).collect::<Vec<_>>().join("→");
    if n != 1 { format!("{}→...", s) } else { s }
}

fn pearson(x: &[f64], y: &[f64]) -> f64 {
    let n = x.len() as f64;
    let mx: f64 = x.iter().sum::<f64>() / n;
    let my: f64 = y.iter().sum::<f64>() / n;

    let mut cov = 0.0;
    let mut var_x = 0.0;
    let mut var_y = 0.0;

    for i in 0..x.len() {
        let dx = x[i] - mx;
        let dy = y[i] - my;
        cov += dx * dy;
        var_x += dx * dx;
        var_y += dy * dy;
    }

    if var_x < 1e-15 || var_y < 1e-15 { return 0.0; }
    cov / (var_x.sqrt() * var_y.sqrt())
}

fn spearman(x: &[f64], y: &[f64]) -> f64 {
    let rx = ranks(x);
    let ry = ranks(y);
    pearson(&rx, &ry)
}

fn ranks(values: &[f64]) -> Vec<f64> {
    let n = values.len();
    let mut indexed: Vec<(usize, f64)> = values.iter().enumerate().map(|(i, &v)| (i, v)).collect();
    indexed.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal));

    let mut r = vec![0.0; n];
    let mut i = 0;
    while i < n {
        let mut j = i;
        while j < n && (indexed[j].1 - indexed[i].1).abs() < 1e-10 {
            j += 1;
        }
        let avg_rank = (i + j + 1) as f64 / 2.0; // average rank for ties
        for k in i..j {
            r[indexed[k].0] = avg_rank;
        }
        i = j;
    }
    r
}

fn partial_correlation(x: &[f64], y: &[f64], z: &[f64]) -> f64 {
    let rxy = pearson(x, y);
    let rxz = pearson(x, z);
    let ryz = pearson(y, z);

    let denom = ((1.0 - rxz * rxz) * (1.0 - ryz * ryz)).sqrt();
    if denom < 1e-15 { return 0.0; }
    (rxy - rxz * ryz) / denom
}

fn p_value_approx(r: f64, n: usize) -> f64 {
    // Approximate p-value from t-distribution for Pearson r
    let df = n as f64 - 2.0;
    if df <= 0.0 || r.abs() >= 1.0 { return if r.abs() >= 1.0 { 0.0 } else { 1.0 }; }
    let t = r * (df / (1.0 - r * r)).sqrt();
    // Use normal approximation for large df
    let p = 2.0 * (1.0 - normal_cdf(t.abs()));
    p
}

fn normal_cdf(x: f64) -> f64 {
    0.5 * (1.0 + erf(x / std::f64::consts::SQRT_2))
}

fn erf(x: f64) -> f64 {
    // Abramowitz and Stegun approximation
    let a1 = 0.254829592;
    let a2 = -0.284496736;
    let a3 = 1.421413741;
    let a4 = -1.453152027;
    let a5 = 1.061405429;
    let p = 0.3275911;

    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let x = x.abs();
    let t = 1.0 / (1.0 + p * x);
    let y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * (-x * x).exp();
    sign * y
}
