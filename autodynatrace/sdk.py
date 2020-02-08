import oneagent
import atexit

sdk = None


def init(forkable=False):
    global sdk
    oneagent.initialize(forkable=forkable)
    sdk = oneagent.get_sdk()


def shutdown():
    oneagent.shutdown()


atexit.register(shutdown)
