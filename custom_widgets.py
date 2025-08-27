# custom_widgets.py
import customtkinter
import math

class Gauge(customtkinter.CTkFrame):
    def __init__(self, *args,
                 label: str = "LABEL",
                 min_value: int = 0,
                 max_value: int = 100,
                 unit: str = "",
                 width: int = 250, # Slightly wider for better spacing
                 height: int = 250,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.min_value = min_value
        self.max_value = max_value
        self.unit = unit
        self.label_text = label

        # Configure the frame to center its contents
        self.pack_propagate(False)

        # --- WIDGETS ---
        # FIX: Added highlightthickness=0 to remove the border icon
        self.canvas = customtkinter.CTkCanvas(self, width=width, height=height-50, bg=self.cget("fg_color")[0], highlightthickness=0)
        self.canvas.pack(pady=(10, 0)) # Pack the canvas at the top

        self.label = customtkinter.CTkLabel(self, text=self.label_text, font=("Arial", 14, "bold"))
        self.label.pack(pady=(5, 10)) # Pack the label below the canvas
        
        # We need to wait for the window to be drawn to get accurate dimensions
        self.after(100, self.initialize_gauge)

    def initialize_gauge(self):
        """Draws the gauge for the first time after the window is created."""
        self.draw_static_elements()
        self.update_value(self.min_value)

    def draw_static_elements(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        center_x, center_y = w / 2, h * 0.9 # Center drawing lower in the canvas
        radius = min(center_x, center_y) * 0.9

        # Draw arcs
        self.canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               start=150, extent=240, style="arc", width=15, outline="#555555")
        
        # Draw tick marks and labels
        for i in range(11):
            angle = 210 - (i * 24)
            rad = math.radians(angle)
            x1 = center_x + radius * math.cos(rad)
            y1 = center_y - radius * math.sin(rad)
            x2 = center_x + radius * 0.9 * math.cos(rad)
            y2 = center_y - radius * 0.9 * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)
            if i % 2 == 0:
                val = self.min_value + (self.max_value - self.min_value) * (i / 10)
                x_text = center_x + radius * 0.7 * math.cos(rad)
                y_text = center_y - radius * 0.7 * math.sin(rad)
                self.canvas.create_text(x_text, y_text, text=f"{int(val/1000)}k" if val >= 1000 else str(int(val)), fill="white", font=("Arial", 10))

    def update_value(self, value):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        center_x, center_y = w / 2, h * 0.9
        radius = min(center_x, center_y) * 0.9
        
        try: numeric_value = float(value)
        except (ValueError, TypeError): numeric_value = self.min_value
        
        clamped_value = max(self.min_value, min(self.max_value, numeric_value))

        self.canvas.delete("dynamic")
        
        percent = (clamped_value - self.min_value) / (self.max_value - self.min_value)
        angle_extent = percent * 240
        self.canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                               start=150, extent=-angle_extent, style="arc", width=15, outline="#1f6aa5", tags="dynamic")
        
        angle = 210 - (percent * 240)
        rad = math.radians(angle)
        x_end = center_x + radius * 0.85 * math.cos(rad)
        y_end = center_y - radius * 0.85 * math.sin(rad)
        self.canvas.create_line(center_x, center_y, x_end, y_end, fill="#1f6aa5", width=3, tags="dynamic")
        self.canvas.create_oval(center_x - 5, center_y - 5, center_x + 5, center_y + 5, fill="#1f6aa5", outline="white", tags="dynamic")
        
        # FIX: Centered the text elements on the canvas
        self.canvas.create_text(center_x, center_y - 20, text=str(int(clamped_value)), fill="white", font=("Arial", 30, "bold"), tags="dynamic")
        self.canvas.create_text(center_x, center_y + 10, text=self.unit, fill="white", font=("Arial", 12), tags="dynamic")