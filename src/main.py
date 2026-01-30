import asyncio
import mqtt
from state import State, TARGET_TEMPERATURE_STATE_KEY, MODE_STATE_KEY, TEMPERATURE_STATE_KEY, PRESSURE_STATE_KEY, HUMIDITY_STATE_KEY
from mode import next_mode
from rotary_encoder import RotaryEncoder
from wlan import WLANhandler
from relay import Relay
from thermostat import Thermostat
from display import Display
from micropython import const
from asyncio_extensions import Subscription, subscribe_event

# --- PIN assignment ---
ROTARY_ENCODER_CLK_PIN = const(2)
ROTARY_ENCODER_DT_PIN = const(3)
ROTARY_ENCODER_SW_PIN = const(4)

RELAY_PIN = const(5)

SCL_PIN = const(22)
SDA_PIN = const(21)
# /--- PIN assignment ---

# --- FIXED VALUES WLANhandler
CYCLE_INTERVAL = const(0.1) # seconds

TARGET_TEMP_MAX = const(25.0)
TARGET_TEMP_MIN = const(7.0)
TARGET_TEMP_STEP_SIZE = const(0.5)
# /--- FIXED VALUES ---


class App:
	state: State
	rotary_encoder: RotaryEncoder
	relay: Relay
	thermostat: Thermostat
	display: Display
	wlan_handler: WLANhandler
	mqtt_handler: mqtt.MQTTHandler

	_sensor_event_subscribtion: Subscription
	_rotary_event_subscribtion: Subscription
	_button_event_subscribtion: Subscription
	_state_changed_event_subscribtion: Subscription


	def __init__(self) -> None:
		# --- HARDWARE ---
		self.rotary_encoder = RotaryEncoder(
			clk=ROTARY_ENCODER_CLK_PIN,
			dt=ROTARY_ENCODER_DT_PIN,
			sw=ROTARY_ENCODER_SW_PIN,
		)

		self.relay = Relay(pin=RELAY_PIN)

		self.thermostat = Thermostat(scl=SCL_PIN, sda=SDA_PIN)

		self.display = Display(scl=SCL_PIN, sda=SDA_PIN)
		# /--- HARDWARE ---

		# --- WLAN ---
		self.wlan_handler = WLANhandler()
		# /--- WLAN ---

		# --- MQTT ---
		self.mqtt_handler = mqtt.MQTTHandler(self.mqtt_callback)
		# /--- MQTT ---

		# --- STATE ---
		self.state = State()
		# /--- STATE ---
		pass

	# --- MAIN LOOP ---
	async def run(self) -> None:
		self._sensor_event_subscribtion = subscribe_event(
			self.thermostat.sensor_event,
			self._sensor_event_listener
		)

		self._rotary_event_subscribtion = subscribe_event(
			self.rotary_encoder.rotary_event,
			self._rotary_event_listener
		)

		self._button_event_subscribtion = subscribe_event(
			self.rotary_encoder.button_event,
			self._button_event_listener
		)

		self._state_changed_event_subscribtion = subscribe_event(
			self.state.changed_event,
			self._state_changed_event_listener
		)

		asyncio.create_task(self.thermostat.run())
		asyncio.create_task(self.wlan_handler.run())
		asyncio.create_task(self.mqtt_handler.run())

		while True:
			await asyncio.sleep(CYCLE_INTERVAL)
	# /--- MAIN LOOP ---

	# --- FUNCTION DECLARATION ---
	def _sensor_event_listener(self) -> None:
		thermostat = self.thermostat

		new_temp = thermostat.temperature
		new_hum = thermostat.humidity
		new_pres = thermostat.pressure

		state = self.state
		state.begin()
		state.set(TEMPERATURE_STATE_KEY, new_temp)
		state.set(HUMIDITY_STATE_KEY, new_hum)
		state.set(PRESSURE_STATE_KEY, new_pres)
		state.commit()

	def _rotary_event_listener(self) -> None:
		state = self.state
		target_temp = float(state.get(TARGET_TEMPERATURE_STATE_KEY))
		delta = self.rotary_encoder.drain_delta()
		new_target_temp = self._normalize_target_temperature(target_temp + delta * TARGET_TEMP_STEP_SIZE)
		state.begin()
		state.set(TARGET_TEMPERATURE_STATE_KEY, new_target_temp)
		state.commit()

	def _button_event_listener(self) -> None:
		state = self.state
		mode = state.get(MODE_STATE_KEY)
		state.begin()
		state.set(MODE_STATE_KEY, next_mode(mode))
		state.commit()

	def _state_changed_event_listener(self) -> None:
		state = self.state
		delta = state.drain_delta()

		if not delta:
			return
		
		self.relay.handle_state_change(state, delta)
		self.display.handle_state_change(state)
		self.mqtt_handler.handle_state_change(state, delta)

	def _normalize_target_temperature(self, value: float) -> float:
		if value > TARGET_TEMP_MAX:
			new_target_temp = TARGET_TEMP_MAX
		elif value < TARGET_TEMP_MIN:
			new_target_temp = TARGET_TEMP_MIN
		else:
			new_target_temp = value

		return new_target_temp

	def mqtt_callback(self, topic: bytes, msg: bytes):
		topic_str = topic.decode()
		msg_str = msg.decode()

		state = self.state

		state.begin()
		if topic_str == mqtt.TARGET_TEMP_SET:
			state.set(TARGET_TEMPERATURE_STATE_KEY, float(msg_str))
		elif topic_str == mqtt.MODE_SET:
			state.set(MODE_STATE_KEY, msg_str)
		state.commit()

	# /--- FUNCTION DECLARATION ---


app = App()
asyncio.run(app.run())
