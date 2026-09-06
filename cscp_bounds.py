"""Schranke für die Bin-Packing-Suche, Signatur `bound_fn(instance, pieces, depth,
bins)` - `bins` ist eine Liste der Restkapazitäten aller bereits geöffneten Bins.
Liefert eine gültige UNTERGRENZE für die insgesamt benötigte Bin-Anzahl, nie eine
Überschätzung. Identisch zu `csbb_bounds.weak_bound` in
cutting-stock-branch-bound-demo - die dortige `strong_bound` wird hier bewusst
nicht erneut eingeführt, ihre Wirkungslosigkeit ist dort bereits bewiesen und
getestet."""


def weak_bound(instance, pieces, depth, bins):
    """L1-Schranke: Restbreite aller noch offenen Stücke, die nicht mehr in die
    Restkapazität bereits geöffneter Bins passt, durch die Rollenbreite geteilt
    (aufgerundet)."""
    remaining_width = sum(pieces[depth:])
    remaining_capacity = sum(bins)
    if remaining_width <= remaining_capacity:
        return len(bins)
    extra = -(-(remaining_width - remaining_capacity) // instance.roll_width)
    return len(bins) + extra
