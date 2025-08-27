# Motorcycle Diagnostic Tool 🏍️🔧

A professional-grade, cross-platform desktop application for real-time motorcycle diagnostics. Built with Python and CustomTkinter, this tool provides a modern dashboard interface for monitoring live engine data and retrieving fault codes using a standard ELM327 adapter.

The project is architecturally sound, featuring a separation of concerns between the UI, diagnostic logic, and a full-featured simulator for hardware-free development.

![Motorcycle Diagnostic Tool Screenshot](image_aa8570.png)

---

### ## Features
- **Modern Graphical User Interface:** A sleek and intuitive UI built with CustomTkinter, featuring dark/light modes and theming.
- **Real-Time Dashboard:** Displays live data on four graphical gauges:
  - Engine Speed (RPM)
  - Vehicle Speed (KPH)
  - Coolant Temperature (°C)
  - Engine Load (%)
- **Full-Featured Diagnostics:**
  - **Live Data Streaming:** Continuously polls the ECU for the smoothest possible gauge animation.
  - **Fault Code Scanning:** Retrieves and displays stored Diagnostic Trouble Codes (DTCs) with descriptions.
  - **DTC Lookup Tool:** A separate pop-up window to manually look up fault codes from a comprehensive local database.
- **Configurable & User-Friendly:**
  - **Settings Menu:** A dedicated settings window to easily configure the connection method (Simulator, Wi-Fi, Bluetooth) and adapter address. Settings are saved between sessions.
  - **Data Logging:** Save the results of any diagnostic session to a timestamped `.txt` log file.
  - **Fullscreen Mode:** Press F11 for an immersive, fullscreen dashboard view.

---

### ## Project Structure
The application is organized into logical modules for maintainability and scalability:
- **`main.py`**: The main entry point for the application.
- **`gui_app.py`**: Contains the main `App` class and all CustomTkinter UI code.
- **`diagnostics.py`**: Handles all communication with the OBD-II adapter.
- **`simulator.py`**: Contains the `OBDSimulator` class for hardware-free testing.
- **`custom_widgets.py`**: Defines the reusable `Gauge` widget.
- **`config_manager.py`**: Manages loading and saving user settings to `settings.ini`.
- **`dtc_codes.json`**: A local database of over 400 DTCs and their descriptions.

---

### ## How to Use

1.  **Clone the repository** and install the required libraries (`customtkinter`, `obd`).
2.  **Run for the first time** (`py main.py`) to generate the default `settings.ini` file.
3.  **Configure:** Click the "Settings" button to choose your connection mode (e.g., "Simulator" or "Wi-Fi") and enter your adapter's address.
4.  **Connect:** Click "Connect & Stream" to begin monitoring your vehicle.

---

### ## Final Step: Packaging the Application

The last step is to package the application into a single `.exe` file for easy distribution.

1.  **Install PyInstaller:**
    ```powershell
    pip install pyinstaller
    ```
2.  **Run the Build Command:** From the project's root directory, run the following command in your terminal. This command is crucial as it correctly bundles all your custom modules and data files.
    ```powershell
    pyinstaller --onefile --windowed --add-data "dtc_codes.json;." --add-data "settings.ini;." main.py
    ```
    * `--onefile`: Creates a single executable.
    * `--windowed`: Hides the command-line console.
    * `--add-data`: Bundles the necessary `json` and `ini` files with your application.

Your final, distributable application will be in the `dist` folder. Congratulations on building a complete, professional, and highly functional piece of software!