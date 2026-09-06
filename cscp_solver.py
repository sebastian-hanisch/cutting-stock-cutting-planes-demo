"""Tiefensuche für Bin Packing wie in cutting-stock-branch-bound-demo, erweitert
um einen echten Symmetrie-/Dominanz-Schnitt: haben mehrere bereits offene Bins
EXAKT dieselbe Restkapazität, sind sie für alle künftigen Entscheidungen
ununterscheidbar - das nächste Stück dort statt hier zu platzieren erzeugt einen
isomorphen Teilbaum. Statt (wie in cutting-stock-branch-bound-demo, bewusst) einen
Kindknoten PRO offenem passendem Bin zu erzeugen, erzeugt dieser Schnitt nur einen
Kindknoten pro DISTINKTER Restkapazität - ein Repräsentant deckt die ganze
Äquivalenzklasse ab. Beweis der Zulässigkeit (Tausch-Argument): siehe
app.py's Formulierungs-Abschnitt.

`use_symmetry_cut=False` reproduziert exakt das Verhalten von
`csbb_solver.solve` - die Baseline für den Vergleich in cscp_evaluation.py."""

from dataclasses import dataclass

from cscp_constants import MAX_NODES_EXPLORED
from cscp_scenario import expand_pieces


@dataclass(frozen=True)
class Node:
    id: int
    parent_id: int
    depth: int  # Anzahl bislang platzierter Stücke
    piece_width: int  # das gerade platzierte Stück, None für die Wurzel
    target: object  # ("existing", bin_index) oder ("new", bin_index), None für die Wurzel
    bins_open: int  # Anzahl offener Bins NACH dieser Entscheidung
    bound: object  # Schranke an diesem Knoten, None an Blättern
    status: str  # root | branch | prune_bound | leaf_new_best | leaf_not_best
    skipped_symmetric: int  # wie viele weitere, gleich-große Bins dieser Knoten mit abdeckt


@dataclass(frozen=True)
class SolveResult:
    best_value: int
    best_bins: tuple  # Restkapazitäten der Bins der besten gefundenen Lösung
    nodes: tuple
    incumbent_history: tuple
    truncated: bool
    pieces: tuple


def solve(instance, bound_fn, use_symmetry_cut=True, max_nodes=MAX_NODES_EXPLORED):
    pieces = expand_pieces(instance)
    n = len(pieces)
    nodes = []
    incumbent_history = []
    best = {"count": None, "bins": None}
    truncated = {"flag": False}
    next_id = [0]

    def new_node(parent_id, depth, piece_width, target, bins_open, bound, status, skipped_symmetric=0):
        node = Node(next_id[0], parent_id, depth, piece_width, target, bins_open, bound, status, skipped_symmetric)
        next_id[0] += 1
        nodes.append(node)
        return node

    root_bound = bound_fn(instance, pieces, 0, [])
    root = new_node(None, 0, None, None, 0, root_bound, "root")

    def branch_options(bins, piece):
        """Eine Option pro Kind: (target, new_bins, skipped_symmetric). Mit
        aktivem Schnitt trägt genau EIN Repräsentant pro Gruppe gleich großer
        Bins die Anzahl der dabei übersprungenen Geschwister."""
        options = []
        rep_index_of_capacity = {}
        for i, cap in enumerate(bins):
            if cap < piece:
                continue
            if use_symmetry_cut and cap in rep_index_of_capacity:
                rep_idx = rep_index_of_capacity[cap]
                options[rep_idx] = (
                    options[rep_idx][0], options[rep_idx][1], options[rep_idx][2] + 1,
                )
                continue
            new_bins = list(bins)
            new_bins[i] -= piece
            if use_symmetry_cut:
                rep_index_of_capacity[cap] = len(options)
            options.append((("existing", i), new_bins, 0))
        options.append((("new", len(bins)), list(bins) + [instance.roll_width - piece], 0))
        return options

    def explore(node, depth, bins):
        piece = pieces[depth]
        options = branch_options(bins, piece)

        for target, new_bins, skipped_symmetric in options:
            if truncated["flag"] or len(nodes) >= max_nodes:
                truncated["flag"] = True
                return

            new_depth = depth + 1
            bins_open = len(new_bins)

            if new_depth == n:
                is_new_best = best["count"] is None or bins_open < best["count"]
                status = "leaf_new_best" if is_new_best else "leaf_not_best"
                child = new_node(node.id, new_depth, piece, target, bins_open, None, status, skipped_symmetric)
                if is_new_best:
                    best["count"] = bins_open
                    best["bins"] = tuple(new_bins)
                    incumbent_history.append((child.id, bins_open))
                continue

            bound = bound_fn(instance, pieces, new_depth, new_bins)
            if best["count"] is not None and bound >= best["count"]:
                new_node(node.id, new_depth, piece, target, bins_open, bound, "prune_bound", skipped_symmetric)
                continue

            child = new_node(node.id, new_depth, piece, target, bins_open, bound, "branch", skipped_symmetric)
            explore(child, new_depth, new_bins)

    explore(root, 0, [])

    return SolveResult(
        best_value=best["count"],
        best_bins=best["bins"],
        nodes=tuple(nodes),
        incumbent_history=tuple(incumbent_history),
        truncated=truncated["flag"],
        pieces=pieces,
    )
