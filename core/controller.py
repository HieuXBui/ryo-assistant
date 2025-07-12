import threading
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pynput import keyboard
from voice.wake_word_detector import WakeWordDetector
from voice.whisper_listener import WhisperListener
from voice.tts_speaker import TTSSpeaker
from core.model_switcher import ModelSwitcher

class AssistantController:
    """
    Central controller for the assistant. Exposes status, mute, voice, TTS, AI, and plugins.
    Now integrates wake word, voice input, AI, and TTS, and notifies the GUI via callbacks.
    """
    def __init__(self):
        self.status = "Idle"
        self.muted = False
        self.mute_callback = None
        self.status_callback = None
        self.transcription_callback = None
        self.gui_refresh_callback = None
        self._gui_root = None
        # Voice integration
        self.wake_word_detector = WakeWordDetector(on_wake_word=self._on_wake_word)
        self.whisper_listener = WhisperListener()
        # AI and TTS integration
        self.model_switcher = ModelSwitcher()
        self.tts_speaker = TTSSpeaker()
        # Placeholders for future integration:
        self.voice = self.wake_word_detector
        self.tts = self.tts_speaker
        self.ai = self.model_switcher
        self.todo_plugin = None
        self.notes_plugin = None
        
        # Initialize todo manager
        from core.todo_manager import TodoManager
        self.todo_manager = TodoManager()
        # Start hotkey listener for mute
        self._start_hotkey_listener()
        # Start wake word detection by default
        self.start_wake_word()

    def set_status(self, status):
        self.status = status
        if self.status_callback:
            self.status_callback(status)

    def get_status(self):
        return self.status

    def set_status_callback(self, callback):
        self.status_callback = callback

    def toggle_mute(self):
        # Use the TTS speaker's toggle_mute method and sync the controller state
        self.muted = self.tts_speaker.toggle_mute()
        print(f"[DEBUG] Controller mute toggled: {self.muted}")
        if self.mute_callback:
            self.mute_callback(self.muted)
        return self.muted

    def is_muted(self):
        return self.tts_speaker.is_muted

    def set_mute_callback(self, callback):
        self.mute_callback = callback

    def set_transcription_callback(self, callback):
        self.transcription_callback = callback
    
    def set_gui_refresh_callback(self, callback):
        self.gui_refresh_callback = callback

    def _start_hotkey_listener(self):
        def on_press(key):
            try:
                if key in {keyboard.Key.ctrl, keyboard.Key.shift}:
                    self._pressed_keys.add(key)
                    if {keyboard.Key.ctrl, keyboard.Key.shift}.issubset(self._pressed_keys):
                        self.toggle_mute()
            except Exception:
                pass
        def on_release(key):
            try:
                self._pressed_keys.remove(key)
            except KeyError:
                pass
        self._pressed_keys = set()
        def run_listener():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        t = threading.Thread(target=run_listener, daemon=True)
        t.start()

    # --- Voice/Wake Word Integration ---
    def start_wake_word(self):
        self.wake_word_detector.start()
    def stop_wake_word(self):
        self.wake_word_detector.stop()

    def _on_wake_word(self):
        # Called from background thread
        self.set_status("Listening (Active)")
        if self.transcription_callback:
            self.transcription_callback("[Wake word detected: Listening...]")
        self.whisper_listener.start_listening()
        # After a short delay, stop and transcribe
        threading.Timer(5.0, self._stop_and_transcribe).start()

    def _stop_and_transcribe(self):
        self.set_status("Thinking")
        self.whisper_listener.stop_and_transcribe(on_finish=self._on_transcription)

    def _on_transcription(self, text):
        # Called from background thread after transcription
        if self.transcription_callback:
            self.transcription_callback(f"You said: {text}")
        self.set_status("Thinking")
        
        # Check if it's a todo command first
        if self._process_todo_command(text):
            return  # Todo command handled, don't send to AI
        
        # Call AI model in a thread
        threading.Thread(target=self._get_and_speak, args=(text,), daemon=True).start()

    def _get_and_speak(self, text):
        try:
            response = self.model_switcher.ask(text)
            if self.transcription_callback:
                self.transcription_callback(f"Ryo: {response}")
            self.set_status("Speaking")
            self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
        except Exception as e:
            if self.transcription_callback:
                self.transcription_callback(f"[Error: {e}]")
            self.set_status("Idle")
            self.start_wake_word()

    def _on_tts_finish(self):
        self.set_status("Idle")
        self.start_wake_word()

    def _process_todo_command(self, text: str) -> bool:
        """Process voice commands for todo management"""
        text_lower = text.lower().strip()
        print(f"[DEBUG] Processing todo command: '{text}'")
        
        # Add todo commands
        add_keywords = ['add', 'put', 'remind me to', 'add to my', 'add to the', 'add to todo', 'add to to-do', 'add to to do']
        if any(keyword in text_lower for keyword in add_keywords):
            print(f"[DEBUG] Detected ADD command")
            task = self._extract_todo_task(text, 'add')
            if task:
                print(f"[DEBUG] Adding task: '{task}'")
                todo = self.todo_manager.add_todo(task)
                print(f"[DEBUG] Todo added with ID: {todo['id']}")
                print(f"[DEBUG] Current todos count: {len(self.todo_manager.get_todos())}")
                response = f"Added task: {task}"
                if self.transcription_callback:
                    self.transcription_callback(f"Ryo: {response}")
                if self.gui_refresh_callback:
                    print(f"[DEBUG] Calling GUI refresh callback")
                    # Use after() for thread safety with a small delay to ensure save completes
                    try:
                        # Try to get the GUI root from the callback function
                        import inspect
                        if hasattr(self.gui_refresh_callback, '__self__'):
                            gui_root = self.gui_refresh_callback.__self__
                            if hasattr(gui_root, 'after'):
                                gui_root.after(100, self.gui_refresh_callback)  # 100ms delay
                            else:
                                self.gui_refresh_callback()
                        else:
                            self.gui_refresh_callback()
                    except Exception as e:
                        print(f"[ERROR] GUI refresh failed: {e}")
                        self.gui_refresh_callback()
                self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
                return True
            else:
                print(f"[DEBUG] No task extracted")
                response = "I didn't catch what task to add. Please try again."
                if self.transcription_callback:
                    self.transcription_callback(f"Ryo: {response}")
                self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
                return True
        
        # Remove todo commands
        remove_keywords = ['remove', 'delete', 'take off', 'remove from', 'delete from', 'remove from todo', 'delete from todo']
        if any(keyword in text_lower for keyword in remove_keywords):
            task = self._extract_todo_task(text, 'remove')
            if task:
                # Find and remove the todo
                removed_task_text = self._remove_todo_by_text(task)
                if removed_task_text:
                    response = f"Removed task: {removed_task_text}"
                else:
                    response = f"Couldn't find task: {task}"
                if self.transcription_callback:
                    self.transcription_callback(f"Ryo: {response}")
                if self.gui_refresh_callback:
                    print(f"[DEBUG] Calling GUI refresh callback (remove)")
                    try:
                        if hasattr(self.gui_refresh_callback, '__self__'):
                            gui_root = self.gui_refresh_callback.__self__
                            if hasattr(gui_root, 'after'):
                                gui_root.after(0, self.gui_refresh_callback)
                            else:
                                self.gui_refresh_callback()
                        else:
                            self.gui_refresh_callback()
                    except Exception as e:
                        print(f"[ERROR] GUI refresh failed: {e}")
                        self.gui_refresh_callback()
                self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
                return True
            else:
                response = "I didn't catch what task to remove. Please try again."
                if self.transcription_callback:
                    self.transcription_callback(f"Ryo: {response}")
                self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
                return True
        
        # List todos commands
        list_keywords = ['what', 'list', 'show', 'what is on my', 'what is in my', 'what are my', 'list my', 'show my']
        todo_keywords = ['todo', 'to-do', 'to do', 'tasks', 'task list']
        if any(list_kw in text_lower for list_kw in list_keywords) and any(todo_kw in text_lower for todo_kw in todo_keywords):
            response = self._get_todo_list_response()
            if self.transcription_callback:
                self.transcription_callback(f"Ryo: {response}")
            self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
            return True
        
        # Clear completed commands
        clear_keywords = ['clear', 'clear completed', 'clear done', 'remove completed', 'remove done']
        if any(keyword in text_lower for keyword in clear_keywords):
            completed_count = self.todo_manager.get_completed_count()
            self.todo_manager.clear_completed()
            response = f"Cleared {completed_count} completed tasks"
            if self.transcription_callback:
                self.transcription_callback(f"Ryo: {response}")
            if self.gui_refresh_callback:
                print(f"[DEBUG] Calling GUI refresh callback (clear)")
                try:
                    if hasattr(self.gui_refresh_callback, '__self__'):
                        gui_root = self.gui_refresh_callback.__self__
                        if hasattr(gui_root, 'after'):
                            gui_root.after(0, self.gui_refresh_callback)
                        else:
                            self.gui_refresh_callback()
                    else:
                        self.gui_refresh_callback()
                except Exception as e:
                    print(f"[ERROR] GUI refresh failed: {e}")
                    self.gui_refresh_callback()
            self.tts_speaker.speak(response, on_finish=self._on_tts_finish)
            return True
        
        return False
    
    def _extract_todo_task(self, text: str, command_type: str) -> str:
        """Extract the actual task text from voice command"""
        original_text = text
        text_lower = text.lower()
        
        print(f"[DEBUG] Original text: '{original_text}'")
        
        # More comprehensive prefix removal
        prefixes_to_remove = [
            'add', 'put', 'remind me to', 'add to my', 'add to the', 'add to todo', 'add to to-do', 'add to to do',
            'remove', 'delete', 'take off', 'remove from', 'delete from', 'remove from todo', 'delete from todo',
            'add to my todo', 'add to my to-do', 'add to my to do', 'add to the todo', 'add to the to-do', 'add to the to do',
            'remove from my todo', 'remove from my to-do', 'remove from my to do', 'remove from the todo', 'remove from the to-do', 'remove from the to do'
        ]
        
        # Sort prefixes by length (longest first) to avoid partial matches
        prefixes_to_remove.sort(key=len, reverse=True)
        
        # Remove prefixes
        for prefix in prefixes_to_remove:
            if text_lower.startswith(prefix):
                text = text[len(prefix):].strip()
                print(f"[DEBUG] Removed prefix '{prefix}', result: '{text}'")
                break
        
        # More comprehensive suffix removal - be more careful about what we remove
        suffixes_to_remove = [
            'to my todo', 'to my to-do', 'to my to do', 'to the todo', 'to the to-do', 'to the to do',
            'from my todo', 'from my to-do', 'from my to do', 'from the todo', 'from the to-do', 'from the to do',
            'to todo', 'to to-do', 'to to do', 'from todo', 'from to-do', 'from to do',
            'in my todo', 'in my to-do', 'in my to do', 'in the todo', 'in the to-do', 'in the to do',
            'in todo', 'in to-do', 'in to do',
            'to my to-do list', 'to my todo list', 'to my to do list',
            'to the to-do list', 'to the todo list', 'to the to do list',
            'to to-do list', 'to todo list', 'to to do list'
        ]
        
        # Sort suffixes by length (longest first)
        suffixes_to_remove.sort(key=len, reverse=True)
        
        # Remove suffixes - but only if they appear at the very end
        for suffix in suffixes_to_remove:
            if text_lower.endswith(suffix):
                text = text[:-len(suffix)].strip()
                print(f"[DEBUG] Removed suffix '{suffix}', result: '{text}'")
                break
        
        # Additional suffix cleanup for common patterns - be more careful
        # Only remove these if they appear at the very end and are clearly not part of the task
        additional_suffixes = ['to the do list', 'to do list', 'to the list', 'to my list', 'to list']
        for suffix in additional_suffixes:
            if text_lower.endswith(suffix):
                text = text[:-len(suffix)].strip()
                print(f"[DEBUG] Removed additional suffix '{suffix}', result: '{text}'")
                break
        
        # Clean up extra words - be more selective about what we remove
        # Only remove words that are clearly not part of the task
        words_to_remove = ['todo', 'to-do', 'to do', 'task', 'tasks', 'item', 'items']
        words = text.split()
        cleaned_words = []
        
        for word in words:
            word_lower = word.lower()
            # Don't remove common words that could be part of the task
            # Only remove obvious todo-related words
            if word_lower not in words_to_remove:
                cleaned_words.append(word)
        
        text = ' '.join(cleaned_words).strip()
        
        # Additional cleanup for common patterns - be more careful
        # Only remove these if they appear as complete phrases
        text = text.replace('to my list', '').replace('to the list', '').replace('to list', '').strip()
        
        print(f"[DEBUG] Final extracted task: '{text}'")
        return text
    
    def _remove_todo_by_text(self, task_text: str):
        """Remove a todo by matching its text content. Returns the removed task text or None."""
        todos = self.todo_manager.get_todos()
        task_text_lower = task_text.lower().strip()
        print(f"[DEBUG] Looking for task: '{task_text}'")
        # First try exact match
        for todo in todos:
            if task_text_lower == todo['text'].lower():
                print(f"[DEBUG] Exact match found: '{todo['text']}'")
                self.todo_manager.delete_todo(todo['id'])
                return todo['text']
        # Then try substring match
        for todo in todos:
            todo_text_lower = todo['text'].lower()
            if task_text_lower in todo_text_lower or todo_text_lower in task_text_lower:
                print(f"[DEBUG] Substring match found: '{todo['text']}'")
                self.todo_manager.delete_todo(todo['id'])
                return todo['text']
        # Finally try word-based matching
        task_words = set(task_text_lower.split())
        for todo in todos:
            todo_words = set(todo['text'].lower().split())
            if len(task_words & todo_words) >= min(len(task_words), len(todo_words)) * 0.5:
                print(f"[DEBUG] Word-based match found: '{todo['text']}'")
                self.todo_manager.delete_todo(todo['id'])
                return todo['text']
        print(f"[DEBUG] No match found for: '{task_text}'")
        return None
    
    def _get_todo_list_response(self) -> str:
        """Generate a response for listing todos"""
        todos = self.todo_manager.get_todos()
        stats = self.todo_manager.get_stats()
        
        if not todos:
            return "You have no tasks in your todo list."
        
        pending_todos = [todo for todo in todos if not todo['completed']]
        completed_todos = [todo for todo in todos if todo['completed']]
        
        response = f"You have {stats['total']} tasks total. "
        
        if pending_todos:
            response += f"{len(pending_todos)} pending: "
            for i, todo in enumerate(pending_todos[:5]):  # Limit to first 5
                response += f"{todo['text']}, "
            response = response.rstrip(", ")
        
        if completed_todos:
            response += f" and {len(completed_todos)} completed tasks."
        
        return response

    # Stubs for future integration:
    def speak(self, text):
        pass
    def process_command(self, text):
        pass
    def add_todo(self, item):
        pass
    def remove_todo(self, item):
        pass
    def list_todos(self):
        return []
    def add_note(self, note):
        pass
    def list_notes(self):
        return []
    def stop(self):
        try:
            self.tts_speaker.stop()
        except Exception:
            pass
        try:
            self.stop_wake_word()
        except Exception:
            pass 