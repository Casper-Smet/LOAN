from mesa import Agent, Model
from collections import namedtuple
from typing import List
import networkx as nx

class KillerAgent(Agent):

    INIT_ENERGY = 20
    NextState = namedtuple("NextState", ["target", "energy_cost"], defaults=[None, 0])

    def __init__(self, unique_id: int, model: Model, creator, pos: int, target_location: int, target_disease: str) -> None:
        super().__init__(unique_id, model)
        self.creator = creator
        self.pos = pos
        self.target_location = target_location
        self.target_disease = target_disease
        self.arrived_on_location = False
        self.shortest_path_to_target_node = []

    def perceive(self) -> None:
        # check if target_location is reached
        if not len(self.shortest_path_to_target_node):
            self.arrived_on_location = self.pos == self.target_location
            self.shortest_path_to_target_node = nx.shortest_path(G=self.model.network, source=self.pos, target=self.target_location)

    def act(self) -> None:
        # follow shortest path
        self.shortest_path_to_target_node


    def update(self) -> None:

        if self.arrived_on_location:
            self.model.restore_vertex(self.target_location)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.creator.spawned_killernanites -= 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
