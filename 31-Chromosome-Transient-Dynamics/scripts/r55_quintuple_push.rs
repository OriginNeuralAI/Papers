//! R(5,5) Quintuple Push: Fix Ω=24 outer layer, sweep inner combinations
//!
//! Quadruple champion: K₄=2537→2431, blue ω=5, Ω=24 outer [24,5,6,8]
//! Strategy: keep the proven (x⁴+8x+12) outer layer fixed,
//! sweep inner quadruples targeting basin injection of 9, 7, 1
//! Early-stop: any seed with blue ω≤5 AND red ω=5 AND K₄≤2410

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) QUINTUPLE PUSH — Ω=24 outer fixed, inner sweep         ║");
    println!("║  Target: K₄≤2410, red ω→5, preserve blue ω=5, basins→[9,7,1,6]║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t_total = Instant::now();
    let p = 43usize;
    let n = 43usize;
    let ne = n * (n - 1) / 2;

    println!("  Ladder: 2709 → 2666 → 2580 → 2537 → ???");
    println!("  ω:      ?/?  → ?/?  → 6/6  → 6/5  → 5/5?");
    println!("  Ω:       56  →  9   →  8   →  24  → 24+\n");

    // The proven Ω=24 outer layer
    let outer = |x: usize| -> usize { (pow_mod(x, 4, p) + 8 * x + 12) % p };

    // Champion inner components from previous sweeps
    let inner_polys: Vec<(usize, usize, usize, &str)> = vec![
        // (degree, b, c, name)
        (3, 3, 5, "x³+3x+5"),
        (3, 0, 7, "x³+7"),
        (2, 3, 11, "x²+3x+11"),
        (2, 1, 13, "x²+x+13"),
        (2, 6, 5, "x²+6x+5"),
        (4, 7, 7, "x⁴+7x+7"),
        (4, 7, 2, "x⁴+7x+2"),
        (3, 12, 5, "x³+12x+5"),
        (2, 9, 12, "x²+9x+12"),
        (4, 8, 12, "x⁴+8x+12"),
    ];

    let make_poly = |d: usize, b: usize, c: usize| -> Vec<usize> {
        (0..p).map(|x| (pow_mod(x, d, p) + b * x + c) % p).collect()
    };

    // ═══════════════════════════════════════════════════════════════
    // STAGE 1: Quintuple sweep — outer fixed, 4 inner layers from champion pool
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Stage 1: Quintuple Sweep (Ω=24 outer × inner quads) ━━━\n");

    let mut best_k4 = usize::MAX;
    let mut best_desc = String::new();
    let mut best_col: Vec<i8> = vec![];
    let mut best_omega = 0;
    let mut best_basins: Vec<usize> = vec![];
    let mut tested = 0u64;

    let mut top10: Vec<(usize, String, usize, Vec<usize>)> = Vec::new();

    let np = inner_polys.len();

    for i1 in 0..np {
        let (d1, b1, c1, _) = inner_polys[i1];
        let f1 = make_poly(d1, b1, c1);

        for i2 in 0..np {
            let (d2, b2, c2, _) = inner_polys[i2];
            let f2 = make_poly(d2, b2, c2);
            let f2f1: Vec<usize> = (0..p).map(|x| f2[f1[x]]).collect();

            for i3 in 0..np {
                let (d3, b3, c3, _) = inner_polys[i3];
                let f3 = make_poly(d3, b3, c3);
                let f3f2f1: Vec<usize> = (0..p).map(|x| f3[f2f1[x]]).collect();

                for i4 in 0..np {
                    let (d4, b4, c4, _) = inner_polys[i4];
                    let f4 = make_poly(d4, b4, c4);
                    let f4f3f2f1: Vec<usize> = (0..p).map(|x| f4[f3f2f1[x]]).collect();

                    // Apply Ω=24 outer layer
                    let quintuple: Vec<usize> = (0..p).map(|x| outer(f4f3f2f1[x])).collect();

                    let basins = GfpSeeder::extract_basins(&quintuple);
                    if basins.n_basins < 2 { continue; }

                    // Check Reeds signature proximity
                    let has_9 = basins.basin_sizes.contains(&9);
                    let has_7 = basins.basin_sizes.contains(&7);
                    let has_6 = basins.basin_sizes.contains(&6);
                    let has_1 = basins.basin_sizes.contains(&1);
                    let reeds_count = (has_9 as u8) + (has_7 as u8) + (has_6 as u8) + (has_1 as u8);

                    for d in 0..basins.n_basins.min(2) {
                        let col = color_from_basins(n, p, &basins.basin_id, d);
                        let k4 = count_mono_k4(n, &col);
                        tested += 1;

                        // Early-stop: Reeds signature + low K₄
                        if k4 <= 2410 && reeds_count >= 3 {
                            println!("  ★ EARLY STOP: K₄={}, basins={:?}, Reeds={}/4, Ω={}",
                                k4, basins.basin_sizes, reeds_count, basins.omega_product);
                        }

                        if k4 < best_k4 {
                            best_k4 = k4;
                            best_omega = basins.omega_product;
                            best_basins = basins.basin_sizes.clone();
                            best_col = col.clone();
                            best_desc = format!(
                                "outer∘{}∘{}∘{}∘{} Ω={} {:?}",
                                inner_polys[i4].3, inner_polys[i3].3,
                                inner_polys[i2].3, inner_polys[i1].3,
                                basins.omega_product, basins.basin_sizes
                            );
                        }

                        if top10.len() < 10 || k4 < top10.last().map(|t| t.0).unwrap_or(usize::MAX) {
                            let desc = format!("{}∘{}∘{}∘{}",
                                inner_polys[i4].3, inner_polys[i3].3,
                                inner_polys[i2].3, inner_polys[i1].3);
                            top10.push((k4, desc, basins.omega_product, basins.basin_sizes.clone()));
                            top10.sort_by_key(|t| t.0);
                            top10.truncate(10);
                        }
                    }
                }
            }

            // Progress
            if tested % 5000 < 50 && tested > 0 {
                let elapsed = t_total.elapsed().as_secs_f64();
                print!("\r  [{:.0}s] {} tested, best K₄={}, {:.0}/s   ",
                    elapsed, tested, best_k4, tested as f64 / elapsed);
            }
        }
    }

    let sweep_time = t_total.elapsed().as_secs_f64();
    println!("\n\n  Sweep: {} quintuples in {:.1}s ({:.0}/s)", tested, sweep_time, tested as f64 / sweep_time);
    println!("  Best raw K₄: {}, Ω: {}, basins: {:?}", best_k4, best_omega, best_basins);
    println!("  → {}\n", best_desc);

    // ═══════════════════════════════════════════════════════════════
    // TOP 10
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Top 10 Quintuples ━━━\n");
    let target = [9usize, 7, 1, 6];
    for (i, (k4, desc, omega, bsizes)) in top10.iter().enumerate() {
        let rc: u8 = target.iter().map(|t| bsizes.contains(t) as u8).sum();
        let m = if rc >= 3 { " ★★" } else if rc >= 2 { " ★" } else { "" };
        println!("  #{}: K₄={}, Ω={}, basins={:?}, Reeds={}/4{} — outer∘{}",
            i+1, k4, omega, bsizes, rc, m, desc);
    }

    // ═══════════════════════════════════════════════════════════════
    // ILS on champion
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ ILS Refinement (1000 rounds) ━━━\n");

    if !best_col.is_empty() {
        let mut current = best_col;
        let mut current_k4 = count_mono_k4(n, &current);
        let start_k4 = current_k4;

        for round in 0..1000 {
            let mut cand = current.clone();
            let kick = if round % 15 == 0 && round > 0 { ne } else { 3 + (round % 25) };
            let mut rng = (round as u64 * 999983).wrapping_mul(6364136223846793005);
            if kick >= ne { for s in cand.iter_mut() { *s = -*s; } }
            else { for _ in 0..kick { rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1); cand[(rng as usize) % ne] *= -1; } }
            greedy_k4(n, &mut cand, 30);
            let k4 = count_mono_k4(n, &cand);
            if k4 < current_k4 { current_k4 = k4; current = cand;
                if round < 100 || k4 < 2400 { println!("    Round {:4}: K₄ = {}", round, k4); }
            }
            if round % 250 == 249 { println!("    Round {:4}: best K₄ = {}", round+1, current_k4); }
        }

        println!("\n  After 1000 ILS: K₄ = {} (from {})", current_k4, start_k4);

        let v = MaxClique::verify_ramsey(n, &current, 5);
        println!("  Bron-Kerbosch: red ω={}, blue ω={}, valid={}\n",
            v.max_red_clique.len(), v.max_blue_clique.len(), v.is_valid);

        if v.is_valid { println!("  ★★★ R(5,5) ≥ 44 CERTIFICATE FOUND! ★★★\n"); }

        // Final ladder
        println!("╔══════════════════════════════════════════════════════════════════╗");
        println!("║  COMPOSITION LADDER — COMPLETE                                  ║");
        println!("╠══════════════════════════════════════════════════════════════════╣");
        println!("║  Level     │ Raw K₄ │ Post-ILS │ Δ    │ ω(R/B) │ Ω             ║");
        println!("║  ──────────┼────────┼──────────┼──────┼────────┼───────────     ║");
        println!("║  Single    │ 2709   │ ~2462    │  —   │  ?/?   │ 56             ║");
        println!("║  Double    │ 2666   │ ~2462    │  0   │  ?/?   │  9             ║");
        println!("║  Triple    │ 2580   │  2443    │ -19  │  6/6   │  8             ║");
        println!("║  Quadruple │ 2537   │  2431    │ -12  │  6/5   │ 24             ║");
        println!("║  Quintuple │ {:4}   │  {:4}    │ {:+4} │  {}/{}   │ {:2}             ║",
            best_k4, current_k4, current_k4 as i64 - 2431,
            v.max_red_clique.len(), v.max_blue_clique.len(), best_omega);
        println!("║  ──────────┼────────┼──────────┼──────┼────────┼───────────     ║");
        println!("║  Reeds     │   ?    │    0     │  —   │  4/4   │ 24             ║");
        println!("║                                                                  ║");
        println!("║  Total time: {:.1}s                                              ║", t_total.elapsed().as_secs_f64());
        println!("╚══════════════════════════════════════════════════════════════════╝");
    }
}

fn color_from_basins(n: usize, p: usize, basin_id: &[usize], dominant: usize) -> Vec<i8> {
    let ne = n * (n - 1) / 2;
    let mut col = vec![0i8; ne];
    for u in 0..n { for v in (u+1)..n {
        let idx = u * n - u * (u + 1) / 2 + v - u - 1;
        let diff = ((v as i64 - u as i64).abs() as usize) % p;
        let key = if diff <= p/2 { diff } else { p - diff };
        col[idx] = if key < basin_id.len() && basin_id[key] == dominant { 1 } else { -1 };
    }} col
}
fn count_mono_k4(n: usize, col: &[i8]) -> usize {
    let edge = |u: usize, v: usize| -> i8 {
        let (a, b) = if u < v { (u, v) } else { (v, u) };
        col[a * n - a * (a + 1) / 2 + b - a - 1]
    };
    let mut c = 0;
    for a in 0..n { for b in a+1..n { let ab = edge(a,b);
        for cc in b+1..n { if edge(a,cc)!=ab || edge(b,cc)!=ab { continue; }
            for d in cc+1..n {
                if edge(a,d)==ab && edge(b,d)==ab && edge(cc,d)==ab { c += 1; }
    }}}} c
}
fn greedy_k4(n: usize, col: &mut Vec<i8>, rounds: usize) {
    let ne = n * (n - 1) / 2;
    for _ in 0..rounds {
        let before = count_mono_k4(n, col); if before == 0 { return; }
        let mut improved = false;
        for e in 0..ne { col[e] *= -1;
            if count_mono_k4(n, col) < before { improved = true; break; }
            col[e] *= -1;
        } if !improved { return; }
    }
}
fn pow_mod(mut base: usize, mut exp: usize, m: usize) -> usize {
    let mut r = 1; base %= m;
    while exp > 0 { if exp%2==1 { r = r*base%m; } exp /= 2; base = base*base%m; } r
}
