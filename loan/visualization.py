from mesa.visualization.ModularVisualization import VisualizationElement


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
