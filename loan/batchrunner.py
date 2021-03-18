from mesa.batchrunner import BatchRunnerMP

from loan.model import HumanModel
from collections import OrderedDict


def run_batch(iterations=100, max_steps=100):
    fixed_params = {}

    variable_params = OrderedDict()
    variable_params["factory_location"] = tuple(range(1, 15))
    variable_params["N"] = (1, 2, 4, 8, 1)
    variable_params["helper_type"] = ("helperagent", "greedyhelperagent")

    model_reporters = {"Hitpoints": HumanModel.get_hitpoints,
                       "Ill vertices": HumanModel.get_ill_vertices,
                       "End time": HumanModel.get_end,
                       "Vertices healed": HumanModel.get_healed_count}

    batch_run = BatchRunnerMP(HumanModel,
                              nr_processes=8,
                              variable_parameters=variable_params,
                              fixed_parameters=fixed_params,
                              iterations=iterations,  # Iterations per combination of parameters
                              max_steps=max_steps,
                              model_reporters=model_reporters)

    batch_run.run_all()  # Run all simulations
    return batch_run.get_model_vars_dataframe()  # Get DataFrame with collected data
