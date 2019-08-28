import oneagent

from ..log import logger
from ..sdk import sdk

try:
    from pymongo import monitoring

    class DynatraceMongoListener(monitoring.CommandListener):

        def __init__(self):
            self.vendor = 'MongoDB'
            self.tracer: oneagent.sdk.tracers.Tracer = None

        def started(self, event):

            try:
                db_name = event.database_name
                collection_name = event.command.get(event.command_name)
                operation = event.command_name
                host, port = event.connection_id
                channel = oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, f'{host}:{port}')

                db_info = sdk.create_database_info(f'{db_name}.{collection_name}', self.vendor, channel)
                self.tracer = sdk.trace_sql_database_request(db_info, operation)
                self.tracer.start()

            except Exception as e:
                logger.debug(f'Error instrumenting MongoDB: {e}')

        def succeeded(self, event):
            self.end(False)

        def failed(self, event):
            self.end(True, message=f'{event.failure}')

        def end(self, failed: bool, message=''):
            if self.tracer is not None:
                if failed:
                    self.tracer.mark_failed('MongoDB Command', message)

                self.tracer.end()


    monitoring.register(DynatraceMongoListener())
    logger.debug('Instrumenting pymongo')
except ImportError:
    pass
