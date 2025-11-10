"""
Configuration for SQLite (Development and Production)
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = 'SmartGardenHub'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_THRESHOLD = 500
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    
    # SQLite database configuration
    base_dir = Path(__file__).parent
    instance_dir = base_dir / 'instance'
    instance_dir.mkdir(exist_ok=True)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Backup configuration
    BACKUP_DIR = str(base_dir / 'backups')
    DATABASE_PATH = None  # Will be set in subclasses

class DevelopmentConfig(Config):
    """Development configuration with SQLite"""
    DEBUG = True
    
    # SQLite database for development
    db_path = Config.instance_dir / 'database.db'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    DATABASE_PATH = str(db_path)
    
    # Enable query logging in development
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration with SQLite"""
    DEBUG = False
    
    # SQLite database for production
    # VPS: /var/www/saroyarsir/smartgardenhub.db
    # Use environment variable if provided, otherwise use VPS default
    db_path = os.environ.get('DATABASE_PATH', '/var/www/saroyarsir/smartgardenhub.db')
    db_path = Path(db_path)
    
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    DATABASE_PATH = str(db_path)
    
    # Production backup settings
    BACKUP_DIR = os.environ.get('BACKUP_DIR', '/var/www/saroyarsir/backups')
    
    # VPS Port
    PORT = int(os.environ.get('PORT', 8001))
    
    # Enable WAL mode for better concurrency in production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 30,  # Increase timeout for busy database
            'check_same_thread': False  # Allow multi-threading
        },
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300  # Recycle connections every 5 minutes
    }

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

