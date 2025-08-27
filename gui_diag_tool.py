import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import obd 
import threading
import time
import random
import json

# --- CONFIGURATION ---
SIMULATOR_MODE = False  # Set to True to enable simulator mode
DTC_FILE = 'dtc_codes.json'
# ---

# --- Global variables ---
connection = None
stop_thread = threading.Event()

def load_codes_from_file():
    try:
        with open(DTC_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showwarning("Warning", f"'{DTC_FILE}' not found. Simulator will not generate DTCs.")
        return None
    except json.JSONDecodeError:
        messagebox.showwarning("Warning", f"Could not decode JSON from '{DTC_FILE}'.")
        return None

ALL_DTC_CODES = load_codes_from_file()

class MockResponse:
    def __init__(self, value=None):
        self.value = value
    def is_null(self):
        return self.value is None

class OBDSimulator:
    def __init__(self, *args, **kwargs):
        self._is_connected = False
        time.sleep(1.5) 
        self._is_connected = True
    def is_connected(self):
        return self._is_connected
    def query(self, command):
        if command.name == "RPM":
            return MockResponse(random.randint(850, 3500))
        elif command.name == "COOLANT_TEMP":
            return MockResponse(random.randint(40, 95))
        elif command.name == "SPEED":
            return MockResponse(random.randint(0, 110))
        elif command.name == "GET_DTC":
            if ALL_DTC_CODES and random.random() < 0.50:
                num_errors = random.randint(1, 3)
                keys = random.sample(list(ALL_DTC_CODES.keys()), k=num_errors)
                return MockResponse([(key, ALL_DTC_CODES[key]) for key in keys])
            else:
                return MockResponse([])
        else:
            return MockResponse(round(random.uniform(10.0, 80.0), 2))
    def close(self):
        self._is_connected = False

def update_output(message, clear=False):
    output_text.config(state="normal")
    if clear:
        output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, message)
    output_text.see(tk.END)
    output_text.config(state="disabled")

def update_status(message):
    status_var.set(message)

def save_log():
    log_content = output_text.get("1.0", tk.END)
    if not log_content.strip():
        messagebox.showwarning("Warning", "Log is empty. Nothing to save.")
        return
    
    file_path = filedialog.asksaveasfilename(
        initialfile=f"diag_log_{time.strftime('%Y%m%d_%H%M%S')}.txt",
        defaultextension=".txt",
        filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            # FIX #2: Added encoding='utf-8' to handle special characters like emojis
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            update_status(f"Log saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log file: {e}")

def run_diagnostics_thread():
    global connection
    selected_brand = brand_combobox.get()
    
    app.after(0, update_status, f"Connecting to {selected_brand}...")
    app.after(0, update_output, f"Attempting to connect to your {selected_brand}... 🏍️\n", True)
    
    try:
        if SIMULATOR_MODE:
            connection = OBDSimulator()
        else:
            connection = obd.OBD("tcp://192.168.0.10:35000", fast=False, timeout=30)
        
        if not connection.is_connected():
            raise ConnectionError("Could not connect to the ECU.")

        app.after(0, update_status, f"Connected to {selected_brand} | Polling live data...")
        app.after(0, update_output, f"✅ Successfully connected!\n" + "-"*50 + "\n", False)
        
        live_data_commands = {
            "Engine Speed (RPM)": obd.commands.RPM,
            "Coolant Temperature (°C)": obd.commands.COOLANT_TEMP,
            "Vehicle Speed (KPH)": obd.commands.SPEED,
        }
        
        while not stop_thread.is_set():
            live_data_str = ""
            for name, cmd in live_data_commands.items():
                response = connection.query(cmd)
                live_data_str += f"{name}: {response.value}\n" if not response.is_null() else f"{name}: N/A\n"
            
            app.after(0, update_output, live_data_str + "\n", True)
            time.sleep(1)

        app.after(0, update_output, "\n--- Live data polling stopped. ---\n", False)
        
        response_dtc = connection.query(obd.commands.GET_DTC)
        if not response_dtc.is_null() and response_dtc.value:
            app.after(0, update_output, "🚨 Found Trouble Codes! 🚨\n", False)
            for code, desc in response_dtc.value:
                app.after(0, update_output, f"  -> {code}: {desc}\n", False)
        else:
            app.after(0, update_output, "👍 No stored trouble codes found.\n", False)

    except Exception as e:
        app.after(0, update_output, f"❌ ERROR: {e}\n", True)
        app.after(0, messagebox.showerror, "Error", f"An error occurred: {e}")
    
    finally:
        if connection:
            connection.close()
        connection = None
        app.after(0, update_status, "Ready")
        app.after(0, connect_button.config, {"state": "normal"})
        app.after(0, disconnect_button.config, {"state": "disabled"})
        
def start_diagnostics():
    stop_thread.clear()
    connect_button.config(state="disabled")
    disconnect_button.config(state="normal")
    diag_thread = threading.Thread(target=run_diagnostics_thread, daemon=True)
    diag_thread.start()

def stop_diagnostics():
    if not stop_thread.is_set():
        update_status("Stopping...")
        stop_thread.set()

def on_closing():
    stop_thread.set()
    if connection:
        connection.close()
    app.destroy()

# --- Main Application Window Setup ---
app = tk.Tk()
app.title("Motorcycle Diagnostic Tool")
app.geometry("650x450")

main_frame = ttk.Frame(app, padding="10")
main_frame.pack(fill="both", expand=True)

control_frame = ttk.Frame(main_frame)
control_frame.pack(fill="x", pady=5)

ttk.Label(control_frame, text="Select Brand:").pack(side="left", padx=5)
brand_combobox = ttk.Combobox(control_frame, values=["Honda", "Yamaha", "Suzuki"], state="readonly")
brand_combobox.pack(side="left", padx=5)
brand_combobox.set("Honda")

connect_button = ttk.Button(control_frame, text="Connect & Stream", command=start_diagnostics)
connect_button.pack(side="left", padx=5)

disconnect_button = ttk.Button(control_frame, text="Stop & Scan DTC", command=stop_diagnostics, state="disabled")
disconnect_button.pack(side="left", padx=5)

save_button = ttk.Button(control_frame, text="Save Log", command=save_log)
save_button.pack(side="left", padx=5)

output_text = tk.Text(main_frame, height=15, wrap="word", state="disabled", bg="#f0f0f0", font=("Consolas", 10))
output_text.pack(fill="both", expand=True, pady=5)

status_var = tk.StringVar()
status_var.set(f"Ready | San Pablo City | {time.strftime('%b %d, %Y')}")
status_bar = ttk.Label(main_frame, textvariable=status_var, relief="sunken", anchor="w")
status_bar.pack(side="bottom", fill="x")

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()