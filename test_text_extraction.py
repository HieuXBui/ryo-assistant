#!/usr/bin/env python3
"""
Test script to verify the improved text extraction for todo commands
"""

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from core.controller import AssistantController

def test_text_extraction():
    """Test the _extract_todo_task method with various inputs"""
    print("Testing text extraction for todo commands...")
    
    # Create a controller instance (we don't need to initialize everything)
    controller = AssistantController()
    
    # Test cases
    test_cases = [
        ("Add groceries to my to-do list", "add"),
        ("Add buy milk to my todo list", "add"),
        ("Add call the doctor to my to-do list", "add"),
        ("Remove groceries from my to-do list", "remove"),
        ("Remove buy milk from my todo list", "remove"),
        ("Remove call the doctor from my to-do list", "remove"),
        ("Add groceries", "add"),
        ("Remove groceries", "remove"),
        ("Add to my todo list buy groceries", "add"),
        ("Remove from my todo list buy groceries", "remove"),
    ]
    
    print("\n" + "="*60)
    print("TESTING TEXT EXTRACTION")
    print("="*60)
    
    for i, (input_text, command_type) in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: '{input_text}'")
        print(f"Command type: {command_type}")
        
        # Extract the task
        extracted = controller._extract_todo_task(input_text, command_type)
        print(f"Extracted: '{extracted}'")
        
        # Simple validation
        if extracted and len(extracted.strip()) > 0:
            print("✓ PASS - Task extracted successfully")
        else:
            print("✗ FAIL - No task extracted")
        
        print("-" * 40)

if __name__ == "__main__":
    test_text_extraction() 