import wrapt

from ...log import logger
from ...sdk import sdk


def instrument():
    @wrapt.patch_function_wrapper("concurrent.futures.thread", "_WorkItem.__init__")
    def dynatrace_submit(wrapped, instance, args, kwargs):
        fn = args[1]
        if hasattr(fn, "__class__"):
            function_name, module, class_name = ("__call__", fn.__module__, fn.__class__.__name__)
        else:
            function_name, module, class_name = (fn.__name__, fn.__module__, fn.__self__.__class__.__name__)
        if class_name == "module":
            method = "{}.{}".format(module, function_name)
        else:
            method = "{}.{}".format(class_name, function_name)

        with sdk.trace_custom_service(method, "Threading"):
            logger.debug("Tracing upstream thread execution {}".format(method))
            link = sdk.create_in_process_link()
            setattr(instance, "__dynatrace_link", link)
            return wrapped(*args, **kwargs)

    @wrapt.patch_function_wrapper("concurrent.futures.thread", "_WorkItem.run")
    def dynatrace_run(wrapped, instance, args, kwargs):
        link = getattr(instance, "__dynatrace_link", None)
        if link is not None:
            logger.debug("Tracing downstream thread execution")
            with sdk.trace_in_process_link(link):
                return wrapped(*args, **kwargs)
        return wrapped(*args, **kwargs)
