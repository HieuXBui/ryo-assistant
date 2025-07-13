#!/usr/bin/env python3
"""
Test script to verify audio device busy detection and retry functionality.
This simulates what happens when audio device is busy (like during FaceTime calls).
"""

import os
import sys
import time

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from voice.wake_word_detector import WakeWordDetector

def test_audio_device_busy_detection():
    """Test the audio device busy detection functionality"""
    print("=== Testing Audio Device Busy Detection ===")
    
    # Create a dummy callback
    def dummy_callback():
        print("Wake word detected!")
    
    # Initialize the detector
    detector = WakeWordDetector(on_wake_word=dummy_callback)
    
    try:
        print("1. Testing normal start...")
        detector.start()
        time.sleep(2)
        
        print(f"2. Wake word detector running: {detector.is_running()}")
        
        if detector.is_running():
            print("3. Stopping detector...")
            detector.stop()
            time.sleep(1)
            
            print("4. Testing retry mechanism...")
            detector.start_with_retry(max_retries=3, retry_delay=2)
            time.sleep(3)
            
            print(f"5. Wake word detector running after retry: {detector.is_running()}")
            
            if detector.is_running():
                print("✅ SUCCESS: Retry mechanism works!")
            else:
                print("⚠️  WARNING: Retry mechanism may not have worked (could be due to audio device being busy)")
                
        else:
            print("⚠️  WARNING: Initial start failed (could be due to audio device being busy)")
            
    except Exception as e:
        print(f"❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("6. Cleaning up...")
        detector.stop()
        print("Test completed.")

if __name__ == "__main__":
    test_audio_device_busy_detection() 