from pathlib import Path

from mesa.batchrunner import BatchRunner, BatchRunnerMP

from loan.helpers import graph_from_json
from loan.model import HumanModel


def run_batch(iterations=50, max_steps=100, use_mp: bool = True, network_path: str = "./loan/data/network.json"):
    graph = graph_from_json(Path(network_path))
    fixed_params = {"N": 1, "network": graph}
    variable_params = {"illness_chance": [0.1, 0.2, 0.3, 0.4]}

    runner = BatchRunnerMP if use_mp else BatchRunner

    batch_run = runner(HumanModel,
                       variable_params,
                       fixed_params,
                       iterations=iterations,  # Iterations per combination of parameters
                       max_steps=max_steps,
                       model_reporters={"Hitpoints": HumanModel.get_hitpoints,
                                        "Ill vertices": HumanModel.get_ill_vertices,
                                        "End time": HumanModel.get_end,
                                        "Vertices healed": HumanModel.get_healed_count})

    batch_run.run_all()  # Run all simulations
    # Get DataFrame with collected data
    run_data = batch_run.get_model_vars_dataframe()
    return run_data
