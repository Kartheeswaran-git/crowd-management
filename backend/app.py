from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import config
from models import db, User, Settings, AlertLog, CountLog
from camera import get_count, get_detections, generate_video_stream, start_camera, stop_camera
from auth import login, register, verify, token_required, admin_required

app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": config.CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route("/api/auth/login", methods=["POST"])
def login_route():
    """User login endpoint"""
    return login()


@app.route("/api/auth/register", methods=["POST"])
@admin_required
def register_route():
    """User registration endpoint (admin only)"""
    return register()


@app.route("/api/auth/verify", methods=["GET"])
def verify_route():
    """Token verification endpoint"""
    return verify()


# ============================================================================
# People Count & Detection Endpoints
# ============================================================================

@app.route("/api/count", methods=["GET"])
@token_required
def count_route():
    """Get current people count and alert status"""
    try:
        people_count = get_count()
        detections = get_detections()
        
        # Get current threshold from settings
        threshold_setting = Settings.query.filter_by(key='crowd_threshold').first()
        threshold = int(threshold_setting.value) if threshold_setting else config.THRESHOLD
        
        # Check if alert should be triggered
        alert = people_count > threshold
        
        # Log the count
        count_log = CountLog(people_count=people_count)
        db.session.add(count_log)
        
        # Log alert if triggered
        if alert:
            alert_log = AlertLog(people_count=people_count, threshold=threshold)
            db.session.add(alert_log)
        
        db.session.commit()
        
        return jsonify({
            'count': people_count,
            'threshold': threshold,
            'alert': alert,
            'detections': detections,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error getting count: {str(e)}'}), 500


@app.route("/api/video-feed", methods=["GET"])
def video_feed():
    """Stream video feed with detection overlay - No auth required for img src"""
    try:
        return Response(
            generate_video_stream(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return jsonify({'message': f'Video feed error: {str(e)}'}), 500


# ============================================================================
# Alert History Endpoints
# ============================================================================

@app.route("/api/alerts", methods=["GET"])
@token_required
def get_alerts():
    """Get alert history with optional filtering"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Query alerts
        alerts = AlertLog.query.filter(
            AlertLog.timestamp >= time_threshold
        ).order_by(AlertLog.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching alerts: {str(e)}'}), 500


@app.route("/api/alerts/clear", methods=["DELETE"])
@admin_required
def clear_alerts():
    """Clear all alert history (admin only)"""
    try:
        AlertLog.query.delete()
        db.session.commit()
        return jsonify({'message': 'Alert history cleared successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error clearing alerts: {str(e)}'}), 500


# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.route("/api/stats", methods=["GET"])
@token_required
def get_stats():
    """Get analytics and statistics"""
    try:
        hours = request.args.get('hours', 24, type=int)
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get count logs
        count_logs = CountLog.query.filter(
            CountLog.timestamp >= time_threshold
        ).order_by(CountLog.timestamp.asc()).all()
        
        # Get alert logs
        alert_logs = AlertLog.query.filter(
            AlertLog.timestamp >= time_threshold
        ).all()
        
        # Calculate statistics
        counts = [log.people_count for log in count_logs]
        avg_count = sum(counts) / len(counts) if counts else 0
        max_count = max(counts) if counts else 0
        min_count = min(counts) if counts else 0
        
        return jsonify({
            'period_hours': hours,
            'total_readings': len(count_logs),
            'total_alerts': len(alert_logs),
            'average_count': round(avg_count, 2),
            'max_count': max_count,
            'min_count': min_count,
            'count_history': [log.to_dict() for log in count_logs[-100:]],  # Last 100 readings
            'recent_alerts': [alert.to_dict() for alert in alert_logs[-20:]]  # Last 20 alerts
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching statistics: {str(e)}'}), 500


# ============================================================================
# Settings Endpoints
# ============================================================================

@app.route("/api/settings", methods=["GET"])
@token_required
def get_settings():
    """Get all settings"""
    try:
        settings = Settings.query.all()
        settings_dict = {s.key: s.value for s in settings}
        
        # Add defaults if not in database
        if 'crowd_threshold' not in settings_dict:
            settings_dict['crowd_threshold'] = str(config.THRESHOLD)
        if 'detection_confidence' not in settings_dict:
            settings_dict['detection_confidence'] = str(config.DETECTION_CONFIDENCE)
        
        return jsonify({'settings': settings_dict}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching settings: {str(e)}'}), 500


@app.route("/api/settings", methods=["PUT"])
@admin_required
def update_settings():
    """Update settings (admin only)"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        updated_settings = []
        
        for key, value in data.items():
            setting = Settings.query.filter_by(key=key).first()
            
            if setting:
                setting.value = str(value)
                setting.updated_at = datetime.utcnow()
            else:
                setting = Settings(key=key, value=str(value))
                db.session.add(setting)
            
            updated_settings.append(key)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully',
            'updated': updated_settings
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating settings: {str(e)}'}), 500


# ============================================================================
# User Management Endpoints
# ============================================================================

@app.route("/api/users", methods=["GET"])
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching users: {str(e)}'}), 500


@app.route("/api/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """Get specific user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching user: {str(e)}'}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.json
        
        if 'username' in data:
            # Check if username is already taken
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'message': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'password' in data:
            user.set_password(data['password'])
        
        if 'role' in data:
            if data['role'] not in ['admin', 'user']:
                return jsonify({'message': 'Invalid role'}), 400
            user.role = data['role']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating user: {str(e)}'}), 500


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prevent deleting yourself
        if user.id == request.user_id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting user: {str(e)}'}), 500


# ============================================================================
# Health Check
# ============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500


# ============================================================================
# Application Initialization
# ============================================================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        start_camera()
        print("Database initialized successfully")
        print("Camera background thread started")
        print(f"Server starting on http://localhost:5001")
        print(f"CORS enabled for: {config.CORS_ORIGINS}")
    
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
