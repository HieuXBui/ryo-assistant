import sounddevice as sd
import numpy as np
import whisper
import tempfile
import scipy.io.wavfile
import threading
import ssl
import certifi

class WhisperListener:
    def __init__(self, model_size="base"):
        # Fix SSL certificate issues on macOS
        try:
            ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
        except:
            pass
        
        try:
            self.model = whisper.load_model(model_size)  # You can use "tiny", "base", "small", "medium", "large"
        except Exception as e:
            print(f"[ERROR] Failed to load Whisper model: {e}")
            print("[INFO] Trying to download with SSL fix...")
            # Try with a different approach
            import os
            os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
            self.model = whisper.load_model(model_size)
            
        self.is_recording = False
        self.audio = None
        self.samplerate = 16000
        self.duration = 5  # seconds
        self.recording_thread = None
        self.on_finish_callback = None

    def start_listening(self):
        if self.is_recording:
            return
        self.is_recording = True
        print("[WhisperListener] Started recording...")
        self.audio = None
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()

    def _record_audio(self):
        self.audio = sd.rec(int(self.duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='int16')
        sd.wait()
        self.is_recording = False
        print("[WhisperListener] Finished recording.")

    def stop_and_transcribe(self, on_finish=None):
        if self.is_recording:
            print("[WhisperListener] Waiting for recording to finish...")
            self.recording_thread.join()
        print("[WhisperListener] Transcribing...")
        if self.audio is None:
            print("[WhisperListener] No audio recorded.")
            if on_finish:
                on_finish("")
            return
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            scipy.io.wavfile.write(f.name, self.samplerate, self.audio)
            result = self.model.transcribe(f.name)
            text = result["text"].strip()
            print(f"[WhisperListener] Transcribed: '{text}'")
            if on_finish:
                on_finish(text) 