//! R(5,5) Fast Push: Quick sweep + targeted verification
//! Uses fast K₄ counting for screening, exact Bron-Kerbosch only on best candidates

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) FAST PUSH — Sweep + Targeted Verify                    ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t = Instant::now();
    let n = 43;
    let ne = n * (n - 1) / 2;

    // Fast edge accessor
    let edge_idx = |u: usize, v: usize| -> usize {
        let (a, b) = if u < v { (u, v) } else { (v, u) };
        a * n - a * (a + 1) / 2 + b - a - 1
    };

    // Fast monochromatic K₄ counter (proxy for K₅ violations)
    let count_mono_k4 = |col: &[i8]| -> usize {
        let edge = |u: usize, v: usize| -> i8 { col[edge_idx(u, v)] };
        let mut count = 0;
        for a in 0..n { for b in a+1..n { let ab = edge(a,b);
            for c in b+1..n { if edge(a,c)!=ab || edge(b,c)!=ab { continue; }
                for d in c+1..n {
                    if edge(a,d)==ab && edge(b,d)==ab && edge(c,d)==ab { count += 1; }
        }}}}
        count
    };

    // Greedy descent minimizing K₄ count
    let greedy = |col: &mut Vec<i8>, rounds: usize| {
        for _ in 0..rounds {
            let before = count_mono_k4(col);
            if before == 0 { return; }
            let mut improved = false;
            for e in 0..ne {
                col[e] = -col[e];
                if count_mono_k4(col) < before { improved = true; break; }
                col[e] = -col[e];
            }
            if !improved { return; }
        }
    };

    println!("━━━ Stage 1: GF(p) Sweep (fast K₄ screening) ━━━\n");

    let primes = [41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83];
    let mut candidates: Vec<(String, Vec<i8>, usize)> = Vec::new();

    for &p in &primes {
        let tp = Instant::now();
        let mut best_k4 = usize::MAX;
        let mut best_desc = String::new();
        let mut best_col = vec![];
        let mut tested = 0;

        for b in 0..p.min(20) {
            for c in 0..p.min(20) {
                let graph = GfpSeeder::functional_graph(p, b, c);
                let basins = GfpSeeder::extract_basins(&graph);
                if basins.n_basins < 2 { continue; }

                for d in 0..basins.n_basins.min(3) {
                    let cfg = isomorphic_engine::isomorphic::gfp_seeding::GfpConfig {
                        prime: p, poly_b: b, poly_c: c, dominant_basin: d,
                    };
                    let mut col = GfpSeeder::ramsey_coloring(n, &cfg);
                    greedy(&mut col, 20);
                    let k4 = count_mono_k4(&col);
                    tested += 1;

                    if k4 < best_k4 {
                        best_k4 = k4;
                        best_desc = format!("GF({}) b={} c={} d={}", p, b, c, d);
                        best_col = col;
                    }
                }
            }
        }

        if !best_col.is_empty() {
            println!("  GF({:2}): best K₄={:4}, {} tested, {:.0}ms — {}",
                p, best_k4, tested, tp.elapsed().as_secs_f64()*1000.0, best_desc);
            candidates.push((best_desc, best_col, best_k4));
        }
    }

    candidates.sort_by_key(|c| c.2);

    println!("\n  Top 5 by mono-K₄ count:");
    for (i, (desc, _, k4)) in candidates.iter().take(5).enumerate() {
        println!("    #{}: {} → {} mono-K₄", i+1, desc, k4);
    }

    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Stage 2: ILS on Top 3 Seeds (200 rounds) ━━━\n");

    for ci in 0..candidates.len().min(3) {
        let (ref desc, ref seed, _) = candidates[ci];
        let mut best = seed.clone();
        let mut best_k4 = count_mono_k4(&best);

        for round in 0..200 {
            let mut cand = best.clone();

            // Perturbation
            let kick = if round % 15 == 0 && round > 0 { ne } // Z₂ complement
                       else { 3 + (round % 30) };

            let mut rng = (round as u64 * 999983 + ci as u64).wrapping_mul(6364136223846793005);
            if kick >= ne {
                for s in cand.iter_mut() { *s = -*s; }
            } else {
                for _ in 0..kick {
                    rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                    cand[(rng as usize) % ne] *= -1;
                }
            }

            greedy(&mut cand, 50);
            let k4 = count_mono_k4(&cand);

            if k4 < best_k4 {
                best_k4 = k4;
                best = cand;
                if round < 50 || k4 < 10 {
                    println!("    Seed {}: round {} → K₄={}", ci+1, round, k4);
                }
            }
        }

        println!("  Seed {} ({}): K₄ {} → {}", ci+1, desc, candidates[ci].2, best_k4);
        candidates[ci].1 = best;
        candidates[ci].2 = best_k4;
    }

    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Stage 3: Exact Bron-Kerbosch on Best 3 ━━━\n");

    candidates.sort_by_key(|c| c.2);

    for (i, (desc, col, k4)) in candidates.iter().take(3).enumerate() {
        let tv = Instant::now();
        let v = MaxClique::verify_ramsey(n, col, 5);
        let ms = tv.elapsed().as_secs_f64() * 1000.0;

        let reds = col.iter().filter(|&&s| s == 1).count();
        println!("  #{} {} (K₄={}, {} red/{} blue):", i+1, desc, k4, reds, ne-reds);
        println!("    Red ω={} {:?}", v.max_red_clique.len(),
            &v.max_red_clique[..v.max_red_clique.len().min(8)]);
        println!("    Blue ω={} {:?}", v.max_blue_clique.len(),
            &v.max_blue_clique[..v.max_blue_clique.len().min(8)]);
        println!("    Valid R(5,5): {}  ({:.0}ms)", v.is_valid, ms);

        if v.is_valid {
            println!("\n  ★★★ R(5,5) ≥ 44 CERTIFICATE FOUND! ★★★\n");
        }
    }

    let total = t.elapsed().as_secs_f64();
    println!("\n╔══════════════════════════════════════════════════════════════════╗");
    println!("║  Total time: {:.1}s                                             ║", total);
    println!("║  Configs tested: ~{}                                         ║",
        primes.len() * 400 * 3);
    println!("╚══════════════════════════════════════════════════════════════════╝");
}
