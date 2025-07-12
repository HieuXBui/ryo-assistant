# === Ryo AI Assistant - Configuration ===
# This file centralizes all the configuration settings for the application.
# It loads sensitive keys from a .env file and defines constants that are used
# throughout the project, making it easy to change settings in one place.

# --- Step 1: Import necessary libraries ---
# === Ryo AI Assistant - Configuration ===
# This file centralizes all the configuration settings for the application.
# It loads sensitive keys from a .env file and defines constants that are used
# throughout the project, making it easy to change settings in one place.

# --- Step 1: Import necessary libraries ---
import os
import pvporcupine
from dotenv import load_dotenv
import sys

# --- Step 2: Load Environment Variables ---

# Define paths for the .env file and its template.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
env_example_path = os.path.join(BASE_DIR, '.env.example')

# Check if the crucial .env file exists before trying to load it.
if not os.path.exists(env_path):
    print("="*60)
    print("WARNING: Configuration file '.env' not found.")
    print("The application will run with limited functionality:")
    print("- Wake word detection will be disabled")
    print("- Some AI models may not work")
    print("")
    print("To enable full functionality, create a .env file with your API keys:")
    print("1. Copy .env.example to .env")
    print("2. Add your API keys to the .env file")
    print("3. Restart the application")
    print("="*60)
    # Don't exit, just continue with limited functionality

# If the .env file exists, load it.
# This is the standard way to handle secret keys without hardcoding them.
load_dotenv()
print(f"[DEBUG] GEMINI_API_KEY loaded: {os.getenv('GEMINI_API_KEY') is not None}")
print(f"[DEBUG] PORCUPINE_ACCESS_KEY loaded: {os.getenv('PORCUPINE_ACCESS_KEY') is not None}")

# --- Step 3: Define Core Application Paths ---

# This calculates the absolute path to the project's root directory.
# It's useful for creating reliable paths to other files, like assets or plugins,
# regardless of where the application is run from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Step 4: AI Model Configuration ---

# Fetches the name of the default AI model from the .env file.
# If the 'DEFAULT_MODEL' variable is not set in .env, it defaults to "Ollama".
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Ollama")

# Fetches the API key for the Google Gemini model from the .env file.
# If not provided, this will be `None`, and the Gemini handler will be disabled.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Step 5: Voice System Configuration ---

# Fetches the access key required for the Porcupine wake word engine.
# This key is obtained from PicoVoice. If it's not provided, wake word detection
# will be disabled.
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")


# --- Step 6: Audio Settings ---
# A global flag to control whether the assistant's responses are spoken out loud.
MUTE_AUDIO = False

# --- GUI Theme and Font Settings ---
# Centralized theme for a consistent look and feel.
THEME = {
    "BG_COLOR": "#0D1B2A",        # Dark blue background
    "TEXT_COLOR": "#E0E1DD",      # Off-white text
    "TEXT_COLOR_MUTED": "#8D99AE", # Muted gray for less important text
    "ACCENT_COLOR": "#415A77",     # Lighter blue for frames/widgets
    "HIGHLIGHT_COLOR": "#00FFFF", # Cyan for status text or highlights
    "FONT_NAME": "Menlo"           # A clean, monospaced font
}
