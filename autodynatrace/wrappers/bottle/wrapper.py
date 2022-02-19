from ...log import logger
from ...sdk import sdk

import os


from bottle import hook, request, response


def instrument():
    @hook("before_request")
    def instrument_before_request():
        try:
            # extract host and port from the request
            host = request.environ.get("HTTP_HOST", "unknown")
            app_name = "{}".format(host)

            virtual_host = os.environ.get("AUTODYNATRACE_VIRTUAL_HOST", "{}".format(host))
            app_name = os.environ.get("AUTODYNATRACE_APPLICATION_ID", "Bottle ({})".format(app_name))
            context_root = os.environ.get("AUTODYNATRACE_CONTEXT_ROOT", "/")

            # Create the oneagent web app
            web_app_info = sdk.create_web_application_info(virtual_host, app_name, context_root)

            with web_app_info:
                # Attempt to extract the x-dynatrace header from the request
                dynatrace_header = request.headers.get("x-dynatrace")
                logger.debug("Bottle - tracing incoming request ({}) with header: {}".format(request.url, dynatrace_header))
                tracer = sdk.trace_incoming_web_request(web_app_info, request.url, request.method, headers=request.headers, str_tag=dynatrace_header)
                tracer.start()
                setattr(request, "__dynatrace_tracer", tracer)
        except Exception as e:
            logger.warning("Bottle - failed to instrument request: {}".format(e))

    @hook("after_request")
    def instrument_after_request():
        try:
            # check if the request was instrumented
            tracer = getattr(request, "__dynatrace_tracer", None)
            if tracer:
                tracer.set_status_code(response.status_code)
                tracer.add_response_headers(response.headers)
                logger.debug("Bottle - ending incoming request ({}) with status: {}".format(request.url, response.status_code))
                tracer.end()
        except Exception as e:
            logger.warning("Bottle - failed to instrument response: {}".format(e))
