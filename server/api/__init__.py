import cherrypy

from .ws import WebSocketAPI, CONFIG as WS_CONFIG
from .nodes import NodesAPI, CONFIG as NODES_CONFIG
from .networks import NetworksAPI, CONFIG as NETWORKS_CONFIG
from .jobs import JobsAPI, CONFIG as JOBS_CONFIG
from .workers import WorkersAPI, CONFIG as WORKERS_CONFIG
from .plugins import PluginsAPI, CONFIG as PLUGINS_CONFIG


CONFIG = {}
CONFIG.update(WS_CONFIG)
CONFIG.update(NODES_CONFIG)
CONFIG.update(NETWORKS_CONFIG)
CONFIG.update(JOBS_CONFIG)
CONFIG.update(WORKERS_CONFIG)
CONFIG.update(PLUGINS_CONFIG)


@cherrypy.expose
class API:
    def __init__(self):
        self.ws = WebSocketAPI()
        self.node = NodesAPI()
        self.network = NetworksAPI()
        self.job = JobsAPI()
        self.worker = WorkersAPI()
        self.plugin = PluginsAPI()
