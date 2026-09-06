"""Erschöpfende Referenzlösung für Bin Packing - unabhängig von der Branch-&-Bound-
Suche, nur für kleine Instanzen praktikabel. Öffnet an jedem Schritt höchstens EIN
neues Bin (statt symmetrisch mehrere identische leere Bins durchzuprobieren) - das
hält die Enumeration bei kleinem n handhabbar, ohne die Korrektheit zu
beeinträchtigen. Identisch zu csbb_bruteforce.py in cutting-stock-branch-bound-demo."""

from cscp_scenario import expand_pieces


def solve_bruteforce(instance):
    pieces = expand_pieces(instance)
    n = len(pieces)
    best = {"count": n}  # triviale obere Schranke: ein Bin pro Stück

    def assign(idx, bins):
        if len(bins) >= best["count"]:
            return
        if idx == n:
            best["count"] = min(best["count"], len(bins))
            return
        piece = pieces[idx]
        for i, cap in enumerate(bins):
            if cap >= piece:
                bins[i] -= piece
                assign(idx + 1, bins)
                bins[i] += piece
        bins.append(instance.roll_width - piece)
        assign(idx + 1, bins)
        bins.pop()

    assign(0, [])
    return best["count"]
