from asyncio import Event, ThreadSafeFlag, create_task, sleep_ms
from machine import Pin 
from micropython import const
import time

ROTARY_DEBOUNCE = const(50) # milliseconds
BUTTON_DEBOUNCE = const(50) # milliseconds

class RotaryEncoder:
	rotary_event: Event
	button_event: Event

	_rotary_flag: ThreadSafeFlag
	_button_flag: ThreadSafeFlag

	_delta: int
	_clk: Pin
	_dt: Pin
	_sw: Pin

	def __init__(self, clk: int, dt: int, sw: int) -> None:
		self.rotary_event = Event()
		self.button_event = Event()

		self._rotary_flag = ThreadSafeFlag()
		self._button_flag = ThreadSafeFlag()

		self._delta = 0

		self._clk = Pin(clk, Pin.IN, Pin.PULL_UP)
		self._dt = Pin(dt, Pin.IN, Pin.PULL_UP)
		self._sw = Pin(sw, Pin.IN, Pin.PULL_UP)
 
		self._clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
					 handler=self._rotary_irq_callback)
		self._sw.irq(trigger=Pin.IRQ_RISING, handler=self._button_irq_callback)

		create_task(self._rotary_flag_listener())
		create_task(self._button_flag_listener())
		pass

	def drain_delta(self) -> int:
		delta = self._delta
		self._delta = 0
		return delta

	def _rotary_irq_callback(self, _) -> None:
		self._delta += 1 if self._clk.value() != self._dt.value() else -1
		self._rotary_flag.set()

	def _button_irq_callback(self, _) -> None:
		self._button_flag.set()
	
	async def _rotary_flag_listener(self) -> None:
		while True:
			await self._rotary_flag.wait()
			await sleep_ms(ROTARY_DEBOUNCE)
			self.rotary_event.set()

	async def _button_flag_listener(self) -> None:
		while True:
			await self._button_flag.wait()
			await sleep_ms(BUTTON_DEBOUNCE)
			self.button_event.set()