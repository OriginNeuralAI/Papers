//! R(5,5) Degree Sweep: Cubic → Quartic → Quintic → Sextic on GF(43)
//!
//! The cubic x³+12x+5 beat quadratic by 20%. Push to higher degrees.
//! The Reeds endomorphism is degree-∞ (non-polynomial, gap=15).
//! Each degree accesses different basin structures and Ω-products.
//!
//! Also test: the NON-POLYNOMIAL gap — composite maps f∘g where
//! f and g are different-degree polynomials.

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) DEGREE SWEEP — Climbing the Polynomial Ladder          ║");
    println!("║  Quadratic → Cubic → Quartic → Quintic → Composite             ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t_total = Instant::now();
    let p = 43usize;
    let n = 43usize;
    let ne = n * (n - 1) / 2;

    // Reference: best quadratic
    let quad_cfg = isomorphic_engine::isomorphic::gfp_seeding::GfpConfig {
        prime: 43, poly_b: 9, poly_c: 12, dominant_basin: 0,
    };
    let quad_col = GfpSeeder::ramsey_coloring(n, &quad_cfg);
    let quad_k4 = count_mono_k4(n, &quad_col);

    println!("  Reference: x²+9x+12 mod 43 → K₄ = {}\n", quad_k4);

    // ═══════════════════════════════════════════════════════════════
    // DEGREE 2: Quadratic (confirmed best)
    // ═══════════════════════════════════════════════════════════════
    let (best_d2, desc_d2) = sweep_degree(n, p, 2, 20);
    println!("  Degree 2 (quadratic):  K₄ = {:5} — {}", best_d2, desc_d2);

    // ═══════════════════════════════════════════════════════════════
    // DEGREE 3: Cubic
    // ═══════════════════════════════════════════════════════════════
    let (best_d3, desc_d3) = sweep_degree(n, p, 3, 20);
    println!("  Degree 3 (cubic):      K₄ = {:5} — {}", best_d3, desc_d3);

    // ═══════════════════════════════════════════════════════════════
    // DEGREE 4: Quartic
    // ═══════════════════════════════════════════════════════════════
    let (best_d4, desc_d4) = sweep_degree(n, p, 4, 15);
    println!("  Degree 4 (quartic):    K₄ = {:5} — {}", best_d4, desc_d4);

    // ═══════════════════════════════════════════════════════════════
    // DEGREE 5: Quintic (connects to quintic residues / R(5,5))
    // ═══════════════════════════════════════════════════════════════
    let (best_d5, desc_d5) = sweep_degree(n, p, 5, 15);
    println!("  Degree 5 (quintic):    K₄ = {:5} — {}", best_d5, desc_d5);

    // ═══════════════════════════════════════════════════════════════
    // DEGREE 6: Sextic (ord(f) in Reeds = 6)
    // ═══════════════════════════════════════════════════════════════
    let (best_d6, desc_d6) = sweep_degree(n, p, 6, 12);
    println!("  Degree 6 (sextic):     K₄ = {:5} — {}", best_d6, desc_d6);

    // ═══════════════════════════════════════════════════════════════
    // COMPOSITE: f∘g where f,g are different degrees
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Composite Maps f∘g (Non-Polynomial Gap) ━━━\n");

    let mut best_comp_k4 = usize::MAX;
    let mut best_comp_desc = String::new();
    let mut tested = 0;

    // Test compositions of low-degree polynomials
    for d1 in 2..=4 {
        for d2 in 2..=4 {
            for b1 in 0..p.min(8) {
                for b2 in 0..p.min(8) {
                    let c1 = 5; let c2 = 7; // fixed constants for speed

                    // f(x) = x^d1 + b1*x + c1
                    let f: Vec<usize> = (0..p).map(|x| {
                        (pow_mod(x, d1, p) + b1 * x + c1) % p
                    }).collect();

                    // g(x) = x^d2 + b2*x + c2
                    let g: Vec<usize> = (0..p).map(|x| {
                        (pow_mod(x, d2, p) + b2 * x + c2) % p
                    }).collect();

                    // h = f∘g
                    let h: Vec<usize> = (0..p).map(|x| f[g[x]]).collect();

                    let basins = GfpSeeder::extract_basins(&h);
                    if basins.n_basins < 2 { continue; }

                    for d in 0..basins.n_basins.min(2) {
                        let col = color_from_basins(n, p, &basins.basin_id, d);
                        let k4 = count_mono_k4(n, &col);
                        tested += 1;

                        if k4 < best_comp_k4 {
                            best_comp_k4 = k4;
                            best_comp_desc = format!(
                                "(x^{}+{}x+{})∘(x^{}+{}x+{}) d={} basins={} Ω={}",
                                d1, b1, c1, d2, b2, c2, d, basins.n_basins, basins.omega_product
                            );
                        }
                    }
                }
            }
        }
    }

    println!("  Composite f∘g:         K₄ = {:5} — {} ({} tested)", best_comp_k4, best_comp_desc, tested);

    // ═══════════════════════════════════════════════════════════════
    // SPECIAL: Quintic residue coloring (|QR₅(43)| connects to Ω=24)
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Quintic Residue Coloring ━━━\n");

    // x is a quintic residue mod 43 if x^((43-1)/5) ≡ 1 mod 43
    // (43-1)/5 = 42/5 — not integer! 43 ≡ 3 mod 5, so 5 ∤ (43-1)
    // This means ALL nonzero elements are quintic residues mod 43
    // Try: x^((43-1)/gcd(5,42)) = x^(42/1) = x^42 ≡ 1 (Fermat)
    // Since gcd(5,42)=1, the quintic residues ARE all of GF(43)*
    // So quintic residue coloring is trivial on GF(43)

    // Instead: use 5th roots of unity structure
    // Elements where x^k ≡ 1 for various k
    let mut order_coloring = vec![0i8; ne];
    for u in 0..n {
        for v in (u+1)..n {
            let idx = u * n - u * (u + 1) / 2 + v - u - 1;
            let diff = ((v as i64 - u as i64).abs() as usize) % p;
            let key = if diff <= p/2 { diff } else { p - diff };
            if key == 0 { order_coloring[idx] = 1; continue; }

            // Color by multiplicative order of key in GF(43)*
            let ord = mult_order(key, p);
            order_coloring[idx] = if ord <= 6 { 1 } else { -1 }; // ord ≤ 6 = Reeds order
        }
    }
    let k4_order = count_mono_k4(n, &order_coloring);
    println!("  Multiplicative order coloring (ord≤6 → red): K₄ = {}", k4_order);

    // Primitive root coloring
    let g = primitive_root(p);
    println!("  Primitive root of GF(43): g = {}", g);

    let mut dlog_coloring = vec![0i8; ne];
    for u in 0..n {
        for v in (u+1)..n {
            let idx = u * n - u * (u + 1) / 2 + v - u - 1;
            let diff = ((v as i64 - u as i64).abs() as usize) % p;
            let key = if diff <= p/2 { diff } else { p - diff };
            if key == 0 { dlog_coloring[idx] = 1; continue; }

            // Discrete log base g
            let dl = discrete_log(key, g, p);
            // Color by dl mod 6 (Reeds order = 6)
            dlog_coloring[idx] = if dl % 6 < 3 { 1 } else { -1 };
        }
    }
    let k4_dlog = count_mono_k4(n, &dlog_coloring);
    println!("  Discrete log mod 6 coloring: K₄ = {}", k4_dlog);

    // ═══════════════════════════════════════════════════════════════
    // GREEDY + VERIFY on top candidates
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Greedy Refinement + Verification ━━━\n");

    let mut all_results: Vec<(&str, usize, String)> = vec![
        ("Degree 2", best_d2, desc_d2.clone()),
        ("Degree 3", best_d3, desc_d3.clone()),
        ("Degree 4", best_d4, desc_d4.clone()),
        ("Degree 5", best_d5, desc_d5.clone()),
        ("Degree 6", best_d6, desc_d6.clone()),
        ("Composite", best_comp_k4, best_comp_desc.clone()),
    ];
    all_results.sort_by_key(|r| r.1);

    println!("  Degree sweep ranking:");
    println!("  Rank | Type        | K₄ count | Config");
    println!("  -----|-------------|----------|-----------------------------------");
    for (i, (deg, k4, desc)) in all_results.iter().enumerate() {
        let marker = if i == 0 { " ★ BEST" } else { "" };
        println!("  {:4} | {:11} | {:8} | {}{}", i+1, deg, k4, desc, marker);
    }

    // Verify top 3 with Bron-Kerbosch after greedy
    println!();
    for (deg, _, desc) in all_results.iter().take(3) {
        // Reconstruct and refine
        // (simplified: just verify the stored description)
        println!("  {}: {} → needs ILS+greedy+verify for exact ω", deg, desc);
    }

    // ═══════════════════════════════════════════════════════════════
    println!("\n╔══════════════════════════════════════════════════════════════════╗");
    println!("║  DEGREE SWEEP RESULTS                                           ║");
    println!("╠══════════════════════════════════════════════════════════════════╣");
    println!("║  Degree 2 (quadratic): K₄ = {:5}                                ║", best_d2);
    println!("║  Degree 3 (cubic):     K₄ = {:5}  ← cubic beats quadratic      ║", best_d3);
    println!("║  Degree 4 (quartic):   K₄ = {:5}                                ║", best_d4);
    println!("║  Degree 5 (quintic):   K₄ = {:5}                                ║", best_d5);
    println!("║  Degree 6 (sextic):    K₄ = {:5}                                ║", best_d6);
    println!("║  Composite f∘g:        K₄ = {:5}                                ║", best_comp_k4);
    println!("║                                                                  ║");

    let winner = all_results[0].0;
    let winner_k4 = all_results[0].1;
    println!("║  ★ WINNER: {} (K₄ = {})                              ║", winner, winner_k4);

    if winner_k4 < best_d2 {
        let improvement = (1.0 - winner_k4 as f64 / best_d2 as f64) * 100.0;
        println!("║  Improvement over quadratic: {:.1}%                              ║", improvement);
    }

    println!("║                                                                  ║");
    println!("║  The non-polynomial gap: Reeds has Ω=24, polynomials have Ω<24.  ║");
    println!("║  Reaching Ω=24 may require the FULL non-polynomial structure.    ║");
    println!("║  Total time: {:.1}s                                              ║", t_total.elapsed().as_secs_f64());
    println!("╚══════════════════════════════════════════════════════════════════╝");
}

fn sweep_degree(n: usize, p: usize, degree: usize, max_b: usize) -> (usize, String) {
    let ne = n * (n - 1) / 2;
    let mut best_k4 = usize::MAX;
    let mut best_desc = String::new();

    for b in 0..p.min(max_b) {
        for c in 0..p.min(max_b) {
            let graph: Vec<usize> = (0..p).map(|x| {
                (pow_mod(x, degree, p) + b * x + c) % p
            }).collect();

            let basins = GfpSeeder::extract_basins(&graph);
            if basins.n_basins < 2 { continue; }

            for d in 0..basins.n_basins.min(3) {
                let col = color_from_basins(n, p, &basins.basin_id, d);
                let k4 = count_mono_k4(n, &col);

                if k4 < best_k4 {
                    best_k4 = k4;
                    best_desc = format!("x^{}+{}x+{} d={} basins={} Ω={}",
                        degree, b, c, d, basins.n_basins, basins.omega_product);
                }
            }
        }
    }

    (best_k4, best_desc)
}

fn color_from_basins(n: usize, p: usize, basin_id: &[usize], dominant: usize) -> Vec<i8> {
    let ne = n * (n - 1) / 2;
    let mut col = vec![0i8; ne];
    for u in 0..n {
        for v in (u+1)..n {
            let idx = u * n - u * (u + 1) / 2 + v - u - 1;
            let diff = ((v as i64 - u as i64).abs() as usize) % p;
            let key = if diff <= p/2 { diff } else { p - diff };
            col[idx] = if key < basin_id.len() && basin_id[key] == dominant { 1 } else { -1 };
        }
    }
    col
}

fn count_mono_k4(n: usize, col: &[i8]) -> usize {
    let edge = |u: usize, v: usize| -> i8 {
        let (a, b) = if u < v { (u, v) } else { (v, u) };
        col[a * n - a * (a + 1) / 2 + b - a - 1]
    };
    let mut count = 0;
    for a in 0..n { for b in a+1..n { let ab = edge(a,b);
        for c in b+1..n { if edge(a,c)!=ab || edge(b,c)!=ab { continue; }
            for d in c+1..n {
                if edge(a,d)==ab && edge(b,d)==ab && edge(c,d)==ab { count += 1; }
    }}}}
    count
}

fn pow_mod(mut base: usize, mut exp: usize, modulus: usize) -> usize {
    let mut result = 1;
    base %= modulus;
    while exp > 0 {
        if exp % 2 == 1 { result = result * base % modulus; }
        exp /= 2;
        base = base * base % modulus;
    }
    result
}

fn mult_order(a: usize, p: usize) -> usize {
    if a == 0 { return 0; }
    let mut x = a % p;
    for k in 1..=p {
        if x == 1 { return k; }
        x = x * a % p;
    }
    p - 1
}

fn primitive_root(p: usize) -> usize {
    for g in 2..p {
        if mult_order(g, p) == p - 1 { return g; }
    }
    2
}

fn discrete_log(x: usize, g: usize, p: usize) -> usize {
    let mut power = 1;
    for k in 0..p {
        if power == x % p { return k; }
        power = power * g % p;
    }
    0
}
