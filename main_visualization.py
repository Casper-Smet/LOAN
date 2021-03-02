from mesa.visualization.ModularVisualization import ModularServer
from tornado import autoreload
from tornado.ioloop import IOLoop

from loan.model import HumanModel
from loan.visualization import tiles, model_params


class Server(ModularServer):
    def launch(self, port=None):
        if port is not None:
            self.port = port

        url = f"http://127.0.0.1:{self.port}"
        print(f"Interface starting at {url}")
        self.listen(self.port)
        autoreload.start()
        IOLoop.current().start()

server = Server(HumanModel, tiles, "Human Model", model_params)
server.launch(port=8581)