import oneagent

sdk = oneagent.get_sdk()


def init():
    oneagent.initialize()
    sdk = oneagent.get_sdk()
