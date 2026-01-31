import asyncio
from config import ID, MQTT_BROKER, MQTT_USER, MQTT_PASSWORD
from state import State, TEMPERATURE_STATE_KEY, HUMIDITY_STATE_KEY, PRESSURE_STATE_KEY, MODE_STATE_KEY, TARGET_TEMPERATURE_STATE_KEY
from machine import idle
from umqtt.simple import MQTTClient
from micropython import const


CHECK_INTERVAL = const(1) # seconds
RECONNECT_INTERVAL = const(30) # seconds

DISCOVER = f"homeassistant/device/{ID}/config"
STATUS = f"{ID}/status"
TARGET_TEMP_STATE = f"{ID}/target_temp/state"
TARGET_TEMP_SET = f"{ID}/target_temp/set"
MODE_STATE = f"{ID}/mode/state"
MODE_SET = f"{ID}/mode/set"
SENSOR_TEMPERATURE = f"{ID}/sensor/temperature"
SENSOR_HUMIDITY = f"{ID}/sensor/humidity"
SENSOR_PRESSURE = f"{ID}/sensor/pressure"

class MQTTHandler:
	client: MQTTClient
	_connected: bool

	def __init__(self, callback) -> None:
		self.callback = callback
		self._connected = False
		self.last_attempt = 0
		client = MQTTClient(
			client_id=ID,
			server=MQTT_BROKER,
			user=MQTT_USER,
			password=MQTT_PASSWORD,
			keepalive=60,
		)
		# set LWT
		client.set_last_will(STATUS, "offline", retain=True)
		# set callback for subscribtions
		client.set_callback(self.callback)

		self.client = client

		self.connect()

	def connected(self) -> bool:
		return self._connected

	async def run(self) -> None:
		while True:
			if self.connected():
				try:
					self.client.check_msg()
					await asyncio.sleep(CHECK_INTERVAL)
				except Exception as e:
					print("MQTT check_msg error:", e)
					self._connected = False
			else:
				while not self.connected():
					await asyncio.sleep(RECONNECT_INTERVAL)
					self.connect()

	def connect(self) -> None:
		if self._connected:
			return

		try:
			client = self.client
			print("connecting to mqtt broker...")
			client.connect()
			idle()
			print("mqtt broker connected.")
			self._connected = True

			# discover for homeassistent
			client.publish(DISCOVER, open("files/discovery.json", "r").read(), retain=True)

			# subscribe topics
			client.subscribe(TARGET_TEMP_SET)
			client.subscribe(MODE_SET)

			# report online
			client.publish(STATUS, "online", retain=True)

		except Exception as e:
			print("MQTT connection failed:", e)
			self._connected = False
		
	def publish(self, topic: str, msg: str, retain: bool = False) -> None:
		if self.connected():
			try:
				self.client.publish(topic, msg, retain)
			except Exception as e:
				print("MQTT publish error:", e)
				self._connected = False

	def handle_state_change(self, state: State, delta: list) -> None:
		if TEMPERATURE_STATE_KEY in delta:
			self.publish(SENSOR_TEMPERATURE, str(state.get(TEMPERATURE_STATE_KEY)))
		if HUMIDITY_STATE_KEY in delta:
			self.publish(SENSOR_HUMIDITY, str(state.get(HUMIDITY_STATE_KEY)))
		if PRESSURE_STATE_KEY in delta:
			self.publish(SENSOR_PRESSURE, str(state.get(PRESSURE_STATE_KEY)))
		if TARGET_TEMPERATURE_STATE_KEY in delta:
			self.publish(TARGET_TEMP_STATE, str(state.get(TARGET_TEMPERATURE_STATE_KEY)))
		if MODE_STATE_KEY in delta:
			self.publish(MODE_STATE, str(state.get(MODE_STATE_KEY)))
		pass