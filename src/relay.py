from state import State, TEMPERATURE_STATE_KEY, TARGET_TEMPERATURE_STATE_KEY, MODE_STATE_KEY
from machine import Pin
from micropython import const
from mode import HEAT_MODE, OFF_MODE

THRESHOLD = const(0.2)

class Relay:
    _pin: Pin

    def __init__(self, pin: int) -> None:
        self._pin = Pin(pin, Pin.OUT, value=1)
        pass

    def handle_state_change(self, state: State, delta: list) -> None:
        if not any(key in delta for key in (
            TEMPERATURE_STATE_KEY,
            TARGET_TEMPERATURE_STATE_KEY,
            MODE_STATE_KEY,
        )):
            return

        temperature = state.get(TEMPERATURE_STATE_KEY)
        target_temperature = state.get(TARGET_TEMPERATURE_STATE_KEY)
        mode = state.get(MODE_STATE_KEY)

        pin = self._pin

        if mode == HEAT_MODE:
            pin.value(0)
        elif mode == OFF_MODE:
            pin.value(1)
        else:
            if target_temperature > temperature + THRESHOLD:
                pin.value(0)
            elif target_temperature < temperature - THRESHOLD:
                pin.value(1)

    def status(self) -> bool:
        return self._pin.value() == 0
