# AI-Powered Crowd Management and People Counting Alert System

A comprehensive full-stack application for real-time crowd monitoring using MobileNet-SSD deep learning architecture for person detection, integrated with a secure Flask backend and modern React.js frontend.

![System Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![React](https://img.shields.io/badge/react-19.2+-61dafb)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Features

### Backend (Python + Flask)
- **AI-Powered Detection**: MobileNet-SSD (Caffe) for real-time person detection
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Role-Based Access Control**: Admin and User roles with different permissions
- **Real-Time Monitoring**: Live people counting with configurable thresholds
- **Alert System**: Automatic crowd alerts when threshold is exceeded
- **Video Streaming**: Live camera feed with detection overlay
- **Analytics**: Historical data logging and statistics
- **RESTful API**: Comprehensive API endpoints for all operations

### Frontend (React.js)
- **Modern UI**: Beautiful, responsive design with glassmorphism effects
- **Real-Time Dashboard**: Live people count and alert status
- **Admin Panel**: User management, threshold configuration, and analytics
- **Live Video Feed**: Real-time camera stream with bounding boxes
- **Alert History**: View and track all crowd alerts
- **Secure Routes**: Protected routes with role-based access
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## 🏗️ System Architecture

```
crowd-management/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── auth.py                # JWT authentication & authorization
│   ├── models.py              # Database models (User, Settings, Alerts, Logs)
│   ├── camera.py              # Camera management & video streaming
│   ├── detect.py              # MobileNet-SSD person detection
│   ├── config.py              # Configuration settings
│   ├── init_db.py             # Database initialization script
│   ├── requirements.txt       # Python dependencies
│   └── models/
│       ├── MobileNetSSD_deploy.prototxt
│       └── MobileNetSSD_deploy.caffemodel
│
└── frontend/
    ├── package.json
    ├── public/
    └── src/
        ├── App.js             # Main app with routing
        ├── api.js             # Axios API client
        ├── context/
        │   └── AuthContext.js # Authentication context
        ├── pages/
        │   ├── Login.js       # Login page
        │   ├── Dashboard.js   # User dashboard
        │   └── Admin.js       # Admin panel
        └── components/
            ├── Navbar.js      # Navigation bar
            └── CounterCard.js # People count display
```

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm**: 8 or higher
- **Camera**: USB webcam, IP camera, or RTSP stream
- **MobileNet-SSD Model Files**: Download links provided below

## 🚀 Installation & Setup

### 1. Download MobileNet-SSD Model Files

Download the pre-trained MobileNet-SSD model files and place them in `backend/models/`:

```bash
cd backend/models

# Download prototxt file
wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/deploy.prototxt -O MobileNetSSD_deploy.prototxt

# Download caffemodel file
wget https://drive.google.com/uc?export=download&id=0B3gersZ2cHIxRm5PMWRoTkdHdHc -O MobileNetSSD_deploy.caffemodel
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with seed data
python init_db.py

# Run the Flask server
python app.py
```

The backend server will start on `http://localhost:5000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🔑 Default Credentials

After running `init_db.py`, use these credentials to log in:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**User Account:**
- Username: `user`
- Password: `user123`

⚠️ **Important**: Change these passwords in production!

## 🎯 Usage

### User Dashboard
1. Log in with user credentials
2. View real-time people count
3. Monitor alert status
4. Watch live camera feed with detection overlay
5. View recent alert history

### Admin Panel
1. Log in with admin credentials
2. Configure crowd threshold
3. Manage users (create, edit, delete)
4. View system statistics and analytics
5. Monitor all alerts and system activity

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

```python
# Crowd Detection
THRESHOLD = 10                    # Alert threshold
DETECTION_CONFIDENCE = 0.5        # Detection confidence (0.0-1.0)

# Camera Settings
CAMERA_SOURCE = "0"               # 0 for USB, or RTSP URL
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# JWT Settings
JWT_ACCESS_TOKEN_EXPIRES = 1 hour
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
DATABASE_URI=sqlite:///database.db
CROWD_THRESHOLD=10
DETECTION_CONFIDENCE=0.5
CAMERA_SOURCE=0
CORS_ORIGINS=http://localhost:3000
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Register new user (admin only)
- `GET /api/auth/verify` - Verify JWT token

### Monitoring
- `GET /api/count` - Get current people count and alert status
- `GET /api/video-feed` - Live video stream with detection overlay

### Alerts & Analytics
- `GET /api/alerts` - Get alert history
- `DELETE /api/alerts/clear` - Clear alert history (admin only)
- `GET /api/stats` - Get system statistics

### Settings
- `GET /api/settings` - Get system settings
- `PUT /api/settings` - Update settings (admin only)

### User Management
- `GET /api/users` - Get all users (admin only)
- `GET /api/users/:id` - Get specific user (admin only)
- `PUT /api/users/:id` - Update user (admin only)
- `DELETE /api/users/:id` - Delete user (admin only)

## 🎨 Technology Stack

### Backend
- **Flask**: Web framework
- **OpenCV**: Computer vision and DNN module
- **MobileNet-SSD**: Deep learning model for person detection
- **SQLAlchemy**: ORM for database operations
- **PyJWT**: JSON Web Token authentication
- **bcrypt**: Password hashing
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **React**: UI library
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Lucide React**: Modern icon library
- **CSS3**: Custom styling with modern features

## 🌐 Deployment

### Production Considerations

1. **Security**:
   - Change default passwords
   - Use strong SECRET_KEY and JWT_SECRET_KEY
   - Enable HTTPS
   - Implement rate limiting
   - Use environment variables for sensitive data

2. **Performance**:
   - Use production WSGI server (Gunicorn, uWSGI)
   - Enable caching
   - Optimize camera resolution for network bandwidth
   - Use CDN for frontend assets

3. **Scalability**:
   - Use PostgreSQL instead of SQLite
   - Implement Redis for caching
   - Use load balancer for multiple instances
   - Deploy on cloud platforms (AWS, Azure, GCP)

### Docker Deployment (Optional)

```dockerfile
# Example Dockerfile for backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🔍 Troubleshooting

### Camera Not Working
- Check camera permissions
- Verify CAMERA_SOURCE in config
- Test camera with `cv2.VideoCapture(0)`

### Model Not Loading
- Ensure model files are in `backend/models/`
- Check file names match exactly
- Verify file integrity

### Authentication Issues
- Clear browser localStorage
- Check JWT token expiration
- Verify CORS settings

## 🚀 Future Enhancements

- [ ] SMS/Email alert notifications
- [ ] Multiple camera support
- [ ] Advanced analytics with charts
- [ ] Mobile app (React Native)
- [ ] IoT integration
- [ ] Edge deployment (Raspberry Pi, Jetson Nano)
- [ ] Face mask detection
- [ ] Social distancing monitoring
- [ ] Heat map visualization
- [ ] Export reports (PDF, CSV)

## 📝 License

This project is licensed under the MIT License.

## 👥 Use Cases

- Shopping malls and retail stores
- Railway stations and airports
- University campuses
- Event halls and conference centers
- Smart city infrastructure
- Public transportation hubs
- Museums and galleries
- Hospitals and clinics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using AI-powered computer vision and modern web technologies**
# crowd-management
