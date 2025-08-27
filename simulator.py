# simulator.py
import time
import random
from dtc_database import DTC_CODES

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

    # --- FIX: These methods are now correctly indented to be part of the class ---
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
            return MockResponse(round(random.uniform(20.0, 85.0), 1))
        elif command.name == "INTAKE_PRESSURE":
            return MockResponse(random.randint(15, 100))
        elif command.name == "INTAKE_TEMP":
            return MockResponse(random.randint(20, 50))
        elif command.name == "CONTROL_MODULE_VOLTAGE":
            return MockResponse(round(random.uniform(12.0, 14.5), 1))
        elif command.name == "GET_DTC":
            if DTC_CODES and random.random() < 0.25:
                num_errors = random.randint(1, 2)
                random_keys = random.sample(list(DTC_CODES.keys()), k=num_errors)
                simulated_errors = [(key, DTC_CODES[key]) for key in random_keys]
                return MockResponse(simulated_errors)
            else:
                return MockResponse([])
        else:
            return MockResponse(None)

    def close(self):
        self._is_connected = False