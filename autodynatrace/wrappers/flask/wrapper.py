import flask
from wsgiref.util import request_uri
import wrapt

from ...log import logger
from ...sdk import sdk
import socket
import os


def instrument():
    @wrapt.patch_function_wrapper("flask", "Flask.full_dispatch_request")
    def full_dispatch_request_dynatrace(wrapped, instance, args, kwargs):
        try:
            env = flask.request.environ
            method = env.get("REQUEST_METHOD", "GET")
            url = env.get("REQUEST_URI") or env.get("RAW_URI") or env.get("werkzeug.request").url or request_uri(env)
            host = env.get("SERVER_NAME") or socket.gethostname() or "localhost"
            app_name = flask.current_app.name

            dt_headers = None
            dt_header = flask.request.headers.get("X-Dynatrace")
            if os.environ.get("AUTODYNATRACE_CAPTURE_HEADERS", False):
                dt_headers = dict(flask.request.headers)

            virtual_host = os.environ.get("AUTODYNATRACE_VIRTUAL_HOST", "{}".format(host))
            app_name = os.environ.get("AUTODYNATRACE_APPLICATION_ID", "Flask ({})".format(app_name))
            context_root = os.environ.get("AUTODYNATRACE_CONTEXT_ROOT", "/")

            wappinfo = sdk.create_web_application_info(virtual_host, app_name, context_root)

        except Exception as e:
            logger.debug("dynatrace - could not instrument: {}".format(e))
            return wrapped(*args, **kwargs)

        try:
            with wappinfo:
                logger.debug("Tracing with header: {}".format(dt_header))
                with sdk.trace_incoming_web_request(wappinfo, url, method, headers=dt_headers, str_tag=dt_header):
                    logger.debug("dynatrace - full_dispatch_request_dynatrace: {}".format(url))
                    return wrapped(*args, **kwargs)
        except Exception as e:
            logger.debug("dynatrace - could not create tracer: {}".format(e))
            return wrapped(*args, **kwargs)
