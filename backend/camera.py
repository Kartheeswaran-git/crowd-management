import os
import threading
import time
import numpy as np

# Conditional import for camera - won't crash if cv2 unavailable
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("WARNING: OpenCV not available. Running in mock mode.")

from detect import detect_people
import config

# Detect if running in cloud environment (no camera hardware)
CLOUD_MODE = os.getenv("CLOUD_MODE", "false").lower() == "true" or not CV2_AVAILABLE

class CameraManager:
    """Manage camera capture and people detection"""
    
    def __init__(self):
        self.cap = None
        self.latest_count = 0
        self.latest_frame = None
        self.latest_detections = []
        self.is_running = False
        self.lock = threading.Lock()
        self.camera_source = config.CAMERA_SOURCE
        self.thread = None
        self.stop_event = threading.Event()
        
    def initialize_camera(self):
        """Initialize camera capture with better error handling"""
        # In cloud mode, skip camera initialization
        if CLOUD_MODE:
            print("Running in CLOUD_MODE - camera hardware disabled")
            return True
            
        if self.cap is not None and self.cap.isOpened():
            return True
        
        # Try to parse camera source as integer (for USB cameras)
        try:
            camera_index = int(self.camera_source)
            # Try multiple camera indices
            for index in [camera_index, 0, 1, 2]:
                print(f"Attempting to open camera at index {index}...")
                self.cap = cv2.VideoCapture(index)
                
                if self.cap.isOpened():
                    # Set camera properties
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
                    
                    # Try to read a test frame
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        print(f"✓ Camera initialized successfully at index {index}")
                        return True
                    else:
                        self.cap.release()
                        print(f"  Camera at index {index} opened but cannot read frames")
                
            print("✗ Failed to initialize any camera")
            return False
            
        except ValueError:
            # Camera source is a string (RTSP URL or video file)
            print(f"Attempting to open camera from source: {self.camera_source}")
            self.cap = cv2.VideoCapture(self.camera_source)
            
            if self.cap.isOpened():
                print(f"✓ Camera initialized successfully from {self.camera_source}")
                return True
            else:
                print(f"✗ Failed to open camera from {self.camera_source}")
                return False

    
    def start(self):
        """Start background capture thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run_capture, daemon=True)
        self.thread.start()
        print("Camera background thread started")

    def stop(self):
        """Stop background capture thread"""
        self.is_running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)
        self.release_camera()
        print("Camera background thread stopped")

    def _run_capture(self):
        """Internal loop for background capture and detection"""
        while not self.stop_event.is_set():
            # In cloud mode, generate mock data
            if CLOUD_MODE:
                # Create a simple mock frame (640x480 black image with text)
                mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                if CV2_AVAILABLE:
                    cv2.putText(mock_frame, "CLOUD MODE - No Camera", (120, 240),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                with self.lock:
                    self.latest_count = 0  # Mock count
                    self.latest_frame = mock_frame
                    self.latest_detections = []
                
                time.sleep(1.0)
                continue
            
            if self.cap is None or not self.cap.isOpened():
                if not self.initialize_camera():
                    time.sleep(1)
                    continue
            
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                print("Error reading frame, attempting to reconnect...")
                self.release_camera()
                time.sleep(1)
                continue
            
            # Perform detection with bounding boxes
            try:
                count, detections, annotated_frame = detect_people(frame, draw_boxes=True)
                
                # Update latest values
                with self.lock:
                    self.latest_count = count
                    self.latest_frame = annotated_frame
                    self.latest_detections = detections
            except Exception as e:
                print(f"Error in background detection: {e}")
            
            # Control frame rate
            time.sleep(1.0 / config.CAMERA_FPS)

    def release_camera(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def get_count(self):
        """Get latest people count"""
        with self.lock:
            return self.latest_count
    
    def get_frame(self):
        """Get latest frame"""
        with self.lock:
            return self.latest_frame
    
    def get_detections(self):
        """Get latest detection details"""
        with self.lock:
            return self.latest_detections
    
    def update_detection(self):
        """No-op in threaded version, data is updated in background"""
        pass
    
    def generate_frames(self):
        """Generate frames for video streaming from latest results"""
        while True:
            # If not running, start the background thread
            if not self.is_running:
                self.start()
            
            with self.lock:
                annotated_frame = self.latest_frame.copy() if self.latest_frame is not None else None
            
            if annotated_frame is None:
                time.sleep(0.1)
                continue
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            
            if not ret:
                time.sleep(0.1)
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Small delay to keep streaming smooth
            time.sleep(1.0 / config.CAMERA_FPS)


# Global camera manager instance
camera_manager = CameraManager()

def get_count():
    """Get current people count"""
    # Ensure background thread is running
    if not camera_manager.is_running:
        camera_manager.start()
    return camera_manager.get_count()

def get_detections():
    """Get current detection details"""
    return camera_manager.get_detections()

def generate_video_stream():
    """Generate video stream for Flask response"""
    return camera_manager.generate_frames()

def start_camera():
    """Start the background camera thread"""
    camera_manager.start()

def stop_camera():
    """Stop the background camera thread"""
    camera_manager.stop()
