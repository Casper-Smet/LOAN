from pathlib import Path

import networkx as nx

from agent import NaniteAgent
from helpers import graph_from_json, plot_graph
from model import HumanModel


def main():
    graph = graph_from_json(Path("./loan/network.json"))
    env = HumanModel(1, graph)
    print(env)
    env.step()
    print(env)
    # a = NaniteAgent(0, env)
    # print(a)
    # best_paths = a.perceive()
    # for p in best_paths:
    #     print(p)
    # plot_graph(graph)


if __name__ == "__main__":
    main()
