from typing import Optional

import oneagent


def get_messaging_type_by_queue_name(queue_name: Optional[str] = None) -> int:
    """Helper function to get queue type by name. If 'VirtualTopic' exists in the destination name
    this queue is a TOPIC type.
    By default the type of queue is QUEUE.
    """
    if queue_name and "VirtualTopic" in queue_name:
        return oneagent.common.MessagingDestinationType.TOPIC

    return oneagent.common.MessagingDestinationType.QUEUE
