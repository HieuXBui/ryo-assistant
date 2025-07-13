# === Ryo AI Assistant - Wake Word Detector ===
# This file is responsible for listening for the "Hey Ryo" wake word.
# It uses the PicoVoice Porcupine engine, which is very efficient and runs offline.

# --- Step 1: Import Necessary Libraries ---

# 'os' is used for interacting with the operating system, like checking if files exist.
import os
# 'struct' is used to handle binary data, which is how audio is processed.
import struct
# 'threading' allows us to run the listening process in the background without freezing the app.
import threading
# 'platform' helps us identify the operating system (e.g., macOS, Windows) to use the correct model file.
import platform
# 'pyaudio' is a library that allows Python to access the microphone.
import pyaudio
# 'pvporcupine' is the official Python library for the Porcupine wake word engine.
import pvporcupine
# We import the specific error class to handle exceptions gracefully.
try:
    from pvporcupine import PorcupineError
except ImportError:
    # If the import fails (e.g., older library version), create a dummy class
    # so the 'except' block doesn't crash the program.
    class PorcupineError(Exception):
        pass
# We import our specific configuration settings from the 'core.config' file.
from core.config import (
    PORCUPINE_ACCESS_KEY, # Your secret key from the PicoVoice console.
    BASE_DIR              # The root directory of our project.
)

# --- Step 2: Define the WakeWordDetector Class ---

class WakeWordDetector:
    """A class dedicated to detecting a wake word using the Porcupine engine."""

    # The __init__ method is the constructor. It's called when we create a new WakeWordDetector object.
    def __init__(self, on_wake_word: callable):
        """
        Initializes the WakeWordDetector.
        Args:
            on_wake_word (callable): The function that should be called when the wake word is detected.
                                     This is a "callback" function.
        """
        # Store the function to call when the wake word is heard.
        self.on_wake_word = on_wake_word
        # Initialize all the components to 'None'. They will be set up in the _initialize_porcupine method.
        self.porcupine = None      # This will hold the Porcupine engine instance.
        self.p_audio = None        # This will hold the PyAudio instance, which manages the microphone.
        self.audio_stream = None   # This is the stream of audio data coming from the microphone.
        self._running = False       # A flag to control the main listening loop.
        self._thread = None         # This will hold the background thread object.

        # Call the private method to set up Porcupine. The underscore indicates it's for internal use.
        self._initialize_porcupine()

    def _initialize_porcupine(self):
        """Sets up the Porcupine engine and the microphone audio stream."""
        try:
            if not PORCUPINE_ACCESS_KEY:
                print("Warning: Porcupine access key not found. Wake word detection is disabled.")
                return

            keyword_paths = self._get_keyword_paths()
            if not keyword_paths:
                print("Warning: No valid Porcupine keyword files found. Wake word detection is disabled.")
                return

            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keyword_paths=keyword_paths,
                sensitivities=[0.90]
            )

            self.p_audio = pyaudio.PyAudio()
            print("Wake word detector initialized successfully.")

        except PorcupineError as e:
            print(f"Failed to initialize Porcupine: {e}")
            self.porcupine = None
            self.p_audio = None
        except Exception as e:
            print(f"An unexpected error occurred during Porcupine initialization: {e}")
            self.porcupine = None
            self.p_audio = None

    def _get_keyword_paths(self):
        """
        Dynamically finds the correct wake word file path based on the OS and architecture.
        This is much more robust than hardcoding a single filename.
        """
        system = platform.system()
        machine = platform.machine()

        # Determine the platform suffix (e.g., 'mac', 'windows', 'linux')
        if system == 'Darwin':
            platform_name = 'mac'
        elif system == 'Windows':
            platform_name = 'windows'
        elif system == 'Linux':
            platform_name = 'linux'
        else:
            platform_name = None # Unsupported OS

        # Determine the architecture suffix for Macs (e.g., 'm1' for arm64)
        if platform_name == 'mac' and machine == 'arm64':
            keyword_file = f"Hey-Ryo_{platform_name}_m1.ppn"
        elif platform_name:
            keyword_file = f"Hey-Ryo_{platform_name}.ppn"
        else:
            keyword_file = None

        # If we have a valid filename, check if it exists
        if keyword_file:
            keyword_path = os.path.join(BASE_DIR, 'assets', keyword_file)
            if os.path.exists(keyword_path):
                print(f"Found custom wake word: {keyword_file.split('.')[0]}")
                return [keyword_path]

        # If no custom file is found, fall back to the built-in keyword
        print("Using built-in 'porcupine' keyword. Create a 'Hey Ryo' model for custom wake word.")
        return [pvporcupine.KEYWORD_PATHS['porcupine']]

    def start(self):
        """Starts the wake word detection process in a separate, non-blocking thread."""
        print(f"[DEBUG] WakeWordDetector.start() called")
        
        # If Porcupine failed to initialize, we can't start.
        if not self.porcupine:
            print("Wake word detection disabled (no Porcupine access key or initialization failed)")
            return

        # If the detector is already running, don't start another one.
        if self._running:
            print("[WakeWordDetector] Already running.")
            return

        # Ensure any existing thread is properly stopped
        if self._thread and self._thread.is_alive():
            print("[DEBUG] Stopping existing thread before restart")
            self.stop()
            import time
            time.sleep(0.1)  # Brief pause to ensure cleanup

        # Open a fresh audio stream each time we start.
        try:
            print(f"[DEBUG] Attempting to open audio stream...")
            print(f"[DEBUG] Sample rate: {self.porcupine.sample_rate}")
            print(f"[DEBUG] Frame length: {self.porcupine.frame_length}")
            print(f"[DEBUG] PyAudio instance: {self.p_audio}")
            
            self.audio_stream = self.p_audio.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            print(f"[DEBUG] Audio stream opened successfully")
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Failed to open audio stream for wake word detector: {e}")
            print(f"[DEBUG] Audio stream error details: {type(e).__name__}: {e}")
            
            # Check if it's a device busy error (common with FaceTime, calls, etc.)
            if "busy" in error_msg or "10863" in error_msg or "cannot do in current context" in error_msg:
                print("[WARNING] Audio device appears to be busy (possibly due to FaceTime, calls, or other audio apps)")
                print("[INFO] Wake word detection will be disabled until audio device is available")
                return
            
            # Try to reinitialize PyAudio and try again
            try:
                print(f"[DEBUG] Attempting to reinitialize PyAudio...")
                if self.p_audio:
                    self.p_audio.terminate()
                self.p_audio = pyaudio.PyAudio()
                print(f"[DEBUG] PyAudio reinitialized, trying again...")
                
                self.audio_stream = self.p_audio.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
                print(f"[DEBUG] Audio stream opened successfully after reinitialization")
            except Exception as e2:
                error_msg2 = str(e2).lower()
                if "busy" in error_msg2 or "10863" in error_msg2 or "cannot do in current context" in error_msg2:
                    print("[WARNING] Audio device still busy after PyAudio reinitialization")
                    print("[INFO] Wake word detection will be disabled until audio device is available")
                    return
                print(f"Failed to reinitialize PyAudio: {e2}")
                # Try one more time with a fresh PyAudio instance
                try:
                    print(f"[DEBUG] Final attempt with fresh PyAudio...")
                    if self.p_audio:
                        self.p_audio.terminate()
                    self.p_audio = pyaudio.PyAudio()
                    self.audio_stream = self.p_audio.open(
                        rate=self.porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=self.porcupine.frame_length
                    )
                    print(f"[DEBUG] Audio stream opened successfully on final attempt")
                except Exception as e3:
                    error_msg3 = str(e3).lower()
                    if "busy" in error_msg3 or "10863" in error_msg3 or "cannot do in current context" in error_msg3:
                        print("[WARNING] Audio device busy on final attempt")
                        print("[INFO] Wake word detection will be disabled until audio device is available")
                    else:
                        print(f"All attempts to open audio stream failed: {e3}")
                    return

        # Set the running flag to True to start the loop in the thread.
        self._running = True
        # Create a new thread. 'target' is the function the thread will run.
        # 'daemon=True' means the thread will automatically exit when the main program ends.
        self._thread = threading.Thread(target=self._run, daemon=True)
        # Start the thread.
        self._thread.start()
        print("Wake word detector started...")

    def _run(self):
        """The main loop that continuously reads audio from the mic and checks for the wake word."""
        print("[WakeWordDetector] Listening for wake word...")
        print(f"[DEBUG] Wake word detection thread started, porcupine: {self.porcupine is not None}")
        
        # This loop will continue as long as the 'running' flag is True.
        while self._running:
            try:
                # Read a chunk of audio data from the microphone stream.
                # We set exception_on_overflow=False to prevent crashes if the CPU is busy
                # and can't process the audio data in time. It just drops the old data.
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                # Convert the raw audio data (bytes) into a list of 16-bit integers that Porcupine can understand.
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                # Feed the audio chunk into the Porcupine engine.
                keyword_index = self.porcupine.process(pcm)

                # The 'process' method returns -1 if no keyword is detected.
                # It returns 0 or greater if a keyword is found (0 corresponds to the first keyword in our list).
                if keyword_index >= 0:
                    print("Wake word detected!")
                    # Call the callback function that was passed to __init__.
                    self.on_wake_word()
                    self._running = False  # Allow restart after detection
                    break # Exit the loop to stop the thread.
            except IOError as e:
                # This error can happen if the audio stream is closed while we're trying to read from it.
                if self._running:
                    print(f"Audio stream error: {e}")
                break # Exit the loop to stop the thread.
            except Exception as e:
                print(f"An unexpected error occurred in the run loop: {e}")
        print("[WakeWordDetector] Exiting listening thread.")

    def is_running(self) -> bool:
        """Checks if the wake word detection thread is currently running."""
        return self._thread is not None and self._thread.is_alive()

    def stop(self):
        """Stops the wake word detection thread and cleanly closes the audio stream."""
        if not self._running:
            return
        print("[WakeWordDetector] Stopping...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=1) # Wait for the thread to finish cleanly.
            self._thread = None

        # Close the stream to release the microphone for other components.
        if self.audio_stream:
            try:
                if self.audio_stream.is_active():
                    self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")
            finally:
                self.audio_stream = None

        # Add a small delay to ensure audio device is fully released
        import time
        time.sleep(0.1)
        print("Wake word detector stopped.")

    def force_restart(self):
        """Force restart the wake word detector by stopping and starting it."""
        print("[DEBUG] Force restarting wake word detector...")
        self.stop()
        import time
        time.sleep(0.5)  # Wait for cleanup
        self.start()

    def start_with_retry(self, max_retries=5, retry_delay=10):
        """Start wake word detection with automatic retry if audio device is busy"""
        print(f"[DEBUG] Starting wake word detection with retry (max {max_retries} attempts, {retry_delay}s delay)")
        
        def retry_worker():
            import time
            for attempt in range(max_retries):
                try:
                    print(f"[DEBUG] Attempt {attempt + 1}/{max_retries} to start wake word detection")
                    self.start()
                    
                    # Check if it actually started
                    if self.is_running():
                        print(f"[DEBUG] Wake word detection started successfully on attempt {attempt + 1}")
                        return
                    else:
                        print(f"[DEBUG] Wake word detection failed to start on attempt {attempt + 1}")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "busy" in error_msg or "10863" in error_msg or "cannot do in current context" in error_msg:
                        print(f"[INFO] Audio device busy on attempt {attempt + 1}, will retry in {retry_delay} seconds...")
                    else:
                        print(f"[ERROR] Unexpected error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:  # Don't sleep after the last attempt
                    time.sleep(retry_delay)
            
            print(f"[WARNING] Failed to start wake word detection after {max_retries} attempts")
            print("[INFO] Audio device may still be busy. Try ending calls or closing audio apps.")
        
        # Run retry in background thread
        threading.Thread(target=retry_worker, daemon=True).start()

    def __del__(self):
        """This is a special Python method called a destructor. It ensures cleanup happens
        when the object is about to be destroyed, preventing resource leaks."""
        # First, ensure the listening thread is stopped.
        if self.is_running():
            self.stop()
            
        if self.p_audio:
            self.p_audio.terminate()
            self.p_audio = None

        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
