##  Dynatrace OneAgent SDK Auto Instrumentation for Python

> **DISCLAIMER**: This project was developed as a hobby. It is not complete, nor supported and only intended as a starting point for those wanting to implement OneAgent SDK for Python with minimal code changes.

[![Downloads](https://pepy.tech/badge/autodynatrace)](https://pepy.tech/project/autodynatrace)

This package will instrument your python code with the OneAgentSDK.

### Usage

`pip install autodynatrace`

For most technologies, just import it in your code.

`import autodynatrace`

### Technologies supported:

- celery
- confluent_kafka
- django
- flask
- pymongo
- redis
- sqlalchemy
- urllib3
- custom annotations

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
### Confluent Kafka

confluent_kafka is written in C, which means we cannot patch the objects, to use it, just replace the `confluent_kafka.Consumer` and `confluent_kafka.Producer` imports with `autodynatrace.wrappers.confluent_kafka.Producer` and `autodynatrace.wrappers.confluent_kafka.Consumer`

```python
import autodynatrace
from autodynatrace.wrappers.confluent_kafka import Consumer, Producer
import time
from concurrent.futures import ThreadPoolExecutor

p = Producer({"bootstrap.servers": "localhost:32769"})
c = Consumer({"bootstrap.servers": "localhost:32769", "group.id": "mygroup", "auto.offset.reset": "earliest"})
c.subscribe(["mytopic"])


@autodynatrace.trace
def produce():
    message = "Hello world!"
    p.produce("mytopic", message.encode("utf-8"))


def producer():
    while True:
        produce()
        time.sleep(2)


def consumer():
    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        print("Received message: {}".format(msg.headers()))

    c.close()


def main():
    with ThreadPoolExecutor(max_workers=2) as e:
        e.submit(producer)
        e.submit(consumer)


if __name__ == "__main__":
    main()
```

### Environment variables

* `AUTODYNATRACE_CAPTURE_HEADERS`: Default: `False`, set to `True` to capture request headers
* `AUTDYNATRACE_LOG_LEVEL`: Default `WARNING`
