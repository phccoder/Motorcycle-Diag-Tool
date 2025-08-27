import obd
import time

def run_diagnostics(brand_name):
    """
    Connects to the motorcycle's ECU and reads basic diagnostic data.
    The brand_name is used for user-friendly prompts.
    """
    print(f"\nAttempting to connect to your {brand_name}... 🏍️")
    print("Make sure you are using the correct physical adapter cable!")
    
    # The python-obd library automatically scans for the connection.
    # The underlying protocol (K-Line/CAN) is handled automatically.
    connection = obd.OBD("tcp://192.168.0.10:35000")

    if not connection.is_connected():
        print(f"❌ Could not connect to the {brand_name} ECU.")
        print("   Please check:")
        print("   1. The ignition is ON.")
        print("   2. The correct adapter cable is securely connected.")
        print("   3. The ELM327 adapter is properly plugged in.")
        return

    print(f"✅ Successfully connected to the {brand_name} ECU!")
    print("-" * 30)

    try:
        # --- Read Live Data (Standard OBD-II Commands) ---
        print("Reading live sensor data...")

        commands_to_check = {
            "Engine Speed (RPM)": obd.commands.RPM,
            "Coolant Temperature": obd.commands.COOLANT_TEMP,
            "Throttle Position": obd.commands.THROTTLE_POS,
            "Vehicle Speed (KPH)": obd.commands.SPEED,
            "Engine Load": obd.commands.ENGINE_LOAD,
        }

        for name, cmd in commands_to_check.items():
            response = connection.query(cmd)
            if not response.is_null():
                print(f"{name}: {response.value}")
            else:
                # This is useful to know which PIDs the ECU doesn't support
                print(f"{name}: Not supported by this ECU.")

        print("-" * 30)

        # --- Read Stored Trouble Codes (DTCs) ---
        print("Checking for Diagnostic Trouble Codes (DTCs)...")
        response_dtc = connection.query(obd.commands.GET_DTC)
        
        if not response_dtc.is_null() and response_dtc.value:
            print("🚨 Found Trouble Codes! 🚨")
            for code, desc in response_dtc.value:
                # The description might be generic for manufacturer-specific codes
                print(f"  -> Code: {code}, Description: {desc}")
        else:
            print("👍 No stored trouble codes found.")

    except Exception as e:
        print(f"An error occurred during diagnosis: {e}")
        
    finally:
        # Always close the connection
        print("-" * 30)
        print("Closing connection.")
        connection.close()

def main_menu():
    """
    Displays a menu for the user to select the motorcycle brand.
    """
    while True:
        print("\n===== Multi-Brand Motorcycle Diagnostic Tool =====")
        print("1. Honda")
        print("2. Yamaha")
        print("3. Suzuki")
        print("4. Exit")
        
        choice = input("Select the brand you are diagnosing: ")
        
        if choice == '1':
            run_diagnostics("Honda")
        elif choice == '2':
            run_diagnostics("Yamaha")
        elif choice == '3':
            run_diagnostics("Suzuki")
        elif choice == '4':
            print("Exiting tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")
        
        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main_menu()