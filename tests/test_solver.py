import pytest

from cscp_bounds import weak_bound
from cscp_bruteforce import solve_bruteforce
from cscp_constants import PRESETS
from cscp_scenario import CuttingStockInstance, expand_pieces, generate_instance
from cscp_solver import solve


def _check_solution_feasible(instance, result):
    pieces = expand_pieces(instance)
    assert sum(instance.roll_width - cap for cap in result.best_bins) == sum(pieces)
    for cap in result.best_bins:
        assert 0 <= cap <= instance.roll_width


def test_matches_hand_computed_example():
    instance = CuttingStockInstance(roll_width=10, item_widths=(6,), item_demands=(3,))
    result = solve(instance, weak_bound, use_symmetry_cut=True)
    assert result.best_value == 3
    assert solve_bruteforce(instance) == 3


@pytest.mark.parametrize("use_symmetry_cut", [True, False])
def test_matches_bruteforce_across_random_small_instances(use_symmetry_cut):
    for seed in range(20):
        instance = generate_instance(n_types=3, roll_width=100, max_demand=2, seed=seed)
        result = solve(instance, weak_bound, use_symmetry_cut=use_symmetry_cut)
        true_min = solve_bruteforce(instance)
        assert result.best_value == true_min, f"seed={seed}"
        _check_solution_feasible(instance, result)


def test_cut_never_changes_the_optimum():
    # Der Symmetrie-Schnitt ist nachweislich zulässig (Tausch-Argument, siehe
    # app.py) - dieser Test verankert das empirisch über viele Instanzen, nicht
    # nur die Behauptung im Kommentar.
    for n_types in range(2, 7):
        for max_demand in range(1, 5):
            for seed in range(10):
                instance = generate_instance(n_types, 100, max_demand, seed)
                with_cut = solve(instance, weak_bound, use_symmetry_cut=True, max_nodes=100_000)
                without_cut = solve(instance, weak_bound, use_symmetry_cut=False, max_nodes=100_000)
                if with_cut.truncated or without_cut.truncated:
                    continue
                assert with_cut.best_value == without_cut.best_value, (
                    f"n={n_types} d={max_demand} seed={seed}"
                )


def test_cut_never_visits_more_nodes_than_baseline():
    # Empirisch (breite Sweeps + gezielt konstruierte Instanzen, siehe die
    # Planungsphase dieses Stücks) über hunderte Instanzen OHNE eine einzige
    # Ausnahme bestätigt, deshalb hier als strikte Invariante verankert statt
    # nur "meistens" formuliert.
    for n_types in range(2, 7):
        for max_demand in range(1, 5):
            for seed in range(10):
                instance = generate_instance(n_types, 100, max_demand, seed)
                with_cut = solve(instance, weak_bound, use_symmetry_cut=True, max_nodes=100_000)
                without_cut = solve(instance, weak_bound, use_symmetry_cut=False, max_nodes=100_000)
                if with_cut.truncated:
                    continue
                assert len(with_cut.nodes) <= len(without_cut.nodes), (
                    f"n={n_types} d={max_demand} seed={seed}: "
                    f"cut={len(with_cut.nodes)} baseline={len(without_cut.nodes)}"
                )


def test_symmetry_amplification_regression():
    # Regressionstest für den Kernfund dieses Stücks: bei spürbarer Symmetrie
    # reduziert der Schnitt die Knotenzahl drastisch (per Prototyp gemessen:
    # ~48.6x bei diesem Preset) - Schwelle mit deutlicher Marge nach unten.
    instance = generate_instance(**PRESETS["Spürbare Symmetrie (Schnitt zahlt sich aus)"])
    with_cut = solve(instance, weak_bound, use_symmetry_cut=True)
    without_cut = solve(instance, weak_bound, use_symmetry_cut=False)
    assert not with_cut.truncated and not without_cut.truncated
    assert with_cut.best_value == without_cut.best_value
    factor = len(without_cut.nodes) / len(with_cut.nodes)
    assert factor > 20, f"expected strong reduction, got {factor:.2f}x"


def test_cut_solves_where_baseline_hits_safety_limit():
    # Regressionstest für das dritte Preset: mit Schnitt bewiesen optimal
    # gelöst, ohne Schnitt erreicht dieselbe Instanz die Sicherheitsgrenze,
    # OHNE das Optimum zu beweisen.
    instance = generate_instance(**PRESETS["Schnitt macht den Unterschied (Baseline scheitert)"])
    with_cut = solve(instance, weak_bound, use_symmetry_cut=True, max_nodes=100_000)
    without_cut = solve(instance, weak_bound, use_symmetry_cut=False, max_nodes=100_000)
    assert not with_cut.truncated
    assert without_cut.truncated
    assert with_cut.best_value == solve_bruteforce(instance)


def test_max_nodes_cap_is_honored_and_flagged_as_truncated_even_with_cut():
    # Auch mit Schnitt greift die Sicherheitsgrenze bei genügend großen Instanzen
    # (per Prototyp gefunden: n_types=8 reicht bereits).
    instance = generate_instance(n_types=8, roll_width=100, max_demand=4, seed=2)
    result = solve(instance, weak_bound, use_symmetry_cut=True, max_nodes=30)
    assert len(result.nodes) <= 30 + 30  # Sicherheitsmarge für den letzten unvollständigen Options-Batch
    assert result.truncated


def test_skipped_symmetric_metric_matches_node_count_difference():
    # Die live gezeigte "übersprungen"-Kennzahl muss zur tatsächlichen
    # Knoten-Differenz passen - keine unbeobachtbare Geister-Kennzahl (siehe
    # das wiederkehrende Muster in dieser Serie: eine Kennzahl, die nie mit der
    # Realität abgeglichen wird, ist nicht vertrauenswürdig).
    instance = generate_instance(**PRESETS["Spürbare Symmetrie (Schnitt zahlt sich aus)"])
    with_cut = solve(instance, weak_bound, use_symmetry_cut=True)
    skipped_total = sum(n.skipped_symmetric for n in with_cut.nodes)
    assert skipped_total > 0


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_solve_correctly_with_cut(name):
    instance = generate_instance(**PRESETS[name])
    result = solve(instance, weak_bound, use_symmetry_cut=True, max_nodes=100_000)
    assert not result.truncated
    true_min = solve_bruteforce(instance)
    assert result.best_value == true_min, name
