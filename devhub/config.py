import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///devhub.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/quarantine'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    DEVHUB_ENABLE_SCRIPT_EXECUTION = os.environ.get('DEVHUB_ENABLE_SCRIPT_EXECUTION', 'false').lower() == 'true'
    DEVHUB_ENABLE_PACKAGE_INSTALL = os.environ.get('DEVHUB_ENABLE_PACKAGE_INSTALL', 'false').lower() == 'true'
    DEVHUB_SCAN_PATH = os.environ.get('DEVHUB_SCAN_PATH', '.')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
