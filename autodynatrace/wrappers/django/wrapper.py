import django
import wrapt

from ...log import logger
from ...sdk import sdk

from .middlewares import insert_dynatrace_middleware
from .db import instrument_db


def instrument():
    @wrapt.patch_function_wrapper("django", "setup")
    def dynatrace_setup(wrapped, instance, args, kwargs):
        from django.conf import settings

        if "autodynatrace.wrappers.django" not in settings.INSTALLED_APPS:
            if isinstance(settings.INSTALLED_APPS, tuple):

                settings.INSTALLED_APPS = settings.INSTALLED_APPS + ("autodynatrace.wrappers.django",)
            else:
                settings.INSTALLED_APPS.append("autodynatrace.wrappers.django")

            logger.debug("Added autodynatrace to settings.INSTALLED_APPS")
        wrapped(*args, **kwargs)


def instrument_django():
    insert_dynatrace_middleware()
    instrument_db()
