# === Ryo AI Assistant - Main GUI Application ===
# This file builds and manages the main user interface for the assistant
# using the 'customtkinter' library, which provides modern-looking widgets.

# --- Step 1: Import Necessary Libraries ---

# 'customtkinter' is a UI library based on Tkinter, but with more customization options.
# We use the alias 'ctk' by convention.
import customtkinter as ctk
import tkinter as tk
import math
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the color theme and font settings from our central configuration file.
from core import config
from core.config import THEME
import random

# --- Enhanced Color Palette and Fonts ---
BG = "#10131a"
CYAN = "#00fff7"
BLUE = "#1a9fff"
TEAL = "#00e6c3"
WHITE = "#e0e1dd"
MUTED = "#8d99ae"
GLOW = CYAN

FONT_FUTURE = (THEME["FONT_NAME"], 16, "bold")
FONT_LABEL = (THEME["FONT_NAME"], 12)
FONT_MONO = (THEME["FONT_NAME"], 10)

class DisplayOrb(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=140, height=140, bg=BG, highlightthickness=0, **kwargs)
        self.radius = 55
        self.animate()

    def animate(self):
        self.delete("all")
        t = time.time()
        # Outer pulsing ring
        pulse = self.radius + 8 * math.sin(t * 2)
        self.create_oval(70-pulse, 70-pulse, 70+pulse, 70+pulse,
                         outline=CYAN, width=4)
        # Main orb
        self.create_oval(70-self.radius, 70-self.radius, 70+self.radius, 70+self.radius,
                         fill=BG, outline=BLUE, width=5)
        # Inner glow
        self.create_oval(70-self.radius//2, 70-self.radius//2, 70+self.radius//2, 70+self.radius//2,
                         fill=CYAN, outline="", width=0, stipple="gray25")
        # Center dot
        self.create_oval(65, 65, 75, 75, fill=WHITE, outline=CYAN, width=2)
        self.after(40, self.animate)

class MicVisualizer(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=120, height=30, bg=BG, highlightthickness=0, **kwargs)
        self.animate()

    def animate(self):
        self.delete("all")
        for i in range(20):
            h = 10 + 10 * random.random() * (0.5 + 0.5 * math.sin(time.time()*2 + i))
            x = 5 + i*5
            self.create_rectangle(x, 25-h, x+3, 25, fill=CYAN, outline="")
        self.after(60, self.animate)

# --- Main Application Class (RyoApp) ---

# Our main application class inherits from ctk.CTk, which is the main window object.
class RyoApp(ctk.CTk):
    """The main graphical user interface for the Ryo Assistant."""

    # The constructor, called when the application starts.
    def __init__(self, assistant_core):
        """Initializes the main application window and all its widgets."""
        # Initialize the parent CTk class.
        super().__init__()

        # Store a reference to the main RyoCore logic object.
        # This allows the GUI to call core functions (like changing the AI model).
        self.assistant_core = assistant_core

        # --- Window Configuration ---
        self.title("Ryo AI Assistant")
        self.geometry("400x600") # Set the initial size of the window.
        self.configure(fg_color=THEME["BG_COLOR"]) # Set the background color.
        self.attributes("-alpha", 0.98) # Make the window slightly transparent.

        # --- Graceful Shutdown --- 
        # This ensures that when the user closes the window, our custom
        # on_closing method is called to clean up background threads.
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Set the overall appearance mode for all widgets.
        ctk.set_appearance_mode("dark")

        # --- Main Frame ---
        # A frame is a container to group and organize other widgets.
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="RYO ASSISTANT", 
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=24, weight="bold"),
            text_color=THEME["HIGHLIGHT_COLOR"]
        )
        self.title_label.pack(pady=(0, 10))

        # --- Tab View for Assistant and To-Do List ---
        self.tab_view = ctk.CTkTabview(self.main_frame, fg_color=THEME["ACCENT_COLOR"])
        self.tab_view.pack(pady=10, fill="both", expand=True)
        self.tab_view.add("Assistant")
        self.tab_view.add("To-Do List")

        # --- Create Tab Content ---
        # We delegate the creation of widgets within each tab to separate methods
        # to keep the __init__ method clean and organized.
        self._create_assistant_tab()
        self._create_todo_tab()

        # --- Enhanced Sci-Fi Layout ---
        # Central Orb
        self.display_orb = DisplayOrb(self.main_frame)
        self.display_orb.pack(pady=(10, 0))
        ctk.CTkLabel(self.main_frame, text="AI CORE", font=FONT_FUTURE, text_color=CYAN, fg_color=BG).pack(pady=(0, 10))

        # Mic Visualizer
        self.mic_viz = MicVisualizer(self.main_frame)
        self.mic_viz.pack(pady=(0, 10))
        ctk.CTkLabel(self.main_frame, text="Listening Status", font=FONT_LABEL, text_color=TEAL).pack(pady=(0, 10))

        # --- Modular Panels ---
        panels_frame = ctk.CTkFrame(self.main_frame, fg_color="#151a22", corner_radius=18)
        panels_frame.pack(fill="both", expand=True, pady=10)

        # System Info Panel
        sys_panel = ctk.CTkFrame(panels_frame, width=180, height=120, fg_color="#181e29", corner_radius=14)
        sys_panel.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(sys_panel, text="SYSTEM INFO", font=FONT_FUTURE, text_color=CYAN).pack(pady=(10,2))
        ctk.CTkLabel(sys_panel, text=f"CPU: 23%\nRAM: 8.2GB/16GB\nBattery: 97%\nOS: macOS 14", font=FONT_LABEL, text_color=WHITE, justify="left").pack(pady=2)
        ctk.CTkProgressBar(sys_panel, width=120, height=10, progress_color=CYAN).pack(pady=8)

        # Notes Panel
        notes_panel = ctk.CTkFrame(panels_frame, width=220, height=120, fg_color="#181e29", corner_radius=14)
        notes_panel.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(notes_panel, text="NOTES", font=FONT_FUTURE, text_color=CYAN).pack(pady=(10,2))
        ctk.CTkTextbox(notes_panel, width=180, height=60, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=2)
        notes_panel.winfo_children()[-1].insert("1.0", "- Buy groceries\n- Call Dr. Banner\n- Project: Ryo v2\n- Meeting 14:00")

        # To-Do Panel
        todo_panel = ctk.CTkFrame(panels_frame, width=220, height=120, fg_color="#181e29", corner_radius=14)
        todo_panel.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(todo_panel, text="TO-DO LIST", font=FONT_FUTURE, text_color=CYAN).pack(pady=(10,2))
        for item in ["[ ] Finish GUI mockup", "[x] Refactor core", "[ ] Add weather API", "[ ] Test TTS"]:
            ctk.CTkLabel(todo_panel, text=item, font=FONT_LABEL, text_color=TEAL if '[x]' in item else CYAN).pack(anchor="w", padx=20)

        # Command Log Panel
        log_panel = ctk.CTkFrame(self.main_frame, width=400, height=80, fg_color="#181e29", corner_radius=14)
        log_panel.pack(pady=(10, 0), fill="x")
        ctk.CTkLabel(log_panel, text="COMMAND LOG", font=FONT_FUTURE, text_color=CYAN).pack(pady=(5,2))
        ctk.CTkTextbox(log_panel, width=360, height=40, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=2)
        log_panel.winfo_children()[-1].insert("1.0", "[LOG 00:42:01] Scanning disk...\n[LOG 00:42:03] Listening for input...\n[LOG 00:42:05] User: 'What's the weather?'\n[LOG 00:42:06] Ryo: '22°C, Clear.'")

        # --- Status & Control Frame ---
        # This frame holds the status label and the model switcher at the bottom.
        self.control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.control_frame.pack(pady=10, fill="x")

        # Use a StringVar for the status label. This is the recommended way to handle
        # text that changes dynamically, as it's thread-safe and ensures the UI updates.
        self.status_var = ctk.StringVar(value="Status: Idle")
        self.status_label = ctk.CTkLabel(
            self.control_frame, 
            textvariable=self.status_var, # Link the label to the StringVar.
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=12),
            text_color=THEME["TEXT_COLOR"]
        )
        self.status_label.pack(side="left", padx=10)

        # --- Model Switcher Dropdown ---
        self.model_switcher = ctk.CTkOptionMenu(
            self.control_frame,
            values=["Ollama", "Gemini"], # The available model choices.
            command=self.assistant_core.set_active_model, # Function to call when a choice is made.
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=12),
            fg_color=THEME["ACCENT_COLOR"],
            button_color=THEME["ACCENT_COLOR"],
            button_hover_color=THEME["HIGHLIGHT_COLOR"]
        )
        self.model_switcher.pack(side="right", padx=10)
        # Set the dropdown's initial value to match the core's active model.
        self.model_switcher.set(self.assistant_core.model_switcher.active_model_name)

        # --- Mute Button ---
        self.mute_button = ctk.CTkButton(
            self.control_frame,
            text="🔇 Mute",
            width=90,
            command=self.toggle_mute,
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=12),
            fg_color=THEME["ACCENT_COLOR"],
            hover_color=THEME["HIGHLIGHT_COLOR"]
        )
        self.mute_button.pack(side="right", padx=(0, 10))

        # --- Keybind Instruction Label ---
        self.keybind_label = ctk.CTkLabel(
            self.main_frame,
            text="Press Control+Shift to mute/unmute",
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=11),
            text_color=THEME["TEXT_COLOR_MUTED"]
        )
        self.keybind_label.pack(side="bottom", pady=(5, 0))

    def toggle_mute(self):
        """Delegates the mute action to the assistant core and updates the button text."""
        is_muted = self.assistant_core.toggle_mute()
        self.update_mute_button_text(is_muted)

    def update_mute_button_text(self, is_muted: bool):
        """Updates the mute button's text based on the mute state."""
        new_text = "Unmute" if is_muted else "Mute"
        self.mute_button.configure(text=new_text)

    def update_response(self, text: str):
        """Clears the response textbox and inserts new text."""
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.insert("1.0", text) # Insert the new text at the beginning.

    def update_status(self, status: str):
        """Updates the status label at the bottom of the window."""
        # When the assistant returns to 'Idle', it's a good time to refresh the to-do list
        # in case a to-do command was just completed.
        if status == "Idle":
            self.refresh_todo_list()

        self.status_var.set(f"Status: {status}")

    def _create_assistant_tab(self):
        """Creates and configures the widgets for the 'Assistant' tab."""
        assistant_tab = self.tab_view.tab("Assistant")
        self.response_textbox = ctk.CTkTextbox(
            assistant_tab,
            wrap="word",
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=14),
            fg_color="transparent",
            text_color=THEME["TEXT_COLOR"],
            border_width=0,
            corner_radius=10
        )
        self.response_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.response_textbox.insert("0.0", "Awaiting your command...")

    def _create_todo_tab(self):
        """Creates and configures all widgets for the 'To-Do List' tab."""
        todo_tab = self.tab_view.tab("To-Do List")

        # --- Frame for Manual Entry ---
        entry_frame = ctk.CTkFrame(todo_tab, fg_color="transparent")
        entry_frame.pack(fill="x", padx=5, pady=5)

        self.todo_entry = ctk.CTkEntry(
            entry_frame, 
            placeholder_text="Add a new task...",
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=12)
        )
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", self._add_todo_from_input) # Bind Enter key

        add_button = ctk.CTkButton(
            entry_frame, 
            text="Add", 
            width=60,
            command=self._add_todo_from_input,
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=12)
        )
        add_button.pack(side="left")

        # --- Scrollable Frame for the To-Do List ---
        self.todo_list_frame = ctk.CTkScrollableFrame(todo_tab, fg_color="transparent")
        self.todo_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.todo_checkboxes = [] # This list will hold the checkbox widgets

        # --- Frame for the Remove Button ---
        remove_frame = ctk.CTkFrame(todo_tab, fg_color="transparent")
        remove_frame.pack(fill="x", padx=5, pady=(0, 5))

        remove_button = ctk.CTkButton(
            remove_frame, 
            text="Remove Selected", 
            command=self._remove_selected_todos,
            font=ctk.CTkFont(family=THEME["FONT_NAME"], size=12)
        )
        remove_button.pack(side="right")

        # Initial population of the list.
        self.refresh_todo_list()

    def _add_todo_from_input(self, event=None):
        """
        Handles the 'Add' button click or 'Enter' key press in the to-do entry.
        It gets the text, adds the item via the core plugin, and refreshes the UI.
        """
        item_text = self.todo_entry.get().strip()
        if item_text:
            self.assistant_core.todo_manager.add_todo(item_text)
            self.todo_entry.delete(0, "end") # Clear the entry box
            self.refresh_todo_list() # Update the list display

    def _remove_selected_todos(self):
        """
        Finds all checked to-do items, tells the core to remove them, 
        and then triggers a UI refresh.
        """
        # Using a list comprehension for a more concise way to find checked items.
        items_to_remove = [cb.cget("text") for cb in self.todo_checkboxes if cb.get() == 1]
        
        if items_to_remove:
            for item_text in items_to_remove:
                # Find and remove the todo by text
                for todo in self.assistant_core.todo_manager.get_todos():
                    if todo['text'] == item_text:
                        self.assistant_core.todo_manager.delete_todo(todo['id'])
                        break
            self.refresh_todo_list()

    def refresh_todo_list(self):
        """Clears and re-populates the to-do list with checkboxes."""
        # Clear existing checkboxes
        for checkbox in self.todo_checkboxes:
            checkbox.destroy()
        self.todo_checkboxes.clear()

        # Get the current list of items from the to-do manager.
        todos = self.assistant_core.todo_manager.get_todos()
        items = [todo['text'] for todo in todos]

        if not items:
            placeholder = ctk.CTkLabel(self.todo_list_frame, text="Your to-do list is empty.", text_color=THEME["TEXT_COLOR_MUTED"])
            placeholder.pack(pady=10)
            self.todo_checkboxes.append(placeholder) # Add to list to be cleared next time
        else:
            for item in items:
                checkbox = ctk.CTkCheckBox(
                    self.todo_list_frame, 
                    text=item,
                    font=ctk.CTkFont(family=THEME["FONT_NAME"], size=14),
                    text_color=THEME["TEXT_COLOR"]
                )
                checkbox.pack(fill="x", padx=10, pady=5, anchor="w")
                self.todo_checkboxes.append(checkbox)

    def on_closing(self):
        """Handles the window close event to ensure a clean shutdown."""
        print("GUI closing, shutting down core processes...")
        self.assistant_core.shutdown()
        self.destroy() # Close the GUI window.

    def run(self):
        """Starts the Tkinter main event loop, which makes the window appear and run."""
        self.mainloop()


if __name__ == "__main__":
    from core.todo_manager import TodoManager
    from core.model_switcher import ModelSwitcher

    class DummyCore:
        def __init__(self):
            self.model_switcher = ModelSwitcher()
            self.todo_manager = TodoManager()
        def set_active_model(self, model_name): pass
        def toggle_mute(self): return False

    app = RyoApp(DummyCore())
    app.run()


