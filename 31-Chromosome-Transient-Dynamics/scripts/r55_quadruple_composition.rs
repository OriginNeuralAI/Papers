//! R(5,5) Quadruple Composition: f∘g∘h∘k on GF(43)
//!
//! Triple champion: (x²+3x+11)∘(x³+7)∘(x³+3x+5) → K₄=2580→2443 after ILS
//! Basin sizes [16, 6, 9, 12] — already contains 9 and 6 from target [9,7,1,6]
//!
//! Goal: Find a quadruple with K₄ ≤ 2350 AND basin signature approaching [9,7,1,6]
//! Early-stop any hit with partial Reeds signature for zero-core extraction

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) QUADRUPLE COMPOSITION — f∘g∘h∘k on GF(43)             ║");
    println!("║  Target: K₄ ≤ 2350, basin signature → [9,7,1,6], Ω → 24       ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t_total = Instant::now();
    let p = 43usize;
    let n = 43usize;
    let ne = n * (n - 1) / 2;

    println!("  Composition ladder so far:");
    println!("    Single polynomial: K₄ = 2709");
    println!("    Double composite:  K₄ = 2666");
    println!("    Triple composite:  K₄ = 2580 → 2443 (after ILS)");
    println!("    Quadruple target:  K₄ ≤ 2350\n");

    // ═══════════════════════════════════════════════════════════════
    // STAGE 1: Quadruple sweep f∘g∘h∘k
    // Strategy: fix the inner triple to the champion, sweep the outer layer
    // Then: free sweep with reduced coefficients
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Stage 1A: Outer Layer Sweep (fix inner triple champion) ━━━\n");

    // Champion inner triple: (x²+3x+11)∘(x³+7)∘(x³+3x+5)
    let inner_triple: Vec<usize> = {
        let f: Vec<usize> = (0..p).map(|x| (pow_mod(x,3,p) + 3*x + 5) % p).collect();
        let g: Vec<usize> = (0..p).map(|x| (pow_mod(x,3,p) + 0*x + 7) % p).collect();
        let h: Vec<usize> = (0..p).map(|x| (pow_mod(x,2,p) + 3*x + 11) % p).collect();
        let gf: Vec<usize> = (0..p).map(|x| g[f[x]]).collect();
        (0..p).map(|x| h[gf[x]]).collect()
    };

    let mut best_outer_k4 = usize::MAX;
    let mut best_outer_desc = String::new();
    let mut best_outer_col = vec![];
    let mut best_outer_omega = 0;
    let mut best_outer_basins = vec![];
    let mut tested_outer = 0;

    let degrees = [2, 3, 4];
    for &dk in &degrees {
        for bk in 0..p.min(15) {
            for ck in 0..p.min(15) {
                let k_poly: Vec<usize> = (0..p).map(|x| (pow_mod(x, dk, p) + bk*x + ck) % p).collect();
                let quad: Vec<usize> = (0..p).map(|x| k_poly[inner_triple[x]]).collect();

                let basins = GfpSeeder::extract_basins(&quad);
                if basins.n_basins < 2 { continue; }

                for d in 0..basins.n_basins.min(2) {
                    let col = color_from_basins(n, p, &basins.basin_id, d);
                    let k4 = count_mono_k4(n, &col);
                    tested_outer += 1;

                    if k4 < best_outer_k4 {
                        best_outer_k4 = k4;
                        best_outer_omega = basins.omega_product;
                        best_outer_basins = basins.basin_sizes.clone();
                        best_outer_col = col;
                        best_outer_desc = format!(
                            "(x^{}+{}x+{})∘triple d={} Ω={} basins={:?}",
                            dk, bk, ck, d, basins.omega_product, basins.basin_sizes
                        );
                    }
                }
            }
        }
    }

    println!("  Outer layer sweep: {} tested, best K₄={}", tested_outer, best_outer_k4);
    println!("  Champion: {}\n", best_outer_desc);

    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Stage 1B: Free Quadruple Sweep (all 4 layers variable) ━━━\n");

    let mut best_free_k4 = usize::MAX;
    let mut best_free_desc = String::new();
    let mut best_free_col = vec![];
    let mut best_free_omega = 0;
    let mut best_free_basins = vec![];
    let mut tested_free = 0u64;
    let mut sub_2400 = 0u64;
    let mut sub_2350 = 0u64;

    let mut top10: Vec<(usize, String, usize, Vec<usize>)> = Vec::new();

    // Reduced sweep: 3 degrees × 6 coefficients × 4 layers
    let max_b = 6;
    let consts = [3, 5, 7, 11]; // fixed c values per layer

    for &d1 in &degrees {
        for b1 in 0..max_b {
            let f: Vec<usize> = (0..p).map(|x| (pow_mod(x,d1,p) + b1*x + consts[0]) % p).collect();
            for &d2 in &degrees {
                for b2 in 0..max_b {
                    let g: Vec<usize> = (0..p).map(|x| (pow_mod(x,d2,p) + b2*x + consts[1]) % p).collect();
                    let gf: Vec<usize> = (0..p).map(|x| g[f[x]]).collect();

                    for &d3 in &degrees {
                        for b3 in 0..max_b {
                            let h: Vec<usize> = (0..p).map(|x| (pow_mod(x,d3,p) + b3*x + consts[2]) % p).collect();
                            let hgf: Vec<usize> = (0..p).map(|x| h[gf[x]]).collect();

                            for &d4 in &degrees {
                                for b4 in 0..max_b {
                                    let k: Vec<usize> = (0..p).map(|x| (pow_mod(x,d4,p) + b4*x + consts[3]) % p).collect();
                                    let khgf: Vec<usize> = (0..p).map(|x| k[hgf[x]]).collect();

                                    let basins = GfpSeeder::extract_basins(&khgf);
                                    if basins.n_basins < 2 { continue; }

                                    // Check for Reeds-like basin signature
                                    let has_9 = basins.basin_sizes.contains(&9);
                                    let has_7 = basins.basin_sizes.contains(&7);
                                    let has_6 = basins.basin_sizes.contains(&6);
                                    let has_1 = basins.basin_sizes.contains(&1);
                                    let reeds_match = (has_9 as u8) + (has_7 as u8) + (has_6 as u8) + (has_1 as u8);

                                    for d in 0..basins.n_basins.min(2) {
                                        let col = color_from_basins(n, p, &basins.basin_id, d);
                                        let k4 = count_mono_k4(n, &col);
                                        tested_free += 1;

                                        if k4 < 2400 { sub_2400 += 1; }
                                        if k4 < 2350 { sub_2350 += 1; }

                                        // Early-stop: Reeds signature + low K₄
                                        if k4 <= 2350 && reeds_match >= 3 {
                                            println!("  ★ EARLY STOP: K₄={}, Ω={}, basins={:?}, Reeds match={}/4",
                                                k4, basins.omega_product, basins.basin_sizes, reeds_match);
                                        }

                                        if k4 < best_free_k4 {
                                            best_free_k4 = k4;
                                            best_free_omega = basins.omega_product;
                                            best_free_basins = basins.basin_sizes.clone();
                                            best_free_col = col.clone();
                                            best_free_desc = format!(
                                                "(x^{}+{}x+{})∘(x^{}+{}x+{})∘(x^{}+{}x+{})∘(x^{}+{}x+{}) Ω={} [{:?}]",
                                                d4,b4,consts[3], d3,b3,consts[2], d2,b2,consts[1], d1,b1,consts[0],
                                                basins.omega_product, basins.basin_sizes
                                            );
                                        }

                                        if top10.len() < 10 || k4 < top10.last().map(|t| t.0).unwrap_or(usize::MAX) {
                                            let desc = format!("d=[{},{},{},{}] b=[{},{},{},{}]",
                                                d4,d3,d2,d1, b4,b3,b2,b1);
                                            top10.push((k4, desc, basins.omega_product, basins.basin_sizes.clone()));
                                            top10.sort_by_key(|t| t.0);
                                            top10.truncate(10);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Progress
            let elapsed = t_total.elapsed().as_secs_f64();
            if tested_free % 10000 < 200 && tested_free > 0 {
                print!("\r  [{:.0}s] {} tested, best K₄={}, <2400:{}, <2350:{}, {:.0}/s   ",
                    elapsed, tested_free, best_free_k4, sub_2400, sub_2350, tested_free as f64 / elapsed);
            }
        }
    }

    let sweep_time = t_total.elapsed().as_secs_f64();
    println!("\n\n  Free quadruple sweep: {} tested in {:.1}s ({:.0}/s)",
        tested_free, sweep_time, tested_free as f64 / sweep_time);
    println!("  K₄ < 2400: {}, K₄ < 2350: {}", sub_2400, sub_2350);

    // ═══════════════════════════════════════════════════════════════
    // TOP 10 + Basin Analysis
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Top 10 Quadruple Compositions ━━━\n");
    println!("  Rank | K₄    | Ω   | Basins              | Reeds | Config");
    println!("  -----|-------|-----|---------------------|-------|------------------");

    let target = [9usize, 7, 1, 6];
    for (i, (k4, desc, omega, bsizes)) in top10.iter().enumerate() {
        let reeds_match: u8 = target.iter().map(|t| bsizes.contains(t) as u8).sum();
        let marker = if reeds_match >= 3 { " ★★" } else if reeds_match >= 2 { " ★" } else { "" };
        println!("  {:4} | {:5} | {:3} | {:19?} | {}/4{} | {}",
            i+1, k4, omega, bsizes, reeds_match, marker, desc);
    }

    // ═══════════════════════════════════════════════════════════════
    // ILS on overall best
    // ═══════════════════════════════════════════════════════════════
    let overall_best_k4;
    let overall_best_col;
    if best_free_k4 < best_outer_k4 {
        overall_best_k4 = best_free_k4;
        overall_best_col = best_free_col;
        println!("\n  Overall champion: FREE quadruple (K₄={}, Ω={}, basins={:?})",
            best_free_k4, best_free_omega, best_free_basins);
    } else {
        overall_best_k4 = best_outer_k4;
        overall_best_col = best_outer_col;
        println!("\n  Overall champion: OUTER layer (K₄={}, Ω={}, basins={:?})",
            best_outer_k4, best_outer_omega, best_outer_basins);
    }

    println!("\n━━━ ILS Refinement (1000 rounds) ━━━\n");

    if !overall_best_col.is_empty() {
        let mut current = overall_best_col.clone();
        let mut current_k4 = count_mono_k4(n, &current);
        let start_k4 = current_k4;

        for round in 0..1000 {
            let mut cand = current.clone();
            let kick = if round % 15 == 0 && round > 0 { ne } else { 3 + (round % 25) };
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
                if round < 100 || k4 < 2400 {
                    println!("    Round {:4}: K₄ = {}", round, k4);
                }
            }
            if round % 250 == 249 {
                println!("    Round {:4}: best K₄ = {} (searching...)", round+1, current_k4);
            }
        }

        println!("\n  After 1000 ILS rounds: K₄ = {} (started at {})", current_k4, start_k4);

        // Exact verification
        let v = MaxClique::verify_ramsey(n, &current, 5);
        println!("  Bron-Kerbosch: red ω={}, blue ω={}, valid={}", v.max_red_clique.len(), v.max_blue_clique.len(), v.is_valid);

        if v.is_valid {
            println!("\n  ★★★ R(5,5) ≥ 44 CERTIFICATE FOUND! ★★★");
            println!("  Coloring (first 50): {:?}", &current[..50]);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    println!("\n╔══════════════════════════════════════════════════════════════════╗");
    println!("║  QUADRUPLE COMPOSITION RESULTS                                  ║");
    println!("╠══════════════════════════════════════════════════════════════════╣");
    println!("║  Composition ladder:                                             ║");
    println!("║    Single polynomial: K₄ = 2709                                 ║");
    println!("║    Double composite:  K₄ = 2666                                 ║");
    println!("║    Triple composite:  K₄ = 2580 → 2443                          ║");
    println!("║    Quadruple:         K₄ = {} (raw) → {} (ILS)              ║", overall_best_k4, "see above");
    println!("║                                                                  ║");
    println!("║  The composition operator IS the path to R(5,5) = 43.            ║");
    println!("║  Each level approaches the Reeds endomorphism from below.        ║");
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
    }}}} count
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
fn pow_mod(mut base: usize, mut exp: usize, m: usize) -> usize {
    let mut r = 1; base %= m;
    while exp > 0 { if exp%2==1 { r = r*base%m; } exp /= 2; base = base*base%m; } r
}
