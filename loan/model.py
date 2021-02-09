from pathlib import Path

import networkx as nx
from mesa import Model
import json
import numpy as np
import matplotlib.pyplot as plt


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


class HumanModel(Model):
    """ Environment representing the human body's circulatory system.
    This environment contains a number of `NaniteAgent`-objects defined in `agent.py`. This class is also responsible for executing steps
    in the simulation and gathering data.
    """
    INIT_HITPOINTS = 60

    def __init__(self, network, hitpoints=INIT_HITPOINTS):
        self.hitpoints = hitpoints
        self.network = network
        self.agents = [1, 2, 3, 4]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: hitpoints {self.INIT_HITPOINTS}; agents {self.agents}"


if __name__ == "__main__":
    env = HumanModel("network")
    print(env)
    graph = graph_from_json(Path("loan/network.json"))
    paths = nx.all_shortest_paths(graph, source=2, target=13, weight="weight")
    for p in paths:
        print(p)
    
    # nx.draw(graph)
    # plt.draw()

