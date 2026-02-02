import os
from datetime import timedelta

# Flask Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "crowd_secret_key_change_in_production")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///database.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_key_change_in_production")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Crowd Detection Configuration
THRESHOLD = int(os.getenv("CROWD_THRESHOLD", "10"))
DETECTION_CONFIDENCE = float(os.getenv("DETECTION_CONFIDENCE", "0.5"))

# Camera Configuration
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")  # 0 for USB, or RTSP URL
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))
CAMERA_FPS = int(os.getenv("CAMERA_FPS", "30"))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Model Paths
MODEL_PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
MODEL_WEIGHTS = "models/MobileNetSSD_deploy.caffemodel"
