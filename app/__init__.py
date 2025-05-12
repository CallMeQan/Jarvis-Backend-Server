# app.py
from os import getenv
from flask import Flask

from .routes.auth import auth_bp

from .config import Config
from .extensions import db, bcrypt # thêm bcrypt


######
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
####

def create_app_with_blueprint():
    # ======================
    # |    Configuration   |
    # ======================
    app = Flask(__name__, static_folder="static")
    app.config.from_object(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app) # thêm bcrypt

    # ======================
    # |     Routing        |
    # ======================

    app.register_blueprint(auth_bp, url_prefix="/auth")

    # ======================
    # |    Final stuff     |
    # ======================
    with app.app_context():
        db.create_all()

    return app

# For local development only
if __name__ == "__main__":
    app = create_app_with_blueprint()
    app.run(debug=True, port=8000, host="0.0.0.0")