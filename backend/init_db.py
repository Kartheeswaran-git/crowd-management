"""
Database Initialization Script
Creates database tables and seeds initial data
"""

from app import app, db
from models import User, Settings
import config

def init_database():
    """Initialize database with tables and seed data"""
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("\nCreating default admin user...")
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Admin user created (username: admin, password: admin123)")
        else:
            print("\n✓ Admin user already exists")
        
        # Check if test user exists
        test_user = User.query.filter_by(username='user').first()
        
        if not test_user:
            print("Creating default test user...")
            test_user = User(username='user', role='user')
            test_user.set_password('user123')
            db.session.add(test_user)
            print("✓ Test user created (username: user, password: user123)")
        else:
            print("✓ Test user already exists")
        
        # Create default settings
        threshold_setting = Settings.query.filter_by(key='crowd_threshold').first()
        if not threshold_setting:
            print("\nCreating default settings...")
            threshold_setting = Settings(key='crowd_threshold', value=str(config.THRESHOLD))
            db.session.add(threshold_setting)
            
            confidence_setting = Settings(key='detection_confidence', value=str(config.DETECTION_CONFIDENCE))
            db.session.add(confidence_setting)
            
            print(f"✓ Default threshold: {config.THRESHOLD}")
            print(f"✓ Default confidence: {config.DETECTION_CONFIDENCE}")
        else:
            print("\n✓ Settings already exist")
        
        # Commit all changes
        db.session.commit()
        print("\n" + "="*50)
        print("Database initialization completed successfully!")
        print("="*50)
        print("\nDefault Credentials:")
        print("  Admin - username: admin, password: admin123")
        print("  User  - username: user, password: user123")
        print("\n⚠️  Please change these passwords in production!")
        print("="*50)


if __name__ == "__main__":
    init_database()
