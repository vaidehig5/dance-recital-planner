from flask import Flask

from backend.routes.api import api_bp
from backend.routes.pages import pages_bp


def create_app() -> Flask:
    """Build and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    return app