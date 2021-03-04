from collections import namedtuple
from typing import List, Tuple

import networkx as nx
from mesa import Agent, Model


class HelperAgent(Agent):
    """HelperAgent contains the Nanite-agent logic for the HelperNanite.
    Execution follows:
     - Perceive
     - Act
     - Update
    """
    NextState = namedtuple("NextState", ["target", "energy_cost"], defaults=[None, 0])

    def __init__(self, unique_id: int, model: Model, pos: int, energy: int):
        super().__init__(unique_id, model)
        self.init_energy = energy
        self.energy = energy
        self.pos = pos
        # self.model.grid.place_agent(self, self.pos)
        # Holds the information about the next move to make
        self.next_state = HelperAgent.NextState()
        self.perception = {}
        self.percept_sequence = []  # Holds information about the visited Vertices
        self.factory_location = self.model.factory_location
        self.alert_for_disease_on_node = False  # (location, disease)
        self.going_with_the_flow = False

    def _move(self) -> None:
        """Moves the agent to the given vertex."""
        # self.pos = self.next_state.target
        self.model.grid.move_agent(self, self.next_state.target)

    def _perceive_paths(self, target: int) -> List[List[int]]:
        """Finds all shortest paths to a given target vertex.
        The shortest path is the path with the least energy cost (least total weight).
        """
        return list(nx.all_shortest_paths(self.model.network, source=self.pos, target=target, weight="weight"))

    def _best_path(self, paths: List[List[int]]) -> Tuple[List[int], int, List[int]]:
        """Finds the best path of given paths.
        The best path is based on the amount of steps necessary to reach the target.
        """
        # per path energy cost
        # per path the total length
        # calculate energy plus total length (cost)
        # select the one with the lowest cost
        # return (path, energy_cost, length)

        # Select path with lowest total cost
        path = min(paths, key=lambda x: len(x) + sum(self._path_cost(x)))
        energy_costs = self._path_cost(path)  # Energy cost
        step_cost = len(path)  # Amount of steps

        # TODO: Take current energy level of agent into account, agent might not reach the target in time
        return path, step_cost, energy_costs

    def _path_cost(self, path: List[int]) -> List[int]:
        """Calculates the cost of a given path."""
        return [self.model.network[path[i]][path[i+1]][0]["weight"] for i in range(len(path)-1)]

    def _get_neighbors_and_weights(self):
        """Gets neighbors and weights of current vertex."""
        # Get all the neighbors on the current position
        neighbors = self.model.network[self.pos]
        # Get the adjacent edges of the current vertex and the weights!
        return [(key, value[0]["weight"]) for key, value in neighbors.items()]

    def perceive(self) -> None:
        """"The perception of the agent.
        Sees:
          - Which vertices are ill. TODO: within N vertices in all directions.
          - If the vertex at the current position is ill.
          - Shortest paths to all ill vertices.
        """
        # Perceive current location on the graph
        self.percept_sequence.append(self.pos)
        # Perceive all the ill vertices from the environment
        self.perception["ill_vertices"] = self.model.ill_vertices
        # Perceive all possible shortest paths to all ill vertices
        self.perception["shortest_paths_per_ill_vertex"] = [
            self._perceive_paths(vert) for vert in self.perception["ill_vertices"]]
        # Perceive if the current vertex is ill
        # Boolean
        self.perception["cur_pos_is_ill"] = self.model.cell_properties[self.pos]["is_ill"]
        # Perceive the heat/inflammation value of the current vertex
        # 0.0 <= x <= 1.0
        self.perception["cur_pos_heat_value"] = self.model.cell_properties[self.pos]["heat_value"]
        # Perceive the current type of illness if the vertex is ill
        # String
        self.perception["cur_pos_illness_type"] = self.model.cell_properties[self.pos]["illness_type"]
        # Perceive the heat value of the neighboring vertices
        self.perception["cur_pos_neighbor_heat_values"] = {neigh: self.model.cell_properties[neigh]["heat_value"]
                                                           for neigh in self.model.get_neighbors(self.pos)}  # String

    def act(self) -> None:
        """Action-selection based on perception.
        Possible actions:
          - Go with the flow, when no ill vertices
          - Decide to which vertex to move, and how
          - TODO: Broadcast ill vertices to other agents within range
        """
        # Check whether the current vertex is ill
        if self.perception["cur_pos_is_ill"]:

            # Get shortest path to factory
            if not self.alert_for_disease_on_node:
                self.alert_for_disease_on_node = (self.pos, self.perception["cur_pos_illness_type"])

            # factory_location gets sick
            if self.factory_location == self.pos:
                self.next_state = HelperAgent.NextState(target=self.pos, energy_cost=0)
            else:
                path, _, energy_costs = self._best_path(self._perceive_paths(self.factory_location))
                self.next_state = HelperAgent.NextState(target=path[1], energy_cost=energy_costs[0])

        elif self.alert_for_disease_on_node:
            if self.factory_location == self.pos:
                self.next_state = HelperAgent.NextState(target=self.pos, energy_cost=0)
            else:
                path, _, energy_costs = self._best_path(self._perceive_paths(self.factory_location))
                self.next_state = HelperAgent.NextState(target=path[1], energy_cost=energy_costs[0])

        # Current vertex is not ill, so go with the flow!
        else:
            # Get the adjacent edges of the current vertex
            neighbors = self.model.get_neighbors(self.pos)
            neighbors_with_heatvalue = list(filter(lambda n: self.model.cell_properties[n]["heat_value"] > 0.0, neighbors))

            if not neighbors_with_heatvalue:  # Path with lowest cost since there's no target
                neigh_with_lowest_cost = min(neighbors, key=lambda n: self._path_cost([self.pos, n])[0])
                lowest_cost = self._path_cost([self.pos, neigh_with_lowest_cost])[0]
                filtered = list(filter(lambda n: self._path_cost([self.pos, n])[0] == lowest_cost, neighbors))
            else:  # Path with heigest heat value
                neigh_with_highest_heat = max(neighbors, key=lambda n: self.model.cell_properties[n]["heat_value"])
                highest_heat = self.model.cell_properties[neigh_with_highest_heat]["heat_value"]
                filtered = list(filter(lambda n: self.model.cell_properties[n]["heat_value"] == highest_heat, neighbors))
                
            # Set the next state.
            new_target = self.model.random.choice(filtered)
            self.next_state = HelperAgent.NextState(target=new_target, energy_cost=self._path_cost([self.pos, new_target])[0])

        self.going_with_the_flow = self.next_state.energy_cost < 4  # Determine if the dynamo should recharge the helperagent

    def update(self) -> None:
        """Updates the current state of the agent."""
        # Always move the HelperAgent
        self._move()

        # Lower the energy of the agent because it moves
        self.energy -= self.next_state.energy_cost

        # Gain energy by recharging via dynamo
        if self.going_with_the_flow:
            self.energy = min(self.energy + 3, self.init_energy)  # Cap the energy of the agent if the 'battery' is full

        # TODO: Consider moving this code to the environment
        if self.energy <= 0:  # If no energy left, agent is dead.
            self.model.grid._remove_agent(self, self.pos)
            self.model.schedule.remove(self)
            self.model.alive_helper_agents -= 1

        self.model.total_energy_agents = self.energy

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Energy {self.energy}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
