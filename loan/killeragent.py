from mesa import Agent, Model


class KillerAgent(Agent):

    def __init__(self, model: Model, creator, pos: int, target_location: int, target_disease: str) -> None:
        super().__init__(model)
        self.creator = creator
        self.pos = pos
        self.target_location = target_location
        self.target_disease = target_disease
        self.arrived_on_location = False

    def perceive(self) -> None:

        # check if target_location is reached
        self.arrived_on_location = self.pos == self.target_location

    def act(self) -> None:
        ...

    def update(self) -> None:

        if self.arrived_on_location:
            self.model.ill_vertices.remove(self.target_location)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.creator.spawned_killernanites -= 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Position {self.pos}"

    def __str__(self) -> str:
        return self.__repr__()
