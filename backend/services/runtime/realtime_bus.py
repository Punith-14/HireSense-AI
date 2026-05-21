from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class RealtimeEvent:
    event_type: str
    payload: dict
    occurred_at: str = field(default_factory=lambda: utc_now().isoformat())


class RealtimeSessionBuffer:
    def __init__(self, max_events=200):
        self._events = deque(maxlen=max_events)

    def publish(self, event_type, payload):
        event = RealtimeEvent(event_type=event_type, payload=payload)
        self._events.append(event)
        return event

    def snapshot(self):
        return list(self._events)
