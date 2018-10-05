import cherrypy
import json
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket


class WebsocketHandler(WebSocket):
    def __init__(self, *args, name, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.address = None

    def received_message(self, message):
        # Overriden by relevant managers
        pass

    def opened(self):
        cherrypy.engine.publish(self.name + "-connected", self)

    def closed(self, code, reason=None):
        cherrypy.engine.publish(self.name + "-disconnected", self)

    def send_json(self, data):
        self.send(json.dumps(data))

    @classmethod
    def with_name(cls, name):
        return lambda *a, **k: cls(*a, name=name, **k)


CONFIG = {
    "/api/ws/broadcast": {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WebsocketHandler.with_name("broadcast")
    },

    "/api/ws/worker": {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WebsocketHandler.with_name("worker")
    }
}


class WebSocketAPI:
    def __init__(self):
        WebSocketPlugin(cherrypy.engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()

    @cherrypy.expose
    def broadcast(self):
        cherrypy.request.ws_handler.address = f"{cherrypy.request.remote.ip}:{cherrypy.request.remote.port}"

    @cherrypy.expose
    def worker(self):
        cherrypy.request.ws_handler.address = f"{cherrypy.request.remote.ip}:{cherrypy.request.remote.port}"
