from .consumer import instrument_consumer
from .publisher import instrument_publisher

def instrument():
    instrument_publisher()
    instrument_consumer()