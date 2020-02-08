import oneagent
import atexit

sdk = None


def shutdown():
    oneagent.shutdown()


def init(forkable=False):
    global sdk
    oneagent.initialize(forkable=forkable)
    atexit.register(shutdown)
    sdk = oneagent.get_sdk()
