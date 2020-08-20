import importlib
import logging
import threading
import os
import sys

from wrapt.importer import when_imported

from .log import init as log_init, logger
from .sdk import init as sdk_init

__version__ = 1.063

os.environ["DT_CUSTOM_PROP"] = "Autodynatrace={}".format(__version__)

log_level_name = os.environ.get("AUTODYNATRACE_LOG_LEVEL", "WARNING")
log_init(logging.getLevelName(log_level_name))

forkable = os.environ.get("AUTODYNATRACE_FORKABLE", "False").strip().lower() in ("true", "1")
sdk_init(forkable=forkable)

from .wrappers.custom import dynatrace_custom_tracer as trace

_LOCK = threading.Lock()
_INSTRUMENTED_LIBS = set()
_INSTRUMENT_LIBS_LAZY = set()

INSTRUMENT_LIBS = {
    "flask": True,
    "urllib3": True,
    "celery": True,
    "pymongo": True,
    "sqlalchemy": True,
    "django": True,
    "redis": True,
    "pika": True,
    "cx_Oracle": True,
    "grpc": True,
    "ruxit": True,
    "confluent_kafka": True,
    "pysnmp": True,
    "concurrent": True,
    "urllib": True,
    "suds": True,
    "subprocess": True,
    "paramiko": True,
}


def load(_):
    pass


def instrument_all(**instrument_libs):
    libs = INSTRUMENT_LIBS.copy()
    libs.update(instrument_libs)
    instrument(**libs)


def _on_import_wrapper(lib):
    def on_import(hook):

        path = "autodynatrace.wrappers.%s" % lib
        try:
            logger.debug("Instrumenting imported lib '{}'".format(lib))
            imported_module = importlib.import_module(path)
            imported_module.instrument()
        except Exception:
            logger.debug("Could not instrument {}".format(lib), exc_info=True)

    return on_import


def instrument(**instrument_libs):

    libs = [l for (l, will_instrument) in instrument_libs.items() if will_instrument]
    for lib in libs:

        if lib in sys.modules:
            instrument_lib(lib)
            _INSTRUMENTED_LIBS.add(lib)

        else:
            when_imported(lib)(_on_import_wrapper(lib))
            _INSTRUMENT_LIBS_LAZY.add(lib)

    patched_libs = get_already_instrumented()
    lazy_libs = get_will_instrument()
    logger.info(
        "Instrumented {}/{} libraries ({}). Will instrument when imported: ({})".format(
            len(patched_libs), len(libs), ", ".join(patched_libs), ", ".join(lazy_libs)
        )
    )


def instrument_lib(lib):
    try:
        logger.debug("Attempting to instrument %s", lib)
        return _instrument_lib(lib)
    except Exception:
        logger.debug("Failed to instrument %s", lib, exc_info=True)
        return False


def _instrument_lib(lib):

    path = "autodynatrace.wrappers.%s" % lib
    with _LOCK:
        if lib in _INSTRUMENTED_LIBS and lib:
            logger.debug("Skipping (already instrumented): {}".format(path))
            return False

        imported_module = importlib.import_module(path)
        imported_module.instrument()
        _INSTRUMENTED_LIBS.add(lib)
        return True


def get_already_instrumented():
    with _LOCK:
        return sorted(_INSTRUMENTED_LIBS)


def get_will_instrument():
    with _LOCK:
        return sorted(_INSTRUMENT_LIBS_LAZY)


instrument_all()
