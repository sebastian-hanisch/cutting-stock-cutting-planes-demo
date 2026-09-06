"""Defaults, slider bounds und Presets für die Cutting-Stock-Symmetrie-Schnitt-Demo."""

DEFAULT_N_TYPES = 4
DEFAULT_MAX_DEMAND = 2
DEFAULT_ROLL_WIDTH = 100
DEFAULT_SEED = 7

N_TYPES_MIN, N_TYPES_MAX = 2, 7
MAX_DEMAND_MIN, MAX_DEMAND_MAX = 1, 4
ROLL_WIDTH_MIN, ROLL_WIDTH_MAX = 50, 200

# Auftragsbreiten werden als Anteil der Rollenbreite gezogen - hält die Instanzen
# unabhängig von der absoluten Rollenbreite vergleichbar (wie in
# cutting-stock-branch-bound-demo).
WIDTH_FRACTION_RANGE = (0.15, 0.6)

# Per Prototyp kalibriert (breite Zufalls-Sweeps + gezielte Suche nach starken
# Fällen): der Baseline-Suchbaum (ohne Schnitt) kann schon bei n_types=7-8
# hunderttausende Knoten erreichen, während derselbe Suchlauf MIT Schnitt fast
# immer im dreistelligen bis niedrigen vierstelligen Bereich bleibt. 100.000 deckt
# jedes Preset mit dem Schnitt komfortabel ab und lässt das "Größere Instanz"-Preset
# bewusst die Baseline daran scheitern.
MAX_NODES_EXPLORED = 100_000
MAX_NODES_RENDERED = 800

PRESETS = {
    "Winzige Instanz (Baum komplett sichtbar)": {
        "n_types": 3, "roll_width": 100, "max_demand": 2, "seed": 9,
    },
    "Spürbare Symmetrie (Schnitt zahlt sich aus)": {
        "n_types": 5, "roll_width": 100, "max_demand": 4, "seed": 3,
    },
    "Schnitt macht den Unterschied (Baseline scheitert)": {
        "n_types": 7, "roll_width": 100, "max_demand": 4, "seed": 5,
    },
}
