import wrapt

from ...log import logger
from ...sdk import sdk

import grpc


def instrument():
    def instrument_grpc_callable(wrapped, instance, args, kwargs):
        try:
            target = instance._channel.target()
            method = instance._method

            if isinstance(method, bytes):
                method = method.decode("utf-8")

            if isinstance(target, bytes):
                target = target.decode("utf-8")

            url = f"grpc://{target}{method}"

        except Exception as e:
            logger.debug("Could not instrument grpc call, error: '{}'", e)
            return wrapped(*args, **kwargs)

        with sdk.trace_outgoing_web_request(url, "POST") as tracer:
            logger.debug("Tracing GRPC, url: '{}'".format(url))
            ret = wrapped(*args, **kwargs)
            try:
                rpc_state = ret[0]
                sdk.add_custom_request_attribute("Status code", "{}".format(rpc_state.code))
                if rpc_state.code == grpc.StatusCode.OK:
                    tracer.set_status_code(200)
                else:
                    tracer.set_status_code(500)
            finally:
                return ret

    @wrapt.patch_function_wrapper("grpc._channel", "_UnaryUnaryMultiCallable._blocking")
    def unary_call_dynatrace(wrapped, instance, args, kwargs):
        return instrument_grpc_callable(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("grpc._channel", "_UnaryStreamMultiCallable.__call__")
    def unary_stream_call_dynatrace(wrapped, instance, args, kwargs):
        return instrument_grpc_callable(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("grpc._channel", "_SingleThreadedUnaryStreamMultiCallable.__call__")
    def single_unary_call_dynatrace(wrapped, instance, args, kwargs):
        return instrument_grpc_callable(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("grpc._channel", "_StreamUnaryMultiCallable._blocking")
    def stream_unary_blocking_dynatrace(wrapped, instance, args, kwargs):
        return instrument_grpc_callable(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("grpc._channel", "_StreamStreamMultiCallable.__call__")
    def stream_call_dynatrace(wrapped, instance, args, kwargs):
        return instrument_grpc_callable(wrapped, instance, args, kwargs)
