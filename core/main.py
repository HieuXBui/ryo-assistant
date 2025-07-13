# === Ryo AI Assistant - Core Orchestrator ===
# This is the main file that launches and runs the entire application.
# It acts as the central hub, connecting all the different parts (voice, AI, GUI) together.

# --- Step 1: System and Path Setup ---

import os
import sys
import re
import threading
import platform
import ssl
import certifi
import time

# To make sure Python can find our other modules (like 'gui', 'voice', etc.),
# we add the main project folder to Python's list of search paths.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# --- Step 2: Import Core Components ---

from pynput import keyboard
from gui.app import RyoApp
from core.model_switcher import ModelSwitcher
from voice.wake_word_detector import WakeWordDetector
from voice.whisper_listener import WhisperListener
from voice.tts_speaker import TTSSpeaker
from core.todo_manager import TodoManager

# --- Step 3: Define the Hotkey Listener Class ---

class HotkeyListener(threading.Thread):
    """A background thread that listens for a global hotkey combination."""
    def __init__(self, on_toggle_mute):
        super().__init__(daemon=True)
        self.on_toggle_mute = on_toggle_mute
        self.current_keys = set()
        self.combination = {keyboard.Key.ctrl, keyboard.Key.shift}
        self.listener = None

    def on_press(self, key):
        """Callback executed when a key is pressed."""
        if key in self.combination:
            self.current_keys.add(key)
            if self.combination.issubset(self.current_keys):
                self.on_toggle_mute()

    def on_release(self, key):
        """Callback executed when a key is released."""
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

    def run(self):
        """Starts the keyboard listener loop."""
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        print("Hotkey listener started (Control+Shift to mute/unmute).")
        self.listener.run()

    def stop(self):
        """Stops the keyboard listener."""
        if self.listener:
            self.listener.stop()
            print("Hotkey listener stopped.")

# --- Step 4: Define the Main RyoCore Class ---

class RyoCore:
    """The central class that initializes, connects, and manages all assistant services."""

    def __init__(self):
        """Constructor that initializes all the modules and the application state."""
        self.model_switcher = ModelSwitcher()
        self.speaker = TTSSpeaker()
        self.listener = WhisperListener()
        self.wake_word_detector = WakeWordDetector(on_wake_word=self.handle_wake_word)
        self.hotkey_listener = HotkeyListener(on_toggle_mute=self.toggle_mute)
        self.todo_manager = TodoManager()
        self.app = RyoApp(assistant_core=self)
        self.state = "idle" # Possible states: idle, listening, thinking, speaking
        self.listening_mode = False
        self.session_timer = None
        self.session_timeout_seconds = 20  # You can adjust this value
        self.interrupt_listening = False
        self.interrupt_thread = None

    def run(self):
        """Starts the application's main loop."""
        self.update_status("Idle")
        self.wake_word_detector.start()
        self.hotkey_listener.start()
        self.app.mainloop()

    def handle_wake_word(self):
        """This function is called by the WakeWordDetector when the wake word is heard."""
        if self.state != "idle":
            return
        self.listening_mode = True
        self._start_session_timer()
        threading.Thread(target=self._activate_listening_sequence, daemon=True).start()

    def restart_listening_window(self):
        if getattr(self.listener, 'is_recording', False):
            print("[DEBUG] Stopping previous recording before starting new one.")
            self.listener.stop_and_transcribe()
        self.listener.start_listening()
        self.app.after(5000, self.process_recorded_audio)

    def _activate_listening_sequence(self):
        """The actual sequence of events to run after the wake word is detected."""
        self.wake_word_detector.stop()
        self.speaker.stop()
        self.update_status("Listening (Active)")
        self.restart_listening_window()

    def process_recorded_audio(self):
        print(f"[DEBUG] process_recorded_audio called. self.state={self.state}")
        if not self.state.startswith("listening"):
            print("[DEBUG] Not in listening state, skipping processing.")
            return
        self.update_status("Thinking")
        self.listener.stop_and_transcribe(on_finish=self.handle_transcription)

    def is_meta_query(self, text: str) -> bool:
        text = text.lower().strip()
        meta_phrases = [
            "what can you do", "help", "who are you", "what are you", "how do you work", "what is this", "what can i say"
        ]
        # Only match if the entire text is a meta phrase or a close variant
        return any(text == phrase or text.rstrip('?!.') == phrase for phrase in meta_phrases)

    def is_prompting_response(self, response: str) -> bool:
        # Returns True if Ryo's response is a prompting question
        response = response.lower().strip()
        prompt_phrases = [
            "how can i help", "what would you like to do", "is there anything else", "can i help with anything else", "what can i do for you"
        ]
        if any(phrase in response for phrase in prompt_phrases):
            return True
        if response.endswith("?") and len(response.split()) <= 10:
            return True
        return False

    def handle_transcription(self, text: str):
        print(f"[DEBUG] handle_transcription called with: {text}")
        if not text or not text.strip():
            self._check_session_continue()
            return
        # Check for stop/cancel/nevermind
        if text.strip().lower() in ["stop", "cancel", "nevermind"]:
            self._end_listening_session(user_cancel=True)
            return
        # Check for meta/help queries
        if self.is_meta_query(text):
            print("[DEBUG] Detected meta/help query. Ending session.")
            self.listening_mode = False
            self.reset_to_idle()
            return
        self.app.update_response(f'You said: "{text}"')
        if self.handle_todo_command(text):
            self._check_session_continue()
            return
        print(f"[DEBUG] Calling _get_and_speak with: {text}")
        self._get_and_speak(text)

    def _get_and_speak(self, text: str):
        print(f"[DEBUG] _get_and_speak called with: {text}")
        self.update_status("Thinking...")
        def ai_worker():
            try:
                self._start_interrupt_listening()
                print(f"[DEBUG] Sending to AI model: {text}")
                response = self.model_switcher.ask(text)
                print(f"[DEBUG] AI model response: {response}")
                self._stop_interrupt_listening()
                self.app.after(0, self.app.update_response, response)
                self.app.after(0, self.update_status, "Speaking")
                # If the response is a prompting question, end session after TTS
                if self.is_prompting_response(response):
                    def end_after_tts():
                        self._stop_interrupt_listening()
                        self.listening_mode = False
                        self.reset_to_idle()
                    self.speaker.speak(response, on_finish=end_after_tts)
                else:
                    self._start_interrupt_listening()
                    self.speaker.speak(response, on_finish=self._on_tts_finish)
            except Exception as e:
                print(f"Error during AI processing or speech: {e}")
                self._stop_interrupt_listening()
                self.app.after(0, self.app.update_response, f"Error: {e}")
                self.app.after(0, self._check_session_continue)
        threading.Thread(target=ai_worker, daemon=True).start()

    def _on_tts_finish(self):
        self._stop_interrupt_listening()
        self._check_session_continue()

    def _start_interrupt_listening(self):
        if self.interrupt_listening:
            return
        self.interrupt_listening = True
        def interrupt_worker():
            # Listen for up to 3 seconds for an interrupt command
            self.listener.start_listening()
            self.app.after(3000, self._process_interrupt_audio)
        self.interrupt_thread = threading.Thread(target=interrupt_worker, daemon=True)
        self.interrupt_thread.start()

    def _process_interrupt_audio(self):
        # Stop and transcribe the short interrupt window
        def on_interrupt_transcribed(text):
            if text and text.strip().lower() in ["stop", "hey ryo"]:
                print("[DEBUG] Interrupt detected: {}".format(text.strip().lower()))
                self._handle_interrupt_command()
        self.listener.stop_and_transcribe(on_finish=on_interrupt_transcribed)

    def _stop_interrupt_listening(self):
        self.interrupt_listening = False
        # No explicit thread stop needed; the short window will end naturally

    def _handle_interrupt_command(self):
        print("[DEBUG] Handling interrupt: stopping TTS and AI, starting new command session.")
        self.speaker.stop()
        # Optionally, cancel AI response if possible (not implemented for subprocess)
        self._stop_interrupt_listening()
        self.listening_mode = True
        self._start_session_timer()
        self.state = "listening"
        self.update_status("Listening (Active)")
        self.restart_listening_window()

    def _check_session_continue(self):
        if self.listening_mode:
            self._start_session_timer()
            self.update_status("Listening (Active)")
            self.restart_listening_window()
        else:
            self.reset_to_idle()

    def _start_session_timer(self):
        if self.session_timer:
            self.app.after_cancel(self.session_timer)
        self.session_timer = self.app.after(self.session_timeout_seconds * 1000, self._end_listening_session)

    def _end_listening_session(self, user_cancel=False):
        self.listening_mode = False
        if self.session_timer:
            self.app.after_cancel(self.session_timer)
            self.session_timer = None
        self.speaker.stop()
        if user_cancel:
            self.app.update_response("Session ended.")
        self.reset_to_idle()

    def set_active_model(self, model_name: str):
        """Allows the GUI to switch the active AI model in a thread-safe way."""
        self.model_switcher.set_active_model(model_name)

    def update_status(self, new_status: str):
        """A thread-safe method to update the application state and the GUI status label."""
        self.state = new_status.lower()
        self.app.after(0, self.app.update_status, new_status)

    def _extract_task(self, command: str, intent: str) -> str:
        """Extracts the core task from a command by stripping away action phrases and unnecessary suffixes/punctuation. Adds debug prints for diagnosis."""
        import re
        original_command = command
        task = command.lower().strip()

        # Normalize dashes to spaces for more robust suffix matching
        task = task.replace('-', ' ')

        # Remove all punctuation except for word characters and spaces
        task = re.sub(r'[^\w\s]', '', task)

        # Define intent-specific prefixes
        prefixes = {
            'add': ['add ', 'put ', 'remind me to '],
            'remove': ['remove ', 'delete ', 'take off ']
        }

        # Remove all matching prefixes
        prefix_found = True
        while prefix_found:
            prefix_found = False
            for prefix in prefixes.get(intent, []):
                if task.startswith(prefix):
                    task = task[len(prefix):].strip()
                    prefix_found = True

        # Define suffixes (both dashed and undashed forms)
        suffixes = [
            'from my to do list',
            'to my to do list',
            'on my to do list',
            'from my list',
            'to my list',
            'my to do list',
            'to do list',
            'list',
            'please'
        ]

        # Remove all matching suffixes using regex
        suffix_found = True
        while suffix_found:
            suffix_found = False
            for suffix in suffixes:
                # Match the suffix at the end, possibly preceded by whitespace
                pattern = r'(\s*' + re.escape(suffix) + r')$'
                new_task = re.sub(pattern, '', task)
                if new_task != task:
                    task = new_task.strip()
                    suffix_found = True

        # Normalize whitespace
        task = re.sub(r'\s+', ' ', task).strip()

        print(f"[DEBUG] _extract_task: original='{original_command}', intent='{intent}', extracted='{task}'")
        return task

    def handle_todo_command(self, text: str) -> bool:
        """Handles commands related to the to-do list with improved parsing."""
        lower_text = text.lower()
        intent = None
        if any(keyword in lower_text for keyword in ['add', 'put', 'remind me to']):
            intent = 'add'
        elif any(keyword in lower_text for keyword in ['remove', 'delete', 'take off']):
            intent = 'remove'
        elif 'what' in lower_text and ('on my to-do list' in lower_text or 'is my to-do list' in lower_text):
            intent = 'list'

        if intent:
            item_text = self._extract_task(text, intent)
            if intent == 'add':
                if item_text:
                    todo = self.todo_manager.add_todo(item_text)
                    response = f"Added task: {item_text}"
                    # Refresh the GUI todo list
                    self.app.after(0, self.app.refresh_todo_list)
                else:
                    response = "I didn't catch what to add."
            elif intent == 'remove':
                if item_text:
                    # Find and remove by text
                    removed = False
                    for todo in self.todo_manager.get_todos():
                        if item_text.lower() in todo['text'].lower():
                            self.todo_manager.delete_todo(todo['id'])
                            removed = True
                            break
                    response = f"Removed task: {item_text}" if removed else f"Couldn't find task: {item_text}"
                    if removed:
                        # Refresh the GUI todo list
                        self.app.after(0, self.app.refresh_todo_list)
                else:
                    response = "I didn't catch what to remove."
            elif intent == 'list':
                todos = self.todo_manager.get_todos()
                if not todos:
                    response = "Your to-do list is empty."
                else:
                    response = "Here's what's on your to-do list:\n"
                    for i, todo in enumerate(todos, 1):
                        status = "✓" if todo['completed'] else "○"
                        response += f"{i}. {status} {todo['text']}\n"
            
            self.update_status("Speaking")
            self.app.update_response(response)
            self.speaker.speak(response, on_finish=self.reset_to_idle)
            return True
        return False

    def toggle_mute(self):
        """Toggles the TTS speaker's mute state and updates the GUI button."""
        is_muted = self.speaker.toggle_mute()
        self.app.update_mute_button_text(is_muted)
        return is_muted

    def shutdown(self):
        """Gracefully shuts down all components of the assistant."""
        print("Shutting down Ryo Core...")
        if hasattr(self, 'hotkey_listener') and self.hotkey_listener.is_alive():
            self.hotkey_listener.stop()
        if hasattr(self, 'wake_word_detector') and self.wake_word_detector.is_running():
            self.wake_word_detector.stop()
        if self.speaker:
            self.speaker.stop()
        # No self.app.quit() here, it causes issues. The main loop will exit naturally.

    def reset_to_idle(self):
        """Resets the application to the idle state and restarts wake word detection."""
        self.update_status("Idle")
        
        # Force stop TTS and whisper listener to ensure audio device is released
        self.speaker.stop()
        self.listener.stop()
        
        # Add a delay and more robust audio device handling
        def delayed_start():
            import time
            time.sleep(1.5)  # Wait 1.5 seconds for audio system to fully settle
            print(f"[DEBUG] Delayed wake word restart")
            try:
                if not self.wake_word_detector.is_running():
                    # Use retry mechanism for better handling of audio device conflicts
                    self.wake_word_detector.start_with_retry(max_retries=3, retry_delay=5)
            except Exception as e:
                print(f"[ERROR] Failed to restart wake word detection: {e}")
                # Try again after another delay
                time.sleep(1.0)
                try:
                    if not self.wake_word_detector.is_running():
                        self.wake_word_detector.start_with_retry(max_retries=2, retry_delay=3)
                except Exception as e2:
                    print(f"[ERROR] Second attempt failed: {e2}")
                    # Final attempt with force restart
                    time.sleep(0.5)
                    try:
                        self.wake_word_detector.force_restart()
                    except Exception as e3:
                        print(f"[ERROR] Force restart also failed: {e3}")
        
        threading.Thread(target=delayed_start, daemon=True).start()
        print(f"[DEBUG] Wake word detection restart scheduled")

    def force_restart_wake_word(self):
        """Manual method to force restart wake word detection - useful for debugging"""
        print(f"[DEBUG] Force restarting wake word detection from main core")
        self.speaker.stop()
        self.listener.stop()
        import time
        time.sleep(0.5)
        self.wake_word_detector.force_restart()

# --- Step 5: SSL Context and Application Entry Point ---

def setup_ssl_context():
    """Fix for macOS SSL certificate errors."""
    if platform.system() == 'Darwin':
        try:
            ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
            print("SSL context configured for macOS.")
        except Exception as e:
            print(f"Error setting SSL context: {e}")

if __name__ == "__main__":
    setup_ssl_context()
    ryo_core = RyoCore()
    try:
        ryo_core.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
    except Exception as e:
        print(f"A fatal error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if ryo_core:
            ryo_core.shutdown()
