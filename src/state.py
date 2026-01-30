from mode import  AUTO_MODE
from asyncio import Event
from micropython import const

TEMPERATURE_STATE_KEY = const("temperature")
HUMIDITY_STATE_KEY = const("humidity")
PRESSURE_STATE_KEY = const("pressure")
TARGET_TEMPERATURE_STATE_KEY = const("target_temperature")
MODE_STATE_KEY = const("mode")

class State:
    changed_event: Event

    _values: dict
    _pending: dict
    _delta: list

    def __init__(self) -> None:
        self.changed_event = Event()

        self._values = {
            TEMPERATURE_STATE_KEY: 20.0,
            HUMIDITY_STATE_KEY: 40.0,
            PRESSURE_STATE_KEY: 960.00,
            TARGET_TEMPERATURE_STATE_KEY: 20.0,
            MODE_STATE_KEY: AUTO_MODE,
        }
        self._pending = {}
        self._delta = []
        pass

    def begin(self) -> None:
        self._pending = {}

    def commit(self) -> None:
        pending = self._pending

        if not pending:
            return

        for key, value in self._pending.items():
            self._values[key] = value
            self._delta.append(key)
        
        self._pending = {}
        self.changed_event.set()

    def get(self, key):
        return self._values[key]

    def set(self, key, value) -> None:
        if value == self._values[key]:
            return

        self._pending[key] = value

    def drain_delta(self) -> list:
        delta = self._delta
        self._delta = []
        return delta
