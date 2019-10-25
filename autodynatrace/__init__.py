import logging
import time

start = time.time()


from .log import init as log_init, logger
from .sdk import init as sdk_init

sdk_init()
log_init(logging.INFO)

from .wrappers import flask, sqlalchemy, urllib3, custom, pymongo, celery

dynatrace_custom_tracer = custom.dynatrace_custom_tracer
logger.debug(f"autodynatrace initialization took {time.time() - start:.2f}s")
