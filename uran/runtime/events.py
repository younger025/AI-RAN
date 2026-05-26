from uran.common.time_utils import now_iso


class EventBus:
    def __init__(self):
        self.events = []

    def emit(self, event_type: str, message: str, payload=None):
        self.events.append({
            "time": now_iso(),
            "type": event_type,
            "message": message,
            "payload": payload or {},
        })

    def list_events(self):
        return list(self.events)