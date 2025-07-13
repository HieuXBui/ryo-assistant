# === Ryo AI Assistant - Ollama Local AI Handler ===
# This file manages all communication with a locally running Ollama instance.
# It allows the assistant to use powerful open-source models without an internet connection.

# --- Step 1: Import Necessary Libraries ---

# 'subprocess' is a standard Python library used to run external command-line programs.
# We use it here to execute the 'ollama' command.
import subprocess

# --- Step 2: Define the OllamaHandler Class ---

class OllamaHandler:
    """A client for interacting with a local Ollama LLM instance via the command line."""

    # The constructor, called when a new OllamaHandler object is created.
    def __init__(self, model: str = "mistral"):
        """Initializes the handler with a specific Ollama model name."""
        # The name of the Ollama model to use (e.g., 'mistral', 'llama3', 'phi3').
        # This model must be pulled first using 'ollama pull <model_name>'.
        self.model = model
        # A system prompt is a set of instructions given to the AI to define its persona and task.
        # This helps ensure its responses are consistent and aligned with its intended character.
        self.system_prompt = (
            "You are Ryo, a smart and efficient AI voice assistant. Keep responses brief and to the point.\n\n"
            "Your personality:\n"
            "- Helpful and direct\n"
            "- Brief and concise\n"
            "- Friendly but not overly chatty\n"
            "- Speak naturally and clearly\n\n"
            "Response guidelines:\n"
            "- Keep responses SHORT (1-2 sentences maximum)\n"
            "- Get straight to the point\n"
            "- No unnecessary explanations unless specifically asked\n"
            "- For math, just give the answer briefly\n"
            "- Be accurate and helpful\n\n"
            "You excel at:\n"
            "- Quick answers to questions\n"
            "- Math calculations\n"
            "- General knowledge\n"
            "- Brief explanations\n\n"
            "IMPORTANT: If the user asks 'what model am I using right now', 'which model am I using', or 'what AI model am I using', always respond with 'You are currently using the Ollama model.'\n\n"
            "Remember: Keep it short and sweet. Don't ramble or over-explain."
        )

    def ask(self, prompt: str) -> str:
        """Sends a prompt to the local Ollama model and returns its response."""
        # We construct the command-line arguments as a list of strings, without the prompt.
        command = [
            "/usr/local/bin/ollama", "run", self.model
        ]
        full_prompt = self.system_prompt + "\n\nUser: " + prompt
        try:
            # Execute the command, passing the prompt via stdin.
            result = subprocess.run(
                command,
                input=full_prompt,
                capture_output=True,  # Capture the command's standard output and standard error.
                text=True,            # Decode stdout and stderr as text using the default encoding.
                check=True,           # If the command returns a non-zero exit code (an error), raise a CalledProcessError.
                timeout=60  # 60 seconds timeout
            )
            # If successful, the model's response is in 'stdout'. We strip any extra whitespace.
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip()
            print(f"Ollama Error: {error_message}")
            return f"I'm having trouble with Ollama right now. ({error_message})"
        except Exception as e:
            print(f"Unexpected error in OllamaHandler.ask: {e}")
            return f"I'm having trouble with Ollama right now. ({e})"
