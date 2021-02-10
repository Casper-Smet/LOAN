import networkx as nx
from mesa import Model
from mesa.datacollection import DataCollector
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
    INTERSECT_ASTRAY_CHANCE = 0.1
    MAX_ILL_VERTICES = 4

    def __init__(self, N: int, network: nx.MultiDiGraph, hitpoints: int = INIT_HITPOINTS, illness_chance: float = ILLNESS_CHANCE, max_ill_vertices: int = MAX_ILL_VERTICES):
        self.num_agents = N
        self.hitpoints = hitpoints
        self._illness_chance = illness_chance
        self._max_ill_vertices = min(max_ill_vertices, len(network.nodes))
        self.network: nx.MultiDiGraph = network
        self.ill_vertices = [2]
        model_stages = ["perceive", "act", "update"]
        self.schedule = StagedActivation(self, stage_list=model_stages)

        # create agents
        for i in range(self.num_agents):
            agent = NaniteAgent(i, self)
            # add to schedule
            self.schedule.add(agent)

        self.datacollector = DataCollector(
            model_reporters={"Hitpoints": "hitpoints", "Ill vertices": "ill_vertices"})
        self.running = True

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
        if self.hitpoints < 1:
            self.running = False
            return

        # if maximum amount of ill vertices is not met, random vertex _may_ get sick
        if len(self.ill_vertices) < self._max_ill_vertices and self.random.random() < self._illness_chance:
            self._set_random_vertex_to_ill()

        # Agents' StagedActivation
        self.schedule.step()

        # Collect data
        # self.datacollector.collect(self)

    def restore_vertex(self, healed_vertex: int):
        """Gets a sign from an agent that an ill vertex has been healed."""
        if healed_vertex in self.ill_vertices:
            self.ill_vertices.remove(healed_vertex)
        else:
            raise ValueError(
                f"healed_vertex is not in ill_vertices, {healed_vertex} not in {self.ill_vertices}")

    def get_hitpoints(self):
        """Gets hitpoints for batchrunner

        :return: HumanModel's hitpoints
        :rtype: int
        """
        return self.hitpoints

    def get_ill_vertices(self):
        """Gets ill_vertices for batchrunner

        :return: HumanModel's ill_vertices
        :rtype: [int]
        """
        return self.ill_vertices

    def get_end(self):
        """Gets step count for batchrunner

        :return: HumanModel's step count
        :rtype: int
        """
        return self.schedule.steps

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: hitpoints {self.hitpoints}; agents {self.num_agents}; ill vertices {self.ill_vertices}"
