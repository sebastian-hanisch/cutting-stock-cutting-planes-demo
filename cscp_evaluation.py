"""Kennzahlen aus einem Suchlauf, plus der Kern-Vergleich dieses Stücks: derselbe
Suchlauf auf DERSELBEN Instanz, einmal ohne, einmal mit aktivem Symmetrie-Schnitt -
anders als cutting-stock-branch-bound-demo's `symmetry_comparison` (die eine
künstlich entsymmetrisierte ZWILLINGS-Instanz zum Vergleich löst), zeigt dieser
Vergleich den echten algorithmischen Effekt auf ein und derselben Instanz."""

from collections import Counter

from cscp_constants import MAX_NODES_EXPLORED
from cscp_solver import solve


def compute_stats(result):
    counts = Counter(node.status for node in result.nodes)
    return {
        "nodes_explored": len(result.nodes),
        "pruned_bound": counts["prune_bound"],
        "leaves_evaluated": counts["leaf_new_best"] + counts["leaf_not_best"],
        "skipped_symmetric_total": sum(n.skipped_symmetric for n in result.nodes),
        "best_value": result.best_value,
        "truncated": result.truncated,
    }


def stats_up_to_step(result, step):
    relevant = [node for node in result.nodes if node.id <= step]
    counts = Counter(node.status for node in relevant)
    current_best = None
    for nid, v in result.incumbent_history:
        if nid <= step:
            current_best = v
    return {
        "nodes_so_far": counts.total(),
        "pruned_bound": counts["prune_bound"],
        "skipped_symmetric_so_far": sum(n.skipped_symmetric for n in relevant),
        "current_best": current_best,
    }


def symmetry_cut_comparison(instance, bound_fn, max_nodes=MAX_NODES_EXPLORED):
    baseline_result = solve(instance, bound_fn, use_symmetry_cut=False, max_nodes=max_nodes)
    cut_result = solve(instance, bound_fn, use_symmetry_cut=True, max_nodes=max_nodes)
    return {
        "baseline_nodes": len(baseline_result.nodes),
        "baseline_best": baseline_result.best_value,
        "baseline_truncated": baseline_result.truncated,
        "cut_nodes": len(cut_result.nodes),
        "cut_best": cut_result.best_value,
        "cut_truncated": cut_result.truncated,
        "skipped_total": sum(n.skipped_symmetric for n in cut_result.nodes),
    }
