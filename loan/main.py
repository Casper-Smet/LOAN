from pathlib import Path

from helpers import graph_from_json, plot_graph
from model import HumanModel


def main():
    graph = graph_from_json(Path("./loan/network.json"))
    env = HumanModel(1, graph)

    for _ in range(10):
        print(env)
        env.step()

    plot_graph(graph)


if __name__ == "__main__":
    main()
