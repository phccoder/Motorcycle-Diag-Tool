# Motorcycle Multi-Brand Diagnostic Tool 🏍️🔧

A user-friendly desktop application for reading live engine data and checking trouble codes on modern Honda, Yamaha, and Suzuki motorcycles. Built with Python and Tkinter, this tool uses a standard ELM327 adapter to provide real-time diagnostics.

This project features a fully functional simulator for development and testing without needing physical hardware.



---

### ## Features
- **Graphical User Interface:** An intuitive and easy-to-use interface built with Tkinter.
- **Live Data Streaming:** Continuously polls and displays real-time sensor data, including:
  - Engine Speed (RPM)
  - Coolant Temperature
  - Vehicle Speed (KPH)
- **Fault Code Scanning:** Reads and displays any stored Diagnostic Trouble Codes (DTCs) after the live stream is stopped.
- **Data Logging:** Save the results of any diagnostic session to a timestamped `.txt` log file.
- **Advanced Simulator:** Run the application in a full simulator mode, which uses a comprehensive local database of DTCs for realistic testing without any hardware.
- **Multi-Brand Support:** Designed for use with Honda, Yamaha, and Suzuki motorcycles (requires brand-specific adapter cables).

---

### ## Hardware Requirements
To use this tool with a real motorcycle, you will need:

1.  **ELM327 V1.5 Adapter:** A high-quality **V1.5** adapter is strongly recommended. The connection type can be Wi-Fi, Bluetooth, or USB.
2.  **Motorcycle Adapter Cables:** A set of cables to connect the 16-pin ELM327 adapter to your motorcycle's diagnostic port (e.g., Honda 4-pin, Yamaha 3/4-pin, Suzuki 6-pin).

---

### ## Software Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/phccoder/Motorcycle-Diag-Tool.git](https://github.com/phccoder/Motorcycle-Diag-Tool.git)
    cd Motorcycle-Diag-Tool
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Install the required Python libraries:**
    ```bash
    pip install obd
    ```

---

### ## How to Use

#### **Simulator Mode (No Hardware Needed)**
1.  Open the `gui_diag_tool.py` script.
2.  Ensure the configuration switch at the top is set to `SIMULATOR_MODE = True`.
3.  Run the script from your terminal:
    ```powershell
    py gui_diag_tool.py
    ```
4.  Click **"Connect & Stream"** to see the simulator in action.

#### **Real Hardware Mode**
1.  **Connect the Hardware:**
    - Connect the appropriate adapter cable to your motorcycle's diagnostic port.
    - Plug in the ELM327 adapter.
    - Connect the adapter to your computer (Wi-Fi/Bluetooth/USB).
    - Turn your motorcycle's ignition to **ON**.
2.  **Configure the Script:**
    - Open `gui_diag_tool.py`.
    - Set `SIMULATOR_MODE = False`.
    - If using a Wi-Fi or Bluetooth adapter, update the connection string in the code (e.g., `obd.OBD("tcp://...")` or `obd.OBD("COM3")`).
3.  **Run the application.**

---

### ## Project Utilities

This repository also contains utility scripts:

-   **`create_json_from_pdf_text.py`**: A one-time script used to parse the provided PDF text data into the `dtc_codes.json` file.
-   **`dtc_simulator.py`**: A simple command-line tool to quickly test the `dtc_codes.json` file by printing random codes to the terminal.