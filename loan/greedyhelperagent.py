from typing import List

from mesa import Model

from loan.helperagent import HelperAgent, NextState

class GreedyHelperAgent(HelperAgent):
    """GreedyHelperAgent contains the Nanite-agent logic for the HelperNanite.
    Greedy and reactive agents graph exploration
    Execution follows:
     - Perceive
     - Act
     - Update
    """

    def __init__(self, unique_id: int, model: Model, pos: int, energy: int):
        """ """
        super().__init__(unique_id, model, pos, energy)
        self.unavailable_vertices = []

    def travelling_to_factory(self):
        """Communicates whether the current agent is travelling to the factory."""
        return self.alert_for_disease_on_node

    def _get_available_agents_on_vertex(self, cell_list: List[int] = None):
        """Gets all of the helperagents on the same node that are NOT going to an AgentFactory."""
        cell_list = cell_list if cell_list is not None else [self.pos]
        return [agent for agent in self.model.grid.get_cell_list_contents(cell_list) if isinstance(agent, HelperAgent) and not agent.travelling_to_factory()]

    def reset_unavailable_vertices(self):
        """Resets unavailable_vertices to an empty list."""
        self.unavailable_vertices = []

    def update_unavailable_vertices(self, vertex: int):
        """Updates the unavailable vertices list by adding the vertex chosen by an agent.

        Args:
            vertex (int): The vertex to be added to the list of unavailable vertices
        """
        self.unavailable_vertices.append(vertex)

    def perceive(self) -> None:
        super().perceive()
        self.perception["agents_on_vertex"] = self._get_available_agents_on_vertex()
        self.perception["all_neighbor_vertices"] = self.model.get_neighbors(self.pos)

    def act(self) -> None:
        """Act."""
        self.available_vertices = set(self.perception["all_neighbor_vertices"]) - set(self.unavailable_vertices)

        # Check whether the current vertex is ill
        if self.perception["cur_pos_is_ill"]:

            # Get shortest path to factory
            if not self.alert_for_disease_on_node:
                self.alert_for_disease_on_node = (self.pos, self.perception["cur_pos_illness_type"])

            # factory_location gets sick
            if self.factory_location == self.pos:
                self.next_state = NextState(target=self.pos, energy_cost=0)
            else:
                path, _, energy_costs = self._best_path(self._perceive_paths(self.factory_location))
                self.next_state = NextState(target=path[1], energy_cost=energy_costs[0])

        elif self.alert_for_disease_on_node:
            if self.factory_location == self.pos:
                self.next_state = NextState(target=self.pos, energy_cost=0)
            else:
                path, _, energy_costs = self._best_path(self._perceive_paths(self.factory_location))
                self.next_state = NextState(target=path[1], energy_cost=energy_costs[0])

        else:
            if not self.available_vertices:  # All next vertices are evenly populated
                # All routes are already taken by the other agents
                for agent in self.perception["agents_on_vertex"]:
                    agent.reset_unavailable_vertices()  # All neighboring vertices are available to all future agents for this step

                # Choose random vertex from all neighbors
                neighbors = self.perception["all_neighbor_vertices"]
                best_neighbors = self._list_of_best_neighbors(neighbors)
                chosen_vertex = self.model.random.choice(best_neighbors)  # Add best choice function
            else:
                # Get random vertex from available vertices and remove from available vertices.
                neighbors = list(self.available_vertices)
                
                best_neighbors = self._list_of_best_neighbors(neighbors)
                chosen_vertex = self.model.random.choice(best_neighbors)  # Add best choice function
                for agent in self.perception["agents_on_vertex"]:
                    agent.update_unavailable_vertices(chosen_vertex)

            
            self.next_state = NextState(target=chosen_vertex, energy_cost=self._path_cost([self.pos, chosen_vertex])[0])

    def update(self) -> None:
        """Update."""
        super().update()

        # reset the unavailable vertices to be sure
        self.reset_unavailable_vertices()
    
    def emojify(self):
        return " 🤑"
