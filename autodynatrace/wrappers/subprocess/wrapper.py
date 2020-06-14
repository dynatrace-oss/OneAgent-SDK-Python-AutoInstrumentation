import six
import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    def dynatrace_trace(wrapped, instance, args, kwargs):
        method = wrapped.__name__
        with sdk.trace_custom_service(method, "Subprocess"):
            logger.debug("Tracing subprocess.{}".format(method))
            sdk.add_custom_request_attribute("args", str(args))
            return wrapped(*args, **kwargs)

    if six.PY3:

        @wrapt.patch_function_wrapper("subprocess", "run")
        def dynatrace_run(wrapped, instance, args, kwargs):
            return dynatrace_trace(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("subprocess", "call")
    def dynatrace_call(wrapped, instance, args, kwargs):
        return dynatrace_trace(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("subprocess", "check_call")
    def dynatrace_check_call(wrapped, instance, args, kwargs):
        return dynatrace_trace(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("subprocess", "check_output")
    def dynatrace_check_output(wrapped, instance, args, kwargs):
        return dynatrace_trace(wrapped, instance, args, kwargs)

    @wrapt.patch_function_wrapper("subprocess", "Popen")
    def dynatrace_run(wrapped, instance, args, kwargs):
        return dynatrace_trace(wrapped, instance, args, kwargs)
