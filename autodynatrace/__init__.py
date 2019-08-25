import logging
import time

start = time.time()


from .log import init as log_init, logger
from .sdk import sdk

log_init(logging.DEBUG)

from .wrappers import flask, sqlalchemy, urllib3
logger.debug(f'autdynatrace initialization took {time.time() - start:.2f}s')
