import os

instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + os.path.join(instance_path, 'devhub.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(instance_path, 'uploads')
    QUARANTINE_FOLDER = os.path.join(instance_path, 'quarantine')
    ENABLE_SCRIPT_EXECUTION = (
        os.environ.get('DEVHUB_ENABLE_SCRIPT_EXECUTION', 'false').lower() == 'true'
    )
    ENABLE_PACKAGE_INSTALL = (
        os.environ.get('DEVHUB_ENABLE_PACKAGE_INSTALL', 'false').lower() == 'true'
    )
    WORKSPACE_ROOTS = [
        p for p in os.environ.get('DEVHUB_WORKSPACE_ROOTS', '').split(':') if p
    ]
    WTF_CSRF_ENABLED = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    UPLOAD_FOLDER = os.path.join(instance_path, 'test_uploads')
    QUARANTINE_FOLDER = os.path.join(instance_path, 'test_quarantine')
