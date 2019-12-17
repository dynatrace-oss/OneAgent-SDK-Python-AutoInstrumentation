import oneagent
import atexit

sdk = None


def init():
    global sdk
    oneagent.initialize()
    sdk = oneagent.get_sdk()


atexit.register(oneagent.shutdown)
