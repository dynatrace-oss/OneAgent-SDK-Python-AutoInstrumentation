import oneagent

from ..log import logger
from ..sdk import sdk

try:
    from pymongo import monitoring

    class DynatraceMongoListener(monitoring.CommandListener):
        def __init__(self):
            self.vendor = "MongoDB"
            self.tracer = None

        def started(self, event):

            try:
                db_name = event.database_name
                collection_name = event.command.get(event.command_name)
                operation = event.command_name
                host, port = event.connection_id
                channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, "{}:{}".format(host, port))

                db_info = sdk.create_database_info("{}.{}".format(db_name, collection_name), self.vendor, channel)
                self.tracer = sdk.trace_sql_database_request(db_info, operation)
                self.tracer.start()

            except Exception as e:
                logger.debug("Error instrumenting MongoDB: {}".format(e))

        def succeeded(self, event):
            self.end(False)

        def failed(self, event):
            self.end(True, message="{}".format(event.failure))

        def end(self, failed, message=""):
            if self.tracer is not None:
                if failed:
                    self.tracer.mark_failed("MongoDB Command", message)

                self.tracer.end()

    monitoring.register(DynatraceMongoListener())
    logger.debug("Instrumenting pymongo")
except ImportError:
    pass
