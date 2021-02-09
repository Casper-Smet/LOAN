from pathlib import Path

import networkx as nx
from mesa import Model


def network_from_json(fp: Path):
    ...


class HumanModel(Model):
    """ Environment representing the human body's circulatory system.
    This environment contains a number of `NaniteAgent`-objects defined in `agent.py`. This class is also responsible for executing steps in the simulation and gathering data.
    """
    INIT_HITPOINTS = 60

    def __init__(self, network):
        self.hitpoints = HumanModel.INIT_HITPOINTS
        self.network = network

if __name__ == "__main__":
    env = HumanModel("network")
