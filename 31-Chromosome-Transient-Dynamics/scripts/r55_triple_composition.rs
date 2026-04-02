//! R(5,5) Triple Composition Sweep: f∘g∘h on GF(43)
//!
//! The composite (x²+6x+5)∘(x⁴+7x+7) hit K₄=2666, beating all pure polynomials.
//! Now: sweep ALL ordered triples of low-degree polynomials to approach the
//! Reeds endomorphism from below.
//!
//! Target: K₄ ≤ 2500 with Ω ≥ 18 and basin signature approaching [9,7,1,6].
//! Any such triple is one non-polynomial perturbation from zero violations.

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) TRIPLE COMPOSITION SWEEP — f∘g∘h on GF(43)             ║");
    println!("║  Climbing from Ω=9 (double) toward Ω=24 (Reeds)               ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t_total = Instant::now();
    let p = 43usize;
    let n = 43usize;
    let ne = n * (n - 1) / 2;

    // Reference points
    let ref_quad = 2709;  // best quadratic
    let ref_comp2 = 2666; // best double composite
    println!("  Reference: quadratic K₄={}, double composite K₄={}\n", ref_quad, ref_comp2);

    // ═══════════════════════════════════════════════════════════════
    // STAGE 1: Triple composition sweep f∘g∘h
    // Degrees 2,3,4 with small coefficients
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Stage 1: Triple Composition f∘g∘h Sweep ━━━\n");

    let degrees = [2, 3, 4];
    let max_b = 8; // coefficient range per polynomial

    let mut best_k4 = usize::MAX;
    let mut best_desc = String::new();
    let mut best_col = vec![];
    let mut best_omega = 0;
    let mut best_basins = vec![];
    let mut tested = 0u64;
    let mut sub_2600 = 0u64;
    let mut sub_2500 = 0u64;

    // Track top 10
    let mut top10: Vec<(usize, String, usize, Vec<usize>)> = Vec::new(); // (k4, desc, omega, basin_sizes)

    for &d1 in &degrees {
        for &d2 in &degrees {
            for &d3 in &degrees {
                for b1 in 0..max_b {
                    let c1 = 5usize; // fix one constant per layer for speed
                    let f: Vec<usize> = (0..p).map(|x| (pow_mod(x, d1, p) + b1 * x + c1) % p).collect();

                    for b2 in 0..max_b {
                        let c2 = 7usize;
                        let g: Vec<usize> = (0..p).map(|x| (pow_mod(x, d2, p) + b2 * x + c2) % p).collect();

                        // g∘f (inner composition)
                        let gf: Vec<usize> = (0..p).map(|x| g[f[x]]).collect();

                        for b3 in 0..max_b {
                            let c3 = 11usize;
                            let h: Vec<usize> = (0..p).map(|x| (pow_mod(x, d3, p) + b3 * x + c3) % p).collect();

                            // h∘g∘f (full triple composition)
                            let hgf: Vec<usize> = (0..p).map(|x| h[gf[x]]).collect();

                            let basins = GfpSeeder::extract_basins(&hgf);
                            if basins.n_basins < 2 { continue; }

                            // Test top 2 dominant basins
                            for d in 0..basins.n_basins.min(2) {
                                let col = color_from_basins(n, p, &basins.basin_id, d);
                                let k4 = count_mono_k4(n, &col);
                                tested += 1;

                                if k4 < 2600 { sub_2600 += 1; }
                                if k4 < 2500 { sub_2500 += 1; }

                                if k4 < best_k4 {
                                    best_k4 = k4;
                                    best_omega = basins.omega_product;
                                    best_basins = basins.basin_sizes.clone();
                                    best_col = col.clone();
                                    best_desc = format!(
                                        "(x^{}+{}x+{})∘(x^{}+{}x+{})∘(x^{}+{}x+{}) d={} Ω={}",
                                        d3, b3, c3, d2, b2, c2, d1, b1, c1, d, basins.omega_product
                                    );
                                }

                                // Track top 10
                                if top10.len() < 10 || k4 < top10.last().map(|t| t.0).unwrap_or(usize::MAX) {
                                    let desc = format!(
                                        "(x^{}+{}x+{})∘(x^{}+{}x+{})∘(x^{}+{}x+{})",
                                        d3, b3, c3, d2, b2, c2, d1, b1, c1
                                    );
                                    top10.push((k4, desc, basins.omega_product, basins.basin_sizes.clone()));
                                    top10.sort_by_key(|t| t.0);
                                    top10.truncate(10);
                                }
                            }
                        }
                    }
                }

                // Progress report per degree triple
                if tested % 5000 < 100 && tested > 0 {
                    let elapsed = t_total.elapsed().as_secs_f64();
                    let rate = tested as f64 / elapsed;
                    print!("\r  [{:.0}s] {} tested, best K₄={}, <2600: {}, <2500: {}, {:.0}/s   ",
                        elapsed, tested, best_k4, sub_2600, sub_2500, rate);
                }
            }
        }
    }

    let sweep_time = t_total.elapsed().as_secs_f64();
    println!("\n\n  Sweep complete: {} triples tested in {:.1}s ({:.0}/s)",
        tested, sweep_time, tested as f64 / sweep_time);
    println!("  Triples with K₄ < 2600: {}", sub_2600);
    println!("  Triples with K₄ < 2500: {}", sub_2500);
    println!();

    // ═══════════════════════════════════════════════════════════════
    // RESULTS: Top 10 triples
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Top 10 Triple Compositions ━━━\n");
    println!("  Rank | K₄    | Ω   | Basins          | Composition");
    println!("  -----|-------|-----|-----------------|------------------------------------------");

    for (i, (k4, desc, omega, bsizes)) in top10.iter().enumerate() {
        let basin_str = format!("{:?}", bsizes);
        let marker = if *omega >= 18 { " ★" } else if *omega == 24 { " ★★" } else { "" };
        println!("  {:4} | {:5} | {:3} | {:15} | {}{}",
            i + 1, k4, omega, basin_str, desc, marker);
    }

    // ═══════════════════════════════════════════════════════════════
    // STAGE 2: ILS refinement on champion
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Stage 2: ILS on Triple Champion ━━━\n");

    if !best_col.is_empty() {
        println!("  Champion: {} (K₄={}, Ω={}, basins={:?})", best_desc, best_k4, best_omega, best_basins);

        let mut current = best_col.clone();
        let mut current_k4 = best_k4;

        for round in 0..500 {
            let mut cand = current.clone();

            // Perturbation
            let kick = if round % 15 == 0 && round > 0 { ne } else { 3 + (round % 20) };
            let mut rng = (round as u64 * 999983).wrapping_mul(6364136223846793005);
            if kick >= ne {
                for s in cand.iter_mut() { *s = -*s; }
            } else {
                for _ in 0..kick {
                    rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                    cand[(rng as usize) % ne] *= -1;
                }
            }

            greedy_k4(n, &mut cand, 30);
            let k4 = count_mono_k4(n, &cand);

            if k4 < current_k4 {
                current_k4 = k4;
                current = cand;
                println!("    Round {}: K₄ improved to {}", round, k4);
            }
        }

        println!("  After 500 ILS rounds: K₄ = {} (started at {})", current_k4, best_k4);

        // Exact verification
        let t_v = Instant::now();
        let v = MaxClique::verify_ramsey(n, &current, 5);
        println!("  Bron-Kerbosch ({:.0}ms): red ω={}, blue ω={}, valid={}",
            t_v.elapsed().as_secs_f64() * 1000.0,
            v.max_red_clique.len(), v.max_blue_clique.len(), v.is_valid);

        if v.is_valid {
            println!("\n  ★★★ R(5,5) ≥ 44 CERTIFICATE FOUND! ★★★");
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // STAGE 3: Basin topology analysis
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Stage 3: Basin Topology of Champions ━━━\n");

    println!("  Target basin signature: [9, 7, 1, 6] (Reeds endomorphism)");
    println!();

    // Check how close top triples are to [9,7,1,6]
    let target = vec![9usize, 7, 1, 6];
    for (i, (k4, desc, omega, bsizes)) in top10.iter().take(5).enumerate() {
        let mut sorted_sizes = bsizes.clone();
        sorted_sizes.sort_by(|a, b| b.cmp(a));

        // Distance to target [9,7,1,6]
        let dist: usize = if sorted_sizes.len() >= 4 {
            sorted_sizes.iter().zip(target.iter()).map(|(&a, &b)| {
                (a as i64 - b as i64).unsigned_abs() as usize
            }).sum()
        } else {
            999
        };

        println!("  #{}: K₄={}, Ω={}, basins={:?} (sorted: {:?}), dist_to_target={}",
            i + 1, k4, omega, bsizes, sorted_sizes, dist);
    }

    // ═══════════════════════════════════════════════════════════════
    println!("\n╔══════════════════════════════════════════════════════════════════╗");
    println!("║  TRIPLE COMPOSITION RESULTS                                     ║");
    println!("╠══════════════════════════════════════════════════════════════════╣");
    println!("║                                                                  ║");
    println!("║  Triples tested:  {}                                        ║", tested);
    println!("║  K₄ < 2600:       {}                                            ║", sub_2600);
    println!("║  K₄ < 2500:       {}                                            ║", sub_2500);
    println!("║  Best triple:     K₄ = {}                                       ║", best_k4);
    println!("║  Best Ω:          {}                                            ║", best_omega);
    println!("║  Best basins:     {:?}                                   ║", best_basins);
    println!("║  vs double comp:  {} (was 2666)                                 ║",
        if best_k4 < 2666 { "IMPROVED" } else { "same level" });
    println!("║  vs quadratic:    {} (was 2709)                                 ║",
        if best_k4 < 2709 { "IMPROVED" } else { "same level" });
    println!("║                                                                  ║");
    println!("║  Total time: {:.1}s                                              ║", t_total.elapsed().as_secs_f64());
    println!("╚══════════════════════════════════════════════════════════════════╝");
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

fn greedy_k4(n: usize, col: &mut Vec<i8>, rounds: usize) {
    let ne = n * (n - 1) / 2;
    for _ in 0..rounds {
        let before = count_mono_k4(n, col);
        if before == 0 { return; }
        let mut improved = false;
        for e in 0..ne {
            col[e] *= -1;
            if count_mono_k4(n, col) < before { improved = true; break; }
            col[e] *= -1;
        }
        if !improved { return; }
    }
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
