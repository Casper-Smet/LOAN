import json
import operator
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def graph_from_json(fp: Path, against_weight: int = 10, with_weight: int = 2, name: str = "HumanBody"):
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
    graph = nx.MultiDiGraph(name=name)
    graph.add_weighted_edges_from(network.tolist())  # Instantiate all edges with corresponding weights

    return graph


def give_node_positions():
    """Returns the node positions."""
    pos = {14: (1, 0), 12: (1, 1), 13: (0, 1), 11: (2, 1), 10: (1, 2), 9: (2, 2), 8: (0, 3),
           7: (1, 3), 6: (2, 3), 5: (0, 4), 4: (1, 4), 3: (2, 4), 2: (1, 5), 1: (1, 6)}
    return pos


def node_positions_on_canvas(all_pos: dict, w_canvas: int = 600, h_canvas: int = 600):
    """Calculate the positions of the nodes based on the height and width of the canvas.
    """
    # get the max coordinates on the x and y axis
    all_coords = list(all_pos.values())
    x_max = max(all_coords, key=operator.itemgetter(0))[0]
    y_max = max(all_coords, key=operator.itemgetter(1))[1]

    # Calculate the multiplication value on both axis with an offset
    x_mult = w_canvas // (x_max + 1)
    y_mult = h_canvas // (y_max + 1)

    # Apply the new position
    new_pos = {}
    for pos in all_pos.items():
        new_pos[pos[0]] = {"x": (pos[1][0] + 1) * x_mult,
                           "y": h_canvas - (pos[1][1] + 1) * y_mult}
    return new_pos


def plot_graph(graph):
    """Plots the given graph.
    For each tuple in pos-dictionairy, tuple[0] is the x-value, tuple[1] is the y-value.
    """
    pos = give_node_positions()

    # Draw all vertices and edges.
    nx.draw_networkx_edges(graph, pos=pos)
    nx.draw_networkx_labels(graph, pos=pos)
    nx.draw_networkx_nodes(graph, pos, nodelist=[5, 8, 13], node_color="tab:blue", node_size=800)  # Deoxygenated blood vertices
    nx.draw_networkx_nodes(graph, pos, nodelist=[3, 6, 9, 11], node_color="tab:red", node_size=800)  # Oxygenated blood vertices
    nx.draw_networkx_nodes(graph, pos, nodelist=[1, 2, 4, 7, 10, 12, 14], node_color="tab:purple", node_size=800)  # Organ-vertices

    plt.title(graph.name)
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    graph = graph_from_json(Path("./loan/network.json"))
    plot_graph(graph)
