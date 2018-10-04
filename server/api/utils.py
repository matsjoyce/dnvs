import cherrypy
import json


def json_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return json.dumps({
        "data": value
    }).encode()
