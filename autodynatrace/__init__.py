import logging
import time

start = time.time()


from .log import init as log_init, logger
from .sdk import init as sdk_init

sdk_init()
log_init(logging.DEBUG)

from .wrappers import w_flask, w_sqlalchemy, w_urllib3, w_celery, w_custom, w_pymongo

dynatrace_custom_tracer = w_custom.dynatrace_custom_tracer
logger.debug("autodynatrace initialization took {:.2f}s".format(time.time() - start))
