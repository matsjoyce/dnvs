import cherrypy


CONFIG = {
    "/api/subnet": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class SubnetsAPI:
    def __init__(self):
        pass
