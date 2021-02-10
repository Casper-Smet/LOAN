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
    INIT_HITPOINTS = 60
    ILLNESS_CHANCE = 0.2
    MAX_ILL_VERTICES = 4

    def __init__(self, N: int, network: nx.MultiDiGraph, hitpoints: int = INIT_HITPOINTS, illness_chance: float = ILLNESS_CHANCE, max_ill_vertices: int = MAX_ILL_VERTICES):
        self.num_agents = N
        self.hitpoints = hitpoints
        self._illness_chance = illness_chance
        self._max_ill_vertices = min(max_ill_vertices, len(network.nodes))
        self.network: nx.MultiDiGraph = network
        self.ill_vertices = []
        model_stages = ["perceive", "act", "update"]
        self.schedule = StagedActivation(self, stage_list=model_stages)

        # create agents
        for i in range(self.num_agents):
            agent = NaniteAgent(i, self)
            # add to schedule
            self.schedule.add(agent)

    def hurt(self):
        """Remove len(ill_verticies) from the model's hitpoints."""
        self.hitpoints -= len(self.ill_vertices)

    def _set_random_vertex_to_ill(self):
        """Sets a random node to ill"""
        options = set(self.network.nodes) - set(self.ill_vertices)
        vertex = self.random.choice(list(options))
        self.ill_vertices.append(vertex)

    def step(self):
        # All vertices that are still ill since last round hurt the human
        self.hurt()

        # if maximum amount of ill vertices is not met, random vertex _may_ get sick
        if len(self.ill_vertices) < self._max_ill_vertices and self.random.random() < self._illness_chance:
            self._set_random_vertex_to_ill()

        # Agents' StagedActivation
        # self.schedule.step()

    def restore_vertex(self, healed_vertex: int):
        """Gets a sign from an agent that an ill vertex has been healed."""
        if healed_vertex in self.ill_vertices:
            self.ill_vertices.remove(healed_vertex)
        else:
            raise ValueError(f"healed_vertex is not in ill_vertices, {healed_vertex} not in {self.ill_vertices}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: hitpoints {self.hitpoints}; agents {self.num_agents}; ill vertices {self.ill_vertices}"
