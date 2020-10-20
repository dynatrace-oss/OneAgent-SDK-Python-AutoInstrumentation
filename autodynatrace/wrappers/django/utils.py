import os

from ...log import logger
from six.moves.urllib import parse

try:
    from django.core.urlresolvers import resolve
except ImportError:
    from django.urls import resolve


def get_host(request):
    host = None
    try:
        host = request.get_host()  # this will include host:port
    except Exception:
        logger.debug("Failed to get Django request host", exc_info=True)

    if not host:
        try:
            if "HTTP_HOST" in request.META:
                host = request.META["HTTP_HOST"]
            else:
                host = request.META["SERVER_NAME"]
                port = str(request.META["SERVER_PORT"])
                if port != ("443" if request.is_secure() else "80"):
                    host = "{0}:{1}".format(host, port)
        except Exception:
            logger.debug("Failed to build Django request host", exc_info=True)
            host = "unknown"

    return host


def get_request_uri(request):

    host = get_host(request)
    return parse.urlunparse(
        parse.ParseResult(scheme=request.scheme, netloc=host, path=request.path, params="", query="", fragment="",)
    )


def get_app_name(request):
    try:
        app_name = resolve(request.path).kwargs.get("name")
        logger.debug("Resolved app_name as '{}' from resolving the path".format(app_name))
        if app_name is None:
            app_name = "{}:{}".format(request.META.get("SERVER_NAME"), request.META.get("SERVER_PORT"))
    except Exception:
        app_name = "{}:{}".format(request.META.get("SERVER_NAME"), request.META.get("SERVER_PORT"))
        logger.debug("Could not get app name, using default: {}".format(app_name))

    return os.environ.get("AUTODYNATRACE_APPLICATION_ID", "Django ({})".format(app_name))
