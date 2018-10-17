import cherrypy
import json


def json_handler(*args, **kwargs):
    try:
        value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    except cherrypy.HTTPError as e:
        raise e
    else:
        return json.dumps({
            "data": value,
            "status": cherrypy.response.status or 200
        }).encode()
