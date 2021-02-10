from pathlib import Path

import networkx as nx

from agent import NaniteAgent
from helpers import graph_from_json, plot_graph
from model import HumanModel


def main():
    graph = graph_from_json(Path("./loan/network.json"))
    env = HumanModel(1, graph)
    # print(env)
    # env.step()
    # print(env)
    # env.step()
    # print(env)
    a = NaniteAgent(0, env)
    # a.pos = env.ill_vertices[0]
    # a._heal()
    # print(env)
    print(a)
    a.perceive()
    a.act()
    a.update()

    # plot_graph(graph)


if __name__ == "__main__":
    main()
