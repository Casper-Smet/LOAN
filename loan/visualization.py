from mesa.visualization.ModularVisualization import VisualizationElement


class NetworkModule(VisualizationElement):
    package_includes = []

    def __init__(self, portrayal_method, canvas_height=500, canvas_width=500, library="sigma"):
        library_types = ["sigma", "d3"]
        if library not in library_types:
            raise ValueError(f"Invalid javascript library type. Expected one of: {library_types}")

        NetworkModule.package_includes = (["NetworkModule_sigma.js", "sigma.min.js"]
                                          if library == "sigma"
                                          else ["NetworkModule_d3.js", "d3.min.js"])

        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = f"new NetworkModule({self.canvas_width}, {self.canvas_height})"
        self.js_code = f"elements.push({new_element});"

    def render(self, model):
        return self.portrayal_method(model.network)
