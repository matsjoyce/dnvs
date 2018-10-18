import cherrypy
import json
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import logging
import threading


logger = logging.getLogger(__name__)


class WebsocketHandler(WebSocket):
    def __init__(self, *args, name, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.address = None
        self.handler = None
        self.lock = threading.RLock()

    def received_message(self, message):
        logger.debug(f"[{self.name}] From {self.address}: {message.data}")
        if self.handler:
            try:
                self.handler.received_message(message)
            except Exception:
                logger.error("Exception in WS", exc_info=True)
        else:
            logger.warning("No handler in WS")

    def opened(self):
        cherrypy.engine.publish(self.name + "-connected", self)

    def closed(self, code, reason=None):
        cherrypy.engine.publish(self.name + "-disconnected", self)

    def send_json(self, data):
        with self.lock:
            logger.debug(f"[{self.name}] To {self.address}: {data}")
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
