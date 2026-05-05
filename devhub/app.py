import os

from flask import Flask

from devhub.config import _PLACEHOLDER_KEY, Config
from devhub.extensions import csrf, db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Refuse to start in production with the placeholder secret key.
    if not app.config.get("TESTING") and os.environ.get("DEVHUB_ENV", "").lower() == "production":
        secret = app.config.get("SECRET_KEY", "")
        if not secret or secret == _PLACEHOLDER_KEY:
            raise RuntimeError(
                "DEVHUB_SECRET_KEY must be set to a strong, unique value when "
                "DEVHUB_ENV=production. The placeholder key is not acceptable."
            )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from devhub.auth import bp as auth_bp
    from devhub.routes.admin import bp as admin_bp
    from devhub.routes.api import bp as api_bp
    from devhub.routes.docs import bp as docs_bp
    from devhub.routes.main import bp as main_bp
    from devhub.routes.packages import bp as packages_bp
    from devhub.routes.progress import bp as progress_bp
    from devhub.routes.projects import bp as projects_bp
    from devhub.routes.scripts import bp as scripts_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(docs_bp, url_prefix="/docs")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(progress_bp, url_prefix="/progress")
    app.register_blueprint(scripts_bp, url_prefix="/scripts")
    app.register_blueprint(packages_bp, url_prefix="/packages")
    app.register_blueprint(auth_bp)

    from devhub.cli import register_commands
    register_commands(app)

    from devhub.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
