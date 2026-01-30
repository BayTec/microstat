import json
import os
from config import ID

DISCOVERY_FILE = "files/discovery.json"


def file_exists(path):
	try:
		os.stat(path)
		return True
	except OSError:
		return False


def generate_discovery_config(device_id):
	return {
		"dev": {
			"identifiers": [
				f"{device_id}"
			],
			"name": f"Room Thermostat {device_id}",
			"model": "Microstat-v1",
			"manufacturer": "MicroFlexi"
		},
		"origin": {
			"name": "Microstat",
			"sw_version": "1.0"
		},
		"availability": {
			"topic": f"{device_id}/status",
			"payload_available": "online",
			"payload_not_available": "offline"
		},
		"cmps": {
			"climate": {
				"platform": "climate",
				"name": "Room Thermostat",
				"unique_id": f"{device_id}_climate",
				"current_temperature_topic": f"{device_id}/sensor/temperature",
				"temperature_command_topic": f"{device_id}/target_temp/set",
				"temperature_state_topic": f"{device_id}/target_temp/state",
				"mode_command_topic": f"{device_id}/mode/set",
				"mode_state_topic": f"{device_id}/mode/state",
				"modes": [
					"off",
					"heat",
					"auto"
				],
				"min_temp": 7,
				"max_temp": 25,
				"temp_step": 0.5
			},
			"humidity": {
				"platform": "sensor",
				"name": "Room Humidity",
				"unique_id": f"{device_id}_humidity",
				"state_topic": f"{device_id}/sensor/humidity",
				"device_class": "humidity",
				"unit_of_measurement": "%"
			},
			"pressure": {
				"platform": "sensor",
				"name": "Room Pressure",
				"unique_id": f"{device_id}_pressure",
				"state_topic": f"{device_id}/sensor/pressure",
				"device_class": "atmospheric_pressure",
				"unit_of_measurement": "hPa"
			}
		}
	}


def should_regenerate(path, current_device_id):
	try:
		with open(path, "r") as f:
			data = json.load(f)

		stored_id = data.get("_meta", {}).get("device_id")
		return stored_id != current_device_id

	except Exception:
		# Corrupt / partial / invalid file → regenerate
		return True


# ---- Boot logic ----

regenerate = False

if not file_exists(DISCOVERY_FILE):
	regenerate = True
else:
	if should_regenerate(DISCOVERY_FILE, ID):
		regenerate = True

if regenerate:
	data = generate_discovery_config(ID)

	with open(DISCOVERY_FILE, "w") as f:
		json.dump(data, f)

	print("Discovery config generated / regenerated")
else:
	print("Discovery config is up-to-date")
