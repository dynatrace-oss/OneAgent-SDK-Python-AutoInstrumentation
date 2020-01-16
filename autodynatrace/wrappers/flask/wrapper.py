import flask
from wsgiref.util import request_uri
import wrapt

from ...log import logger
from ...sdk import sdk
import socket


def instrument():
    @wrapt.patch_function_wrapper("flask", "Flask.full_dispatch_request")
    def full_dispatch_request_dynatrace(wrapped, instance, argv, kwargs):
        try:
            env = flask.request.environ
            method = env.get("REQUEST_METHOD", "GET")
            url = env.get("werkzeug.request").url or env.get("REQUEST_URI", "/") or request_uri(env)
            host = env.get("SERVER_NAME") or socket.gethostname() or "localhost"
            port = env.get("SERVER_PORT", 80)
            dt_headers = dict(flask.request.headers)
            wappinfo = sdk.create_web_application_info("{}:{}".format(host, port), "Flask", "/")

        except Exception as e:
            logger.debug("dynatrace - could not instrument: {}".format(e))
            return wrapped(*argv, **kwargs)

        with sdk.trace_incoming_web_request(wappinfo, url, method, headers=dt_headers):
            logger.debug("dynatrace - full_dispatch_request_dynatrace: {}".format(url))
            return wrapped(*argv, **kwargs)
