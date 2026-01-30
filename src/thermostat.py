import asyncio
from lib.bme280 import BME280
from machine import Pin, I2C

READ_INTERVAL = const(5) # seconds
FREQUENCY = const(100000)

class Thermostat:
	sensor_event: asyncio.Event
	temperature: float
	humidity: float
	pressure: float

	_sensor: BME280

	def __init__(self, scl: int, sda: int) -> None:
		self.sensor_event = asyncio.Event()

		self.temperature = 20.0
		self.humidity = 60.0
		self.pressure = 0.0

		i2c = I2C(0, scl=Pin(scl), sda=Pin(sda))
		self._sensor = BME280(i2c=i2c)

	async def run(self) -> None:
		while True:
			self.temperature, self.pressure, self.humidity = self._sensor.read_compensated_data()

			# convert pressure to hPa
			self.pressure = self.pressure / 100

			self.temperature = round(self.temperature, 1)
			self.pressure = round(self.pressure, 1)
			self.humidity = round(self.humidity, 1)

			self.sensor_event.set()

			await asyncio.sleep(READ_INTERVAL)