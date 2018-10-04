import cherrypy

from .utils import json_handler


CONFIG = {
    "/api/worker": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class WorkersAPI:
    def __init__(self):
        pass

    @cherrypy.tools.json_out(handler=json_handler)
    def GET(self):
        workers, = cherrypy.engine.publish("view-workers")
        return {
            "workers": [worker.json() for worker in workers.values()]
        }
