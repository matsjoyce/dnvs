import cherrypy

from .ws import WebSocketAPI, CONFIG as WS_CONFIG
from .nodes import NodesAPI, CONFIG as NODES_CONFIG
from .subnets import SubnetsAPI, CONFIG as SUBNETS_CONFIG
from .jobs import JobsAPI, CONFIG as JOBS_CONFIG
from .workers import WorkersAPI, CONFIG as WORKERS_CONFIG


CONFIG = {}
CONFIG.update(WS_CONFIG)
CONFIG.update(NODES_CONFIG)
CONFIG.update(SUBNETS_CONFIG)
CONFIG.update(JOBS_CONFIG)
CONFIG.update(WORKERS_CONFIG)


@cherrypy.expose
class API:
    def __init__(self):
        self.ws = WebSocketAPI()
        self.node = NodesAPI()
        self.subnet = SubnetsAPI()
        self.job = JobsAPI()
        self.worker = WorkersAPI()
