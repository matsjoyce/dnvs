import cherrypy


CONFIG = {
    "/api/node": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class NodesAPI:
    def __init__(self):
        pass
