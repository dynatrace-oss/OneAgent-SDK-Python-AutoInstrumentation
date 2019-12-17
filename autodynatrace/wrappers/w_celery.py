from ..log import logger
from ..sdk import sdk

DT_KEY = "__dynatrace_tag"

try:
    import celery
    import wrapt
    from celery.signals import (
        before_task_publish,
        after_task_publish,
        task_prerun,
        task_failure,
        task_success,
        task_postrun,
    )

    from celery import registry

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

    @before_task_publish.connect
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

    @after_task_publish.connect
    def dt_after_task_publish(**kwargs):
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

    @task_prerun.connect
    def dt_task_prerun(*args, **kwargs):
        task = kwargs.get("sender")
        task_id = kwargs.get("task_id")
        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        tracer = sdk.trace_custom_service("run({})".format(task.name), "Celery worker")
        tracer.start()
        add_tracer(task, task_id, tracer)

    @task_postrun.connect
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

    logger.debug("Instrumenting celery")
except ImportError:
    pass
