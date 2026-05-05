import os
from flask import Flask
from devhub.config import config
from devhub.extensions import db, migrate, login_manager, bcrypt
from devhub.models import User

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name not in config:
            config_name = 'default'

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from devhub.auth import auth
    from devhub.routes.dashboard import dashboard
    from devhub.routes.docs import docs_bp
    from devhub.routes.reports import reports_bp
    from devhub.routes.scripts import scripts_bp
    from devhub.routes.packages import packages_bp
    from devhub.routes.admin import admin_bp
    from devhub.routes.api import api_bp

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(docs_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(scripts_bp)
    app.register_blueprint(packages_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    from devhub.cli import register_commands
    register_commands(app)

    return app
