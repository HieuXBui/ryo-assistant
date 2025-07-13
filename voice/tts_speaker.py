# === Ryo AI Assistant - Text-to-Speech Speaker ===
# This file is responsible for converting the AI's text responses into audible speech.

import asyncio
import threading
import subprocess
import os
from core.config import BASE_DIR

# Dynamically import edge_tts to handle potential import errors gracefully.
try:
    import edge_tts
except ImportError:
    edge_tts = None

class TTSSpeaker:
    """Handles text-to-speech generation and playback with real-time controls."""

    def __init__(self, voice: str = "en-US-AriaNeural"):
        """Initializes the speaker, audio file directory, and playback state."""
        self.voice = voice
        self.output_file = os.path.join(BASE_DIR, "assets", "response.mp3")
        self.is_muted = False
        self.playback_process = None
        self.on_finish_callback = None
        self.last_text = None  # To remember the last thing to say

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        if not edge_tts:
            print("Warning: 'edge_tts' library not found. TTS will be disabled.")

    def speak(self, text: str, on_finish: callable = None):
        """
        Generates and speaks the given text aloud.

        This method is the main entry point for making the assistant speak. It handles
        interrupting previous speech, managing the muted state, and running the
        entire process in a background thread to keep the application responsive.

        Args:
            text (str): The text to be spoken.
            on_finish (callable, optional): A callback function to execute when
                                            speaking is complete. Defaults to None.
        """
        self.stop()  # Stop any previous playback before starting a new one.
        self.on_finish_callback = on_finish
        self.last_text = text  # Remember what we need to say in case we're unmuted.

        print(f"[DEBUG] TTS speak called with muted={self.is_muted}, text='{text[:50]}...'")
        if self.is_muted or not edge_tts:
            print(f"[DEBUG] TTS skipping speech due to muted={self.is_muted} or no edge_tts={not edge_tts}")
            if self.on_finish_callback:
                threading.Thread(target=self.on_finish_callback, daemon=True).start()
            return

        thread = threading.Thread(target=self._generate_and_play, args=(text,), daemon=True)
        thread.start()

    def _generate_and_play(self, text: str):
        """
        The core worker method that handles audio generation and playback.
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _main() -> None:
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(self.output_file)

            loop.run_until_complete(_main())
            loop.close()

            self.playback_process = subprocess.Popen(
                ["mpv", "--no-video", "--audio-display=no", "--no-terminal", self.output_file],
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            self.playback_process.wait()

        except FileNotFoundError:
            print("Error: 'mpv' command not found. Please install mpv to hear speech.")
        except Exception as e:
            print(f"An error occurred in TTS generation/playback: {e}")
        finally:
            # Ensure the playback process is completely stopped
            if self.playback_process and self.playback_process.poll() is None:
                try:
                    self.playback_process.terminate()
                    self.playback_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.playback_process.kill()
                except Exception as e:
                    print(f"Error terminating playback process: {e}")
            self.playback_process = None
            
            # Add a small delay to ensure audio device is released
            import time
            time.sleep(0.2)
            
            if self.on_finish_callback:
                self.on_finish_callback()

    def toggle_mute(self) -> bool:
        """
        Toggles the mute state of the speaker.
        Returns the new mute state (True if muted, False if not).
        """
        self.is_muted = not self.is_muted
        print(f"[DEBUG] TTS toggle_mute: {'muted' if self.is_muted else 'unmuted'}")

        if self.is_muted:
            self.stop()
        else:
            if self.last_text:
                print(f"[DEBUG] TTS unmuted, replaying last text: {self.last_text[:50]}...")
                self.speak(self.last_text, self.on_finish_callback)
        
        return self.is_muted

    def stop(self):
        """
        Forcefully stops any currently playing speech.
        """
        self.last_text = None
        
        if self.playback_process and self.playback_process.poll() is None:
            try:
                self.playback_process.terminate()
                self.playback_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.playback_process.kill()
            except Exception as e:
                print(f"Error terminating playback process: {e}")
        self.playback_process = None
