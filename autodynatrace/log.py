import logging

logger = logging.getLogger("autodynatrace")


def init(level=logging.INFO):
    ch = logging.StreamHandler()
    f = logging.Formatter(
        "%(asctime)s: %(process)d %(levelname)s %(name)s - %(funcName)s: %(message)s"
    )
    ch.setFormatter(f)
    logger.addHandler(ch)
    logger.setLevel(level)
