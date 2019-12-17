import wrapt

from ..log import logger
from ..sdk import sdk
import socket

try:

    @wrapt.patch_function_wrapper("flask_apispec", "wrapper.Wrapper.call_view")
    def call_view_dynatrace(wrapped, instance, argv, kwargs):
        with sdk.trace_custom_service(instance.func.__name__, "View"):
            logger.debug("injected method {}".format(wrapped))
            return wrapped(*argv, **kwargs)

    logger.debug("Instrumenting flask_apispec")
except ImportError:
    pass

try:
    from wsgiref.util import request_uri
    import flask

    @wrapt.patch_function_wrapper("flask", "Flask.full_dispatch_request")
    def full_dispatch_request_dynatrace(wrapped, instance, argv, kwargs):
        logger.debug("injected method {}".format(wrapped))

        try:
            env = flask.request.environ
            method = env.get("REQUEST_METHOD", "GET")
            url = env.get("REQUEST_URI", "/") or request_uri(env)
            host = env.get("SERVER_NAME") or socket.gethostname() or "localhost"
            dt_headers = dict(flask.request.headers) if env.get("DT_CAPTURE_HEADERS", False) else {}
            wappinfo = sdk.create_web_application_info(host, "Flask", "/")

        except Exception as e:
            logger.debug("dynatrace - could not instrument: {}".format(e))
            return wrapped(*argv, **kwargs)

        with sdk.trace_incoming_web_request(wappinfo, url, method, headers=dt_headers):
            logger.debug("dynatrace - full_dispatch_request_dynatrace")
            return wrapped(*argv, **kwargs)

    logger.debug("Instrumenting flask")

except ImportError:
    pass

try:

    @wrapt.patch_function_wrapper("flask_jwt_extended", "create_access_token")
    def create_access_token_dynatrace(wrapped, instance, argv, kwargs):
        logger.debug("injected method {}".format(wrapped))
        with sdk.trace_custom_service(wrapped.__name__, "flask_jwt_extended"):
            return wrapped(*argv, **kwargs)

    logger.debug("Instrumenting flask_jwt_extended")
except ImportError:
    pass

try:

    @wrapt.patch_function_wrapper("flask_bcrypt", "Bcrypt.check_password_hash")
    def check_password_hash_dynatrace(wrapped, instance, argv, kwargs):
        logger.debug("injected method {}".format(wrapped))
        with sdk.trace_custom_service(wrapped.__name__, "flask_bcrypt"):
            return wrapped(*argv, **kwargs)

    logger.debug("Instrumenting flask_bcrypt")
except ImportError:
    pass
