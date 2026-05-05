import os

_DEV_SECRET_KEY = 'dev-secret-key-change-in-production'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', _DEV_SECRET_KEY)
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

    @classmethod
    def init_app(cls, app):
        sk = os.environ.get('SECRET_KEY') or app.config.get('SECRET_KEY', '')
        if not sk or sk == _DEV_SECRET_KEY:
            raise RuntimeError(
                'SECRET_KEY must be set to a strong random value in production. '
                'Set the SECRET_KEY environment variable.'
            )

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
