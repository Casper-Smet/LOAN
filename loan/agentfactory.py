from uuid import uuid1

from mesa import Agent, Model

from loan.killeragent import KillerAgent
from loan.helperagent import HelperAgent

class AgentFactory(Agent):

    def __init__(self, unique_id: int, model: Model, pos: int) -> None:
        super().__init__(unique_id, model)
        self.pos = pos
        self.visiting_agents = []
        self.helper_agents_with_alerts = []
        self.library_of_diseases = []
        self.nanite_queue = []
        self.spawned_killernanites = 0
        self.nanite_to_spawn = None
        self.newly_found_disease = None

    def perceive(self) -> None:
        # agents visiting on own position carrying alerts for diseases on certain nodes
        self.visiting_agents = self.model.network.nodes[self.pos]['agent']
        self.helper_agents_with_alerts = [a for a in self.visiting_agents if isinstance(a, HelperAgent) and a.alert_for_disease_on_node]

    def act(self) -> None:

        for helper_agent in self.helper_agents_with_alerts:
            location, disease = helper_agent.alert_for_disease_on_node

            # Find the unique ID for the next agent
            next_id = uuid1().int  # len(self.model.schedule.agents)

            # check if disease is known
            if disease in self.library_of_diseases:

                # send killer nanite immediately to location if disease is known
                self.nanite_to_spawn = KillerAgent(next_id, self.model, self, self.pos, location, disease)

            else:
                # new disease
                self.newly_found_disease = disease

                # make killer nanite wait for one or more timesteps by adding to queue
                self.nanite_queue.append(KillerAgent(next_id, self.model, self, self.pos, location, disease))

        # spawn the longest waiting killer nanite
        if len(self.nanite_queue): # and self.nanite_to_spawn == None ??
            self.nanite_to_spawn = self.nanite_queue.pop()

    def update(self) -> None:
        # reset alert_for_disease_on_node for helper agents
        for helper_agent in self.helper_agents_with_alerts:
            helper_agent.alert_for_disease_on_node = False

        # spawn killer nanite
        if self.nanite_to_spawn != None:
            self.model.grid.place_agent(self.nanite_to_spawn, self.pos)
            self.model.schedule.add(self.nanite_to_spawn)
            self.spawned_killernanites += 1
            self.nanite_to_spawn = None

        # update disease library
        if self.newly_found_disease != None:
            self.library_of_diseases.append(self.newly_found_disease)
            self.newly_found_disease = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
