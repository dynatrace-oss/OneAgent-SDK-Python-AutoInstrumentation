from django.apps import AppConfig, apps
from ...log import logger
from .wrapper import instrument_django


class DynatraceConfig(AppConfig):
    name = "autodynatrace.wrappers.django"
    label = "dynatrace_django"

    def ready(self):
        instrument_django()
