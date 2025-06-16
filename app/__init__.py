# app.py
from os import getenv
from flask import Flask

from .routes import auth_bp, chatbot_bp

from .config import Config
from .extensions import db, mail, jwt

def create_app(config_name=None, config_override=None):
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)
    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
    with app.app_context():
        db.create_all()
    return app

# For local development only
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000, host="0.0.0.0")