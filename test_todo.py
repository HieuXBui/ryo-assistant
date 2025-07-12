#!/usr/bin/env python3
"""
Simple test script to verify the todo system is working correctly
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from core.todo_manager import TodoManager

def test_todo_manager():
    """Test the TodoManager functionality"""
    print("Testing TodoManager...")
    
    # Create a test instance
    todo_manager = TodoManager("test_todos.json")
    
    # Test adding todos
    print("\n1. Adding todos...")
    todo1 = todo_manager.add_todo("Buy groceries")
    todo2 = todo_manager.add_todo("Call Dr. Banner")
    todo3 = todo_manager.add_todo("Project: Ryo v2")
    
    print(f"Added: {todo1['text']} (ID: {todo1['id']})")
    print(f"Added: {todo2['text']} (ID: {todo2['id']})")
    print(f"Added: {todo3['text']} (ID: {todo3['id']})")
    
    # Test getting todos
    print("\n2. Getting all todos...")
    todos = todo_manager.get_todos()
    print(f"Found {len(todos)} todos:")
    for todo in todos:
        status = "✓" if todo['completed'] else "○"
        print(f"  {status} {todo['text']} (ID: {todo['id']})")
    
    # Test toggling completion
    print("\n3. Toggling completion...")
    todo_manager.toggle_todo(todo1['id'])
    todos = todo_manager.get_todos()
    print("After toggle:")
    for todo in todos:
        status = "✓" if todo['completed'] else "○"
        print(f"  {status} {todo['text']} (ID: {todo['id']})")
    
    # Test stats
    print("\n4. Getting stats...")
    stats = todo_manager.get_stats()
    print(f"Total: {stats['total']}")
    print(f"Completed: {stats['completed']}")
    print(f"Pending: {stats['pending']}")
    print(f"Completion rate: {stats['completion_rate']:.1f}%")
    
    # Test deleting
    print("\n5. Deleting a todo...")
    todo_manager.delete_todo(todo2['id'])
    todos = todo_manager.get_todos()
    print(f"After deletion, found {len(todos)} todos:")
    for todo in todos:
        status = "✓" if todo['completed'] else "○"
        print(f"  {status} {todo['text']} (ID: {todo['id']})")
    
    # Clean up test file
    try:
        os.remove("test_todos.json")
        print("\n6. Cleaned up test file")
    except:
        pass
    
    print("\n✅ TodoManager test completed successfully!")

if __name__ == "__main__":
    test_todo_manager() 