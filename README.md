##  OneAgent-SDK-Python-AutoInstrumentation

[![Actions Status](https://github.com/dynatrace-oss/OneAgent-SDK-Python-AutoInstrumentation/workflows/Tests/badge.svg)](https://github.com/dynatrace-oss/OneAgent-SDK-Python-AutoInstrumentation/actions)
 [![Downloads](https://pepy.tech/badge/autodynatrace)](https://pepy.tech/project/autodynatrace)

Dynatrace provides a [powerful SDK](https://github.com/Dynatrace/OneAgent-SDK-for-Python) that can be used to achieve code level visibility and transaction tracing for applications written in multiple languages, including python. This project provides a library called *autodynatrace*, which is a wrapper around the OneAgent SDK for Python and allows you to instrument python applications with minimal code changes.


### Usage

`pip install autodynatrace`

### Option 1 - Instrumentation without code changes

Add the environment variable `AUTOWRAPT_BOOTSTRAP=autodynatrace` to your python processes

### Option 2 - Semi-Auto Instrumentation

For most technologies, just import it in your code.

`import autodynatrace`

### Technologies supported:

- **celery**
- **concurrent.futures**
- **confluent_kafka**
- **cx_Oracle**
- **django**
- **fastapi**
- **flask**
- **grpc**
- **paramiko**
- **pika** (RabbitMQ)
- **psycopg2**
- **pymongo**
- **pysnmp**
- **redis**
- **ruxit** (Dynatrace plugin framework)
- **sqlalchemy**
- **subprocess**
- **suds**
- **starlette**
- **tornado**
- **urllib**
- **urllib3**
- **custom annotations**

### Django

For Django, add `"autodynatrace.wrappers.django"` to `INSTALLED_APPS`

### Environment variables

* `AUTODYNATRACE_CAPTURE_HEADERS`: Default: `False`, set to `True` to capture request headers
* `AUTODYNATRACE_LOG_LEVEL`: Default `WARNING`
* `AUTODYNATRACE_FORKABLE`: Default `False`, set to `True` to [instrument forked processes](https://github.com/Dynatrace/OneAgent-SDK-for-Python#using-the-oneagent-sdk-for-python-with-forked-child-processes-only-available-on-linux). Use this for gunicorn/uwsgi
* `AUTODYNATRACE_VIRTUAL_HOST`: Overwrite the default Virtual Host for web frameworks
* `AUTODYNATRACE_APPLICATION_ID`: Overwrite the default Application Name for web frameworks
* `AUTODYNATRACE_CONTEXT_ROOT`: Overwrite the default Context Root for web frameworks
* `AUTODYNATRACE_CUSTOM_SERVICE_NAME`: Overwrite the custom service name (used by `@autodynatrace.trace`)
* `AUTODYNATRACE_CUSTOM_SERVICE_USE_FQN`: Default `False`, set to `True` to use fully qualified names for service and method names in custom traced services
* `AUTODYNATRACE_INSTRUMENT_<LIB_NAME>`: If set to `False`, Disables the instrumentation for a specific lib, example: `AUTODYNATRACE_INSTRUMENT_CONCURRENT=False`, default is `True`
