from mesa import Agent


class NaniteAgent(Agent):
    """NaniteAgent contains the Nanite-agent logic.
    Execution follows:
     - Perceive
     - Act
     - Update
    """
    INIT_ENERGY = 20

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, energy=NaniteAgent.INIT_ENERGY)
        self.energy = energy

    def step():
        pass
