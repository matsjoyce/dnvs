import cherrypy

from .utils import json_handler


CONFIG = {
    "/api/plugin": {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }
}


@cherrypy.expose
class PluginsAPI:
    def __init__(self):
        pass

    @cherrypy.tools.json_out(handler=json_handler)
    def GET(self):
        plugins, = cherrypy.engine.publish("view-plugins")
        return {
            "plugins": [plugin.json() for plugin in plugins.values()]
        }

