from asyncio import Event
from machine import Pin 
from micropython import schedule


class RotaryEncoder:
	rotary_event: Event
	button_event: Event

	_delta: int
	_clk: Pin
	_dt: Pin
	_sw: Pin

	def __init__(self, clk: int, dt: int, sw: int) -> None:
		self.rotary_event = Event()
		self.button_event = Event()

		self._delta = 0

		self._clk = Pin(clk, Pin.IN, Pin.PULL_UP)
		self._dt = Pin(dt, Pin.IN, Pin.PULL_UP)
		self._sw = Pin(sw, Pin.IN, Pin.PULL_UP)
 
		self._clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
					 handler=self._rotary_irq_callback)
		self._sw.irq(trigger=Pin.IRQ_FALLING, handler=self._button_irq_callback)
		pass

	def drain_delta(self) -> int:
		delta = self._delta
		self._delta = 0
		return delta

	def _rotary_irq_callback(self, _) -> None:
		self._delta += 1 if self._clk.value() != self._dt.value() else -1
		schedule(lambda _: self.rotary_event.set(), None)

	def _button_irq_callback(self, _) -> None:
		schedule(lambda _: self.button_event.set(), None)
	