import cherrypy


CONFIG = {
    "/api/job": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class JobsAPI:
    def __init__(self):
        pass
