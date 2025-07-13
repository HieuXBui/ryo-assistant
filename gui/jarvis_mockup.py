import customtkinter as ctk
import tkinter as tk
import math
import time
import random
import tkinter.font as tkfont
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.controller import AssistantController
from core.system_monitor import SystemMonitor
from core.todo_manager import TodoManager

# --- Load Orbitron Font ---
ORBITRON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/Orbitron-Regular.ttf'))
try:
    temp_root = tk.Tk()
    temp_root.withdraw()
    if not "Orbitron" in tkfont.families():
        tkfont.Font(root=temp_root, name="Orbitron", family="Orbitron", size=16, weight="bold")
        temp_root.tk.call("font", "create", "Orbitron", "-family", "Orbitron", "-size", 16, "-weight", "bold")
        temp_root.tk.call("font", "configure", "Orbitron", "-family", "Orbitron", "-size", 16, "-weight", "bold")
        temp_root.tk.call("font", "create", "OrbitronFile", "-family", "Orbitron", "-size", 16, "-weight", "bold", "-file", ORBITRON_PATH)
    temp_root.destroy()
except Exception as e:
    print(f"[WARN] Could not load Orbitron font: {e}")

# --- Enhanced Color Palette and Fonts ---
BG = "#10131a"
CYAN = "#00fff7"
BLUE = "#1a9fff"
TEAL = "#00e6c3"
WHITE = "#e0e1dd"
MUTED = "#8d99ae"
GLOW = CYAN

FONT_FUTURE = ("Orbitron", 18, "bold")
FONT_LABEL = ("Orbitron", 13)
FONT_MONO = ("Menlo", 10)

# --- Draggable Panel Mixin ---
class DraggablePanel:
    def make_draggable_handle(self, handle, panel):
        self._bind_drag_recursive_handle(handle, panel)
        if not hasattr(self, '_drag_data'): self._drag_data = {}

    def _bind_drag_recursive_handle(self, widget, panel):
        widget.bind("<Button-1>", lambda e: self._on_drag_start(e, panel))
        widget.bind("<B1-Motion>", lambda e: self._on_drag_motion(e, panel))
        widget.bind("<ButtonRelease-1>", lambda e: self._on_drag_stop(e, panel))
        for child in getattr(widget, 'winfo_children', lambda:[])():
            self._bind_drag_recursive_handle(child, panel)

    def _on_drag_start(self, event, panel):
        self._drag_data[panel] = {
            "x": event.x_root - panel.winfo_rootx(),
            "y": event.y_root - panel.winfo_rooty(),
            "dragging": True
        }

    def _on_drag_motion(self, event, panel):
        if self._drag_data.get(panel, {}).get("dragging", False):
            x = event.x_root - self._drag_data[panel]["x"] - panel.master.winfo_rootx()
            y = event.y_root - self._drag_data[panel]["y"] - panel.master.winfo_rooty()
            panel.place(x=x, y=y)

    def _on_drag_stop(self, event, panel):
        if panel in self._drag_data:
            self._drag_data[panel]["dragging"] = False

class DisplayOrb(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=180, height=180, bg=BG, highlightthickness=0, **kwargs)
        self.radius = 70
        self.animate()

    def animate(self):
        self.delete("all")
        t = time.time()
        # Outer pulsing ring
        pulse = self.radius + 12 * math.sin(t * 2)
        self.create_oval(90-pulse, 90-pulse, 90+pulse, 90+pulse,
                         outline=CYAN, width=5)
        # Main orb
        self.create_oval(90-self.radius, 90-self.radius, 90+self.radius, 90+self.radius,
                         fill=BG, outline=BLUE, width=7)
        # Inner glow
        self.create_oval(90-self.radius//2, 90-self.radius//2, 90+self.radius//2, 90+self.radius//2,
                         fill=CYAN, outline="", width=0, stipple="gray25")
        # Center dot
        self.create_oval(85, 85, 95, 95, fill=WHITE, outline=CYAN, width=2)
        self.after(40, self.animate)

class MicVisualizer(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=140, height=32, bg=BG, highlightthickness=0, **kwargs)
        self.animate()

    def animate(self):
        self.delete("all")
        for i in range(24):
            h = 10 + 12 * random.random() * (0.5 + 0.5 * math.sin(time.time()*2 + i))
            x = 6 + i*5
            self.create_rectangle(x, 28-h, x+3, 28, fill=CYAN, outline="")
        self.after(60, self.animate)

class JarvisUI(ctk.CTk, DraggablePanel):
    """
    JARVIS-style GUI, now ready for backend integration.
    Accepts an AssistantController instance and exposes methods for status/mute updates.
    All visual mockup panels are preserved and clearly commented for future development.
    """
    def __init__(self, controller: AssistantController):
        super().__init__()
        self.controller = controller
        self.title("Ryo JARVIS HUD Prototype")
        self.geometry("1280x820")
        
        # --- Model Switcher Dropdown ---
        self.model_var = ctk.StringVar(value=self.controller.model_switcher.active_model_name)
        self.model_switcher = ctk.CTkOptionMenu(
            self,
            values=["Ollama", "Gemini"],
            variable=self.model_var,
            command=self._on_model_switch,
            width=120,
            font=("Orbitron", 14),
            fg_color=BLUE,
            button_color=BLUE,
            button_hover_color=CYAN,
            text_color=BG
        )
        self.model_switcher.place(x=160, y=20)
        
        # --- Transparency Options ---
        # Option 1: Semi-transparent background (0.0 = fully transparent, 1.0 = fully opaque)
        self.attributes('-alpha', 0.9)  # 90% opacity
        
        # Option 2: For macOS - make background transparent (requires Tk 8.6+)
        # self.configure(bg='systemTransparent')  # Uncomment for fully transparent background
        
        # Option 3: Use a very dark, semi-transparent background
        self.configure(fg_color=BG)
        
        # Initialize system monitor
        self.system_monitor = SystemMonitor()
        self.system_monitor.start_monitoring()
        
        # Use the controller's todo manager to ensure we're working with the same data
        self.todo_manager = self.controller.todo_manager
        
        self.panel_positions = {}
        self.panels = {}
        self._build_layout()
        self._add_reset_button()
        # Example: self.status_label = ctk.CTkLabel(...)
        # Add a mute button and status label, wired to controller
        self.status_var = ctk.StringVar(value=f"Status: {self.controller.get_status()}")
        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, font=("Orbitron", 16), text_color="#00fff7", fg_color=BG)
        self.status_label.place(x=40, y=780)
        # Register mute callback so GUI updates when hotkey is used
        self.controller.set_mute_callback(self._on_mute_changed)
        # Register status callback so GUI updates when backend status changes
        self.controller.set_status_callback(self._on_status_changed)
        # --- Main response textbox for recognized speech and AI responses ---
        self.response_box = ctk.CTkTextbox(self, width=600, height=60, font=("Orbitron", 16), fg_color="#181e29", text_color="#00fff7")
        self.response_box.place(x=340, y=720)
        self._set_response_box("Say 'Hey Ryo' to begin...")
        # Register transcription callback
        self.controller.set_transcription_callback(self._on_transcription)
        # Register GUI refresh callback for todo updates
        self.controller.set_gui_refresh_callback(self._refresh_todo_list)
        # --- Placeholders ---
        # All mockup panels (weather, hacking console, AI core, etc.) remain unchanged
        # Add comments like:
        # # Placeholder: Weather panel (not yet implemented)
        # ...
        # Bind window close event to cleanup
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _add_reset_button(self):
        reset_btn = ctk.CTkButton(self, text="Reset Layout", fg_color=BLUE, text_color=BG, font=FONT_LABEL, command=self._reset_layout)
        reset_btn.place(x=20, y=20)
        
        # Add wake word restart button
        restart_wake_btn = ctk.CTkButton(self, text="Restart Wake Word", fg_color=TEAL, text_color=BG, font=FONT_LABEL, command=self._restart_wake_word)
        restart_wake_btn.place(x=20, y=100)
        
        # Add transparency toggle button
        self.transparency_level = 0.9  # Start with 90% opacity
        transparency_btn = ctk.CTkButton(self, text="Toggle Transparency", fg_color=TEAL, text_color=BG, font=FONT_LABEL, command=self._toggle_transparency)
        transparency_btn.place(x=20, y=60)

    def _restart_wake_word(self):
        """Manually restart wake word detection"""
        self.controller.force_restart_wake_word()

    def _reset_layout(self):
        for name, panel in self.panels.items():
            x, y = self.panel_positions[name]
            panel.place(x=x, y=y)
    
    def _toggle_transparency(self):
        """Toggle between different transparency levels"""
        if self.transparency_level == 0.9:
            self.transparency_level = 0.7  # More transparent
        elif self.transparency_level == 0.7:
            self.transparency_level = 0.5  # Even more transparent
        elif self.transparency_level == 0.5:
            self.transparency_level = 0.3  # Very transparent
        elif self.transparency_level == 0.3:
            self.transparency_level = 0.9  # Back to original
        self.attributes('-alpha', self.transparency_level)

    def _build_layout(self):
        # --- Central Orb ---
        center_x = 640
        self.display_orb = DisplayOrb(self)
        self.display_orb.place(x=center_x-90, y=60)  # orb is 180px wide
        ctk.CTkLabel(self, text="RYO AI", font=("Orbitron", 22, "bold"), text_color=CYAN, fg_color=BG).place(x=center_x, y=210, anchor="center")

        # --- Sci-Fi Welcome Text ---
        ctk.CTkLabel(self, text="Hello, Hieu", font=("Orbitron", 32, "bold"), text_color=CYAN, fg_color=BG).place(x=center_x, y=400, anchor="center")

        # Mic Visualizer
        self.mic_viz = MicVisualizer(self)
        self.mic_viz.place(x=center_x-60, y=260)  # visualizer is 120px wide
        ctk.CTkLabel(self, text="Listening Status", font=FONT_LABEL, text_color=TEAL, fg_color=BG).place(x=center_x, y=300, anchor="center")

        # --- Modular Panels (Draggable, Transparent, with Handle) ---
        def glassy_panel(*args, **kwargs):
            return ctk.CTkFrame(*args, fg_color="#181e29", corner_radius=18, border_width=2, border_color=CYAN, **kwargs)
        def handle_bar(parent, text):
            bar = ctk.CTkFrame(parent, height=28, fg_color=CYAN, corner_radius=12)
            bar.pack(fill="x", pady=(0, 4))
            ctk.CTkLabel(bar, text=text, font=FONT_FUTURE, text_color=BG).pack(side="left", padx=12)
            return bar

        # System Info Panel
        sys_panel = glassy_panel(self, width=260, height=230)
        sys_panel.place(x=30, y=100)
        sys_handle = handle_bar(sys_panel, "SYSTEM INFO")
        self.make_draggable_handle(sys_handle, sys_panel)
        
        # Create system info labels
        self.sys_labels = {}
        self.sys_progress_bars = {}
        
        # CPU Info
        self.sys_labels['cpu'] = ctk.CTkLabel(sys_panel, text="PROCESSOR: 0.0%", font=FONT_LABEL, text_color=WHITE, justify="left")
        self.sys_labels['cpu'].pack(pady=1, padx=10, anchor="w")
        self.sys_progress_bars['cpu'] = ctk.CTkProgressBar(sys_panel, width=180, height=8, progress_color=CYAN)
        self.sys_progress_bars['cpu'].pack(pady=2)
        
        # Memory Info
        self.sys_labels['memory'] = ctk.CTkLabel(sys_panel, text="MEMORY: 0.0GB/0.0GB", font=FONT_LABEL, text_color=WHITE, justify="left")
        self.sys_labels['memory'].pack(pady=1, padx=10, anchor="w")
        self.sys_progress_bars['memory'] = ctk.CTkProgressBar(sys_panel, width=180, height=8, progress_color=CYAN)
        self.sys_progress_bars['memory'].pack(pady=2)
        
        # Battery Info
        self.sys_labels['battery'] = ctk.CTkLabel(sys_panel, text="POWER: 0% (PLUGGED)", font=FONT_LABEL, text_color=WHITE, justify="left")
        self.sys_labels['battery'].pack(pady=1, padx=10, anchor="w")
        self.sys_progress_bars['battery'] = ctk.CTkProgressBar(sys_panel, width=180, height=8, progress_color=CYAN)
        self.sys_progress_bars['battery'].pack(pady=2)
        
        # Temperature Info
        self.sys_labels['temp'] = ctk.CTkLabel(sys_panel, text="THERMAL: 0.0°C", font=FONT_LABEL, text_color=WHITE, justify="left")
        self.sys_labels['temp'].pack(pady=1, padx=10, anchor="w")
        self.sys_progress_bars['temp'] = ctk.CTkProgressBar(sys_panel, width=180, height=8, progress_color=CYAN)
        self.sys_progress_bars['temp'].pack(pady=2)
        
        # Storage Info
        self.sys_labels['disk'] = ctk.CTkLabel(sys_panel, text="STORAGE: 0.0GB/0.0GB", font=FONT_LABEL, text_color=WHITE, justify="left")
        self.sys_labels['disk'].pack(pady=1, padx=10, anchor="w")
        self.sys_progress_bars['disk'] = ctk.CTkProgressBar(sys_panel, width=180, height=8, progress_color=CYAN)
        self.sys_progress_bars['disk'].pack(pady=2)
        
        # Uptime Info
        self.sys_labels['uptime'] = ctk.CTkLabel(sys_panel, text="ONLINE: 00:00", font=FONT_LABEL, text_color=WHITE, justify="left")
        self.sys_labels['uptime'].pack(pady=1, padx=10, anchor="w")
        
        self.panels['sys'] = sys_panel
        self.panel_positions['sys'] = (30, 100)
        
        # Start updating system info
        self._update_system_info()

        # Notes Panel
        notes_panel = glassy_panel(self, width=320, height=85)
        notes_panel.place(x=270, y=80)
        notes_handle = handle_bar(notes_panel, "NOTES")
        self.make_draggable_handle(notes_handle, notes_panel)
        ctk.CTkTextbox(notes_panel, width=240, height=80, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=2)
        notes_panel.winfo_children()[-1].insert("1.0", "- Buy groceries\n- Call Dr. Banner\n- Project: Ryo v2\n- Meeting 14:00")
        self.panels['notes'] = notes_panel
        self.panel_positions['notes'] = (270, 80)

        # To-Do Panel
        todo_panel = glassy_panel(self, width=320, height=200)
        todo_panel.place(x=770, y=80)
        todo_handle = handle_bar(todo_panel, "TASK MANAGER")
        self.make_draggable_handle(todo_handle, todo_panel)
        
        # Todo input frame
        todo_input_frame = ctk.CTkFrame(todo_panel, fg_color="transparent")
        todo_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.todo_entry = ctk.CTkEntry(
            todo_input_frame, 
            placeholder_text="Enter new task...",
            font=FONT_LABEL,
            height=30
        )
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", self._add_todo)
        
        add_btn = ctk.CTkButton(
            todo_input_frame,
            text="ADD",
            font=FONT_LABEL,
            width=60,
            height=30,
            fg_color=TEAL,
            text_color=BG,
            command=self._add_todo
        )
        add_btn.pack(side="right")
        
        # Todo list frame with scroll
        self.todo_list_frame = ctk.CTkScrollableFrame(
            todo_panel, 
            width=280, 
            height=120,
            fg_color="transparent"
        )
        self.todo_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Todo items will be stored here
        self.todo_items = {}
        
        # Stats and controls frame
        stats_frame = ctk.CTkFrame(todo_panel, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        # Stats label
        self.todo_stats = ctk.CTkLabel(
            stats_frame, 
            text="TASKS: 0 | COMPLETED: 0", 
            font=FONT_LABEL, 
            text_color=TEAL
        )
        self.todo_stats.pack(side="left")
        
        # Clear completed button
        clear_btn = ctk.CTkButton(
            stats_frame,
            text="CLEAR DONE",
            font=FONT_LABEL,
            width=80,
            height=25,
            fg_color="#ff4444",
            text_color=WHITE,
            command=self._clear_completed_todos
        )
        clear_btn.pack(side="right")
        
        self.panels['todo'] = todo_panel
        self.panel_positions['todo'] = (770, 80)
        
        # Load and display todos
        self._refresh_todo_list()

        # Command Log Panel
        log_panel = glassy_panel(self, width=340, height=110)
        log_panel.place(x=1000, y=80)
        log_handle = handle_bar(log_panel, "COMMAND LOG")
        self.make_draggable_handle(log_handle, log_panel)
        ctk.CTkTextbox(log_panel, width=260, height=60, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=2)
        log_panel.winfo_children()[-1].insert("1.0", "[LOG 00:42:01] Scanning disk...\n[LOG 00:42:03] Listening for input...\n[LOG 00:42:05] User: 'What's the weather?'\n[LOG 00:42:06] Ryo: '22°C, Clear.'")
        self.panels['log'] = log_panel
        self.panel_positions['log'] = (1000, 80)

        # --- Floating HUD Widgets (Draggable, with Handle) ---
        hud1 = glassy_panel(self, width=220, height=80)
        hud1.place(x=60, y=650)
        hud1_handle = handle_bar(hud1, "MIC/NET STATUS")
        self.make_draggable_handle(hud1_handle, hud1)
        ctk.CTkLabel(hud1, text="MIC: ON\nNET: OK", font=FONT_LABEL, text_color=CYAN).pack(pady=4)
        ctk.CTkProgressBar(hud1, width=160, height=14, progress_color=CYAN).pack(pady=7)
        self.panels['hud1'] = hud1
        self.panel_positions['hud1'] = (60, 650)

        hud2 = glassy_panel(self, width=260, height=80)
        hud2.place(x=1050, y=700)
        hud2_handle = handle_bar(hud2, "SYSTEM LOAD")
        self.make_draggable_handle(hud2_handle, hud2)
        ctk.CTkProgressBar(hud2, width=200, height=14, progress_color=BLUE).pack(pady=18)
        self.panels['hud2'] = hud2
        self.panel_positions['hud2'] = (1050, 700)

        # --- Quick Links Panel (Draggable, with Handle) ---
        quick_panel = glassy_panel(self, width=220, height=220)
        quick_panel.place(x=60, y=400)
        quick_handle = handle_bar(quick_panel, "QUICK LAUNCH")
        self.make_draggable_handle(quick_handle, quick_panel)
        for app in ["VLC", "Paint", "Word", "Discord", "Terminal"]:
            ctk.CTkButton(quick_panel, text=app, fg_color=TEAL, text_color=BG, width=140, height=34, font=FONT_LABEL).pack(pady=3)
        self.panels['quick'] = quick_panel
        self.panel_positions['quick'] = (60, 400)

        # --- Communication/Side Panel (Draggable, with Handle) ---
        comm_panel = glassy_panel(self, width=220, height=220)
        comm_panel.place(x=1050, y=400)
        comm_handle = handle_bar(comm_panel, "COMMUNICATION")
        self.make_draggable_handle(comm_handle, comm_panel)
        ctk.CTkTextbox(comm_panel, width=180, height=140, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=7)
        comm_panel.winfo_children()[-1].insert("1.0", "[13:36] SYSTEM ONLINE\n[13:37] RYO READY\n[13:38] USER LOGGED IN")
        self.panels['comm'] = comm_panel
        self.panel_positions['comm'] = (1050, 400)

        # --- Mic/Audio Status Indicator (Clickable) ---
        initial_mute_text = "● MUTED" if self.controller.is_muted() else "● UNMUTE"
        self.mic_status = ctk.CTkButton(
            self, 
            text=initial_mute_text, 
            font=FONT_FUTURE, 
            text_color=CYAN, 
            fg_color=BG,
            hover_color=BG,
            command=self.toggle_mute,
            width=120,
            height=40
        )
        self.mic_status.place(x=center_x, y=350, anchor="center")

    def set_status(self, status):
        self.controller.set_status(status)
        # Use after to ensure thread safety
        self.after(0, lambda: self.status_var.set(f"Status: {status}"))

    def _on_status_changed(self, status):
        # Called from backend thread, so use after for thread safety
        self.after(0, lambda: self.status_var.set(f"Status: {status}"))

    def toggle_mute(self):
        print(f"[DEBUG] GUI toggle_mute called")
        muted = self.controller.toggle_mute()
        print(f"[DEBUG] GUI toggle_mute result: {muted}")
        self._on_mute_changed(muted)

    def _on_mute_changed(self, muted):
        """Update the mute button text based on mute state"""
        if muted:
            self.mic_status.configure(text="● MUTED")
        else:
            self.mic_status.configure(text="● UNMUTE")
    
    def _update_system_info(self):
        """Update system info display with real data"""
        try:
            # Get system info from monitor
            info = self.system_monitor.get_system_info_text()
            progress_values = self.system_monitor.get_progress_values()
            
            # Update labels and progress bars
            for metric in ['cpu', 'memory', 'battery', 'temp', 'disk', 'uptime']:
                if metric in info and metric in self.sys_labels:
                    self.sys_labels[metric].configure(text=info[metric])
                    
                    # Update progress bar if it exists
                    if metric in self.sys_progress_bars and metric in progress_values:
                        value = progress_values[metric] / 100.0
                        self.sys_progress_bars[metric].set(value)
                        
                        # Update color based on status
                        color = self.system_monitor.get_status_color(metric, progress_values[metric])
                        self.sys_progress_bars[metric].configure(progress_color=color)
            
            # Schedule next update
            self.after(2000, self._update_system_info)
            
        except Exception as e:
            print(f"[ERROR] Failed to update system info: {e}")
            # Retry in 5 seconds if there's an error
            self.after(5000, self._update_system_info)
    
    def _add_todo(self, event=None):
        """Add a new todo item"""
        text = self.todo_entry.get().strip()
        if text:
            todo = self.todo_manager.add_todo(text)
            self.todo_entry.delete(0, "end")
            self._refresh_todo_list()
    
    def _delete_todo(self, todo_id):
        """Delete a todo item"""
        self.todo_manager.delete_todo(todo_id)
        self._refresh_todo_list()
    
    def _toggle_todo(self, todo_id):
        """Toggle todo completion status"""
        self.todo_manager.toggle_todo(todo_id)
        self._refresh_todo_list()
    
    def _clear_completed_todos(self):
        """Clear all completed todos"""
        self.todo_manager.clear_completed()
        self._refresh_todo_list()
    
    def _refresh_todo_list(self):
        """Refresh the todo list display"""
        print(f"[DEBUG] Refreshing todo list")
        # Clear existing items
        for widget in self.todo_list_frame.winfo_children():
            widget.destroy()
        
        # Clear stored items
        self.todo_items.clear()
        
        # Get todos from manager
        todos = self.todo_manager.get_todos()
        print(f"[DEBUG] Found {len(todos)} todos")
        
        if not todos:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.todo_list_frame,
                text="No tasks assigned",
                font=FONT_LABEL,
                text_color=MUTED
            )
            empty_label.pack(pady=20)
        else:
            # Create todo items
            for todo in todos:
                print(f"[DEBUG] Creating todo item: {todo['text']}")
                self._create_todo_item(todo)
        
        # Update stats
        stats = self.todo_manager.get_stats()
        self.todo_stats.configure(
            text=f"TASKS: {stats['total']} | COMPLETED: {stats['completed']}"
        )
        print(f"[DEBUG] Updated stats: {stats['total']} total, {stats['completed']} completed")
    
    def _create_todo_item(self, todo):
        """Create a todo item widget"""
        # Create frame for this todo
        item_frame = ctk.CTkFrame(self.todo_list_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=2)
        
        # Toggle button (checkbox)
        toggle_btn = ctk.CTkButton(
            item_frame,
            text="✓" if todo['completed'] else "○",
            width=25,
            height=25,
            font=FONT_LABEL,
            fg_color=TEAL if todo['completed'] else BG,
            text_color=BG if todo['completed'] else TEAL,
            command=lambda: self._toggle_todo(todo['id'])
        )
        toggle_btn.pack(side="left", padx=(0, 5))
        
        # Todo text label
        text_color = MUTED if todo['completed'] else WHITE
        text_label = ctk.CTkLabel(
            item_frame,
            text=todo['text'],
            font=FONT_LABEL,
            text_color=text_color,
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            item_frame,
            text="×",
            width=25,
            height=25,
            font=FONT_LABEL,
            fg_color="#ff4444",
            text_color=WHITE,
            command=lambda: self._delete_todo(todo['id'])
        )
        delete_btn.pack(side="right")
        
        # Store reference
        self.todo_items[todo['id']] = {
            'frame': item_frame,
            'toggle': toggle_btn,
            'label': text_label,
            'delete': delete_btn
        }

    def _set_response_box(self, text):
        self.response_box.configure(state="normal")
        self.response_box.delete("1.0", "end")
        self.response_box.insert("1.0", text)
        self.response_box.configure(state="disabled")

    def _on_transcription(self, text):
        # If this is the wake word detected message, clear the prompt
        if "Wake word detected" in text:
            self.after(0, lambda: self._set_response_box("Listening..."))
        # If this is a user transcription, show it
        elif text.startswith("You said: "):
            user_text = text[len("You said: "):]
            self.after(0, lambda: self._set_response_box(user_text))
        # If this is an AI response, replace the box with the response
        elif text.startswith("Ryo: "):
            ai_text = text[len("Ryo: "):]
            self.after(0, lambda: self._set_response_box(ai_text))
        # Otherwise, just show the text
        else:
            self.after(0, lambda: self._set_response_box(text))

    def _on_close(self):
        # Stop system monitoring
        try:
            self.system_monitor.stop_monitoring()
        except Exception:
            pass
            
        # Destroy the GUI immediately
        self.destroy()
        # Stop TTS and background processes in a background thread to avoid freezing
        import threading
        def cleanup():
            try:
                self.controller.tts_speaker.stop()
            except Exception:
                pass
            try:
                self.controller.stop_wake_word()
            except Exception:
                pass
        threading.Thread(target=cleanup, daemon=True).start()

    def _on_model_switch(self, value):
        self.controller.model_switcher.set_active_model(value)
        self.model_var.set(value)

if __name__ == "__main__":
    controller = AssistantController()
    app = JarvisUI(controller)
    app.mainloop() 