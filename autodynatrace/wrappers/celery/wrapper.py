import sys

from celery import signals
from celery import registry

from ...log import logger
from ...sdk import sdk, shutdown, init
import oneagent


DT_KEY = "__dynatrace_tag"

CELERY_WORKER_PROCESS = sys.argv and sys.argv[0].endswith("celery") and "worker" in sys.argv

if CELERY_WORKER_PROCESS:
    logger.debug("It looks like we are initializing Celery workers, reinitializing with forkable=True")
    shutdown()
    init(forkable=True)


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

    def dt_after_task_publish(**kwargs):
        # This is executed on the app side, after a task has been sent to Celery
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

    def dt_before_task_publish(**kwargs):
        # This is executed on the app side, before a task has been sent to Celery
        task_name = kwargs.get("sender")
        task = registry.tasks.get(task_name)
        task_id = get_task_id(kwargs)

        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        msi_handle = sdk.create_messaging_system_info(
            "Celery",
            kwargs.get("routing_key", "celery"),
            oneagent.common.MessagingDestinationType.QUEUE,
            oneagent.sdk.Channel(oneagent.sdk.ChannelType.OTHER, "celery"),
        )

        with msi_handle:
            tracer = sdk.trace_outgoing_message(msi_handle)
            tracer.start()
            tag: str = tracer.outgoing_dynatrace_string_tag.decode("utf-8")
            logger.debug("Celery - inserting tag {}".format(tag))
            kwargs["headers"][DT_KEY] = tag
            add_tracer(task, task_id, tracer)

    def dt_task_prerun(*args, **kwargs):
        # This is executed on the worker, before a task is run
        task = kwargs.get("sender")
        task_id = kwargs.get("task_id")
        if task is None or task_id is None:
            logger.debug("Could not obtain task or task_id")
            return

        msi_handle = sdk.create_messaging_system_info(
            "Celery",
            task.request.delivery_info.get("routing_key", "celery"),
            oneagent.common.MessagingDestinationType.QUEUE,
            oneagent.sdk.Channel(oneagent.sdk.ChannelType.OTHER),
        )

        with msi_handle:
            with sdk.trace_incoming_message_receive(msi_handle):
                tag = getattr(task.request, DT_KEY, "")
                logger.debug("Celery - received tag: {}".format(tag))
                tracer = sdk.trace_incoming_message_process(msi_handle, str_tag=tag)
                tracer.start()
                add_tracer(task, task_id, tracer)

    def dt_task_postrun(*args, **kwargs):
        # This is executed on the worker, after a task is run
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
