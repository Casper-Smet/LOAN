from mesa.visualization.ModularVisualization import ModularServer
from tornado import autoreload
from tornado.ioloop import IOLoop

from model import HumanModel
from visualization import NetworkModule


class Server(ModularServer):
    def launch(self, port=None):
        if port is not None:
            self.port = port

        url = f"http://127.0.0.1:{self.port}"
        print(f"Interface starting at {url}")
        self.listen(self.port)
        autoreload.start()
        IOLoop.current().start()


def network_portrayal(model):
    # print(network.nodes.data("agent"))
    # print(network.edges)

    agent_pos = model.agents[0].pos
    portrayal = {}
    portrayal["nodes"] = [{"id": node_id,
                           "x": 10,
                           "size": 10,
                           "color": "#007959" if node_id in model.ill_vertices else "#CC0000",
                           "label": f"{node_id} - 🕵️" if node_id == agent_pos else f"{node_id}"
                           }
                          for (node_id, agents) in model.network.nodes.data("agent")]

    portrayal["edges"] = [{"id": edge_id,
                           "type": 'curve',
                           "source": source,
                           "target": target,
                           "color": "#000000"}
                          for edge_id, (source, target, _) in enumerate(model.network.edges)]

    return portrayal

if __name__ == "__main__":
    js_engine = "sigma"
    network = NetworkModule(network_portrayal, 600, 600, library=js_engine)
    tiles = [network]
    model_params = {}
    server = Server(HumanModel, tiles, "Human Model", model_params)
    server.launch(port=8583)
