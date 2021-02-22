from mesa.visualization.ModularVisualization import ModularServer
from tornado import autoreload
from tornado.ioloop import IOLoop

from model import HumanModel
from visualization import NetworkModule
from helpers import give_node_positions, node_positions_on_canvas


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
    new_positions = node_positions_on_canvas(give_node_positions())
    portrayal = {}
    portrayal["nodes"] = [{"id": node_id,
                           "x": new_positions.get(node_id).get("x"),
                           "y": new_positions.get(node_id).get("y"),
                           "size": 20,
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
    
    portrayal["energy"] = model.agents[0].energy

    return portrayal

if __name__ == "__main__":
    network = NetworkModule(network_portrayal, 600, 600)
    tiles = [network]
    model_params = {}
    server = Server(HumanModel, tiles, "Human Model", model_params)
    server.launch(port=8581)
