from ...log import logger
from six.moves.urllib import parse


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
