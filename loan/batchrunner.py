from pathlib import Path

from mesa.batchrunner import BatchRunner

from loan.helpers import graph_from_json
from loan.model import HumanModel
from collections import OrderedDict

def run_batch(iterations=1_0_0, max_steps=1_0_0, network_path: str = "./loan/data/network.json"):
    graph = graph_from_json(Path(network_path))
    fixed_params = {}#{"network": graph}
    variable_params = OrderedDict({"factory_location": tuple(range(1, 15)),
                                   "N": (1, 2, 4, 8, 10),
                                   "helper_type": ("helperagent", "greedyhelperagent")})

    batch_run = BatchRunner(HumanModel,
                            variable_parameters=variable_params,
                            fixed_parameters=fixed_params,
                            iterations=iterations,  # Iterations per combination of parameters
                            max_steps=max_steps,
                            model_reporters={"Hitpoints": HumanModel.get_hitpoints,
                                             "Ill vertices": HumanModel.get_ill_vertices,
                                             "End time": HumanModel.get_end,
                                             "Vertices healed": HumanModel.get_healed_count})

    batch_run.run_all()  # Run all simulations
    run_data = batch_run.get_model_vars_dataframe()  # Get DataFrame with collected data
    return run_data
