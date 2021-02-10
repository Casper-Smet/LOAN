import networkx as nx
from mesa import Model
from mesa.time import StagedActivation

from agent import NaniteAgent


class HumanModel(Model):
    """ Environment representing the human body's circulatory system.
    This environment contains a number of `NaniteAgent`-objects defined in `agent.py`. This class is also responsible for executing steps
    in the simulation and gathering data.
    """
    # CONSTANTINOPLE (the birthplace of the constant)
    INIT_HITPOINTS = 0.2
    ILLNESS_CHANCE = 1
    MAX_ILL_VERTICES = 4

    def __init__(self, N: int, network: nx.MultiDiGraph, hitpoints: int = INIT_HITPOINTS, illness_chance: float = ILLNESS_CHANCE, max_ill_vertices: int = MAX_ILL_VERTICES):
        self.num_agents = N
        self.hitpoints = hitpoints
        self._illness_chance = illness_chance
        self._max_ill_vertices = max_ill_vertices
        self.network: nx.MultiDiGraph = network
        self.ill_vertices = [3]
        model_stages = ["perceive", "act", "update"]
        self.schedule = StagedActivation(self, stage_list=model_stages)

        # create agents
        for i in range(self.num_agents):
            agent = NaniteAgent(i, self)
            # add to schedule
            self.schedule.add(agent)

    def _set_random_node_to_ill(self):
        """Sets a random node to ill"""
        if len(self.ill_vertices) == len(self.network.nodes):
            return
        while (node := self.random.choice(list(self.network.nodes))) in self.ill_vertices:
            continue
        self.ill_vertices.append(node)

    def step(self):
        # random Node _may_ get sick
        if len(self.ill_vertices) < self._max_ill_vertices and self.random.random() < self._illness_chance:
            self._set_random_node_to_ill()

        # Agents' StagedActivation
        # self.schedule.step()

    def healed(self, healed_vertex: int):
        """Gets a sign from an agent that an ill vertex has been healed. 
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: hitpoints {self.INIT_HITPOINTS}; agents {self.num_agents}; ill nodes {self.ill_vertices}"
