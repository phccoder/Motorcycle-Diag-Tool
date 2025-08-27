# simulator.py
import time
import random
from dtc_database import DTC_CODES # Import the dictionary directly

class MockResponse:
    """A simple class to mimic the response object from python-obd."""
    def __init__(self, value=None):
        self.value = value
    def is_null(self):
        return self.value is None

class OBDSimulator:
    """A simulator class that uses the new, imported DTC database."""
    def __init__(self, *args, **kwargs):
        self._is_connected = False
        time.sleep(1.5) 
        self._is_connected = True

    def is_connected(self):
        return self._is_connected

    def query(self, command):
        if command.name == "RPM":
            return MockResponse(random.randint(850, 4500))
        elif command.name == "SPEED":
            return MockResponse(random.randint(0, 110))
        elif command.name == "COOLANT_TEMP":
            return MockResponse(random.randint(40, 95))
        elif command.name == "ENGINE_LOAD":
            return MockResponse(round(random.uniform(20.0, 85.0), 2))
        elif command.name == "GET_DTC":
            if DTC_CODES and random.random() < 0.25:
                num_errors = random.randint(1, 2)
                # Get a random sample of code keys from the imported dictionary
                random_keys = random.sample(list(DTC_CODES.keys()), k=num_errors)
                # Format the codes like the python-obd library does
                simulated_errors = [(key, DTC_CODES[key]) for key in random_keys]
                return MockResponse(simulated_errors)
            else:
                return MockResponse([])
        else:
            return MockResponse(None)

    def close(self):
        self._is_connected = False