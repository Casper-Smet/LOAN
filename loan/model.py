from pathlib import Path
from typing import List

import networkx as nx
import copy
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from mesa.time import StagedActivation

from loan.agentfactory import AgentFactory
from loan.helperagent import HelperAgent
from loan.helpers import graph_from_json


class HumanModel(Model):
    """ Environment representing the human body's circulatory system.
    This environment contains a number of `HelperAgent`-objects defined in `agent.py`. This class is also responsible for executing steps
    in the simulation and gathering data.
    """
    # CONSTANTINOPLE (the birthplace of the constant)
    INIT_HITPOINTS = 60
    ILLNESS_CHANCE = 0.2
    INTERSECT_ASTRAY_CHANCE = 0.2
    MAX_ILL_VERTICES = 4
    NUM_AGENTS = 1
    GRAPH = graph_from_json(Path("./loan/data/network.json"))

    def __init__(self, N: int = NUM_AGENTS, network: nx.MultiDiGraph = GRAPH, hitpoints: int = INIT_HITPOINTS,
                 illness_chance: float = ILLNESS_CHANCE, max_ill_vertices: int = MAX_ILL_VERTICES):
        self.num_agents = N
        self.hitpoints = hitpoints
        self._illness_chance = illness_chance
        self._max_ill_vertices = min(max_ill_vertices, len(network.nodes))
        self.network: nx.MultiDiGraph = network
        self.grid = NetworkGrid(self.network)
        self.ill_vertices = []
        model_stages = ["perceive", "act", "update"]
        self.schedule = StagedActivation(self, stage_list=model_stages)
        self.factory_location = self.random.choice(list(network.nodes))
        self.agents = []
        self.healed_count = 0  # Amount of healed vertices at end of simulation

        # store the properties of the vertices into an dictionary
        props = {"heat_value": 0.0,    # float -> between 1.0 and 0.0
                 "is_ill": False,      # bool -> if the current vertex is ill
                 # str -> current illness (if the vertex is ill)
                 "illness_type": None}
        self.cell_properties = {x: copy.deepcopy(props) for x in self.network.nodes}

        # create agents
        for i in range(self.num_agents):
            # spawn agent on random node
            node_to_spawn = self.random.choice(list(self.network.nodes))
            agent = HelperAgent(i, self, node_to_spawn)
            self.grid.place_agent(agent, node_to_spawn)
            # add to schedule
            self.schedule.add(agent)
            # add to agent list
            self.agents.append(agent)

        agentfactory = AgentFactory(self.num_agents + 1, self, self.factory_location)
        self.grid.place_agent(agentfactory, agentfactory.pos)
        self.schedule.add(agentfactory)

        self.datacollector = DataCollector(model_reporters={"Hitpoints": "hitpoints", "Ill vertices": "ill_vertices"})
        self.running = True

    def hurt(self):
        """Remove len(ill_verticies) from the model's hitpoints."""
        self.hitpoints -= len(self.ill_vertices)

    def _get_random_sickness(self) -> str:
        """Chooses a random sickness to return."""
        illness = ["capitalism", "kovid++", "Caring Too Much", "Cutie Pox"]
        return self.random.choice(illness)

    def _update_own_props(self, vertex: int, is_healed: bool):
        """Updates the properties of one cell based on if it is healed and the illness of the neighbors."""

        if is_healed:
            self.cell_properties.get(vertex)["is_ill"] = False
            self.cell_properties.get(vertex)["illness_type"] = None

            if any(self.cell_properties.get(n).get("is_ill") for n in self.get_neighbors(vertex)):
                # A neighboring cell is ill, so heat_value cannot be changed to 0.0
                self.cell_properties.get(vertex)["heat_value"] = 0.5
            else:
                self.cell_properties.get(vertex)["heat_value"] = 0.0
        else:
            self.cell_properties.get(vertex)["is_ill"] = True
            self.cell_properties.get(vertex)["illness_type"] = self._get_random_sickness()
            self.cell_properties.get(vertex)["heat_value"] = 1.0

    def _update_neighbor_props(self, vertex: int, is_healed: bool):
        """Updates the heat_values of the neighbors of an particular vertex based on if the current vertex is healed."""
        neighbors = self.get_neighbors(vertex)

        for direct_neigh in neighbors:
            neigh_prop = self.cell_properties.get(direct_neigh)

            if not is_healed:
                # the middle vertex is sick, so update all the values of the neighbors
                if not neigh_prop.get("is_ill"):
                    # the current neighbor is not sick itself, so set the heat_value to 0.5
                    self.cell_properties.get(direct_neigh)["heat_value"] = 0.5

            else:
                # the middle value has been healed so update all the neighbors correctly
                # get all secondary neighbors minus the original vertex
                secondary_neighbors = [self.cell_properties.get(n).get(
                    "is_ill") for n in self.get_neighbors(direct_neigh) if n is not vertex]
                if any(secondary_neighbors):
                    # the neighbor has an ill neighbor so the heat_value stays 0.5
                    self.cell_properties.get(direct_neigh)["heat_value"] = 0.5
                else:
                    # the neighbor has no ill neighbors so no residual heat
                    self.cell_properties.get(direct_neigh)["heat_value"] = 0.0

    def _set_random_vertex_to_ill(self):
        """Sets a random node to ill"""
        options = set(self.network.nodes) - set(self.ill_vertices)
        vertex = self.random.choice(list(options))
        self.ill_vertices.append(vertex)

        # update the cell properties of the current vertex
        self._update_own_props(vertex, False)

        # update the heat_value of the neighbors of the vertex
        self._update_neighbor_props(vertex, False)

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
        self.datacollector.collect(self)

    def restore_vertex(self, healed_vertex: int):
        """Gets a sign from an agent that an ill vertex has been healed."""
        if healed_vertex in self.ill_vertices:
            self.ill_vertices.remove(healed_vertex)

            # update the cell properties of the current vertex
            self._update_own_props(healed_vertex, True)
            self._update_neighbor_props(healed_vertex, True)

            self.healed_count += 1
        else:
            raise ValueError(
                f"healed_vertex is not in ill_vertices, {healed_vertex} not in {self.ill_vertices}")

    def get_healed_count(self):
        """Gets amount of vertices that have been healed for batchrunner

        :return: HumanModel's healed_count
        :rtype: int
        """
        return self.healed_count

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

    def get_neighbors(self, vertex) -> List:
        """Gets list of neighbor vertices of given vertex.

        :return: HumanModel's neighbors of vertex
        :rtype: [int]
        """
        return list(self.network.neighbors(vertex))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: hitpoints {self.hitpoints}; agents {self.num_agents}; ill vertices {self.ill_vertices}"
