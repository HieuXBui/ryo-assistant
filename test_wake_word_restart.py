#!/usr/bin/env python3
"""
Test script to verify wake word detection restart functionality.
This script simulates the AI response flow and checks if wake word detection restarts properly.
"""

import os
import sys
import time
import threading

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from core.main import RyoCore

def test_wake_word_restart():
    """Test the wake word restart functionality"""
    print("=== Testing Wake Word Restart Functionality ===")
    
    # Initialize the core
    core = RyoCore()
    
    try:
        print("1. Starting wake word detection...")
        core.wake_word_detector.start()
        time.sleep(2)
        
        print(f"2. Wake word detector running: {core.wake_word_detector.is_running()}")
        
        print("3. Simulating AI response completion...")
        # Simulate the flow that happens after AI response
        core.reset_to_idle()
        
        print("4. Waiting for restart...")
        time.sleep(3)  # Wait for the delayed restart
        
        print(f"5. Wake word detector running after restart: {core.wake_word_detector.is_running()}")
        
        if core.wake_word_detector.is_running():
            print("✅ SUCCESS: Wake word detection restarted successfully!")
        else:
            print("❌ FAILED: Wake word detection did not restart")
            
        print("6. Testing force restart...")
        core.force_restart_wake_word()
        time.sleep(1)
        
        print(f"7. Wake word detector running after force restart: {core.wake_word_detector.is_running()}")
        
        if core.wake_word_detector.is_running():
            print("✅ SUCCESS: Force restart worked!")
        else:
            print("❌ FAILED: Force restart did not work")
            
    except Exception as e:
        print(f"❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("8. Cleaning up...")
        core.shutdown()
        print("Test completed.")

if __name__ == "__main__":
    test_wake_word_restart() 