"""Validate solver decisions through reconstruction, an audit and the teacher scorer."""

from decimal import Decimal

from .audit import audit_baseline, require
from .s2_model import SCALE
from .s2_placement import reconstruct


def validate_solution(original_nodes, original_edges, solution, reference):
    """Cross-check a feasible assignment without trusting its reported objective."""
    require(solution["has_solution"], "No solution to validate")
    require(solution["status"] in ("FEASIBLE", "OPTIMAL"), "Solution has a non-feasible status")
    require(solution["optimality_proven_for_formulation"] == (solution["status"] == "OPTIMAL"),
            "Optimality flag disagrees with solver status")
    level = solution["l_init"]
    require(solution["l_max"] == 14, "Wrong maximum level")
    nodes, edges = reconstruct(original_nodes, original_edges, solution["edge_decisions"],
                               solution["original_output_levels"])
    independent = audit_baseline(original_nodes, original_edges, nodes, edges, level)
    for name, _, _, _ in original_nodes:
        require(independent["l_in"][name] == solution["original_input_levels"][name], "Model input level disagrees")
        require(independent["l_out"][name] == solution["original_output_levels"][name], "Model output level disagrees")
    exact = Decimal(independent["latency_decimal_ms"])
    require(exact * SCALE == solution["objective_scaled"], "Model objective disagrees with independent cost")
    require(exact == Decimal(solution["objective_decimal_ms"]), "Decimal objective disagrees")
    scored = reference.evaluate_dag(nodes, edges, level, 14)
    require(scored is not None, "Reference rejects reconstructed graph")
    error = abs(Decimal(str(scored["latency"])) - exact)
    require(error <= Decimal("0.0000001"), "Teacher and independent costs disagree")
    require(scored["l_in"] == independent["l_in"] and scored["l_out"] == independent["l_out"],
            "Teacher and independent node levels disagree")
    teacher_edges = {(e["from"], e["to"]): e["level"] for e in independent["edge_levels"]}
    require(scored["edge_lvl"] == teacher_edges, "Teacher and independent edge levels disagree")
    require(reference.depth_of(nodes, edges) == independent["depth"], "Depth disagrees")
    require(tuple(reference.budget_of(nodes, edges, level, 14)) ==
            (independent["n_b1"], independent["n_b2"], independent["budget"]), "Counts or budget disagree")
    actual_shared = {(n, mode) for n, _, _ in original_edges for mode in (1, 2)
                     if any(d["from"] == n and d["refresh"] == mode for d in solution["edge_decisions"])}
    claimed_shared = {(d["after"], d["type"]) for d in solution["shared_refreshes"]}
    require(actual_shared == claimed_shared, "Shared activation disagrees")
    require(solution["best_bound_scaled"] <= solution["objective_scaled"] + 1e-5, "Bound exceeds objective")
    gap = max(0.0, (solution["objective_scaled"] - solution["best_bound_scaled"]) /
              max(1, abs(solution["objective_scaled"])))
    require(abs(gap - solution["relative_gap"]) < 1e-12, "Reported gap disagrees with bound")
    if solution["optimality_proven_for_formulation"]:
        require(solution["status"] == "OPTIMAL", "Optimality claim has wrong status")
        require(abs(solution["best_bound_scaled"] - solution["objective_scaled"]) < 1e-5,
                "Optimal status has a nonzero bound gap")
    return {
        "nodes": nodes, "edges": edges, "audit": independent,
        "reference_latency_ms": scored["latency"],
        "reference_decimal_absolute_error_ms": str(error),
        "checks": {"original_graph_and_ciphertexts": True, "canonical_chains_and_sharing": True,
                   "level_domains_and_merges": True, "bootstrap_eligibility_and_counts": True,
                   "model_reconstruction_audit_agreement": True, "reference_score_and_metrics_agreement": True},
    }
