##  Dynatrace OneAgent SDK Auto Instrumentation for Python

> **DISCLAIMER**: This project was developed as a hobby. It is not complete, nor supported and only intended as a starting point for those wanting to implement OneAgent SDK for Python with minimal code changes.

[![Downloads](https://pepy.tech/badge/autodynatrace)](https://pepy.tech/project/autodynatrace)

This package will instrument your python code with the [OneAgent SDK for Python](https://github.com/Dynatrace/OneAgent-SDK-for-Python).

### Usage

`pip install autodynatrace`

For most technologies, just import it in your code.

`import autodynatrace`

### Technologies supported:

- **celery**
- **concurrent.futures**
- **confluent_kafka**
- **cx_Oracle**
- **django**
- **flask**
- **grpc**
- **pika** (RabbitMQ)
- **pymongo**
- **pysnmp**
- **redis**
- **ruxit** (Dynatrace plugin framework)
- **sqlalchemy**
- **subprocess**
- **suds**
- **urllib**
- **urllib3**
- **custom annotations**

### Django

For Django, add `"autodynatrace.wrappers.django"` to `INSTALLED_APPS`

### Environment variables

* `AUTODYNATRACE_CAPTURE_HEADERS`: Default: `False`, set to `True` to capture request headers
* `AUTODYNATRACE_LOG_LEVEL`: Default `WARNING`
* `AUTODYNATRACE_FORKABLE`: Default `False`, set to `True` to [instrument forked processes](https://github.com/Dynatrace/OneAgent-SDK-for-Python#using-the-oneagent-sdk-for-python-with-forked-child-processes-only-available-on-linux)
* `AUTODYNATRACE_VIRTUAL_HOST`: Overwrite the default Virtual Host for Flaks and Django
* `AUTODYNATRACE_APPLICATION_ID`: Overwrite the default Application Name for Flask and Django
* `AUTODYNATRACE_CONTEXT_ROOT`: Overwrite the default Context Root for Flask and Django
