import oneagent

sdk: oneagent.SDK = None


def init():
    global sdk
    oneagent.initialize()
    sdk = oneagent.get_sdk()

