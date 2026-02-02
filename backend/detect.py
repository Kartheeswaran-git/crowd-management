import cv2
import numpy as np
import os
import config
import threading

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Load model with error handling
net = None
model_loaded = False

def load_model():
    """Load MobileNet-SSD model"""
    global net, model_loaded
    
    try:
        if not os.path.exists(config.MODEL_PROTOTXT):
            print(f"Warning: Model prototxt not found at {config.MODEL_PROTOTXT}")
            return False
        
        if not os.path.exists(config.MODEL_WEIGHTS):
            print(f"Warning: Model weights not found at {config.MODEL_WEIGHTS}")
            return False
        
        net = cv2.dnn.readNetFromCaffe(config.MODEL_PROTOTXT, config.MODEL_WEIGHTS)
        model_loaded = True
        print("MobileNet-SSD model loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

# Try to load model on import
load_model()


# Global lock for thread-safe inference
model_lock = threading.Lock()

def detect_people(frame, draw_boxes=False, confidence_threshold=None):
    """
    Detect people in a frame using MobileNet-SSD
    
    Args:
        frame: Input image frame
        draw_boxes: Whether to draw bounding boxes on the frame
        confidence_threshold: Minimum confidence for detection (uses config default if None)
    
    Returns:
        tuple: (count, detections_list, annotated_frame)
    """
    global net, model_loaded
    
    # Minimum confidence
    if confidence_threshold is None:
        confidence_threshold = config.DETECTION_CONFIDENCE
        
    try:
        # Use a lock to ensure thread-safe access to the model
        with model_lock:
            if not model_loaded:
                # Try to load model again
                if not load_model():
                    return 0, [], frame
            
            h, w = frame.shape[:2]
            
            # Create blob from image
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)), 
                0.007843,
                (300, 300), 
                127.5
            )
            
            # Set input and forward pass
            net.setInput(blob)
            detections = net.forward()
            
            count = 0
            detections_list = []
            annotated_frame = frame.copy() if draw_boxes else frame
            
            # Process detections
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > confidence_threshold:
                    idx = int(detections[0, 0, i, 1])
                    
                    if idx < len(CLASSES) and CLASSES[idx] == "person":
                        count += 1
                        
                        # Get bounding box coordinates
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        
                        # Handle NaN/Inf and clip coordinates to frame boundaries
                        # This prevents the "Illegal instruction: 4" crash on macOS
                        box = np.nan_to_num(box, nan=0, posinf=0, neginf=0)
                        startX = int(max(0, min(w - 1, box[0])))
                        startY = int(max(0, min(h - 1, box[1])))
                        endX = int(max(0, min(w - 1, box[2])))
                        endY = int(max(0, min(h - 1, box[3])))
                        
                        # Store detection info
                        detections_list.append({
                            'confidence': float(confidence),
                            'bbox': {
                                'x1': startX,
                                'y1': startY,
                                'x2': endX,
                                'y2': endY
                            }
                        })
                        
                        # Draw bounding box if requested
                        if draw_boxes:
                            # Draw rectangle
                            cv2.rectangle(annotated_frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                            
                            # Draw label with confidence
                            label = f"Person: {confidence:.2f}"
                            y = startY - 15 if startY - 15 > 15 else startY + 15
                            cv2.putText(annotated_frame, label, (startX, y),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return count, detections_list, annotated_frame
            
    except Exception as e:
        print(f"Error in detection: {e}")
        return 0, [], frame
