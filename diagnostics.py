# diagnostics.py
import obd
import threading
import time
from simulator import OBDSimulator

def run_diagnostics_thread(config, callbacks, stop_event):
    connection = None
    try:
        brand = config['brand']
        mode = config['connection_mode']
        address = config['address']

        callbacks['status'](f"Connecting to {brand} via {mode}...")
        callbacks['output'](f"Attempting to connect... 🏍️\n", True)

        if mode == 'Simulator':
            connection = OBDSimulator()
        else:
            connection = obd.OBD(address, fast=False, timeout=30)
        
        if not connection.is_connected(): raise ConnectionError("Could not connect to the ECU.")

        callbacks['status'](f"Connected to {brand} | Polling live data...")
        callbacks['output'](f"✅ Successfully connected!\n", True)

        gauge_commands = {
            'rpm': obd.commands.RPM,
            'speed': obd.commands.SPEED,
            'temp': obd.commands.COOLANT_TEMP,
            'load': obd.commands.ENGINE_LOAD
        }

        secondary_commands = {
            'Intake Pressure (kPa)': obd.commands.INTAKE_PRESSURE,
            'Intake Temp (°C)': obd.commands.INTAKE_TEMP,
            'Battery Voltage (V)': obd.commands.CONTROL_MODULE_VOLTAGE
        }
        
        # --- CLEANED UP CONTINUOUS DATA LOOP ---
        while not stop_event.is_set():
            # This single block now correctly updates both gauges and the text panel
            for key, cmd in gauge_commands.items():
                response = connection.query(cmd)
                if not response.is_null(): callbacks[f'update_{key}'](response.value)

            secondary_data_str = ""
            for name, cmd in secondary_commands.items():
                response = connection.query(cmd)
                value = response.value if not response.is_null() else "N/A"
                secondary_data_str += f"{name}: {value}\n"
            
            callbacks['update_secondary_data'](secondary_data_str)
            
            # Use the correct, shorter sleep time from our previous fix
            time.sleep(0.1)

        # (DTC Scan logic remains the same)
        callbacks['output']("\n--- Live data polling stopped. ---\n", False)
        response_dtc = connection.query(obd.commands.GET_DTC)
        dtc_list = response_dtc.value
        
        if not response_dtc.is_null() and dtc_list:
            # Call the new dedicated callback with the list of found codes
            callbacks['display_dtcs'](dtc_list)
        else:
            callbacks['output']("👍 No stored trouble codes found.\n", False)

    except Exception as e:
        callbacks['output'](f"❌ ERROR: {e}\n", True)
        callbacks['error']("Error", f"An error occurred: {e}")
    
    finally:
        if connection: connection.close()
        callbacks['status']("Ready")
        callbacks['reset_buttons']()