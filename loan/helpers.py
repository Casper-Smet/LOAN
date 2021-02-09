import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def graph_from_json(fp: Path, against_weight: int = 4, with_weight: int = 2):
    """Loads a graph from given filepath.

    Each row in `network` represents an edge and contains an array with 3 elements.
    The first two elements combined are the from and to vertices for the edge.
    The third element indicates if the edge is going with or against the stream.
    With is indicated by `0`. Against is indicated by `1`.
    """
    with open(fp) as f:
        network = np.array(json.load(f).get("network"), dtype=int)

    # Change all weights to corresponding energy cost
    network[:, 2] = np.where(network[:, 2] == 0, with_weight, against_weight)

    # Building and filling the graph
    graph = nx.MultiDiGraph(name="HumanBody")
    graph.add_weighted_edges_from(network.tolist())  # Instantiate all edges with corresponding weights

    return graph


def plot_graph(graph):
    """Plots the given graph."""
    pos = nx.spring_layout(graph)  # Save positions of all vertices
    options = {"edgecolors": "tab:grey", "node_size": 800, "alpha": 0.95}

    # Draw all nodes
    nx.draw_networkx_nodes(graph, pos, nodelist=[3, 6, 9, 11], node_color="tab:red", **options)  # Oxygenated blood vertices
    nx.draw_networkx_nodes(graph, pos, nodelist=[5, 8, 13], node_color="tab:blue", **options)  # Deoxygenated blood vertices
    nx.draw_networkx_nodes(graph, pos, nodelist=[1, 2, 4, 7, 10, 12, 14], node_color="tab:purple", **options)  # Organ-vertices

    # Draw all edges
    nx.draw_networkx_edges(graph, pos, width=1.0, alpha=0.5)
    plt.show()
