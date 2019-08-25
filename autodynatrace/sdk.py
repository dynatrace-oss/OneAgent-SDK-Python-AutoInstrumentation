import oneagent

sdk = None


def init():
    global sdk
    oneagent.initialize()
    sdk = oneagent.get_sdk()

