import cherrypy

from .utils import json_handler


CONFIG = {
    "/api/job": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class JobsAPI:
    def __init__(self):
        pass

    @cherrypy.tools.json_out(handler=json_handler)
    def GET(self):
        jobs, = cherrypy.engine.publish("view-jobs")
        return {
            "jobs": [job.json() for job in jobs.values()]
        }
