import logging

from .sdk import init as sdk_init
from .log import init as log_init

sdk_init()
log_init(logging.DEBUG)

from .wrappers import flask, sqlalchemy