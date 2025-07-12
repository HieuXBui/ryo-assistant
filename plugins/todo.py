# === Ryo AI Assistant - To-Do List Plugin ===
# This file defines a self-contained plugin for managing a simple to-do list.
# It demonstrates how new functionalities can be added to the assistant.

# --- Step 1: Import necessary libraries ---
import os
from rapidfuzz import process, fuzz
# We import BASE_DIR to reliably create paths relative to the project root.
from core.config import BASE_DIR

# --- Step 2: Define the TodoPlugin Class ---

class TodoPlugin:
    """Manages the to-do list, including loading, saving, and editing items."""

    # The __init__ method is the constructor, called when a TodoPlugin object is created.
    def __init__(self):
        """Initializes the plugin, sets up file paths, and loads existing items."""
        # Define the path to the 'config' directory where we'll store data.
        self.config_dir = os.path.join(BASE_DIR, "config")
        # Define the full path to the to-do list file.
        self.todo_file = os.path.join(self.config_dir, "todo.txt")
        
        # Create the 'config' directory if it doesn't already exist.
        # 'exist_ok=True' prevents an error if the directory is already there.
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load the to-do items from the file into memory. The underscore indicates
        # that _load_items is an internal 'helper' method for this class.
        self.items = self._load_items()

    def _load_items(self) -> list:
        """Loads to-do items from the 'todo.txt' file into a Python list."""
        # If the to-do file doesn't exist yet, there are no items to load.
        if not os.path.exists(self.todo_file):
            return [] # Return an empty list.
        
        # 'with open(...)' is the standard, safe way to handle files in Python.
        # It ensures the file is automatically closed even if errors occur.
        # 'r' stands for 'read mode'.
        with open(self.todo_file, 'r') as f:
            # This is a list comprehension. It's a concise way to create a list.
            # It reads each line from the file, removes leading/trailing whitespace (.strip()),
            # and adds it to the list, but only if the line isn't empty.
            return [line.strip() for line in f if line.strip()]

    def _save_items(self):
        """Saves the current list of items back to the 'todo.txt' file."""
        # We open the file in 'write mode' ('w'). This will overwrite the file
        # with the new content, which is what we want.
        with open(self.todo_file, 'w') as f:
            # Loop through each item in our current list.
            for item in self.items:
                # Write the item to the file, followed by a newline character
                # so each item is on its own line.
                f.write(f"{item}\n")

    def add_item(self, item_text: str) -> str:
        """Adds a new item to the list, saves it, and returns a confirmation message."""
        # Basic validation: if the user's command was empty, ask for clarification.
        if not item_text:
            return "I didn't catch that. What should I add?"
        
        # Add the new item to the end of our list in memory.
        self.items.append(item_text)
        # Save the updated list to the file to make it permanent.
        self._save_items()
        # Return a user-friendly confirmation string.
        return f"Okay, added '{item_text}' to your to-do list."

    def remove_item(self, item_text: str) -> str:
        """Removes an item using fuzzy string matching to find the best fit."""
        if not self.items:
            return "Your to-do list is already empty."

        if not item_text:
            return "I didn't catch that. What should I remove?"

        # Use rapidfuzz to find the best match. It's generally faster and was
        # installed as a dependency of thefuzz anyway. We use WRatio for a good
        # balance of matching logic.
        # extractOne returns (match, score, index), so we only need the first two.
        result = process.extractOne(item_text, self.items, scorer=fuzz.WRatio)
        if not result:
            return f"I couldn't find anything like '{item_text}' on your list."

        best_match, score, _ = result

        # We set a confidence threshold to avoid incorrect removals.
        # If the score is, say, 70 or higher, we're confident it's the right item.
        if score >= 70:
            self.items.remove(best_match)
            self._save_items()
            return f"Removed '{best_match}' from your to-do list."
        else:
            return f"I couldn't find anything like '{item_text}' on your list."

    def list_items(self) -> str:
        """Generates a formatted string of all current to-do items."""
        # If the list is empty, return a specific message.
        if not self.items:
            return "Your to-do list is empty."
        
        # Start building the response string that the assistant will speak.
        response = "Here's what's on your to-do list:\n"
        # 'enumerate' adds a counter to the loop. We start counting from 1.
        for i, item in enumerate(self.items, 1):
            # Append each item as a numbered list entry.
            response += f"{i}. {item}\n"
        return response
