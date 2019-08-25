import wrapt

from ..log import logger
from ..sdk import sdk


try:
    import urllib3


    @wrapt.patch_function_wrapper('urllib3', 'HTTPConnectionPool.urlopen')
    def urlopen_dynatrace(wrapped, instance: urllib3.connectionpool.HTTPConnectionPool, args, kwargs):

        try:
            host = instance.host
            port = instance.port
            headers = instance.headers

            if args is not None and len(args) == 2:
                method = args[0]
                path = args[1]
            else:
                method = kwargs.get('method', 'GET')
                path = kwargs.get('path', None)
                if path is None:
                    path = kwargs.get('url', None)

            protocol = 'http' if type(instance) is urllib3.connectionpool.HTTPConnectionPool else 'https'
            url = f'{protocol}://{host}:{port}{path}'

            with sdk.trace_outgoing_web_request(url, method, headers=headers) as tracer:
                dynatrace_tag = tracer.outgoing_dynatrace_string_tag
                headers = kwargs.get('headers')
                if headers is not None:
                    headers['x-dynatrace'] = dynatrace_tag
                    kwargs['headers'] = headers
                logger.debug(f'Tracing urllib3. URL: "{url}", x-dynatrace: {dynatrace_tag}')
                rv = wrapped(*args, **kwargs)
                tracer.set_status_code(rv.status)
                return rv

        except Exception as e:
            logger.debug(f'Could not instrument urllib3: {e}')
            return wrapped(*args, **kwargs)

    logger.debug('Instrumenting urllib3')

except ImportError:
    pass
