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
            "workers": [{
                "id": worker.id,
                "address": worker.address,
                "state": worker.state.name,
                "current_job": worker.current_job.id if worker.current_job else None
            } for worker in workers.values()]
        }
