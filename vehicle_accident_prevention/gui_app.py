# ============================================================
# gui_app.py — Smart Vehicle Accident Prevention GUI Dashboard
# Powered by Project Chrono 10.0 & Python
# ============================================================

import sys, os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

PROJECT_DIR = r"C:\Simulation System\vehicle_accident_prevention"
sys.path.insert(0, PROJECT_DIR)

from config import (OBSTACLE_POSITION_X, FRICTION_COEFFICIENT, GRAVITY,
                    safe_stopping_distance, kmh_to_ms, GRAPH_OUTPUT_DIR, DATA_OUTPUT_DIR)
from chrono_simulation import ChronoVehicleSimulation
from braking_system import AutoEmergencyBraking


class VehicleSimulationGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Vehicle Accident Prevention & Simulation System — Project Chrono")
        self.geometry("1100x720")
        self.minsize(980, 650)
        self.configure(bg="#1e1e2e")

        # Simulation State
        self.sim = None
        self.aeb = None
        self.adapter = None
        self.is_running = False
        self.current_speed_kmh = 40.0
        self.sim_time = 0.0
        self.dt = 0.02  # 50 Hz UI update
        self.collision_detected = False

        self._setup_styles()
        self._create_layout()
        self.reset_simulation()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#181825", borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground="#cdd6f4",
                        padding=[12, 6], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#89b4fa")],
                  foreground=[("selected", "#11111b")])

    def _create_layout(self):
        # Header
        header = tk.Frame(self, bg="#11111b", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        title_lbl = tk.Label(header, text="🚗 Smart Vehicle Accident Prevention Simulation (Project Chrono 10.0)",
                             font=("Segoe UI", 14, "bold"), fg="#89b4fa", bg="#11111b")
        title_lbl.pack(side=tk.LEFT, padx=15, pady=8)

        status_lbl = tk.Label(header, text="Physics: pychrono.core Active",
                              font=("Segoe UI", 9, "bold"), fg="#a6e3a1", bg="#181825", padx=8, pady=3)
        status_lbl.pack(side=tk.RIGHT, padx=15, pady=10)

        # Tabs: Simulation View & Graphs View
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_sim = tk.Frame(self.notebook, bg="#1e1e2e")
        self.tab_graphs = tk.Frame(self.notebook, bg="#1e1e2e")

        self.notebook.add(self.tab_sim, text="  🖥️ Live 3D/2D Simulation  ")
        self.notebook.add(self.tab_graphs, text="  📊 Analytics & Graphs  ")

        self._build_simulation_tab()
        self._build_graphs_tab()

    def _build_simulation_tab(self):
        # Top Controls Bar
        ctrl_frame = tk.Frame(self.tab_sim, bg="#24273a", bd=1, relief=tk.RIDGE)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(ctrl_frame, text="Select Speed:", font=("Segoe UI", 10, "bold"),
                 fg="#cdd6f4", bg="#24273a").pack(side=tk.LEFT, padx=(10, 5), pady=8)

        for spd in [20, 40, 60]:
            btn = tk.Button(ctrl_frame, text=f"{spd} km/h", font=("Segoe UI", 9, "bold"),
                            bg="#45475a", fg="#cdd6f4", activebackground="#89b4fa",
                            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                            command=lambda s=spd: self.set_speed(s))
            btn.pack(side=tk.LEFT, padx=3, pady=6)

        # Custom Speed Slider
        tk.Label(ctrl_frame, text="Speed Slider:", font=("Segoe UI", 9),
                 fg="#a6adc8", bg="#24273a").pack(side=tk.LEFT, padx=(15, 5))
        self.speed_slider = tk.Scale(ctrl_frame, from_=10, to=80, orient=tk.HORIZONTAL,
                                     bg="#24273a", fg="#cdd6f4", highlightthickness=0,
                                     troughcolor="#313244", length=140,
                                     command=lambda val: self.set_speed(float(val)))
        self.speed_slider.set(self.current_speed_kmh)
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        # Action Buttons
        self.btn_start = tk.Button(ctrl_frame, text="▶ START SIMULATION", font=("Segoe UI", 10, "bold"),
                                   bg="#a6e3a1", fg="#11111b", activebackground="#94e2d5",
                                   relief=tk.FLAT, padx=15, pady=4, cursor="hand2",
                                   command=self.toggle_simulation)
        self.btn_start.pack(side=tk.LEFT, padx=(20, 5))

        btn_reset = tk.Button(ctrl_frame, text="🔄 RESET", font=("Segoe UI", 10, "bold"),
                              bg="#f38ba8", fg="#11111b", activebackground="#eba0ac",
                              relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
                              command=self.reset_simulation)
        btn_reset.pack(side=tk.LEFT, padx=5)

        # Road Canvas (Visual Simulation Area)
        canvas_container = tk.Frame(self.tab_sim, bg="#181825", bd=2, relief=tk.SOLID)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(canvas_container, bg="#181825", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw_scene())

        # Telemetry Dashboard Bar
        tele_frame = tk.Frame(self.tab_sim, bg="#11111b", height=100)
        tele_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # 4 Telemetry Cards
        self.card_speed = self._create_tele_card(tele_frame, "CURRENT SPEED", "40.0 km/h", "#89b4fa")
        self.card_dist = self._create_tele_card(tele_frame, "DISTANCE TO OBSTACLE", "80.0 m", "#f9e2af")
        self.card_pos = self._create_tele_card(tele_frame, "VEHICLE POSITION", "0.0 m", "#cdd6f4")
        self.card_status = self._create_tele_card(tele_frame, "AEB SYSTEM STATUS", "NORMAL CRUISING", "#a6e3a1")

    def _create_tele_card(self, parent, title, val, color):
        card = tk.Frame(parent, bg="#1e1e2e", bd=1, relief=tk.RIDGE)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#a6adc8", bg="#1e1e2e")
        lbl_t.pack(anchor="w", padx=8, pady=(4, 0))
        lbl_v = tk.Label(card, text=val, font=("Segoe UI", 14, "bold"), fg=color, bg="#1e1e2e")
        lbl_v.pack(anchor="w", padx=8, pady=(0, 4))
        return lbl_v

    def _build_graphs_tab(self):
        top_bar = tk.Frame(self.tab_graphs, bg="#24273a")
        top_bar.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(top_bar, text="Select Graph:", font=("Segoe UI", 10, "bold"),
                 fg="#cdd6f4", bg="#24273a").pack(side=tk.LEFT, padx=10)

        graph_files = [
            ("01_speed_vs_time.png", "Speed vs Time"),
            ("02_acceleration_vs_time.png", "Acceleration vs Time"),
            ("03_position_vs_time.png", "Position vs Time"),
            ("04_braking_distance_vs_speed.png", "Braking Distance vs Speed"),
            ("05_scenario_comparison.png", "Scenario Comparison"),
        ]

        for fname, label in graph_files:
            b = tk.Button(top_bar, text=label, font=("Segoe UI", 9),
                          bg="#313244", fg="#cdd6f4", activebackground="#89b4fa",
                          relief=tk.FLAT, padx=8, pady=3, cursor="hand2",
                          command=lambda f=fname: self.load_graph_image(f))
            b.pack(side=tk.LEFT, padx=4)

        self.graph_canvas = tk.Label(self.tab_graphs, bg="#181825", text="Click a graph button above to view",
                                     font=("Segoe UI", 12), fg="#a6adc8")
        self.graph_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.load_graph_image("01_speed_vs_time.png")

    def load_graph_image(self, filename):
        path = os.path.join(GRAPH_OUTPUT_DIR, filename)
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((880, 440), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.graph_canvas.configure(image=photo, text="")
            self.graph_canvas.image = photo
        else:
            self.graph_canvas.configure(text=f"Graph not found: {filename}\nRun simulation first.", image="")

    def set_speed(self, spd):
        self.current_speed_kmh = float(spd)
        self.speed_slider.set(self.current_speed_kmh)
        if not self.is_running:
            self.reset_simulation()

    def reset_simulation(self):
        self.is_running = False
        self.sim_time = 0.0
        self.collision_detected = False
        self.btn_start.configure(text="▶ START SIMULATION", bg="#a6e3a1")

        # Initialize Project Chrono System
        self.sim = ChronoVehicleSimulation(self.current_speed_kmh)
        self.aeb = AutoEmergencyBraking()

        class Adapter:
            def __init__(self, cs):
                self.cs = cs
                self.speed = cs.speed_ms
                self.position_x = 0.0
                self.braking_applied = False
            def get_distance_to_obstacle(self, obs_x):
                return obs_x - self.position_x
            def apply_braking(self, t):
                self.braking_applied = True

        self.adapter = Adapter(self.sim)
        self.update_telemetry(self.current_speed_kmh, OBSTACLE_POSITION_X, 0.0, "READY TO START", "#a6e3a1")
        self.draw_scene()

    def toggle_simulation(self):
        if self.is_running:
            self.is_running = False
            self.btn_start.configure(text="▶ RESUME", bg="#a6e3a1")
        else:
            self.is_running = True
            self.btn_start.configure(text="⏸ PAUSE", bg="#f9e2af")
            self.run_step()

    def run_step(self):
        if not self.is_running:
            return

        pos_x = self.sim.get_vehicle_position()
        spd_ms = self.sim.get_vehicle_speed()
        self.adapter.speed = spd_ms
        self.adapter.position_x = pos_x

        # AEB Logic Check
        aeb_status = self.aeb.check_and_brake(self.adapter, OBSTACLE_POSITION_X, self.sim_time)

        # Collision Check
        dist = OBSTACLE_POSITION_X - pos_x
        if dist <= 1.5 and spd_ms > 0.1:
            self.collision_detected = True
            self.is_running = False
            self.update_telemetry(spd_ms * 3.6, dist, pos_x, "💥 COLLISION OCCURRED!", "#f38ba8")
            self.draw_scene()
            messagebox.showwarning("Collision Detected", f"Vehicle collided with obstacle at {spd_ms*3.6:.1f} km/h!")
            return

        # Advance Chrono dynamics step
        pos_x, spd_ms = self.sim.step(self.dt, self.sim_time, self.adapter.braking_applied)
        self.sim_time += self.dt

        # Check vehicle stopped safely
        if self.adapter.braking_applied and spd_ms <= 0.02:
            self.is_running = False
            self.btn_start.configure(text="✔ COMPLETED", bg="#89b4fa")
            margin = OBSTACLE_POSITION_X - pos_x
            status_text = f"🛑 ACCIDENT PREVENTED! (Margin: {margin:.1f}m)"
            self.update_telemetry(0.0, max(dist, 0.0), pos_x, status_text, "#a6e3a1")
            self.draw_scene()
            messagebox.showinfo("Simulation Result", f"SUCCESS!\nVehicle stopped safely!\nDistance to obstacle: {margin:.2f} meters")
            return

        # Update Telemetry Display
        status_text = "NORMAL CRUISING"
        status_color = "#a6e3a1"
        if aeb_status == "WARNING":
            status_text = "⚠️ WARNING: OBSTACLE AHEAD!"
            status_color = "#f9e2af"
        elif aeb_status == "BRAKING":
            status_text = "🚨 EMERGENCY BRAKING ACTIVE!"
            status_color = "#f38ba8"

        self.update_telemetry(spd_ms * 3.6, dist, pos_x, status_text, status_color)
        self.draw_scene()

        # Next Step
        self.after(int(self.dt * 1000), self.run_step)

    def update_telemetry(self, speed, dist, pos, status, color):
        self.card_speed.configure(text=f"{max(speed, 0.0):.1f} km/h")
        self.card_dist.configure(text=f"{max(dist, 0.0):.1f} m")
        self.card_pos.configure(text=f"{pos:.1f} m")
        self.card_status.configure(text=status, fg=color)

    def draw_scene(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 100 or h < 100:
            return

        # Background Landscape
        c.create_rectangle(0, 0, w, h * 0.45, fill="#181825", outline="")
        c.create_rectangle(0, h * 0.45, w, h, fill="#313244", outline="")  # Ground terrain

        # Road
        road_y_top = h * 0.50
        road_y_bot = h * 0.85
        c.create_rectangle(0, road_y_top, w, road_y_bot, fill="#45475a", outline="#585b70", width=2)

        # Road Center Lane Markings
        dash_y = (road_y_top + road_y_bot) / 2
        for x in range(0, w, 40):
            c.create_line(x, dash_y, x + 20, dash_y, fill="#f9e2af", width=3)

        # Coordinate Scaling: Map 0m to 100m road into canvas width
        max_dist_m = 95.0
        margin_x = 50
        scale = (w - 2 * margin_x) / max_dist_m

        # Obstacle Position
        obs_x_px = margin_x + OBSTACLE_POSITION_X * scale
        obs_w = 25
        obs_h = 45
        obs_y = dash_y - obs_h / 2

        # Draw Obstacle
        c.create_rectangle(obs_x_px, obs_y, obs_x_px + obs_w, obs_y + obs_h,
                           fill="#f38ba8", outline="#eba0ac", width=2)
        c.create_text(obs_x_px + obs_w / 2, obs_y - 12, text="OBSTACLE (80m)",
                      font=("Segoe UI", 9, "bold"), fill="#f38ba8")

        # Vehicle Position
        pos_x_m = self.sim.get_vehicle_position() if self.sim else 0.0
        car_x_px = margin_x + pos_x_m * scale
        car_w = 55
        car_h = 32
        car_y = dash_y - car_h / 2

        # Draw Radar Beam (from vehicle to obstacle)
        if car_x_px < obs_x_px:
            beam_color = "#f38ba8" if (self.adapter and self.adapter.braking_applied) else "#89dceb"
            beam_dash = (4, 4)
            c.create_polygon([car_x_px + car_w, car_y + car_h / 2,
                              obs_x_px, obs_y + 5,
                              obs_x_px, obs_y + obs_h - 5],
                             fill=beam_color, stipple="gray25", outline=beam_color, dash=beam_dash)

        # Draw Car Body
        c.create_rectangle(car_x_px, car_y, car_x_px + car_w, car_y + car_h,
                           fill="#89b4fa", outline="#b4befe", width=2)
        # Car Roof / Windows
        c.create_rectangle(car_x_px + 12, car_y + 4, car_x_px + car_w - 12, car_y + car_h - 4,
                           fill="#11111b", outline="#89b4fa")
        # Headlights
        c.create_oval(car_x_px + car_w - 4, car_y + 3, car_x_px + car_w + 3, car_y + 9, fill="#f9e2af", outline="")
        c.create_oval(car_x_px + car_w - 4, car_y + car_h - 9, car_x_px + car_w + 3, car_y + car_h - 3, fill="#f9e2af", outline="")

        c.create_text(car_x_px + car_w / 2, car_y - 12, text="CAR",
                      font=("Segoe UI", 9, "bold"), fill="#89b4fa")

        # Safety Zone Boundary Marker
        req_stop = safe_stopping_distance(kmh_to_ms(self.current_speed_kmh))
        safe_x_px = obs_x_px - req_stop * scale
        if safe_x_px > margin_x:
            c.create_line(safe_x_px, road_y_top - 5, safe_x_px, road_y_bot + 5,
                          fill="#fab387", dash=(3, 3), width=2)
            c.create_text(safe_x_px, road_y_top - 14, text=f"AEB Zone ({req_stop:.1f}m)",
                          font=("Segoe UI", 8, "bold"), fill="#fab387")


if __name__ == "__main__":
    app = VehicleSimulationGUI()
    app.mainloop()
