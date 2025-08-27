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
        address = config['address'] # Get address from config

        callbacks['status'](f"Connecting to {brand} via {mode}...")
        callbacks['output'](f"Attempting to connect... 🏍️\n", True)

        if mode == 'Simulator':
            connection = OBDSimulator()
        else:
            # Use the address from the settings file
            connection = obd.OBD(address, fast=False, timeout=30)
        
        if not connection.is_connected(): raise ConnectionError("Could not connect to the ECU.")

        callbacks['status'](f"Connected to {brand} | Polling live data...")
        callbacks['output'](f"✅ Successfully connected!\n", True)
        
        # --- UPDATED CONTINUOUS DATA LOOP ---
        while not stop_event.is_set():
            # Query RPM
            rpm_response = connection.query(obd.commands.RPM)
            if not rpm_response.is_null(): callbacks['update_rpm'](rpm_response.value)

            # Query Speed
            speed_response = connection.query(obd.commands.SPEED)
            if not speed_response.is_null(): callbacks['update_speed'](speed_response.value)
            
            # Query Coolant Temp (New)
            temp_response = connection.query(obd.commands.COOLANT_TEMP)
            if not temp_response.is_null(): callbacks['update_temp'](temp_response.value)
            
            # Query Engine Load (New)
            load_response = connection.query(obd.commands.ENGINE_LOAD)
            if not load_response.is_null(): callbacks['update_load'](load_response.value)
            
            time.sleep(0.1)

        # (DTC Scan logic after loop is the same)
        callbacks['output']("\n--- Live data polling stopped. ---\n", False)
        response_dtc = connection.query(obd.commands.GET_DTC)
        if not response_dtc.is_null() and response_dtc.value:
            callbacks['output']("🚨 Found Trouble Codes! 🚨\n", False)
            for code, desc in response_dtc.value:
                callbacks['output'](f"  -> {code}: {desc}\n", False)
        else:
            callbacks['output']("👍 No stored trouble codes found.\n", False)

    except Exception as e:
        callbacks['output'](f"❌ ERROR: {e}\n", True)
        callbacks['error']("Error", f"An error occurred: {e}")
    
    finally:
        if connection: connection.close()
        callbacks['status']("Ready")
        callbacks['reset_buttons']()