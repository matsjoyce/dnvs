import cherrypy

from .utils import json_handler


CONFIG = {
    "/api/network": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class NetworksAPI:
    def __init__(self):
        pass

    @cherrypy.tools.json_out(handler=json_handler)
    def GET(self):
        networks, = cherrypy.engine.publish("view-networks")
        return {
            "networks": [network.json() for network in networks.values()]
        }

    @cherrypy.tools.json_out(handler=json_handler)
    @cherrypy.tools.json_in()
    def POST(self):
        net = cherrypy.request.json["network"]
        network, = cherrypy.engine.publish("network-create", net)
        return network.json()
