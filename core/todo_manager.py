import json
import os
from datetime import datetime
from typing import List, Dict

class TodoManager:
    """Manages to-do list with sci-fi styling and persistence"""
    
    def __init__(self, file_path: str = "data/todos.json"):
        self.file_path = file_path
        self.todos = []
        self._ensure_data_dir()
        self.load_todos()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists"""
        dir_path = os.path.dirname(self.file_path)
        if dir_path:  # Only create directory if there is a directory path
            os.makedirs(dir_path, exist_ok=True)
    
    def load_todos(self):
        """Load todos from file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    self.todos = json.load(f)
            else:
                self.todos = []
        except Exception as e:
            print(f"[ERROR] Failed to load todos: {e}")
            self.todos = []
    
    def save_todos(self):
        """Save todos to file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.todos, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save todos: {e}")
    
    def add_todo(self, text: str) -> Dict:
        """Add a new todo item"""
        todo = {
            'id': len(self.todos) + 1,
            'text': text,
            'completed': False,
            'created': datetime.now().isoformat(),
            'priority': 'normal'
        }
        self.todos.append(todo)
        self.save_todos()
        return todo
    
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo item by ID"""
        for i, todo in enumerate(self.todos):
            if todo['id'] == todo_id:
                del self.todos[i]
                self.save_todos()
                return True
        return False
    
    def toggle_todo(self, todo_id: int) -> bool:
        """Toggle completion status of a todo"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = not todo['completed']
                self.save_todos()
                return True
        return False
    
    def get_todos(self) -> List[Dict]:
        """Get all todos"""
        return self.todos
    
    def get_completed_count(self) -> int:
        """Get count of completed todos"""
        return sum(1 for todo in self.todos if todo['completed'])
    
    def get_pending_count(self) -> int:
        """Get count of pending todos"""
        return sum(1 for todo in self.todos if not todo['completed'])
    
    def clear_completed(self):
        """Remove all completed todos"""
        self.todos = [todo for todo in self.todos if not todo['completed']]
        self.save_todos()
    
    def format_todo_display(self, todo: Dict) -> str:
        """Format todo for sci-fi display"""
        status = "✓" if todo['completed'] else "○"
        priority_icon = "⚡" if todo.get('priority') == 'high' else "●"
        return f"{status} {priority_icon} {todo['text']}"
    
    def get_stats(self) -> Dict:
        """Get todo statistics"""
        total = len(self.todos)
        completed = self.get_completed_count()
        pending = self.get_pending_count()
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': completion_rate
        } 