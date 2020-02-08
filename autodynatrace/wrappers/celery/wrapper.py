from celery import signals
from celery import registry

from ...log import logger
from ...sdk import sdk

DT_KEY = "__dynatrace_tag"


def instrument():
    def get_task_id(context):
        headers = context.get("headers")
        body = context.get("body")
        if headers:
            return headers.get("id")
        else:
            return body.get("id")

    def add_tracer(task, task_id, tracer):
        tracer_dict = getattr(task, DT_KEY, None)
        if tracer_dict is None:
            tracer_dict = dict()
            setattr(task, DT_KEY, tracer_dict)

        tracer_dict[task_id] = tracer

    def get_tracer(task, task_id):
        tracer_dict = getattr(task, DT_KEY, None)
        if tracer_dict is not None:
            return tracer_dict.get(task_id, None)

    def remove_tracer(task, task_id):
        tracer_dict = getattr(task, DT_KEY, None)
        if tracer_dict is not None:
            tracer_dict.pop(task_id, None)

    def dt_before_task_publish(**kwargs):
        task_name = kwargs.get("sender")
        task = registry.tasks.get(task_name)
        task_id = get_task_id(kwargs)

        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        tracer = sdk.trace_custom_service("publish({})".format(task_name), "Celery")
        tracer.start()
        add_tracer(task, task_id, tracer)

    def dt_after_task_publish(**kwargs):
        logger.debug("Caceta")
        task_name = kwargs.get("sender")
        task = registry.tasks.get(task_name)
        task_id = get_task_id(kwargs)

        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        tracer = get_tracer(task, task_id)
        if tracer is not None:
            tracer.end()
            remove_tracer(task, task_id)

    def dt_task_prerun(*args, **kwargs):
        task = kwargs.get("sender")
        task_id = kwargs.get("task_id")
        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        tracer = sdk.trace_custom_service("run({})".format(task.name), "Celery worker")
        tracer.start()
        add_tracer(task, task_id, tracer)

    def dt_task_postrun(*args, **kwargs):
        task = kwargs.get("sender")
        task_id = kwargs.get("task_id")

        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        tracer = get_tracer(task, task_id)
        if tracer is not None:
            tracer.end()
            remove_tracer(task, task_id)

    signals.task_prerun.connect(dt_task_prerun, weak=False)
    signals.task_postrun.connect(dt_task_postrun, weak=False)
    signals.after_task_publish.connect(dt_after_task_publish, weak=False)
    signals.before_task_publish.connect(dt_before_task_publish, weak=False)
