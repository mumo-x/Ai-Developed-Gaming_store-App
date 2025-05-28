import cv2
import time
import sys

def test_camera():
    """Test camera functionality"""
    print("Testing camera...")
    
    # Try to open the camera
    print("Opening camera...")
    start_time = time.time()
    cap = cv2.VideoCapture(0)
    end_time = time.time()
    
    print(f"Camera initialization took {end_time - start_time:.2f} seconds")
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return False
    
    print("Camera opened successfully.")
    
    # Read a frame
    print("Reading frame...")
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame from camera.")
        cap.release()
        return False
    
    print("Frame read successfully.")
    print(f"Frame dimensions: {frame.shape}")
    
    # Save the frame
    print("Saving test frame...")
    cv2.imwrite("camera_test.jpg", frame)
    print("Test frame saved to camera_test.jpg")
    
    # Release the camera
    print("Releasing camera...")
    cap.release()
    print("Camera released.")
    
    return True

if __name__ == "__main__":
    print("Camera Test Utility")
    print("==================")
    print()
    
    success = test_camera()
    
    if success:
        print("\nCamera test completed successfully!")
    else:
        print("\nCamera test failed. Please check your camera connection.")
    
    input("\nPress Enter to exit...")