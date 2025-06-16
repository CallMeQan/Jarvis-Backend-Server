# app.py
import os
from flask import Flask

from .routes import auth_bp, chatbot_bp
from .modules.chatbot_utils.install_utils import install_models

from .config import Config
from .extensions import db, mail, jwt

def create_app_with_blueprint(config_name=None, config_override=None):
    if not os.getenv("MODEL_INSTALLED"):
        install_models()
        os.environ["MODEL_INSTALLED"] = "true"
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

create_app = create_app_with_blueprint

# For local development only
if __name__ == "__main__":
    app = create_app_with_blueprint()
    app.run(debug=True, port=8000, host="0.0.0.0")