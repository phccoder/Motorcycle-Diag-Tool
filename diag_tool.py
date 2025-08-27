import tkinter as tk
from tkinter import ttk, messagebox
import obd
import threading
import time

# --- Global variable to hold the OBD connection ---
connection = None

def update_output(message):
    """Safely updates the text box from any thread."""
    output_text.config(state="normal")
    output_text.insert(tk.END, message)
    output_text.see(tk.END) # Auto-scroll to the bottom
    output_text.config(state="disabled")

def update_status(message):
    """Updates the status bar."""
    status_var.set(message)

def clear_output():
    """Clears the output text box."""
    output_text.config(state="normal")
    output_text.delete('1.0', tk.END)
    output_text.config(state="disabled")

def run_diagnostics_thread():
    """
    This function runs in a separate thread to avoid freezing the GUI.
    It contains the core logic from your original script.
    """
    global connection
    selected_brand = brand_combobox.get()
    
    if not selected_brand:
        messagebox.showerror("Error", "Please select a motorcycle brand first.")
        update_status("Ready")
        connect_button.config(state="normal")
        return

    # --- GUI Updates from the Thread ---
    # Use app.after to schedule GUI updates on the main thread
    app.after(0, update_status, f"Connecting to {selected_brand}...")
    app.after(0, clear_output)
    app.after(0, update_output, f"Attempting to connect to your {selected_brand}... 🏍️\n")
    app.after(0, update_output, "Ensure ignition is ON and hardware is connected.\n\n")

    try:
        connection = obd.OBD("tcp://199.10.0.10:35000", fast=False, timeout=30)
        
        if not connection.is_connected():
            error_message = f"❌ Could not connect to the {selected_brand} ECU.\nPlease check connections and ignition.\n"
            app.after(0, update_output, error_message)
            app.after(0, messagebox.showerror, "Connection Failed", error_message)
            disconnect() # Reset state
            return

        app.after(0, update_status, f"Connected to {selected_brand}!")
        app.after(0, update_output, f"✅ Successfully connected to the {selected_brand} ECU!\n")
        app.after(0, update_output, "-" * 50 + "\n")
        app.after(0, update_output, "Reading live sensor data...\n")

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
                result = f"{name}: {response.value}\n"
            else:
                result = f"{name}: Not supported by this ECU.\n"
            app.after(0, update_output, result)
            time.sleep(0.1) # Small delay between commands

        app.after(0, update_output, "-" * 50 + "\n")
        app.after(0, update_output, "Checking for Diagnostic Trouble Codes (DTCs)...\n")
        
        response_dtc = connection.query(obd.commands.GET_DTC)
        
        if not response_dtc.is_null() and response_dtc.value:
            app.after(0, update_output, "🚨 Found Trouble Codes! 🚨\n")
            for code, desc in response_dtc.value:
                dtc_result = f"  -> Code: {code}, Description: {desc}\n"
                app.after(0, update_output, dtc_result)
        else:
            app.after(0, update_output, "👍 No stored trouble codes found.\n")

    except Exception as e:
        error_info = f"\nAn unexpected error occurred: {e}\n"
        app.after(0, update_output, error_info)
        app.after(0, messagebox.showerror, "Error", error_info)
    
    finally:
        # Re-enable the connect button and update state
        app.after(0, disconnect_button.config, {"state": "normal"})


def start_diagnostics():
    """Starts the diagnostic process in a new thread."""
    connect_button.config(state="disabled") # Prevent multiple clicks
    diag_thread = threading.Thread(target=run_diagnostics_thread, daemon=True)
    diag_thread.start()

def disconnect():
    """Closes the connection and resets the GUI state."""
    global connection
    if connection and connection.is_connected():
        connection.close()
        update_output("\nConnection closed.\n")
    connection = None
    update_status("Ready")
    connect_button.config(state="normal")
    disconnect_button.config(state="disabled")

def on_closing():
    """Handles window close event."""
    disconnect()
    app.destroy()

# --- Main Application Window Setup ---
app = tk.Tk()
app.title("Motorcycle Diagnostic Tool")
app.geometry("650x450")

main_frame = ttk.Frame(app, padding="10")
main_frame.pack(fill="both", expand=True)

# --- Top Frame for Controls ---
control_frame = ttk.Frame(main_frame)
control_frame.pack(fill="x", pady=5)

ttk.Label(control_frame, text="Select Brand:").pack(side="left", padx=5)
brand_combobox = ttk.Combobox(control_frame, values=["Honda", "Yamaha", "Suzuki"], state="readonly")
brand_combobox.pack(side="left", padx=5)
brand_combobox.set("Honda") # Default value

connect_button = ttk.Button(control_frame, text="Connect & Scan", command=start_diagnostics)
connect_button.pack(side="left", padx=5)

disconnect_button = ttk.Button(control_frame, text="Disconnect", command=disconnect, state="disabled")
disconnect_button.pack(side="left", padx=5)

# --- Output Text Area ---
output_text = tk.Text(main_frame, height=15, wrap="word", state="disabled", bg="#f0f0f0")
output_text.pack(fill="both", expand=True, pady=5)

# --- Status Bar ---
status_var = tk.StringVar()
status_var.set("Ready | San Pablo City | Aug 27, 2025")
status_bar = ttk.Label(main_frame, textvariable=status_var, relief="sunken", anchor="w")
status_bar.pack(side="bottom", fill="x")

# --- Set protocol for window close and start GUI loop ---
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()