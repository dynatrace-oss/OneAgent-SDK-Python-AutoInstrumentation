import oneagent
import atexit

from .log import logger

sdk = None


def shutdown():
    oneagent.shutdown()


def init(forkable=False):
    global sdk
    oneagent.initialize(forkable=forkable)
    state = oneagent.get_sdk().agent_state
    logger.debug("Initialized autodynatrace with AgentState: {}".format(state))
    if state != oneagent.common.AgentState.ACTIVE:
        logger.warning("Could not initialize the OneAgent SDK, AgentState: {}".format(state))

    atexit.register(shutdown)
    sdk = oneagent.get_sdk()
