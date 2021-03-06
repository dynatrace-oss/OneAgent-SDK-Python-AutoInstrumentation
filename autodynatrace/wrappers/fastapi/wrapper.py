import fastapi
from fastapi.middleware import Middleware
from .middleware import DynatraceASGIMiddleware
import wrapt


def instrument():
    @wrapt.patch_function_wrapper("fastapi.applications", "FastAPI.__init__")
    def init_dynatrace(wrapped, instance, args, kwargs):
        middlewares = kwargs.pop("middleware", [])
        middlewares.insert(0, Middleware(DynatraceASGIMiddleware))
        kwargs.update({"middleware": middlewares})
        return wrapped(*args, **kwargs)
