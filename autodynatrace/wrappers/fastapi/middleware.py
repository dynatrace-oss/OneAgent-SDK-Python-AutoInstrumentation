import os

from ...log import logger
from ...sdk import sdk


class DynatraceASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # If this is not an http request, do nothing and return
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_headers = scope.get("headers", [])
        headers = {}
        for key, value in request_headers:
            key = key.decode() if isinstance(key, bytes) else key
            value = value.decode() if isinstance(value, bytes) else value
            headers[key.lower()] = value

        dt_tag = headers.get("x-dynatrace")

        host = ""
        # scope["server"] is optional, if missing, it defaults to None.
        # https://asgi.readthedocs.io/en/latest/specs/www.html
        if scope.get("server") and scope["server"][1]:
            # [host, port]
            host = f"{scope['server'][0]}:{scope['server'][1]}"
        elif scope.get("server"):
            # [path, None]
            host = f"{scope['server'][0]}"

        url = f"{scope['scheme']}://{host}{scope['path']}?{scope['query_string'].decode()}"
        method = scope.get("method", "GET")
        app = scope.get("app")
        app_name = app.title if app is not None else "FastAPI"
        root = scope.get("root_path", "/")

        virtual_host = os.environ.get("AUTODYNATRACE_VIRTUAL_HOST", f"{host}")
        app_name = os.environ.get("AUTODYNATRACE_APPLICATION_ID", f"{app_name}")
        context_root = os.environ.get("AUTODYNATRACE_CONTEXT_ROOT", root or "/")

        with sdk.create_web_application_info(virtual_host, app_name, context_root) as web_app_info:
            with sdk.trace_incoming_web_request(
                web_app_info, url, method, headers=headers, str_tag=dt_tag,
            ) as tracer:
                logger.debug(f"dynatrace - asgi - Tracing url: '{url}' with tag {dt_tag}")

                async def wrapped_send(message):
                    if message.get("type") == "http.response.start" and "status" in message:
                        tracer.set_status_code(message["status"])

                    if "headers" in message:
                        response_headers = {}
                        for k, v in message["headers"]:
                            k = k.decode() if isinstance(k, bytes) else k
                            v = v.decode() if isinstance(v, bytes) else v
                            response_headers[k.lower()] = v

                        tracer.add_response_headers(response_headers)

                    return await send(message)

                return await self.app(scope, receive, wrapped_send)
