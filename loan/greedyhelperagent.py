from loan.helperagent import HelperAgent
from typing import List


class GreedyHelperAgent(HelperAgent):
    """GreedyHelperAgent contains the Nanite-agent logic for the HelperNanite.
    Greedy and reactive agents graph exploration
    Execution follows:
     - Perceive
     - Act
     - Update
    """

    def _get_same_node_neighbors(self, cell_list: List[int] = None):
        """Gets all of the neighbors on the same node that are NOT going to an AgentFactory"""
        cell_list = cell_list if cell_list is not None else [self.pos]
        return [agent for agent in self.model.grid.get_cell_list_contents(cell_list) if not agent.travelling_to_factory()]

    def travelling_to_factory(self):
        """Communicates whether the current agent is travelling to the factory."""
        return self.alert_for_disease_on_node

    def reset_unavailable_nodes(self):
        """Resets unavailable_nodes to an empty list."""
        self.unavailable_nodes = []

    def perceive(self) -> None:
        super().perceive()
        self.perception["same_node_neighbors"] = self._get_same_node_neighbors()

    def act(self) -> None:
        """Act."""
        """
        best_nodes = set([1,2,3,4])
        available_nodes = best_nodes - self.unavailable_nodes  # difference
        if len(available_nodes) == 0:
            chosen_node = best(best_nodes)
        else:
            chosen_node = best(available_node)
        for agent in self.perception["same_node_neighbors"]:
            agent.unavailable_nodes.append(chosen_node)
        """

        """
        best_nodes = set([1,2,3,4])
        available_nodes = best_nodes - self.unavailable_nodes  # difference
        chosen_node = best(available_node)
        
        if len(available_nodes) == 1:
            for agent in self.perception["same_node_neighbors"]:
                agent.reset_unavaible()
        else:
            for agent in self.perception["same_node_neighbors"]:
                agent.unavailable_nodes.append(chosen_node)
        """
        ...

        def update(self) -> None:
            """[summary]
            """

            # super().update()
            # self.unailable.clean()
            ...
