from mesa import Agent, Model

from loan.killeragent import KillerAgent


class AgentFactory(Agent):

    def __init__(self, unique_id: int, model: Model, pos: int) -> None:
        super().__init__(unique_id, model)
        self.pos = pos
        self.visiting_agents = []
        self.alerted_diseases = []
        self.library_of_diseases = []
        self.nanite_queue = []
        self.spawned_killernanites = 0
        self.nanite_to_spawn = None
        self.newly_found_disease = None

    def perceive(self) -> None:
        # agents visiting on own position carrying alerts for diseases on certain nodes
        self.visiting_agents = self.model.network.nodes[self.pos]["agent"]
        self.alerted_diseases = [a.alert_for_disease_on_node for a in self.visiting_agents if a.alert_for_disease_on_node]

        # message from killer nanite about destroyed diseases?

    def act(self) -> None:

        for location, disease in self.alerted_diseases:

            # check if disease is known
            if disease in self.library_of_diseases:

                # send killer nanite immediately to location if disease is known
                self.nanite_to_spawn = KillerAgent(self.spawned_killernanites, self.model, self, self.pos, location, disease)

            else:
                # new disease
                self.newly_found_disease = disease

                # spawn the longest waiting killer nanite
                if len(self.nanite_queue):
                    self.nanite_to_spawn = self.nanite_queue.pop()

                # make killer nanite wait for one or more timesteps by adding to queue
                self.nanite_queue.append(KillerAgent(self.spawned_killernanites, self.model, self, self.pos, location, disease))

    def update(self) -> None:
        # spawn killer nanite if necessary
        if self.nanite_to_spawn != None:
            self.model.schedule.add(self.nanite_to_spawn)
            self.model.grid.place_agent(self.nanite_to_spawn, self.pos)
            self.spawned_killernanites += 1

        # update disease library
        if self.newly_found_disease != None:
            self.library_of_diseases.append(self.newly_found_disease)
            self.newly_found_disease = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
