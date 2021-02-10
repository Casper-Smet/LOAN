from collections import namedtuple
from typing import List, Tuple

import networkx as nx
from mesa import Agent


class NaniteAgent(Agent):
    """NaniteAgent contains the Nanite-agent logic.
    Execution follows:
     - Perceive
     - Act
     - Update
    """
    INIT_ENERGY = 20
    NextState = namedtuple("NextState", ["heal", "target"], defaults=[False, None])

    def __init__(self, unique_id: int, model, energy: int = INIT_ENERGY):
        super().__init__(unique_id, model)
        self.energy = energy
        self.pos = self.random.choice(list(self.model.network.nodes))
        self.next_state = NaniteAgent.NextState()  # Holds the information about the next move to make
        self.perception = {}

    def _heal(self) -> None:
        """Heals vertex at current position, calls self.model.healed(healed_vertex: int)."""
        self.model.restore_vertex(self.pos)

    def _move(self) -> None:
        """Moves the agent to the given vertex."""
        self.pos = self.next_state.target

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

        path = min(paths, key=lambda x: len(x) + sum(self._path_cost(x)))  # Select path with lowest total cost
        energy_costs = self._path_cost(path)  # Energy cost
        step_cost = len(path)  # Amount of steps

        # TODO: Take current energy level of agent into account, agent might not reach the target in time
        return path, step_cost, energy_costs

    def _path_cost(self, path: List[int]) -> List[int]:
        """Calculates the cost of a given path."""
        return [self.model.network[path[i]][path[i+1]][0]["weight"] for i in range(len(path)-1)]

    def perceive(self) -> None:
        """"The perception of the agent.
        Sees:
          - Which vertices are ill. TODO: within N vertices in all directions.
          - If the vertex at the current position is ill.
          - Shortest paths to all ill vertices.
        """
        # Perceive all the ill vertices from the environment
        self.perception["ill_vertices"] = self.model.ill_vertices
        # Perceive if the current vertex is ill
        self.perception["cur_pos_is_ill"] = self.pos in self.perception["ill_vertices"]
        # Perceive all possible shortest paths to all ill vertices
        self.perception["shortest_paths_per_ill_vertex"] = [self._perceive_paths(vert) for vert in self.perception["ill_vertices"]]

    def act(self) -> None:
        """Action-selection based on perception.
        Possible actions:
          - Heal the vertex at the current position
          - Go with the flow, when no ill vertices
          - Decide to which vertex to move, and how
          - TODO: Broadcast ill vertices to other agents within range
        """
        if self.perception["cur_pos_is_ill"]:
            # Check whether the current vertex is ill
            self.next_state = NaniteAgent.NextState(target=None, heal=True)

        elif not len(self.perception["ill_vertices"]):
            # No ill vertices, so go with the flow!
            neighbors = self.model.network[self.pos]
            # Get the adjacent edges of the current vertex!
            adj_edges = [(key, value[0]["weight"]) for key, value in neighbors.items()]
            # Select the target vertex based on laziness (use the least energy)!
            # TODO: Adding probability
            new_target = min(adj_edges, key=lambda x: x[1])[0]
            # Set the next state.
            self.next_state = NaniteAgent.NextState(target=new_target, heal=False)

        else:
            # There are ill vertices, so find your destination vertex!
            best_paths = []
            for target_paths in self.perception["shortest_paths_per_ill_vertex"]:
                best_paths.append(self._best_path(target_paths))

            # Select the best path which will best_paths per target
            chosen_path = min(best_paths, key=lambda x: x[1] + sum(x[2]))  # Select path which will take the least amount of steps
            # TODO: Add probability behaviour!

            self.next_state = NaniteAgent.NextState(target=chosen_path[1], heal=False)

    def update(self) -> None:
        """Updates the current state of the agent."""
        if self.next_state.heal:
            self._heal()
        else:
            self._move()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Energy {self.energy}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
