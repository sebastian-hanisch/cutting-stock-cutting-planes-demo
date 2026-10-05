"""Unabhängiges Orakel: Teilmengen-DP (minimale Behälterzahl über alle Stückmengen-Reihenfolgen)
statt Tiefensuche - prüft den Solver mit und ohne Symmetrie-Schnitt sowie die Gültigkeit der
Schranke an zufälligen Teilzuständen."""

import random

from cscp_bounds import weak_bound
from cscp_scenario import CuttingStockInstance, expand_pieces
from cscp_solver import solve


def _subset_dp(pieces, width):
    n = len(pieces)
    inf = 10 ** 9
    dp = [(inf, 0)] * (1 << n)  # (Bins, Füllstand des letzten Bins), lexikographisch minimal
    dp[0] = (1, 0)
    for mask in range(1 << n):
        bins, fill = dp[mask]
        if bins == inf:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            cand = (bins, fill + pieces[i]) if fill + pieces[i] <= width else (bins + 1, pieces[i])
            if cand < dp[mask | 1 << i]:
                dp[mask | 1 << i] = cand
    return dp[(1 << n) - 1][0]


def _min_total_bins(rest, bins, width):
    best = [10 ** 9]

    def rec(i, bs):
        if len(bs) >= best[0]:
            return
        if i == len(rest):
            best[0] = len(bs)
            return
        for k, cap in enumerate(bs):
            if cap >= rest[i]:
                bs[k] -= rest[i]
                rec(i + 1, bs)
                bs[k] += rest[i]
        bs.append(width - rest[i])
        rec(i + 1, bs)
        bs.pop()

    rec(0, list(bins))
    return best[0]


def _random_instance(rng):
    width = rng.choice([10, 20, 50, 100])
    n_types = rng.randint(1, 4)
    widths = tuple(rng.choice([1, width // 4, width // 3, width // 2, width - 1, width, rng.randint(1, width)])
                   for _ in range(n_types))
    demands = tuple(rng.randint(1, 3) for _ in range(n_types))
    return CuttingStockInstance(width, widths, demands)


def test_solver_matches_subset_dp_with_and_without_cut():
    rng = random.Random(11)
    checked = 0
    while checked < 60:
        inst = _random_instance(rng)
        pieces = expand_pieces(inst)
        if len(pieces) > 9:
            continue
        checked += 1
        opt = _subset_dp(list(pieces), inst.roll_width)
        for cut in (True, False):
            res = solve(inst, weak_bound, use_symmetry_cut=cut)
            assert res.best_value == opt, (inst, cut)
            assert len(res.best_bins) == opt
            assert sum(inst.roll_width - c for c in res.best_bins) == sum(pieces)


def test_weak_bound_never_exceeds_true_completion_optimum():
    rng = random.Random(5)
    checked = 0
    while checked < 40:
        inst = _random_instance(rng)
        pieces = expand_pieces(inst)
        if len(pieces) < 2 or len(pieces) > 8:
            continue
        checked += 1
        d = rng.randint(0, len(pieces) - 1)
        bins = []
        for p in pieces[:d]:
            fits = [k for k, c in enumerate(bins) if c >= p]
            if fits and rng.random() < 0.7:
                bins[rng.choice(fits)] -= p
            else:
                bins.append(inst.roll_width - p)
        assert weak_bound(inst, pieces, d, bins) <= _min_total_bins(pieces[d:], bins, inst.roll_width)
