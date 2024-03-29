from mesa.visualization.ModularVisualization import VisualizationElement
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from loan.agentfactory import AgentFactory
from loan.helperagent import HelperAgent
from loan.helpers import give_node_positions, node_positions_on_canvas
from loan.killeragent import KillerAgent


class NetworkModule(VisualizationElement):
    package_includes = ["sigma.min.js"]
    local_includes = ["loan/js/GraphNetwork.js"]

    def __init__(self, portrayal_method, canvas_height=700, canvas_width=600):

        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = f"new GraphModule({self.canvas_width}, {self.canvas_height})"
        self.js_code = f"elements.push({new_element});"

    def render(self, model):
        return self.portrayal_method(model)


def network_portrayal(model):
    new_positions = node_positions_on_canvas(give_node_positions())
    portrayal = {}
    portrayal["nodes"] = [{"id": node_id,
                           "x": new_positions.get(node_id).get("x"),
                           "y": new_positions.get(node_id).get("y"),
                           "size": 20,
                           "color": set_colour(model.cell_properties.get(node_id).get("heat_value")),
                           "label": build_label(node_id, agents)}
                          for (node_id, agents) in model.network.nodes.data("agent")]

    portrayal["edges"] = [{"id": edge_id,
                           "type": "curvedArrow",
                           "source": source,
                           "target": target,
                           "color": "#000000"}
                          for edge_id, (source, target, _) in enumerate(model.network.edges)]

    return portrayal


def build_label(vertex_id, agents):
    """Builds the emoji representation of all agents on a single vertex"""
    return f"{vertex_id}" + "".join(agent.emojify() for agent in agents)


def set_colour(heat_value):
    """"""
    if heat_value < 0.5:
        colour = "#007959"
    elif heat_value < 1.0:
        colour = "#fc7702"
    else:
        colour = "#CC0000"
    return colour


health_chart = ChartModule([{"Label": "Hitpoints", "Color": "Red"}], canvas_height=80, canvas_width=250, 
                           data_collector_name="datacollector")

helperagent_chart = ChartModule([{"Label": "Helper Agents energy", "Color": "Blue"}], canvas_height=80, canvas_width=250,
                                data_collector_name="datacollector")

tiles = [NetworkModule(network_portrayal, 400, 500), health_chart, helperagent_chart]

textvalue = """Welcome to your imperfect body!"""

model_params = {
    "how_to": UserSettableParameter("static_text", value=textvalue),
    "N": UserSettableParameter("slider", "Number of helper agents", 1, 1, 10, 1),
    "hitpoints": UserSettableParameter("slider", "Max hitpoints", 150, 1, 1000, 1),
    "max_helperagent_energy": UserSettableParameter("slider", "Max energy of agents", 100, 1, 500, 1),
    "illness_chance": UserSettableParameter("slider", "Vertex illness chance", 0.2, 0, 1, 0.05),
    "max_ill_vertices": UserSettableParameter("slider", "Max simultaneous ill vertices", 4, 0, 15, 1),
    "helper_type": UserSettableParameter("choice", "Helper Type", value="helperagent", choices=["helperagent", "greedyhelperagent"]),
}
