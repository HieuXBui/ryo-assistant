#!/usr/bin/env python3
"""
Test script to verify voice command processing for todo management
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from core.controller import AssistantController

def test_voice_commands():
    """Test voice command processing"""
    print("Testing voice command processing...")
    
    # Create controller without starting audio components
    controller = AssistantController()
    
    # Test cases for adding todos
    add_tests = [
        "add buy groceries",
        "add to my todo buy milk",
        "add to the todo list call mom",
        "remind me to finish project",
        "put clean room on my todo",
        "add to my to-do list study for exam",
        "add to the to do list exercise",
        "add to my to-do list buy groceries",
        "add to the todo list call doctor",
        "add to my to do list write report"
    ]
    
    print("\n=== Testing ADD Commands ===")
    for test in add_tests:
        print(f"\nTesting: '{test}'")
        result = controller._process_todo_command(test)
        print(f"Result: {result}")
        todos = controller.todo_manager.get_todos()
        print(f"Current todos: {[todo['text'] for todo in todos]}")
    
    # Test cases for removing todos
    remove_tests = [
        "remove buy groceries",
        "delete call mom",
        "remove from my todo buy milk",
        "delete from the todo list clean room",
        "take off study for exam from my todo"
    ]
    
    print("\n=== Testing REMOVE Commands ===")
    for test in remove_tests:
        print(f"\nTesting: '{test}'")
        result = controller._process_todo_command(test)
        print(f"Result: {result}")
        todos = controller.todo_manager.get_todos()
        print(f"Current todos: {[todo['text'] for todo in todos]}")
    
    # Test list command
    print("\n=== Testing LIST Command ===")
    list_test = "list my todos"
    print(f"Testing: '{list_test}'")
    result = controller._process_todo_command(list_test)
    print(f"Result: {result}")
    
    # Test clear command
    print("\n=== Testing CLEAR Command ===")
    clear_test = "clear completed"
    print(f"Testing: '{clear_test}'")
    result = controller._process_todo_command(clear_test)
    print(f"Result: {result}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_voice_commands() 