import os
import sys
import threading
from typing import Optional
from ai.ollama_handler import OllamaHandler

class ModelSwitcher:
    """
    Manages different AI models and handles switching between them.
    This is a simplified implementation that can be enhanced later.
    """
    
    def __init__(self):
        self.active_model_name = "Ollama"  # Default model
        self.ollama_handler = OllamaHandler(model="mistral")
        self.models = {
            "Ollama": self._ollama_ask,
            "Gemini": self._gemini_ask
        }
        
    def set_active_model(self, model_name: str):
        """Switch to a different AI model"""
        if model_name in self.models:
            self.active_model_name = model_name
            print(f"[ModelSwitcher] Switched to {model_name}")
        else:
            print(f"[ModelSwitcher] Unknown model: {model_name}")
    
    def ask(self, question: str) -> str:
        """Ask a question to the active AI model"""
        if self.active_model_name in self.models:
            return self.models[self.active_model_name](question)
        else:
            return f"Error: Unknown model {self.active_model_name}"
    
    def _ollama_ask(self, question: str) -> str:
        """Handle basic AI queries and calculations, otherwise call Ollama LLM"""
        question_lower = question.lower().strip()
        
        # Handle specific system queries only - be very specific
        if question_lower in ["what time is it", "what's the time", "time"]:
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
        elif question_lower in ["what date is it", "what's the date", "date", "what day is it"]:
            from datetime import datetime
            return f"Today's date is {datetime.now().strftime('%B %d, %Y')}"
        elif "weather" in question_lower and ("what" in question_lower or "how" in question_lower):
            return "I don't have access to real-time weather data, but you can check your local weather app or website."
        elif question_lower in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]:
            return "Hello! I'm Ryo, your AI assistant. How can I help you today?"
        elif question_lower in ["help", "what can you do", "what can you help with"]:
            return """I can help you with:
- Math calculations and problem solving
- Managing your todo list (add, remove, list tasks)
- Telling time and date
- Answering general questions
- Basic conversations

Try saying things like:
- \"What's 15 plus 27?\"
- \"Add groceries to my list\"
- \"What time is it?\"
- \"Hello\" or \"How are you?\" """
        elif question_lower in ["how are you", "how are you doing"]:
            return "I'm doing well, thank you for asking! I'm ready to help you with tasks and questions."
        
        # For ALL other queries (including math, general knowledge, etc.), call the real Ollama LLM
        try:
            print(f"[ModelSwitcher] Calling Ollama with: '{question}'")
            response = self.ollama_handler.ask(question)
            if response and response.strip():
                return response.strip()
            else:
                return "I'm sorry, I didn't get a response from the AI model."
        except Exception as e:
            print(f"[ModelSwitcher] Ollama error: {e}")
            return f"I'm having trouble reaching the Ollama model right now. ({e})"
    
    def _gemini_ask(self, question: str) -> str:
        """Handle Gemini-style responses (similar to Ollama for now)"""
        return self._ollama_ask(question) 