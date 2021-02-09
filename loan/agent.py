from mesa import Agent


class NaniteAgent(Agent):
    """NaniteAgent contains the Nanite-agent logic.
    Execution follows:
     - Perceive
     - Act
     - Update
    """
    INIT_ENERGY = 20

    def __init__(self, unique_id, model, energy=INIT_ENERGY):
        super().__init__(unique_id, model)
        self.energy = energy

    def step():
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.model}/{self.unique_id}: Energy-level {self.energy}"

    def __str__(self) -> str:
        return self.__repr__()


if __name__ == "__main__":
    a = NaniteAgent(0, None)
    print(a)
