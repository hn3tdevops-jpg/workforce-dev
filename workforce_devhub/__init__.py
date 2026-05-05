import os

from flask import Flask, render_template

from .cli.commands import register_commands
from .config import Config
from .extensions import csrf, db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QUARANTINE_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .blueprints.admin import admin_bp
    from .blueprints.api import api_bp
    from .blueprints.auth import auth_bp
    from .blueprints.docs import docs_bp
    from .blueprints.files import files_bp
    from .blueprints.main import main_bp
    from .blueprints.packages import packages_bp
    from .blueprints.progress import progress_bp
    from .blueprints.projects import projects_bp
    from .blueprints.scripts import scripts_bp
    from .blueprints.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(scripts_bp)
    app.register_blueprint(packages_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    register_commands(app)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
