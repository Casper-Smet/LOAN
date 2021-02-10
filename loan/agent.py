import networkx as nx

from collections import namedtuple
from mesa import Agent
from networkx.algorithms.shortest_paths.generic import shortest_path


class NaniteAgent(Agent):
    """NaniteAgent contains the Nanite-agent logic.
    Execution follows:
     - Perceive
     - Act
     - Update
    """
    INIT_ENERGY = 20
    NextState = namedtuple("NextState", ["heal", "target"], defaults=[False])

    def __init__(self, unique_id: int, model, energy: int = INIT_ENERGY):
        super().__init__(unique_id, model)
        self.energy = energy
        self.pos = self.random.choice(list(self.model.network.nodes))
        self.next_state = None  # Holds the information about the next move to make

    def _heal(self):
        """Heals vertex at current position, calls self.model.healed(healed_vertex: int)."""
        self.model.healed(self.pos)

    def _move(self):
        """Moves the agent to the given vertex."""
        self.pos = self.next_state.target

    def _perceive_paths(self, target):
        """Finds all shortest paths to a given target vertex.
        The shortest path is the path with the least energy cost.
        """
        return list(nx.all_shortest_paths(self.model.network, source=self.pos, target=target, weight="weight"))

    def _best_paths(self, paths):
        """Finds the best path of given paths.
        The best path is based on the amount of steps necessary.
        """
        path = min(paths, key=lambda x: len(x))  # Select path which will take the least amount of steps
        energy_costs = self._path_cost(path)  # Energy cost is the same for all shortest paths
        step_cost = len(path)

        # TODO: Take current energy level of agent into account
        return path, energy_costs, step_cost

    def _path_cost(self, path: list):
        """Calculates the cost of a given path."""
        return [self.model.network[path[i]][path[i+1]][0]["weight"] for i in range(len(path)-1)]

    def perceive(self):
        """"The perception of the agent.
        Sees:
          - Which vertices are ill. TODO: within N vertices in all directions.
          - Paths to all ill vertices.
        """
        # Perceive all the ill vertices from the environment
        ill_vertices = self.model.ill_vertices
        # Perceive if the current vertex is ill
        if self.pos in ill_vertices:
            is_ill = True
        else:
            is_ill = False

        # Perceive all possible shortest paths to all ill vertices
        self.perception = [self._perceive_paths(vert) for vert in ill_vertices], is_ill

    def act(self):
        """Action-selection based on perception.
        Possible actions:
          - Go with the flow
          - Go against the flow
          - Heal the vertex at the current position
          - TODO: Broadcast ill vertices to other agents within range
        """
        if self.perception[1]:  # If current vertex is ill
            self.next_state = NextState(target=None, heal=True)
        else:  # Move if current vertex is nog ill
            best_paths = [self._best_paths(path) for path in self.perception]  # The best path for each ill vertex
            chosen_path = min(best_paths, key=lambda x: x[1] + x[2])  # Select path which will take the least amount of steps
            # TODO: Add probability behaviour

            self.next_state = NextState(target=chosen_path[1], heal=False)

    def update(self):
        """Updates the current state of the agent."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Energy {self.energy}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
