# simulator.py
import time
import random
import json

DTC_FILE = 'dtc_codes.json'

def load_codes_from_file():
    """Loads the DTC codes from the local JSON file."""
    try:
        with open(DTC_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # In a real app, you might log this error, but for the simulator, we can return None
        return None

ALL_DTC_CODES = load_codes_from_file()

class MockResponse:
    """A simple class to mimic the response object from python-obd."""
    def __init__(self, value=None):
        self.value = value
    def is_null(self):
        return self.value is None

class OBDSimulator:
    """A simulator class that pretends to be an OBD connection."""
    def __init__(self, *args, **kwargs):
        self._is_connected = False
        time.sleep(1.5) 
        self._is_connected = True

    def is_connected(self):
        return self._is_connected

    def query(self, command):
        # This logic is expanded to include the new sensors
        if command.name == "RPM":
            return MockResponse(random.randint(850, 4500))
        elif command.name == "SPEED":
            return MockResponse(random.randint(0, 110))
        elif command.name == "COOLANT_TEMP": # New
            return MockResponse(random.randint(40, 95))
        elif command.name == "ENGINE_LOAD": # New
            return MockResponse(round(random.uniform(20.0, 85.0), 2))
        elif command.name == "GET_DTC":
            if ALL_DTC_CODES and random.random() < 0.25: # Lowered chance for cleaner display
                num_errors = random.randint(1, 2)
                keys = random.sample(list(ALL_DTC_CODES.keys()), k=num_errors)
                return MockResponse([(key, ALL_DTC_CODES[key]) for key in keys])
            else:
                return MockResponse([])
        else:
            return MockResponse(None)

    def close(self):
        self._is_connected = False