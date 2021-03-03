from mesa.visualization.ModularVisualization import VisualizationElement

from loan.helpers import give_node_positions, node_positions_on_canvas


class NetworkModule(VisualizationElement):
    package_includes = ["sigma.min.js"]
    local_includes = ["loan/js/GraphNetwork.js"]

    def __init__(self, portrayal_method, canvas_height=600, canvas_width=600):

        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = f"new GraphModule({self.canvas_width}, {self.canvas_height})"
        self.js_code = f"elements.push({new_element});"

    def render(self, model):
        return self.portrayal_method(model)


def network_portrayal(model):
    # print(network.nodes.data("agent"))
    # print(network.edges)

    agent_pos = model.agents[0].pos
    new_positions = node_positions_on_canvas(give_node_positions())
    portrayal = {}
    portrayal["nodes"] = [{"id": node_id,
                           "x": new_positions.get(node_id).get("x"),
                           "y": new_positions.get(node_id).get("y"),
                           "size": 20,
                           "color": "#007959" if node_id in model.ill_vertices else "#CC0000",
                           "label": f"{node_id} - 🕵️" if node_id == agent_pos else f"{node_id}"}
                          for (node_id, _) in model.network.nodes.data("agent")]

    portrayal["edges"] = [{"id": edge_id,
                           "type": "curve",
                           "source": source,
                           "target": target,
                           "color": "#000000"}
                          for edge_id, (source, target, _) in enumerate(model.network.edges)]

    portrayal["energy"] = model.agents[0].energy

    return portrayal


tiles = [NetworkModule(network_portrayal, 600, 600)]
model_params = {}
