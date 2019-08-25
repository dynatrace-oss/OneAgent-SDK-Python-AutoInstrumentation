import wrapt

from ..log import logger
from ..sdk import sdk

try:
    @wrapt.patch_function_wrapper('flask_apispec', 'wrapper.Wrapper.call_view')
    def call_view_dynatrace(wrapped, instance, argv, kwargs):
        with sdk.trace_custom_service(instance.func.__name__, 'View'):
            logger.debug(f'injected method {wrapped}')
            return wrapped(*argv, **kwargs)

    logger.debug('Instrumenting flask_apispec')
except ImportError:
    pass

try:
    import flask

    @wrapt.patch_function_wrapper('flask', 'Flask.full_dispatch_request')
    def full_dispatch_request_dynatrace(wrapped, instance, argv, kwargs):
        logger.debug(f'injected method {wrapped}')

        try:
            env = flask.request.environ
            method = env.get('REQUEST_METHOD', 'GET')
            url = env.get('REQUEST_URI', '/')
            host = env.get('HTTP_HOST', 'localhost')
            headers = flask.request.headers
            dt_headers = {}
            dt_correlation_header = None
            for header in headers:
                dt_headers[header[0]] = header[1]
                if header[0].lower() == 'x-dynatrace':
                    dt_correlation_header = header[1]

                    logger.debug(f'Got correlation header: {dt_correlation_header}')

            logger.info(dt_headers)
            wappinfo = sdk.create_web_application_info(host, 'Flask', '/')

        except Exception as e:
            logger.debug(f'dynatrace - could not instrument: {e}')
            return wrapped(*argv, **kwargs)

        with sdk.trace_incoming_web_request(wappinfo, url, method, headers=dt_headers, str_tag=dt_correlation_header):
            logger.debug(f'dynatrace - full_dispatch_request_dynatrace')
            return wrapped(*argv, **kwargs)

    logger.debug('Instrumenting flask')

except ImportError:
    pass

try:

    @wrapt.patch_function_wrapper('flask_jwt_extended', 'create_access_token')
    def create_access_token_dynatrace(wrapped, instance, argv, kwargs):
        logger.debug(f'injected method {wrapped}')
        with sdk.trace_custom_service(wrapped.__name__, 'flask_jwt_extended'):
            return wrapped(*argv, **kwargs)


    logger.debug('Instrumenting flask_jwt_extended')
except ImportError:
    pass

try:
    @wrapt.patch_function_wrapper('flask_bcrypt', 'Bcrypt.check_password_hash')
    def check_password_hash_dynatrace(wrapped, instance, argv, kwargs):
        logger.debug(f'injected method {wrapped}')
        with sdk.trace_custom_service(wrapped.__name__, 'flask_bcrypt'):
            return wrapped(*argv, **kwargs)


    logger.debug('Instrumenting flask_bcrypt')
except ImportError:
    pass
