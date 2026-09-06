# Symmetrie-Schnitte am Cutting-Stock-Problem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-cutting-stock-cutting-planes-demo.streamlit.app/)**

Drittes Stück der Cutting-Stock-Linie (nach
[cutting-stock-branch-bound-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-bound-demo)):
ein unabhängiger Zweig direkt von der Wurzel, parallel zu
[cutting-stock-dp-demo](https://github.com/sebastian-hanisch/cutting-stock-dp-demo).
Dort blieb Bin Packings berüchtigte Schwäche - austauschbare (symmetrische)
Bins blähen den Suchbaum unnötig auf - bewusst unangetastet, nur diagnostisch
gemessen (Vergleich mit einer künstlich entsymmetrisierten Zwillingsinstanz).
Dieses Stück behebt es tatsächlich: ein echter, algorithmischer
**Symmetrie-Schnitt**, der redundante Äste erst gar nicht erzeugt - auf
derselben Instanz, ohne sie zu verändern.

## Der Schnitt

An jedem Suchbaum-Knoten werden die offenen Bins nach Restkapazität
gruppiert. Haben zwei oder mehr offene Bins exakt dieselbe Restkapazität,
sind sie für alle künftigen Entscheidungen ununterscheidbar - das nächste
Stück dort statt hier zu platzieren erzeugt einen isomorphen Teilbaum. Der
Schnitt erzeugt deshalb pro Gruppe gleich großer Bins nur EINEN
Repräsentanten als Kindoption; die übrigen zählen als übersprungen, ohne
selbst einen Knoten zu erzeugen.

**Zulässigkeitsbeweis (Tausch-Argument)**: sei $B$ eine optimale Lösung, die
Bin $j$ statt des Repräsentanten $i$ (identische Restkapazität) verwendet -
das Vertauschen der Rollen von $i$ und $j$ in $B$ ist ebenfalls zulässig und
liefert dieselbe Bin-Anzahl. Der Repräsentant deckt also jede erreichbare
Optimallösung mit ab; kein Optimum geht verloren.

## Warum kein LP-Schranken-Schnitt wie in cutting-planes-demo (erste Linie)

Rucksack hat eine LP-Relaxation, die Cover-Cuts messbar verschärfen. Bin
Packings kompakte Formulierung (Kantorovich-Modell) hat zwar auch eine
LP-Relaxation, aber Symmetrie-Constraints schneiden dort nur symmetrische
GANZZAHLIGE Lösungen weg, nicht den fraktionalen LP-Wert selbst - eine
LP-Schranken-Verbesserung wäre hier keine ehrliche Demonstration. Die
wirklich starke, Muster-basierte LP-Relaxation (Gilmore-Gomory) ist bewusst
für Column Generation später in dieser Linie reserviert. Dieser Schnitt
wirkt deshalb direkt auf den kombinatorischen Suchraum - eine andere,
ebenso legitime Familie von "Cutting Planes" im weiteren Sinne.

## Empirisch bestätigt, nicht nur angenommen

Vor der Umsetzung per Prototyp geprüft: über 800 zufällige Instanzen
(n_types 2-6, max_demand 1-4) hielt die Invariante `nodes_mit_schnitt <=
nodes_ohne_schnitt` ausnahmslos - keine einzige Ausnahme trotz
unterschiedlicher Verzweigungs-/Inkumbenten-Reihenfolge. Bei spürbarer
Symmetrie reduziert der Schnitt die Knotenzahl um mehr als das 40-fache; bei
einer gezielt größeren Instanz (7 Auftragstypen) erreicht die Baseline die
Sicherheitsgrenze von 100.000 Knoten, OHNE das Optimum zu beweisen, während
dieselbe Instanz mit Schnitt in weniger als 300 Knoten bewiesen optimal
gelöst ist.

## Visualisierung

Suchbaum wie in `cutting-stock-branch-bound-demo`, aber Knoten, an denen der
Schnitt tatsächlich etwas übersprungen hat, sind sichtbar markiert (violett
umrandet, mit Anzahl der übersprungenen baugleichen Bins) - keine
unbeobachtbare Kennzahl, sondern direkt im Baum nachvollziehbar. Zusätzlich
ein Vorher/Nachher-Balkendiagramm (ohne vs. mit Schnitt, auf derselben
Instanz) als Kernbeleg.

## Verifikation

- **Bruteforce-Cross-Check**: mit UND ohne Schnitt, gegen dieselbe
  unabhängige Referenz.
- **Optimalitäts-Erhaltung**: der Schnitt ändert nie das gefundene Optimum,
  über viele Zufallsinstanzen geprüft.
- **Knoten-Reduktions-Invariante**: `nodes_mit_schnitt <= nodes_ohne_schnitt`
  gilt strikt, empirisch bestätigt (siehe oben), als Regressionstest
  verankert.
- **Symmetrie-Verstärkungs-Test**: das "Spürbare Symmetrie"-Preset zeigt
  einen Reduktionsfaktor über 20× (gemessen: ~48,6×).
- **Sicherheitsgrenzen-Test**: auch mit Schnitt greift die Grenze bei
  genügend großen Instanzen zuverlässig.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Suchbaum-Animation, Vorher/Nachher-Vergleich, Formulierungs-Expander |
| `cscp_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `cscp_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `cscp_scenario.py` | Zufällige Cutting-Stock-Instanzen, Bin-Packing-Brücke |
| `cscp_bounds.py` | `weak_bound` (L1-Schranke) |
| `cscp_solver.py` | n-äre Tiefensuche mit optionalem Symmetrie-Schnitt |
| `cscp_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) |
| `cscp_evaluation.py` | Kennzahlen, Vorher/Nachher-Vergleich |
| `cscp_visualization.py` | Suchbaum- und Vergleichsdiagramm (Plotly) |
| `tests/` | Bruteforce-Cross-Check, Optimalitäts- und Knoten-Reduktions-Invarianten, Symmetrie-Verstärkung, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
