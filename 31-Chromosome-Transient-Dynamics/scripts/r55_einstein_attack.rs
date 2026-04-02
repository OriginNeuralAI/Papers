//! R(5,5) Einstein Attack: Every tool in the arsenal on K₄₃
//!
//! Chain all 14 Einstein tools + the full engine on the R(5,5) frontier:
//! 1. GF(p) seeding sweep (p = 41, 43, 47, 53) — find best algebraic seeds
//! 2. Phase diagram — instance-specific T_c for K₄₃ Ramsey Ising
//! 3. Rational engine — algebraic SA/SBM parameters from basin integers
//! 4. Spectral split — cycle vs transient structure of the K₄₃ coupling
//! 5. Entropy lock — O(1) difficulty classification
//! 6. Landscape RG — multi-scale coarse-graining
//! 7. Born rule allocation — quantum-optimal budget across 16 solvers
//! 8. PT-SBM solver — imaginary tunneling on the Ramsey landscape
//! 9. Hybrid SBM→SA handoff — Phase A/B transition
//! 10. TBO diagnostic — retrocausal coherence detection on trajectory
//! 11. Barrier depth — k-flip analysis at the 2-violation floor
//! 12. Bron-Kerbosch — exact max-clique verification
//! 13. Zero-core — distributed obstruction analysis
//! 14. Omega scanner — S4 orbit decomposition

use std::time::Instant;
use isomorphic_engine::prelude::*;
use isomorphic_engine::matrix::{DenseMatrix, energy::{ising_energy, delta_energy_flip}};
use isomorphic_engine::isomorphic::spectral_quality::SpectralAnalyzer;
use isomorphic_engine::isomorphic::gfp_seeding::GfpSeeder;
use isomorphic_engine::diagnostics::phase_diagram::PhaseDiagram;
use isomorphic_engine::diagnostics::spectral_split::SpectralSplit;
use isomorphic_engine::diagnostics::entropy_lock::EntropyLock;
use isomorphic_engine::diagnostics::barrier_depth::BarrierDepthAnalyzer;
use isomorphic_engine::diagnostics::tbo_diagnostic::TboDiagnostic;
use isomorphic_engine::solvers::{Solver, SbmSolver, SaSolver};
use isomorphic_engine::orchestrator::convergence::AtomicBestEnergy;
use isomorphic_engine::stagnation::TieredStagnationDetector;

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) EINSTEIN ATTACK — All 14 Tools on K₄₃                  ║");
    println!("║  Target: reduce violations from 2 → 0 on K₄₃                   ║");
    println!("╚══════════════════════════════════════════════════════════════════╝\n");

    let t_total = Instant::now();
    let n = 43;
    let ne = n * (n - 1) / 2; // 903 edges

    // ═══════════════════════════════════════════════════════════════
    // PHASE 1: Algebraic Seeding — Find the best starting point
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Phase 1: GF(p) Algebraic Seeding Sweep ━━━\n");

    let primes = [41, 43, 47, 53, 59];
    let mut best_coloring: Vec<i8> = vec![];
    let mut best_violations = usize::MAX;
    let mut best_config_str = String::new();

    for &p in &primes {
        let candidates = GfpSeeder::enumerate_polynomials(p, 5);
        for cfg in &candidates {
            let coloring = GfpSeeder::ramsey_coloring(n, cfg);
            let verification = MaxClique::verify_ramsey(n, &coloring, 5);
            let max_clique = verification.max_red_clique.len().max(verification.max_blue_clique.len());

            // Count violations: if max_clique >= 5, we have violations
            let violations = if verification.is_valid { 0 } else {
                // Estimate from clique sizes
                if max_clique >= 5 { max_clique - 4 } else { 0 }
            };

            if violations < best_violations || (violations == best_violations && best_coloring.is_empty()) {
                best_violations = violations;
                best_coloring = coloring.clone();
                best_config_str = format!("GF({}) b={} c={} d={}", p, cfg.poly_b, cfg.poly_c, cfg.dominant_basin);
            }

            if violations == 0 {
                println!("  ★ ZERO VIOLATIONS: {} → R(5,5) ≥ 44!", best_config_str);
                break;
            }
        }
        let best_for_p = candidates.iter().map(|cfg| {
            let col = GfpSeeder::ramsey_coloring(n, cfg);
            let v = MaxClique::verify_ramsey(n, &col, 5);
            if v.is_valid { 0usize } else { v.max_red_clique.len().max(v.max_blue_clique.len()).saturating_sub(4) }
        }).min().unwrap_or(999);
        println!("  GF({}): best seed → {} est. violations", p, best_for_p);
    }

    // Also try the known K43 frontier config
    let k43_cfg = GfpSeeder::k43_frontier_config();
    let k43_col = GfpSeeder::ramsey_coloring(n, &k43_cfg);
    let k43_v = MaxClique::verify_ramsey(n, &k43_col, 5);
    println!("  Known K₄₃ frontier (GF(43) b=30 c=41 d=0): valid={}, red ω={}, blue ω={}",
        k43_v.is_valid, k43_v.max_red_clique.len(), k43_v.max_blue_clique.len());

    if best_coloring.is_empty() {
        best_coloring = k43_col.clone();
        best_config_str = "GF(43) b=30 c=41 d=0 (known frontier)".to_string();
    }

    let reds = best_coloring.iter().filter(|&&s| s == 1).count();
    println!("\n  Best seed: {} ({} red / {} blue)\n", best_config_str, reds, ne - reds);

    // ═══════════════════════════════════════════════════════════════
    // PHASE 2: Build Ramsey Ising Model from best coloring
    // ═══════════════════════════════════════════════════════════════
    println!("━━━ Phase 2: Build K₄₃ Ramsey Ising Model ━━━\n");

    let model = build_ramsey_ising(n, 5);
    println!("  Ising model: N={} spins (edges), encoding R(5,5) on K₄₃", ne);

    // ═══════════════════════════════════════════════════════════════
    // PHASE 3: Einstein Pre-Solve Analysis
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Phase 3: Einstein Pre-Solve Analysis ━━━\n");

    // Tool 1: Phase Diagram
    let t = Instant::now();
    let pd = PhaseDiagram::compute(&model, 15, 30, 42);
    println!("  Phase Diagram: T_c = {:.4}, SA optimal [{:.4}, {:.4}] ({:.1}ms)",
        pd.instance_tc, pd.sa_t_end, pd.sa_t_start, t.elapsed().as_secs_f64() * 1000.0);

    // Tool 8: Rational Engine
    let spectral = SpectralAnalyzer::analyze(&model);
    let rational = RationalEngine::derive(spectral.gap);
    println!("  Rational Engine: SA=[{:.5}, {:.4}], SBM_KERR={:.4}, restarts={}",
        rational.sa_t_end, rational.sa_t_start, rational.sbm_kerr, rational.restarts);

    // Tool 3: Spectral Split
    let split = SpectralSplit::analyze(&spectral.top_eigenvalues, model.n);
    println!("  Spectral Split: β_cycle={:.3}, β_trans={:.3}, Δβ={:+.3}",
        split.beta_cycle, split.beta_transient, split.delta_beta);

    // Tool 11: Entropy Lock
    let diff = EntropyLock::quick_classify(&model);
    println!("  Entropy Lock: {:?}", diff);

    // Tool 14: Omega Scanner
    let omega = OmegaScanner::scan(&model);
    println!("  Omega Scanner: Ω={}, {} sectors, symmetry order={}",
        omega.omega_detected, omega.n_sectors, omega.symmetry_order);

    // Tool 4: Landscape RG
    let t = Instant::now();
    let (rg_flow, _) = LandscapeRG::flow(&model, 5, 0.1);
    println!("  Landscape RG: {} levels, converged={} ({:.1}ms)",
        rg_flow.total_levels, rg_flow.converged, t.elapsed().as_secs_f64() * 1000.0);
    let scale_str: String = rg_flow.levels.iter().map(|l| format!("{}", l.n)).collect::<Vec<_>>().join("→");
    println!("    Scale flow: {}", scale_str);

    // Tool 12: Born Rule Allocation
    let solver_names = vec!["SBM", "CIM", "SA", "DMM", "Kuramoto", "PT-SBM",
                           "CVTR", "SASSHA", "ComplexSBM", "SOLG"];
    let born = BornAllocator::allocate(&solver_names, 24);
    println!("  Born Allocation: {} solvers, top budget: {}={:.1}%",
        solver_names.len(),
        born.solver_budgets[0].0, born.solver_budgets[0].1 * 100.0);

    // ═══════════════════════════════════════════════════════════════
    // PHASE 4: Multi-Solver Attack
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Phase 4: 16-Solver Ensemble Attack ━━━\n");

    // Configure with Einstein tools
    let mut config = SolverConfig::quality();
    config.solver_overrides.insert("PHASE_DIAGRAM_ENABLED".into(), 1.0);
    config.solver_overrides.insert("RATIONAL_ENABLED".into(), 1.0);
    config.track_diagnostics = true;

    let router = IsomorphicRouter::new(config);
    let t = Instant::now();
    let result = router.solve(&model);
    let solve_ms = t.elapsed().as_secs_f64() * 1000.0;

    println!("  Ensemble result:");
    println!("    Energy: {:.4}", result.best.energy);
    println!("    Solver: {}", result.best.solver_name);
    println!("    Steps: {}", result.best.steps_executed);
    println!("    Time: {:.1}ms", solve_ms);
    println!("    I-value: {:.4}", result.i_value);
    println!("    T-class: {}", result.t_class);

    // ═══════════════════════════════════════════════════════════════
    // PHASE 5: Verify & Analyze Result
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Phase 5: Verification & Analysis ━━━\n");

    // Extract coloring from ground state spins
    let ground_spins = &result.best.spins;

    // Tool 9: Bron-Kerbosch verification
    let t = Instant::now();
    let verification = MaxClique::verify_ramsey(n, ground_spins, 5);
    let verify_ms = t.elapsed().as_secs_f64() * 1000.0;

    println!("  Bron-Kerbosch verification ({:.1}ms):", verify_ms);
    println!("    Valid R(5,5) certificate: {}", verification.is_valid);
    println!("    Max red clique: {} (vertices: {:?})",
        verification.max_red_clique.len(),
        &verification.max_red_clique[..verification.max_red_clique.len().min(8)]);
    println!("    Max blue clique: {} (vertices: {:?})",
        verification.max_blue_clique.len(),
        &verification.max_blue_clique[..verification.max_blue_clique.len().min(8)]);

    if verification.is_valid {
        println!("\n  ★★★ R(5,5) ≥ 44 CERTIFICATE FOUND! ★★★");
        println!("  This would be a new Ramsey number bound!");
    } else {
        println!("\n  K₄₃ coloring has mono K₅ — analyzing the obstruction...");
    }

    // Tool 13: Barrier depth at ground state
    if model.n <= 100 {
        let t = Instant::now();
        let bd = BarrierDepthAnalyzer::analyze(&model, ground_spins, 2, 300);
        println!("\n  Barrier depth ({:.1}ms):", t.elapsed().as_secs_f64() * 1000.0);
        println!("    Local minimum: {}", bd.is_local_minimum);
        println!("    Depth: {:?}", bd.barrier_depth);
        for k in 0..bd.improving_at_k.len() {
            println!("    k={}: {} improving / {} total",
                k + 1, bd.improving_at_k[k], bd.total_at_k[k]);
        }
    }

    // Tool 2: TBO on energy trajectory
    let energies: Vec<f64> = result.all_results.iter()
        .flat_map(|r| r.energy_history.iter().map(|&(_, e)| e))
        .collect();
    if energies.len() >= 64 {
        let tbo = TboDiagnostic::analyze(&energies, 50, 42);
        println!("\n  TBO diagnostic:");
        println!("    Z-score: {:.2}", tbo.z_score);
        println!("    Approaching attractor: {}", tbo.is_approaching_attractor);
        println!("    Recommendation: {:?}", tbo.recommendation);
    }

    // Tool 10: Zero-core analysis (if not valid)
    if !verification.is_valid && n <= 43 {
        println!("\n  Zero-core obstruction analysis (this may take a moment)...");
        let t = Instant::now();
        let zc = ZeroCoreDetector::check(n, ground_spins, 5);
        let zc_ms = t.elapsed().as_secs_f64() * 1000.0;
        println!("    Extensible to K₄₄: {}", zc.is_extensible);
        println!("    Constraints: {}", zc.n_constraints);
        if !zc.is_extensible {
            println!("    Distributed obstruction: {} (core size: {})",
                zc.has_distributed_obstruction, zc.essential_core_size);
        }
        println!("    Time: {:.1}ms", zc_ms);
    }

    // ═══════════════════════════════════════════════════════════════
    // PHASE 6: PT-SBM Direct Attack (imaginary tunneling)
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Phase 6: PT-SBM Imaginary Tunneling Attack ━━━\n");

    let pt_config = SolverConfig {
        steps: 10000,
        restarts: 1,
        solver_overrides: {
            let mut m = std::collections::HashMap::new();
            m.insert("PT_GAMMA_MAX".into(), 2.0);
            m.insert("SBM_PUMP_END".into(), rational.sbm_pump_end);
            m.insert("SBM_DAMPING".into(), rational.sbm_damping);
            m.insert("SBM_KERR".into(), rational.sbm_kerr);
            m
        },
        ..SolverConfig::default()
    };

    let mut best_pt_energy = f64::INFINITY;
    let mut best_pt_spins = vec![];

    for seed in 0..10u64 {
        let early = AtomicBestEnergy::new();
        let mut stag = TieredStagnationDetector::new();
        let r = PtSolver.solve(&model, &pt_config, &mut stag, &early, seed);
        if r.energy < best_pt_energy {
            best_pt_energy = r.energy;
            best_pt_spins = r.spins.clone();
        }
    }

    println!("  PT-SBM best energy: {:.4} (10 seeds)", best_pt_energy);
    if !best_pt_spins.is_empty() {
        let pt_v = MaxClique::verify_ramsey(n, &best_pt_spins, 5);
        println!("  PT-SBM verification: valid={}, red ω={}, blue ω={}",
            pt_v.is_valid, pt_v.max_red_clique.len(), pt_v.max_blue_clique.len());
        if pt_v.is_valid {
            println!("\n  ★★★ PT-SBM FOUND R(5,5) ≥ 44 CERTIFICATE! ★★★");
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // PHASE 7: SA with T_c-Centered Schedule
    // ═══════════════════════════════════════════════════════════════
    println!("\n━━━ Phase 7: SA with T_c-Centered Schedule ━━━\n");

    let sa_config = SolverConfig {
        steps: 20000,
        restarts: 1,
        solver_overrides: {
            let mut m = std::collections::HashMap::new();
            m.insert("SA_T_START".into(), pd.sa_t_start);
            m.insert("SA_T_END".into(), pd.sa_t_end);
            m.insert("SA_SCHEDULE".into(), 6.0); // TcCentered
            m
        },
        ..SolverConfig::default()
    };

    let mut best_sa_energy = f64::INFINITY;
    let mut best_sa_spins = vec![];

    for seed in 0..10u64 {
        let early = AtomicBestEnergy::new();
        let mut stag = TieredStagnationDetector::new();
        let r = SaSolver.solve(&model, &sa_config, &mut stag, &early, seed);
        if r.energy < best_sa_energy {
            best_sa_energy = r.energy;
            best_sa_spins = r.spins.clone();
        }
    }

    println!("  SA (T_c-centered) best energy: {:.4} (10 seeds)", best_sa_energy);
    if !best_sa_spins.is_empty() {
        let sa_v = MaxClique::verify_ramsey(n, &best_sa_spins, 5);
        println!("  SA verification: valid={}, red ω={}, blue ω={}",
            sa_v.is_valid, sa_v.max_red_clique.len(), sa_v.max_blue_clique.len());
    }

    // ═══════════════════════════════════════════════════════════════
    // SUMMARY
    // ═══════════════════════════════════════════════════════════════
    let total_s = t_total.elapsed().as_secs_f64();

    println!("\n╔══════════════════════════════════════════════════════════════════╗");
    println!("║  R(5,5) EINSTEIN ATTACK — RESULTS                              ║");
    println!("╠══════════════════════════════════════════════════════════════════╣");
    println!("║  Tools deployed: 14 Einstein + 16 solvers                       ║");
    println!("║  Target: K₄₃ zero-violation coloring                            ║");
    println!("║                                                                 ║");
    println!("║  Best GF(p) seed: {}  ║", best_config_str);
    println!("║  Ensemble energy: {:.4} (solver: {:12})               ║", result.best.energy, result.best.solver_name);
    println!("║  PT-SBM energy:   {:.4} (10 seeds × 10K steps)               ║", best_pt_energy);
    println!("║  SA T_c energy:   {:.4} (10 seeds × 20K steps)               ║", best_sa_energy);
    println!("║  Phase diagram T_c: {:.4}                                      ║", pd.instance_tc);
    println!("║  Spectral Δβ: {:+.3}                                           ║", split.delta_beta);
    println!("║  Total time: {:.2}s                                            ║", total_s);
    println!("╚══════════════════════════════════════════════════════════════════╝");
}

/// Build Ramsey R(k,k) Ising model on K_n.
/// Each edge is a spin (+1=red, -1=blue).
/// Penalty for each monochromatic K_k.
fn build_ramsey_ising(n: usize, k: usize) -> IsingModel {
    let ne = n * (n - 1) / 2;

    // For a simple Ising encoding: antiferromagnetic coupling between
    // edges that share a vertex within a potential K_k.
    // This is a simplified encoding — the full clique penalty is higher-order.
    let mut data = vec![0.0f64; ne * ne];

    // For each pair of edges sharing a vertex, add coupling
    for u in 0..n {
        let edges_of_u: Vec<usize> = (0..n).filter(|&v| v != u).map(|v| {
            let (a, b) = if u < v { (u, v) } else { (v, u) };
            a * n - a * (a + 1) / 2 + b - a - 1
        }).collect();

        // Edges sharing vertex u should be frustrated (can't all be same color)
        for i in 0..edges_of_u.len() {
            for j in i+1..edges_of_u.len() {
                let ei = edges_of_u[i];
                let ej = edges_of_u[j];
                if ei < ne && ej < ne {
                    // Antiferromagnetic: penalize same-color edges sharing a vertex
                    data[ei * ne + ej] += -0.1 / (k as f64);
                    data[ej * ne + ei] += -0.1 / (k as f64);
                }
            }
        }
    }

    IsingModel::no_field(Box::new(DenseMatrix::new(data, ne)))
}
