# gui_app.py
import customtkinter
from tkinter import messagebox, filedialog
import threading
import time
import webbrowser
from diagnostics import run_diagnostics_thread
from custom_widgets import Gauge
from dtc_database import DTC_CODES 
from simulator import OBDSimulator
from config_manager import load_settings, save_settings

class ToplevelSettings(customtkinter.CTkToplevel):
    def __init__(self, master, current_settings, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.transient(master)
        self.grab_set()
        self.title("Settings")
        self.geometry("400x250")
        self.resizable(False, False)

        self.label_mode = customtkinter.CTkLabel(self, text="Connection Mode:")
        self.label_mode.pack(padx=20, pady=(20, 5))
        
        self.mode_var = customtkinter.StringVar(value=current_settings.get('connection_mode'))
        self.mode_menu = customtkinter.CTkOptionMenu(self, variable=self.mode_var, values=["Simulator", "Wi-Fi", "Bluetooth"])
        self.mode_menu.pack(padx=20, pady=5)

        self.label_address = customtkinter.CTkLabel(self, text="Address (IP:Port or COM Port):")
        self.label_address.pack(padx=20, pady=(10, 5))
        
        self.address_entry = customtkinter.CTkEntry(self, placeholder_text="e.g., tcp://192.168.0.10:35000 or COM3", width=250)
        self.address_entry.pack(padx=20, pady=5)
        self.address_entry.insert(0, current_settings.get('address'))

        self.save_button = customtkinter.CTkButton(self, text="Save Settings", command=self.save_and_close)
        self.save_button.pack(padx=20, pady=20)

    def save_and_close(self):
        new_settings = {
            'connection_mode': self.mode_var.get(),
            'address': self.address_entry.get()
        }
        save_settings(new_settings)
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        self.destroy()

class ToplevelDTC(customtkinter.CTkToplevel):
    def __init__(self, master, all_codes, *args, **kwargs): 
        super().__init__(master, *args, **kwargs)
        self.transient(master)
        self.grab_set()
        self.all_codes = all_codes
        self.title("DTC Code Lookup")
        self.geometry("400x200")
        self.resizable(False, False)
        self.after(250, lambda: self.iconbitmap(''))

        self.label = customtkinter.CTkLabel(self, text="Enter DTC Code (e.g., P0401):")
        self.label.pack(padx=20, pady=(20, 5))

        self.entry = customtkinter.CTkEntry(self, placeholder_text="P0XXX")
        self.entry.pack(padx=20, pady=5)
        self.entry.bind("<Return>", self.search_code)

        self.search_button = customtkinter.CTkButton(self, text="Search", command=self.search_code)
        self.search_button.pack(padx=20, pady=5)

        self.result_label = customtkinter.CTkLabel(self, text="", wraplength=350)
        self.result_label.pack(padx=20, pady=(10, 20))

    def search_code(self, event=None):
        code = self.entry.get().strip().upper()
        if not code:
            self.result_label.configure(text="Please enter a code.", text_color="yellow")
            return
        
        if self.all_codes:
            description = self.all_codes.get(code)
            if description:
                self.result_label.configure(text=f"{code}: {description}", text_color="white")
            else:
                self.result_label.configure(text=f"Code '{code}' not found in database.", text_color="orange")
        else:
            self.result_label.configure(text="DTC database is not loaded.", text_color="red")
# ===================================================================

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Motorcycle Diagnostic Tool")
        self.geometry("800x850") # Made window taller
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        
        self.stop_thread = threading.Event()
        self.settings = load_settings()
        
        self.fullscreen_state = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.dtc_widgets = [] # To keep track of DTC result widgets

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Row for gauges
        self.grid_rowconfigure(2, weight=0) # Row for new data panel
        self.grid_rowconfigure(3, weight=1) # Row for textbox

        control_frame = customtkinter.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        brand_label = customtkinter.CTkLabel(control_frame, text="Select Brand:")
        brand_label.pack(side="left", padx=(10, 0))
        self.brand_combobox = customtkinter.CTkComboBox(self, values=["Honda", "Yamaha", "Suzuki"])
        self.brand_combobox.pack(in_=control_frame, side="left", padx=5)
        self.brand_combobox.set("Honda")
        self.connect_button = customtkinter.CTkButton(self, text="Connect & Stream", command=self.start_diagnostics)
        self.connect_button.pack(in_=control_frame, side="left", padx=5)
        self.disconnect_button = customtkinter.CTkButton(self, text="Stop & Scan DTC", command=self.stop_diagnostics, state="disabled")
        self.disconnect_button.pack(in_=control_frame, side="left", padx=5)
        save_button = customtkinter.CTkButton(self, text="Save Log", command=self.save_log)
        save_button.pack(in_=control_frame, side="left", padx=5)
        lookup_button = customtkinter.CTkButton(self, text="DTC Lookup", command=self.open_dtc_lookup_window)
        lookup_button.pack(in_=control_frame, side="left", padx=5)
        # --- Add the new Settings Button ---
        settings_button = customtkinter.CTkButton(self, text="Settings", command=self.open_settings_window)
        settings_button.pack(in_=control_frame, side="left", padx=5)

        gauge_frame = customtkinter.CTkFrame(self)
        gauge_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        gauge_frame.grid_columnconfigure((0, 1), weight=1)
        gauge_frame.grid_rowconfigure((0, 1), weight=1)

        self.rpm_gauge = Gauge(gauge_frame, label="ENGINE SPEED", min_value=0, max_value=8000, unit="RPM")
        self.rpm_gauge.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.speed_gauge = Gauge(gauge_frame, label="VEHICLE SPEED", min_value=0, max_value=120, unit="KPH")
        self.speed_gauge.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.temp_gauge = Gauge(gauge_frame, label="COOLANT TEMP", min_value=0, max_value=120, unit="°C")
        self.temp_gauge.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.load_gauge = Gauge(gauge_frame, label="ENGINE LOAD", min_value=0, max_value=100, unit="%")
        self.load_gauge.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        secondary_data_frame = customtkinter.CTkFrame(self)
        secondary_data_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.secondary_data_label = customtkinter.CTkLabel(secondary_data_frame, text="Waiting for data...", font=("Consolas", 14), justify="left")
        self.secondary_data_label.pack(padx=10, pady=10)

        # --- OUTPUT TEXTBOX for logs and DTCs ---
        self.output_text = customtkinter.CTkTextbox(self, state="disabled", font=("Consolas", 12), height=150)
        self.output_text.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.status_var = customtkinter.StringVar(value=f"Ready | Press F11 for Fullscreen")
        status_bar = customtkinter.CTkLabel(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")

        dtc_frame_label = customtkinter.CTkLabel(self, text="Diagnostic Trouble Codes (DTCs)", font=("Arial", 14, "bold"))
        dtc_frame_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.dtc_scrollable_frame = customtkinter.CTkScrollableFrame(self, height=150)
        self.dtc_scrollable_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.status_var = customtkinter.StringVar(value=f"Ready | Press F11 for Fullscreen")
        status_bar = customtkinter.CTkLabel(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="ew")

    def open_settings_window(self):
        """Opens the settings dialog."""
        self.settings = load_settings() # Re-load settings in case they were changed
        ToplevelSettings(self, self.settings)

    def start_diagnostics(self):
        self.stop_thread.clear()
        self.connect_button.configure(state="disabled")
        self.disconnect_button.configure(state="normal")
        
        self.settings = load_settings()
        
        config = {
            'brand': self.brand_combobox.get(),
            'connection_mode': self.settings.get('connection_mode'),
            'address': self.settings.get('address')
        }
        
        callbacks = {
            'status': self.update_status, 'output': self.update_output,
            'error': messagebox.showerror, 'reset_buttons': self.reset_buttons,
            'update_rpm': self.rpm_gauge.update_value,
            'update_speed': self.speed_gauge.update_value,
            'update_temp': self.temp_gauge.update_value,
            'update_load': self.load_gauge.update_value,
            'update_secondary_data': self.update_secondary_data,
            'display_dtcs': self.display_dtc_results
        }
        
        diag_thread = threading.Thread(target=run_diagnostics_thread, args=(config, callbacks, self.stop_thread), daemon=True)
        diag_thread.start()

    def update_secondary_data(self, data_string):
        self.secondary_data_label.configure(text=data_string)

    def display_dtc_results(self, dtc_list):
        # Clear any old results first
        for widget in self.dtc_widgets:
            widget.destroy()
        self.dtc_widgets = []

        # Update the main log
        self.update_output("🚨 Found Trouble Codes! 🚨\n", False)

        for code, desc in dtc_list:
            # Create a frame for each DTC
            entry_frame = customtkinter.CTkFrame(self.dtc_scrollable_frame)
            entry_frame.pack(fill="x", padx=5, pady=5)
            self.dtc_widgets.append(entry_frame)

            label_text = f"{code}: {desc}"
            label = customtkinter.CTkLabel(entry_frame, text=label_text, wraplength=500, justify="left")
            label.pack(side="left", padx=10, pady=5)
            
            # Create a troubleshoot button for each code
            troubleshoot_button = customtkinter.CTkButton(
                entry_frame,
                text="Troubleshoot",
                width=100,
                # Pass the code to the command using a lambda
                command=lambda c=code: self.open_troubleshoot_link(c)
            )
            troubleshoot_button.pack(side="right", padx=10, pady=5)

    def open_troubleshoot_link(self, code):
        """Opens a web browser to a specific page for the given DTC."""
        # We'll use obd-codes.com, which has a predictable URL structure
        url = f"https://www.obd-codes.com/{code.lower()}"
        self.update_status(f"Opening browser for {code}...")
        webbrowser.open_new_tab(url)

    def toggle_fullscreen(self, event=None):
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def open_dtc_lookup_window(self):
        if DTC_CODES:
            # Pass the imported dictionary directly to the lookup window
            ToplevelDTC(self, all_codes=DTC_CODES)
        else:
            messagebox.showerror("Error", "DTC database could not be loaded.")
            
    def update_output(self, message, clear=False):
        self.output_text.configure(state="normal")
        if clear: self.output_text.delete('1.0', "end")
        self.output_text.insert("end", message)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def update_status(self, message):
        self.status_var.set(message)

    def reset_buttons(self):
        self.connect_button.configure(state="normal")
        self.disconnect_button.configure(state="disabled")

    def stop_diagnostics(self):
        if not self.stop_thread.is_set():
            self.update_status("Stopping...")
            self.stop_thread.set()

    def save_log(self):
        log_content = self.output_text.get("1.0", "end")
        if not log_content.strip():
            messagebox.showwarning("Warning", "Log is empty.")
            return
        file_path = filedialog.asksaveasfilename(
            initialfile=f"diag_log_{time.strftime('%Y%m%d_%H%M%S')}.txt",
            defaultextension=".txt",
            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            self.update_status(f"Log saved to {file_path}")

    def on_closing(self):
        self.stop_thread.set()
        self.destroy()

# This is the end of the App class. There should be no more functions after this.