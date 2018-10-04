import cherrypy
import pathlib

from .api import API, CONFIG as API_CONFIG
from .managers import Manager


STATIC_DIR = pathlib.Path(__file__).parent.parent / "ui"

CONFIG = {
    "/static": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": STATIC_DIR
    }
}
CONFIG.update(API_CONFIG)


class Root:
    def __init__(self):
        self.api = API()

    @cherrypy.expose
    def index(self):
        return (STATIC_DIR / "main.html").open()


def run(address, port):
    cherrypy.config.update({
        "server.socket_host": address,
        "server.socket_port": port,
        "log.screen": False,
        "log.access_file": "",
        "log.error_file": ""
    })
    Manager.register_managers(cherrypy.engine)
    cherrypy.quickstart(Root(), "/", config=CONFIG)
