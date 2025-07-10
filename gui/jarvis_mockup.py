import customtkinter as ctk
import tkinter as tk
import math
import time

ctk.set_appearance_mode("dark")

# --- Color Palette ---
BG = "#10131a"
CYAN = "#00fff7"
BLUE = "#1a9fff"
TEAL = "#00e6c3"
WHITE = "#e0e1dd"
MUTED = "#8d99ae"
GLOW = CYAN

FONT_FUTURE = ("Orbitron", 14, "bold")
FONT_LABEL = ("Menlo", 12)
FONT_MONO = ("Menlo", 10)

class AnimatedOrb(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=200, height=200, bg=BG, highlightthickness=0, **kwargs)
        self.radius = 80
        self.pulse = 0
        self.animate()

    def animate(self):
        self.delete("all")
        # Pulsing glow
        pulse_radius = self.radius + 10 * math.sin(time.time() * 2)
        self.create_oval(100-pulse_radius, 100-pulse_radius, 100+pulse_radius, 100+pulse_radius,
                         fill=CYAN, outline=GLOW, width=4, stipple="gray50")
        # Core orb
        self.create_oval(100-self.radius, 100-self.radius, 100+self.radius, 100+self.radius,
                         fill=BG, outline=CYAN, width=6)
        # Inner glow
        self.create_oval(100-self.radius//2, 100-self.radius//2, 100+self.radius//2, 100+self.radius//2,
                         fill=CYAN, outline="", width=0, stipple="gray25")
        # Center dot
        self.create_oval(95, 95, 105, 105, fill=WHITE, outline=CYAN, width=2)
        self.after(30, self.animate)

class JarvisMockup(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ryo JARVIS HUD Prototype")
        self.geometry("1200x800")
        self.configure(fg_color=BG)
        self._build_layout()

    def _build_layout(self):
        # --- Central Orb ---
        self.orb = AnimatedOrb(self)
        self.orb.place(relx=0.5, rely=0.45, anchor="center")
        ctk.CTkLabel(self, text="VOICE CORE", font=FONT_FUTURE, text_color=CYAN, fg_color=BG).place(relx=0.5, rely=0.68, anchor="center")

        # --- Left Panel: System Info ---
        left_panel = ctk.CTkFrame(self, width=220, height=500, fg_color="#151a22", corner_radius=20)
        left_panel.place(relx=0.08, rely=0.45, anchor="center")
        ctk.CTkLabel(left_panel, text="SYSTEM", font=FONT_FUTURE, text_color=CYAN).pack(pady=(20,5))
        ctk.CTkLabel(left_panel, text="CPU: 23%\nRAM: 8.2GB/16GB\nPower: 97%", font=FONT_LABEL, text_color=WHITE, justify="left").pack(pady=5)
        ctk.CTkLabel(left_panel, text="Drive: 512GB/1TB", font=FONT_LABEL, text_color=TEAL).pack(pady=5)
        ctk.CTkLabel(left_panel, text="Date: 2042-07-10\nTime: 13:37", font=FONT_LABEL, text_color=MUTED).pack(pady=5)
        ctk.CTkLabel(left_panel, text="Quick Launch", font=FONT_FUTURE, text_color=CYAN).pack(pady=(30,5))
        for app in ["VLC", "Paint", "Word", "Discord", "Terminal"]:
            ctk.CTkButton(left_panel, text=app, fg_color=TEAL, text_color=BG, width=160, height=28, font=FONT_LABEL).pack(pady=2)

        # --- Right Panel: Stats, Weather, Links ---
        right_panel = ctk.CTkFrame(self, width=220, height=500, fg_color="#151a22", corner_radius=20)
        right_panel.place(relx=0.92, rely=0.45, anchor="center")
        ctk.CTkLabel(right_panel, text="STATS", font=FONT_FUTURE, text_color=CYAN).pack(pady=(20,5))
        ctk.CTkLabel(right_panel, text="CPU: |||||||---\nRAM: ||||||----\nTemp: 42°C", font=FONT_LABEL, text_color=WHITE, justify="left").pack(pady=5)
        ctk.CTkLabel(right_panel, text="Weather: 22°C, Clear", font=FONT_LABEL, text_color=TEAL).pack(pady=5)
        ctk.CTkLabel(right_panel, text="Links", font=FONT_FUTURE, text_color=CYAN).pack(pady=(30,5))
        for link in ["Discord", "Chat", "Docs", "GitHub"]:
            ctk.CTkButton(right_panel, text=link, fg_color=BLUE, text_color=BG, width=160, height=28, font=FONT_LABEL).pack(pady=2)

        # --- Bottom Left: Status Wheel ---
        bl_panel = ctk.CTkFrame(self, width=180, height=120, fg_color="#151a22", corner_radius=20)
        bl_panel.place(relx=0.13, rely=0.88, anchor="center")
        ctk.CTkLabel(bl_panel, text="MIC: ON\nNET: OK", font=FONT_LABEL, text_color=CYAN).pack(pady=10)
        ctk.CTkProgressBar(bl_panel, width=120, height=12, progress_color=CYAN).pack(pady=5)

        # --- Bottom Right: HACKING Panel ---
        br_panel = ctk.CTkFrame(self, width=260, height=120, fg_color="#151a22", corner_radius=20)
        br_panel.place(relx=0.87, rely=0.88, anchor="center")
        ctk.CTkLabel(br_panel, text="HACKING...", font=FONT_FUTURE, text_color=CYAN).pack(pady=5)
        ctk.CTkProgressBar(br_panel, width=180, height=12, progress_color=BLUE).pack(pady=5)
        ctk.CTkTextbox(br_panel, width=220, height=40, font=FONT_MONO, fg_color="#11141a", text_color=TEAL).pack(pady=5)

        # --- Notes Panel ---
        notes_panel = ctk.CTkFrame(self, width=320, height=180, fg_color="#151a22", corner_radius=20)
        notes_panel.place(relx=0.28, rely=0.18, anchor="center")
        ctk.CTkLabel(notes_panel, text="NOTES / MEMORY LOGS", font=FONT_FUTURE, text_color=CYAN).pack(pady=5)
        ctk.CTkTextbox(notes_panel, width=260, height=90, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=5)
        # Insert dummy notes
        notes_panel.winfo_children()[-1].insert("1.0", "- Buy groceries\n- Call Dr. Banner\n- Project: Ryo v2\n- Meeting 14:00\n- Remember: 'Trust no one'")

        # --- To-Do Panel ---
        todo_panel = ctk.CTkFrame(self, width=320, height=180, fg_color="#151a22", corner_radius=20)
        todo_panel.place(relx=0.72, rely=0.18, anchor="center")
        ctk.CTkLabel(todo_panel, text="TO-DO LIST", font=FONT_FUTURE, text_color=CYAN).pack(pady=5)
        for item in ["[ ] Finish GUI mockup", "[x] Refactor core", "[ ] Add weather API", "[ ] Test TTS"]:
            ctk.CTkLabel(todo_panel, text=item, font=FONT_LABEL, text_color=TEAL if '[x]' in item else CYAN).pack(anchor="w", padx=20)

        # --- Communication/Side Panel (Tabs) ---
        comm_panel = ctk.CTkFrame(self, width=180, height=320, fg_color="#151a22", corner_radius=20)
        comm_panel.place(relx=0.07, rely=0.18, anchor="center")
        ctk.CTkLabel(comm_panel, text="COMMUNICATION", font=FONT_FUTURE, text_color=CYAN).pack(pady=5)
        ctk.CTkTextbox(comm_panel, width=140, height=200, font=FONT_MONO, fg_color="#11141a", text_color=WHITE).pack(pady=5)
        comm_panel.winfo_children()[-1].insert("1.0", "[13:36] SYSTEM ONLINE\n[13:37] RYO READY\n[13:38] USER LOGGED IN")

        # --- Mic/Audio Status Indicator ---
        mic_status = ctk.CTkLabel(self, text="● MUTE", font=FONT_FUTURE, text_color=CYAN, fg_color=BG)
        mic_status.place(relx=0.5, rely=0.78, anchor="center")

if __name__ == "__main__":
    app = JarvisMockup()
    app.mainloop() 