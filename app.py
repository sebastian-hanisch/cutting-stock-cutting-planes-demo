"""
Symmetrie-Schnitte am Cutting-Stock-Problem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Drittes Stück der Cutting-Stock-Linie: ein unabhängiger Zweig von
cutting-stock-branch-bound-demo (parallel zu cutting-stock-dp-demo), der einen
echten, algorithmischen Symmetrie-Schnitt in die Bin-Packing-Suche einbaut - eine
Vorbereitung für cutting-stock-branch-cut-demo, das diesen Schnitt später mit
echter Verzweigung an jedem Knoten kombiniert.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import cscp_constants as C
from cscp_bounds import weak_bound
from cscp_bruteforce import solve_bruteforce
from cscp_evaluation import stats_up_to_step, symmetry_cut_comparison
from cscp_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from cscp_scenario import expand_pieces, generate_instance
from cscp_solver import solve
from cscp_visualization import build_comparison_chart, build_tree_figure

st.set_page_config(page_title="Symmetrie-Schnitte am Cutting-Stock-Problem – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    result = solve(instance, weak_bound, use_symmetry_cut=True)
    true_optimum = solve_bruteforce(instance)
    return instance, result, true_optimum


@st.cache_data(show_spinner=False)
def _compute_comparison(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    return symmetry_cut_comparison(instance, weak_bound)


st.title("✂️📦 Symmetrie-Schnitte am Cutting-Stock-Problem")
st.markdown(
    """
Drittes Stück der Cutting-Stock-Linie - ein unabhängiger Zweig von
[cutting-stock-branch-bound-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-bound-demo),
parallel zu
[cutting-stock-dp-demo](https://github.com/sebastian-hanisch/cutting-stock-dp-demo).
Dort blieb Bin Packings berüchtigte Schwäche - austauschbare (symmetrische) Bins
blähen den Suchbaum unnötig auf - bewusst UNANGETASTET, nur diagnostisch
gemessen (Vergleich mit einer künstlich entsymmetrisierten Zwillingsinstanz).
Dieses Stück behebt es tatsächlich: ein echter, algorithmischer **Symmetrie-
Schnitt**, der redundante Äste erst gar nicht erzeugt - auf DERSELBEN Instanz,
ohne sie zu verändern.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie jedes Stück dieser Linie - ein Verfahren an einem "
    "wachsenden Beispiel."
)

with st.expander("So funktioniert der Schnitt", expanded=True):
    st.markdown(
        r"""
Wie in `cutting-stock-branch-bound-demo` verzweigt die Suche an jedem Knoten
n-är: das nächste Stück geht in eines der bereits offenen Bins, in das es noch
passt, oder ein neues Bin wird geöffnet. **Haben zwei offene Bins exakt dieselbe
Restkapazität**, sind sie für alle künftigen Entscheidungen ununterscheidbar -
das Stück dort statt hier zu platzieren führt zu einem isomorphen Teilbaum,
reiner Mehraufwand ohne neuen Erkenntnisgewinn.

Der Schnitt: pro Gruppe gleich großer offener Bins wird nur EIN Repräsentant zu
einer Kindoption, alle anderen werden übersprungen - im Baum unten sichtbar
markiert (violett umrandet, "×N baugleiche Bin(s) übersprungen"). Das ändert nie
das gefundene Optimum: eine Lösung, die Bin *j* statt des Repräsentanten *i*
verwendet, lässt sich durch Vertauschen von *i* und *j* in eine gleich gute
Lösung umwandeln, die den Repräsentanten nutzt - siehe den Beweis im
Formulierungs-Abschnitt weiter unten.

Anders als bei [cutting-planes-demo](https://github.com/sebastian-hanisch/cutting-planes-demo)
aus der ersten (Rucksack-)Linie wirkt dieser Schnitt NICHT auf eine LP-Schranke:
Bin Packings kompakte Formulierung hat zwar eine LP-Relaxation, aber
Symmetrie-Constraints schneiden dort nur symmetrische GANZZAHLIGE Lösungen weg,
nicht den fraktionalen Wert selbst - eine LP-Schranken-Verbesserung wäre hier
keine ehrliche Demonstration. Die wirklich starke, Muster-basierte LP-Relaxation
kommt erst mit Column Generation später in dieser Linie. Dieser Schnitt wirkt
deshalb direkt auf den kombinatorischen Suchraum.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winzige Instanz (Baum komplett sichtbar)": "3 Auftragstypen - der komplette Suchbaum passt aufs Bild, mit mindestens einem sichtbaren Schnitt.",
    "Spürbare Symmetrie (Schnitt zahlt sich aus)": "Mehrere Aufträge derselben Breite - der Schnitt reduziert die Knotenzahl auf dieser Instanz um mehr als das 40-fache.",
    "Schnitt macht den Unterschied (Baseline scheitert)": "Ohne Schnitt erreicht die Suche die Sicherheitsgrenze, OHNE das Optimum zu beweisen - mit Schnitt ist dieselbe Instanz in Sekundenbruchteilen gelöst.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_types = st.slider("Anzahl Auftragstypen", *bounds("n_types_slider"), key="n_types_slider")
    roll_width = st.slider("Rollenbreite", *bounds("roll_width_slider"), key="roll_width_slider")
    max_demand = st.slider(
        "Maximaler Bedarf je Auftragstyp", *bounds("max_demand_slider"), key="max_demand_slider",
        help="Höherer Bedarf bedeutet mehr identische Stücke - mehr Symmetrie, mehr Gelegenheit für den Schnitt.",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        width="stretch",
        on_click=randomize_seed,
        help="Würfelt neue Auftragsbreiten und -mengen.",
    )

sync_query_params(n_types, roll_width, max_demand, seed)

scenario_key = (int(n_types), int(roll_width), int(max_demand), int(seed))

with st.spinner("Durchsuche den Baum..."):
    instance, result, true_optimum = _compute_solve(*scenario_key)

pieces = expand_pieces(instance)
st.caption(
    f"🔗 {instance.n_types} Auftragstypen, Breiten {instance.item_widths} mit Bedarf "
    f"{instance.item_demands} → {len(pieces)} Einzelstücke, Rollenbreite {instance.roll_width}."
)

st.markdown("## 🎯 Der Suchbaum MIT Symmetrie-Schnitt")

if "cscp_step" not in st.session_state or st.session_state.get("cscp_step_owner") != scenario_key:
    st.session_state["cscp_step"] = len(result.nodes) - 1
    st.session_state["cscp_step_owner"] = scenario_key

max_step = len(result.nodes) - 1
step_col, play_col = st.columns([5, 1])
with step_col:
    if max_step == 0:
        step = 0
        st.caption("Nur der Wurzelknoten - kein Regler nötig.")
    else:
        step = st.slider(
            "Schritt (Knoten)", 0, max_step, key="cscp_step",
            help="Ein Schritt = ein besuchter Suchbaum-Knoten, in Besuchsreihenfolge.",
        )
with play_col:
    auto_play = st.button("▶️ Abspielen", width="stretch")

render_note = (
    f" (zeigt die ersten {C.MAX_NODES_RENDERED:,} von {len(result.nodes):,} Knoten)"
    if len(result.nodes) > C.MAX_NODES_RENDERED
    else ""
)
st.caption(f"{len(result.nodes):,} Knoten insgesamt besucht{render_note}.")

tree_slot = st.empty()


def _render(current_step):
    tree_slot.plotly_chart(
        build_tree_figure(result, current_step, C.MAX_NODES_RENDERED),
        width="stretch", key=f"tree_{current_step}",
    )


if auto_play:
    n_frames = min(max_step + 1, 60)
    frame_skip = max(1, (max_step + 1) // n_frames)
    for s in list(range(0, max_step, frame_skip)) + [max_step]:
        _render(s)
        time.sleep(0.08)
    step = max_step
else:
    _render(step)

live = stats_up_to_step(result, step)
lm1, lm2, lm3, lm4 = st.columns(4)
lm1.metric("Besuchte Knoten (bisher)", f"{live['nodes_so_far']:,}")
lm2.metric(
    "Gestutzt (Bound)", f"{live['pruned_bound']:,}",
    help="Äste, die abgebrochen wurden, weil die Schranke keine Verbesserung mehr versprach.",
)
lm3.metric(
    "Durch Symmetrie übersprungen (bisher)", f"{live['skipped_symmetric_so_far']:,}",
    help="Baugleiche Bins, die der Symmetrie-Schnitt gar nicht erst als eigene Kindoption erzeugt hat.",
)
lm4.metric(
    "Bester Fund bisher", live["current_best"] if live["current_best"] is not None else "–",
    help="Die wenigsten Rollen einer bislang vollständig gefundenen Lösung.",
)

if result.truncated:
    st.error(
        f"⛔ Abgebrochen bei {C.MAX_NODES_EXPLORED:,} untersuchten Knoten - das gezeigte Ergebnis ist die "
        f"beste bislang gefundene, nicht garantiert optimale Lösung."
    )
else:
    st.caption(
        f"Bewiesenes Optimum: **{result.best_value}** Rollen - stimmt mit der unabhängigen "
        f"Bruteforce-Referenz überein."
        if result.best_value == true_optimum
        else f"⚠️ Optimum {result.best_value} weicht von der Bruteforce-Referenz {true_optimum} ab - bitte melden."
    )

st.markdown("---")

st.subheader("📐 Wie viele Knoten schneidet der Symmetrie-Schnitt wirklich ab?")
st.markdown(
    """
Live für Ihre aktuelle Instanz: derselbe Suchlauf, einmal ohne, einmal mit
aktivem Symmetrie-Schnitt - auf EXAKT derselben Instanz, kein künstlicher
Vergleichszwilling.
"""
)

cmp = _compute_comparison(*scenario_key)
st.plotly_chart(build_comparison_chart(cmp), width="stretch", key="comparison_chart")

cc1, cc2, cc3 = st.columns(3)
cc1.metric(
    "Ohne Schnitt", f"{cmp['baseline_nodes']:,} Knoten" + (" (abgebrochen)" if cmp["baseline_truncated"] else ""),
)
cc2.metric(
    "Mit Schnitt", f"{cmp['cut_nodes']:,} Knoten" + (" (abgebrochen)" if cmp["cut_truncated"] else ""),
    delta=f"{cmp['cut_nodes'] - cmp['baseline_nodes']:,} ggü. ohne Schnitt", delta_color="inverse",
)
cc3.metric("Insgesamt übersprungen", f"{cmp['skipped_total']:,}")

if cmp["baseline_truncated"] and not cmp["cut_truncated"]:
    st.success(
        f"✅ Ohne Schnitt erreicht die Suche die Sicherheitsgrenze von {C.MAX_NODES_EXPLORED:,} Knoten, "
        f"OHNE das Optimum zu beweisen. Mit Schnitt ist dieselbe Instanz mit **{cmp['cut_nodes']:,}** Knoten "
        f"vollständig gelöst - der Unterschied zwischen praktisch unlösbar und Sekundenbruchteilen."
    )
elif cmp["baseline_best"] != cmp["cut_best"] and not (cmp["baseline_truncated"] or cmp["cut_truncated"]):
    st.warning("⚠️ Die beiden Varianten sind sich uneinig - das sollte nie passieren, bitte melden.")
elif cmp["cut_nodes"] and cmp["baseline_nodes"] / cmp["cut_nodes"] >= 1.5:
    factor = cmp["baseline_nodes"] / cmp["cut_nodes"]
    st.success(
        f"✅ Bei dieser Instanz durchsucht die Baseline **{factor:.1f}×** so viele Knoten wie die Version "
        f"mit Symmetrie-Schnitt - für dasselbe bewiesene Optimum. Der Unterschied ist reine Verschwendung: "
        f"rein austauschbare Bins, kein zusätzlicher Erkenntnisgewinn."
    )
else:
    st.info(
        "Bei dieser Instanz macht sich Symmetrie kaum bemerkbar - probieren Sie das Preset "
        "\"Spürbare Symmetrie\" oder mehrere Aufträge derselben Breite."
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Der Schnitt**: an jedem Suchbaum-Knoten werden die offenen Bins nach
Restkapazität gruppiert. Pro Gruppe mit identischer Restkapazität wird nur EIN
Repräsentant (das mit dem kleinsten Index) zu einer Kindoption; die übrigen
Bins dieser Gruppe werden nicht als eigener Ast erzeugt.

**Zulässigkeitsbeweis (Tausch-Argument)**: sei $B$ eine optimale Lösung, in
der Stück $p$ in Bin $j$ gelegt wird, während zum selben Zeitpunkt ein anderes
Bin $i$ mit identischer Restkapazität existiert ($i$ der Repräsentant, $i \neq
j$). Da $i$ und $j$ zu diesem Zeitpunkt exakt dieselbe Restkapazität haben,
ist das Vertauschen der Rollen von $i$ und $j$ in allen folgenden Schritten
von $B$ ebenfalls zulässig und liefert dieselbe Anzahl benötigter Bins. Jede
über $j$ erreichbare Lösung ist also auch über den Repräsentanten $i$
erreichbar - kein Optimum geht verloren, nur redundante, isomorphe Teilbäume
werden nie erst erzeugt.

**Warum keine LP-Schranken-Schnitte wie in cutting-planes-demo (erste
Linie)**: Bin Packings kompakte Formulierung (Kantorovich-Modell) hat zwar
eine LP-Relaxation, aber Symmetrie-Constraints (z. B. $y_k \geq y_{k+1}$,
Bins in kanonischer Reihenfolge) schneiden nur symmetrische GANZZAHLIGE
Lösungen weg - der fraktionale LP-Optimalwert selbst bleibt unverändert
(eine symmetrische fraktionale Lösung erfüllt solche Constraints oft
trivial). Eine LP-Schranken-Demonstration wäre hier also keine ehrliche
Illustration von "Schnitte verbessern die Schranke", wie es
cutting-planes-demo für Rucksack zeigt. Die wirklich starke, Muster-basierte
LP-Relaxation (Gilmore-Gomory) ist bewusst für Column Generation später in
dieser Linie reserviert. Dieser Schnitt wirkt deshalb direkt auf den
kombinatorischen Suchraum - eine andere, ebenso legitime Familie von
"Cutting Planes" im weiteren Sinne: gültige Restriktionen, die nachweislich
nie das Optimum verlieren.

**Vorgeschmack auf `cutting-stock-branch-cut-demo`**: dieser Schnitt wirkt
bereits an JEDEM Verzweigungsknoten, nicht nur einmalig an der Wurzel -
genau die Form, die das nächste (konvergierende) Stück dieser Linie braucht,
im Gegensatz zur ersten Linie, wo Schnitte nur am Wurzelknoten gefunden und
dann eingefroren wurden ("Cut-and-Branch").

Implementiert in `cscp_solver.py` (Verzweigung mit Schnitt),
`cscp_evaluation.py` (Vorher/Nachher-Vergleich) und `cscp_bruteforce.py`
(unabhängige Referenzlösung für Tests).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
