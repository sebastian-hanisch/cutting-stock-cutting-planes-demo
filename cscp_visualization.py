"""Plotly-Suchbaum, Portierung von csbb_visualization.py - erweitert um sichtbare
Markierung der Knoten, an denen der Symmetrie-Schnitt tatsächlich etwas
übersprungen hat (`skipped_symmetric > 0`), plus die Vorher/Nachher-Balkengrafik
für den Kernvergleich dieses Stücks."""

STATUS_STYLE = {
    "root": {"color": "#14233B", "label": "Start"},
    "branch": {"color": "#1f77b4", "label": "Verzweigt (weiter untersucht)"},
    "prune_bound": {"color": "#d68a2e", "label": "Gestutzt (Bound zu schwach)"},
    "leaf_new_best": {"color": "#2ca02c", "label": "Neue beste Lösung"},
    "leaf_not_best": {"color": "#c4cbd8", "label": "Vollständig, nicht besser"},
}
STATUS_ORDER = ["root", "branch", "prune_bound", "leaf_new_best", "leaf_not_best"]
SYMMETRIC_SKIP_COLOR = "#8e44ad"


def _compute_layout(nodes):
    by_id = {n.id: n for n in nodes}
    children = {}
    for n in nodes:
        if n.parent_id is not None:
            children.setdefault(n.parent_id, []).append(n.id)

    x_of = {}
    next_leaf_slot = [0]

    def assign(node_id):
        kids = children.get(node_id, [])
        if not kids:
            x_of[node_id] = next_leaf_slot[0]
            next_leaf_slot[0] += 1
            return x_of[node_id]
        xs = [assign(k) for k in kids]
        x_of[node_id] = sum(xs) / len(xs)
        return x_of[node_id]

    assign(nodes[0].id)
    return {nid: (x_of[nid], -by_id[nid].depth) for nid in x_of}


def _node_label(node):
    if node.status == "root":
        return "Start<br>noch kein Stück platziert"

    kind, idx = node.target
    placement = f"Neues Bin {idx + 1} geöffnet" if kind == "new" else f"In Bin {idx + 1} gelegt"
    label = f"Stück (Breite {node.piece_width}) - {placement}<br>Offene Bins: {node.bins_open}"
    if node.bound is not None:
        label += f"<br>Schranke: {node.bound}"
    if node.skipped_symmetric > 0:
        label += (
            f"<br><b>×{node.skipped_symmetric} baugleiche Bin(s) übersprungen</b> "
            "(identische Restkapazität - Symmetrie-Schnitt)"
        )
    return label


def build_tree_figure(result, step, render_cap):
    import plotly.graph_objects as go

    layout_nodes = list(result.nodes)[:render_cap]
    layout = _compute_layout(layout_nodes)
    nodes = [n for n in layout_nodes if n.id <= step]
    rendered_ids = {n.id for n in nodes}

    fig = go.Figure()

    edge_x, edge_y = [], []
    for n in nodes:
        if n.parent_id is not None and n.parent_id in rendered_ids:
            x0, y0 = layout[n.parent_id]
            x1, y1 = layout[n.id]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(color="#c4cbd8", width=1.5), hoverinfo="skip", showlegend=False))

    for status in STATUS_ORDER:
        group = [n for n in nodes if n.status == status]
        if not group:
            continue
        style = STATUS_STYLE[status]
        xs = [layout[n.id][0] for n in group]
        ys = [layout[n.id][1] for n in group]
        texts = [_node_label(n) for n in group]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers", name=style["label"],
                marker=dict(size=11 if status != "leaf_new_best" else 15, color=style["color"],
                            line=dict(width=1, color="white"),
                            symbol="star" if status == "leaf_new_best" else "circle"),
                hovertext=texts, hoverinfo="text",
            )
        )

    skip_group = [n for n in nodes if n.skipped_symmetric > 0]
    if skip_group:
        xs = [layout[n.id][0] for n in skip_group]
        ys = [layout[n.id][1] for n in skip_group]
        texts = [_node_label(n) for n in skip_group]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers", name="Symmetrie-Schnitt griff hier",
                marker=dict(size=20, color="rgba(0,0,0,0)", line=dict(width=2.5, color=SYMMETRIC_SKIP_COLOR)),
                hovertext=texts, hoverinfo="text",
            )
        )

    fig.update_layout(
        template="plotly_white", height=460,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=40, l=10, r=10, b=10),
    )
    return fig


def build_comparison_chart(comparison):
    import plotly.graph_objects as go

    labels = ["Ohne Schnitt (Baseline)", "Mit Symmetrie-Schnitt"]
    values = [comparison["baseline_nodes"], comparison["cut_nodes"]]
    colors = ["#c4cbd8", "#8e44ad"]
    fig = go.Figure(
        go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:,}" for v in values], textposition="outside")
    )
    fig.update_layout(
        template="plotly_white", height=360,
        yaxis=dict(title="Anzahl besuchter Knoten"),
        margin=dict(t=30, l=10, r=10, b=10),
        showlegend=False,
    )
    return fig
