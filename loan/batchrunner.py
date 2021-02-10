from pathlib import Path

from mesa.batchrunner import BatchRunner, BatchRunnerMP

from helpers import graph_from_json
from model import HumanModel, get_hitpoints, get_ill_vertices


def run_batch(iterations=5, max_steps=100, use_mp: bool = True):
    graph = graph_from_json(Path("./loan/network.json"))
    fixed_params = {"N": 1, "network": graph}
    variable_params = {"illness_chance": [0.1, 0.2, 0.3, 0.4]
    }

    runner = BatchRunnerMP if use_mp else BatchRunner

    batch_run = runner(
        HumanModel,
        variable_params,
        fixed_params,
        iterations=iterations,  # Iterations per combination of parameters
        max_steps=max_steps,
        model_reporters={"Hitpoints": get_hitpoints, "Ill vertices": get_ill_vertices}
        )

    batch_run.run_all()  # Run all simulations
    run_data = batch_run.get_model_vars_dataframe()  # Get DataFrame with collected data
    return run_data


if __name__ == "__main__":
    df = run_batch(use_mp=False)
    print(df)
