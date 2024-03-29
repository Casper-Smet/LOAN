from collections import namedtuple

import networkx as nx
from mesa import Agent, Model


class KillerAgent(Agent):
    def __init__(self, unique_id: int, model: Model, creator, pos: int, target_location: int, target_disease: str) -> None:
        super().__init__(unique_id, model)
        self.creator = creator
        self.pos = pos
        self.target_location = target_location
        self.target_disease = target_disease
        self.arrived_on_location = False
        self.shortest_path_to_target_node = []

    def perceive(self) -> None:
        self.arrived_on_location = self.pos == self.target_location
        self.shortest_path_to_target_node = nx.shortest_path(G=self.model.network, source=self.pos, target=self.target_location)

    def act(self) -> None:
        ...

    def update(self) -> None:
        if self.arrived_on_location:
            if self.pos in self.model.ill_vertices:
                self.model.restore_vertex(self.pos)
            self.model.grid._remove_agent(self, self.pos)
            self.model.schedule.remove(self)
        else:
            self.model.grid.move_agent(self, self.shortest_path_to_target_node[1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
    
    def emojify(self):
        return " 💉"