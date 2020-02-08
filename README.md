##  Dynatrace OneAgent SDK Auto Instrumentation for Python

> **DISCLAIMER**: This project was developed as a hobby. It is not complete, nor supported and only intended as a starting point for those wanting to implement OneAgent SDK for Python with minimal code changes.

[![Downloads](https://pepy.tech/badge/autodynatrace)](https://pepy.tech/project/autodynatrace)

This package will instrument your python code with the OneAgentSDK.

### Usage

`pip install autodynatrace`

Just import it in your code.

`import autodynatrace`

### Django

For Django, add `"autodynatrace.wrappers.django"` to `INSTALLED_APPS`

### Celery

For Celery, in your tasks files, you need to call `autodynatrace.set_forkable()` after importing autodynatrace, see [this issue](https://github.com/Dynatrace/OneAgent-SDK-for-Python/issues/9) for more info.

```python
import autodynatrace
import random
import time
from celery import Celery

autodynatrace.set_forkable()
app = Celery("tasks", broker="pyamqp://guest@localhost//")


@app.task
def add(x, y):
    time.sleep(random.randint(1, 3))
    return x + y
```


### Technologies supported:

- celery
- django
- flask
- pymongo
- redis
- sqlalchemy
- urllib3
- custom annotations

### Environment variables

* `AUTODYNATRACE_CAPTURE_HEADERS`: Default: `False`, set to `True` to capture request headers
* `AUTDYNATRACE_LOG_LEVEL`: Default `WARNING`
