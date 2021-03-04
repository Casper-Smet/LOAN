from uuid import uuid1

from mesa import Agent, Model

from loan.helperagent import HelperAgent
from loan.killeragent import KillerAgent


class AgentFactory(Agent):

    def __init__(self, unique_id: int, model: Model, pos: int) -> None:
        super().__init__(unique_id, model)
        self.pos = pos
        self.helper_agents_with_alerts = []     # A list with agents on the factory position that have found a illness
        self.library_of_diseases = []           # A list with previously encountered illness
        self.nanite_queue = []                  #
        self.killer_agents_to_spawn = []             #
        self.newly_found_disease = None         #

    def perceive(self) -> None:
        # agents visiting on own position carrying alerts for diseases on certain nodes
        visiting_agents = self.model.network.nodes[self.pos]["agent"]
        self.helper_agents_with_alerts = [a for a in visiting_agents if isinstance(a, HelperAgent) and a.alert_for_disease_on_node]

    def act(self) -> None:
        for helper_agent in self.helper_agents_with_alerts:

            target, disease = helper_agent.alert_for_disease_on_node

            # Find the unique ID for the next agent
            next_id = uuid1().int

            # check if disease is known
            if disease in self.library_of_diseases:

                # send killer nanite immediately to location if disease is known
                self.killer_agents_to_spawn.append(KillerAgent(next_id, self.model, self, self.pos, target, disease))

            else:
                # new disease
                self.newly_found_disease = disease

                # make killer nanite wait for one or more timesteps by adding to queue
                self.nanite_queue.append(KillerAgent(next_id, self.model, self, self.pos, target, disease))

        # spawn the longest waiting killer nanite
        if len(self.nanite_queue):
            self.killer_agents_to_spawn.append(self.nanite_queue.pop())

    def update(self) -> None:
        # reset alert_for_disease_on_node for helper agents
        for helper_agent in self.helper_agents_with_alerts:
            helper_agent.alert_for_disease_on_node = False

        # spawn killer nanite
        for agent in self.killer_agents_to_spawn:
            self.model.grid.place_agent(agent, self.pos)
            self.model.schedule.add(agent)
            self.killer_agents_to_spawn.remove(agent)

        # update disease library
        if self.newly_found_disease is not None:
            self.library_of_diseases.append(self.newly_found_disease)
            self.newly_found_disease = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
