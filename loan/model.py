from pathlib import Path

import networkx as nx
from mesa import Model

from helpers import graph_from_json, plot_graph


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

    plot_graph(graph)
