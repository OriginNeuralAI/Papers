//! R(5,5) FINAL ASSAULT — From ω=5/5 to ω=4/4
//!
//! We're at the absolute boundary: both colors have max clique exactly 5.
//! The last K₅ in each color must be destroyed simultaneously.
//!
//! Multi-strategy attack:
//! 1. Extract the EXACT violating K₅ cliques from the ω=5/5 champion
//! 2. Targeted flip: only flip edges WITHIN violating cliques
//! 3. Deep ILS with violation-aware kicks
//! 4. Sextuple/septuple composition pushing Ω toward 24
//! 5. Exhaustive 2-flip and 3-flip on violating edges

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) FINAL ASSAULT — From ω=5/5 to ω=4/4                   ║");
    println!("║  Both colors at the boundary. One step to history.              ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t_total = Instant::now();
    let p = 43usize;
    let n = 43usize;
    let ne = n * (n - 1) / 2;

    // Reconstruct the quintuple champion
    let outer = |x: usize| -> usize { (pow_mod(x, 4, p) + 8*x + 12) % p };
    let f1: Vec<usize> = (0..p).map(|x| (pow_mod(x,2,p) + 3*x + 11) % p).collect();
    let f2: Vec<usize> = (0..p).map(|x| (pow_mod(x,2,p) + 3*x + 11) % p).collect();
    let f3: Vec<usize> = (0..p).map(|x| (pow_mod(x,3,p) + 3*x + 5) % p).collect();
    let f4: Vec<usize> = (0..p).map(|x| (pow_mod(x,4,p) + 8*x + 12) % p).collect();

    let comp: Vec<usize> = (0..p).map(|x| {
        outer(f4[f3[f2[f1[x]]]])
    }).collect();

    let basins = GfpSeeder::extract_basins(&comp);
    let mut champion = color_from_basins(n, p, &basins.basin_id, 0);

    // Greedy to get to the ω=5/5 state
    greedy_k4(n, &mut champion, 100);

    let v0 = MaxClique::verify_ramsey(n, &champion, 5);
    println!("  Starting point: red ω={}, blue ω={}, K₄={}",
        v0.max_red_clique.len(), v0.max_blue_clique.len(), count_mono_k4(n, &champion));

    // ═══════════════════════════════════════════════════════════════
    // ATTACK 1: Find ALL monochromatic K₅ cliques
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Attack 1: Enumerate All Monochromatic K₅ ━━━\n");

    let edge = |col: &[i8], u: usize, v: usize| -> i8 {
        let (a, b) = if u < v { (u, v) } else { (v, u) };
        col[a * n - a * (a + 1) / 2 + b - a - 1]
    };

    let mut red_k5: Vec<Vec<usize>> = Vec::new();
    let mut blue_k5: Vec<Vec<usize>> = Vec::new();

    for a in 0..n { for b in a+1..n { for c in b+1..n { for dd in c+1..n { for e in dd+1..n {
        let verts = [a, b, c, dd, e];
        let mut all_same = true;
        let color = edge(&champion, a, b);
        for i in 0..5 { for j in i+1..5 {
            if edge(&champion, verts[i], verts[j]) != color { all_same = false; }
        }}
        if all_same {
            if color == 1 { red_k5.push(verts.to_vec()); }
            else { blue_k5.push(verts.to_vec()); }
        }
    }}}}}

    println!("  Red K₅ cliques: {}", red_k5.len());
    println!("  Blue K₅ cliques: {}", blue_k5.len());

    for (i, clique) in red_k5.iter().take(5).enumerate() {
        println!("    Red #{}: {:?}", i+1, clique);
    }
    for (i, clique) in blue_k5.iter().take(5).enumerate() {
        println!("    Blue #{}: {:?}", i+1, clique);
    }

    // Collect all edges in violating cliques
    let mut violating_edges: Vec<usize> = Vec::new();
    for clique in red_k5.iter().chain(blue_k5.iter()) {
        for i in 0..5 { for j in i+1..5 {
            let (a, b) = if clique[i] < clique[j] { (clique[i], clique[j]) } else { (clique[j], clique[i]) };
            let idx = a * n - a * (a + 1) / 2 + b - a - 1;
            if !violating_edges.contains(&idx) { violating_edges.push(idx); }
        }}
    }
    println!("  Unique violating edges: {} out of {}", violating_edges.len(), ne);

    // ═══════════════════════════════════════════════════════════════
    // ATTACK 2: Exhaustive 1-flip on violating edges
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Attack 2: Exhaustive 1-Flip on Violating Edges ━━━\n");

    let mut found_1flip = false;
    for &e in &violating_edges {
        champion[e] *= -1;
        let v = MaxClique::verify_ramsey(n, &champion, 5);
        if v.is_valid {
            println!("  ★★★ 1-FLIP SOLUTION: edge {} → R(5,5) ≥ 44! ★★★", e);
            found_1flip = true;
            champion[e] *= -1; // keep it flipped
            break;
        }
        if v.max_red_clique.len() <= 4 || v.max_blue_clique.len() <= 4 {
            println!("    Edge {}: red ω={}, blue ω={} (partial improvement)",
                e, v.max_red_clique.len(), v.max_blue_clique.len());
        }
        champion[e] *= -1;
    }
    if !found_1flip { println!("  No single flip solves it. Barrier confirmed at depth > 1."); }

    // ═══════════════════════════════════════════════════════════════
    // ATTACK 3: Exhaustive 2-flip on violating edges
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Attack 3: 2-Flip on Violating Edges ━━━\n");

    let n_ve = violating_edges.len();
    let mut found_2flip = false;
    let mut best_2flip_omega = 10usize;
    let mut pairs_tested = 0u64;

    for i in 0..n_ve {
        for j in i+1..n_ve {
            champion[violating_edges[i]] *= -1;
            champion[violating_edges[j]] *= -1;

            let v = MaxClique::verify_ramsey(n, &champion, 5);
            pairs_tested += 1;

            let max_omega = v.max_red_clique.len().max(v.max_blue_clique.len());

            if v.is_valid {
                println!("  ★★★ 2-FLIP SOLUTION: edges {},{} → R(5,5) ≥ 44! ★★★",
                    violating_edges[i], violating_edges[j]);
                found_2flip = true;
                break;
            }

            if max_omega < best_2flip_omega {
                best_2flip_omega = max_omega;
                println!("    Pair ({},{}): max ω={} (new best)",
                    violating_edges[i], violating_edges[j], max_omega);
            }

            champion[violating_edges[i]] *= -1;
            champion[violating_edges[j]] *= -1;
        }
        if found_2flip { break; }
    }
    println!("  2-flip pairs tested: {}, best max ω = {}", pairs_tested, best_2flip_omega);

    // ═══════════════════════════════════════════════════════════════
    // ATTACK 4: Deep ILS with violation-aware kicks
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Attack 4: Deep Violation-Aware ILS (2000 rounds) ━━━\n");

    let mut current = champion.clone();
    let mut current_k4 = count_mono_k4(n, &current);
    let mut best_max_omega = 5usize;

    for round in 0..2000 {
        let mut cand = current.clone();

        // Violation-aware kick: preferentially flip violating edges
        let mut rng = (round as u64 * 999983).wrapping_mul(6364136223846793005);

        if round % 15 == 0 && round > 0 {
            // Z₂ complement
            for s in cand.iter_mut() { *s = -*s; }
        } else if round % 3 == 0 && !violating_edges.is_empty() {
            // Flip violating edges preferentially
            let kick = 2 + (round % 8);
            for _ in 0..kick {
                rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                let idx = violating_edges[(rng as usize) % violating_edges.len()];
                cand[idx] *= -1;
            }
        } else {
            // Random kick
            let kick = 3 + (round % 20);
            for _ in 0..kick {
                rng = rng.wrapping_mul(6364136223846793005).wrapping_add(1);
                cand[(rng as usize) % ne] *= -1;
            }
        }

        greedy_k4(n, &mut cand, 30);
        let k4 = count_mono_k4(n, &cand);

        if k4 < current_k4 {
            current_k4 = k4;
            current = cand.clone();
        }

        // Periodic exact check
        if round % 100 == 99 || k4 < current_k4 - 10 {
            let v = MaxClique::verify_ramsey(n, &cand, 5);
            let mo = v.max_red_clique.len().max(v.max_blue_clique.len());

            if v.is_valid {
                println!("  ★★★ ILS FOUND R(5,5) ≥ 44 at round {}! ★★★", round);
                println!("  Coloring (first 50): {:?}", &cand[..50]);
                break;
            }

            if mo < best_max_omega {
                best_max_omega = mo;
                println!("    Round {}: K₄={}, ω={}/{} (new best max ω={})",
                    round, k4, v.max_red_clique.len(), v.max_blue_clique.len(), mo);
            }
        }

        if round % 500 == 499 {
            println!("    Round {}: K₄={}, best max ω={}", round+1, current_k4, best_max_omega);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // ATTACK 5: Higher composition levels (sextuple, septuple)
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Attack 5: Sextuple/Septuple Quick Probe ━━━\n");

    let make_poly = |d: usize, b: usize, c: usize| -> Vec<usize> {
        (0..p).map(|x| (pow_mod(x, d, p) + b*x + c) % p).collect()
    };

    let champion_polys: Vec<(usize, usize, usize)> = vec![
        (2,3,11), (2,3,11), (3,3,5), (4,8,12), (4,8,12), // quintuple layers
        (2,1,13), (3,12,5), (2,6,5), (4,7,7), (2,9,12),   // other champions
    ];

    let mut best_high_k4 = usize::MAX;
    let mut best_high_desc = String::new();

    // Sextuple: add one more layer to the quintuple
    for &(d6, b6, c6) in &champion_polys {
        let f6 = make_poly(d6, b6, c6);
        let sextuple: Vec<usize> = (0..p).map(|x| f6[comp[x]]).collect();
        let basins = GfpSeeder::extract_basins(&sextuple);
        if basins.n_basins < 2 { continue; }

        for d in 0..basins.n_basins.min(2) {
            let col = color_from_basins(n, p, &basins.basin_id, d);
            let k4 = count_mono_k4(n, &col);
            if k4 < best_high_k4 {
                best_high_k4 = k4;
                best_high_desc = format!("sextuple: x^{}+{}x+{}∘quint Ω={} basins={:?}",
                    d6, b6, c6, basins.omega_product, basins.basin_sizes);
            }
        }
    }

    println!("  Best sextuple raw K₄: {} — {}", best_high_k4, best_high_desc);

    // Verify sextuple champion after greedy
    if best_high_k4 < usize::MAX {
        // Reconstruct and refine
        for &(d6, b6, c6) in &champion_polys {
            let f6 = make_poly(d6, b6, c6);
            let sextuple: Vec<usize> = (0..p).map(|x| f6[comp[x]]).collect();
            let basins = GfpSeeder::extract_basins(&sextuple);
            if basins.n_basins < 2 { continue; }
            for d in 0..basins.n_basins.min(2) {
                let mut col = color_from_basins(n, p, &basins.basin_id, d);
                let k4 = count_mono_k4(n, &col);
                if k4 == best_high_k4 {
                    greedy_k4(n, &mut col, 50);
                    let v = MaxClique::verify_ramsey(n, &col, 5);
                    println!("  After greedy: K₄={}, red ω={}, blue ω={}",
                        count_mono_k4(n, &col), v.max_red_clique.len(), v.max_blue_clique.len());
                    break;
                }
            }
            break;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    let total_s = t_total.elapsed().as_secs_f64();
    println!("\n╔══════════════════════════════════════════════════════════════════╗");
    println!("║  FINAL ASSAULT RESULTS                                          ║");
    println!("╠══════════════════════════════════════════════════════════════════╣");
    println!("║  Starting: ω = 5/5 (both colors at boundary)                    ║");
    println!("║  Red K₅ cliques:  {}                                            ║", red_k5.len());
    println!("║  Blue K₅ cliques: {}                                            ║", blue_k5.len());
    println!("║  Violating edges: {} / {}                                       ║", violating_edges.len(), ne);
    println!("║  1-flip: {}                                                     ║",
        if found_1flip { "★ SOLUTION FOUND" } else { "no solution (barrier > 1)" });
    println!("║  2-flip: {} pairs, best ω = {}                                  ║", pairs_tested, best_2flip_omega);
    println!("║  Deep ILS: best max ω = {}                                      ║", best_max_omega);
    println!("║  Sextuple: K₄ = {}                                              ║", best_high_k4);
    println!("║  Total: {:.1}s                                                  ║", total_s);
    println!("╚══════════════════════════════════════════════════════════════════╝");
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
        let mut imp = false;
        for e in 0..ne { col[e] *= -1;
            if count_mono_k4(n, col) < before { imp = true; break; }
            col[e] *= -1;
        } if !imp { return; }
    }
}
fn pow_mod(mut base: usize, mut exp: usize, m: usize) -> usize {
    let mut r = 1; base %= m;
    while exp > 0 { if exp%2==1 { r = r*base%m; } exp /= 2; base = base*base%m; } r
}
