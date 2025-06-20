from os import getenv
from dotenv import load_dotenv
load_dotenv()

class Config:
    SESSION_TYPE = "filesystem"  # Read doc for more info
    SECRET_KEY = getenv("SECRET_KEY", "default")
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = int(getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
    JWT_REFRESH_TOKEN_EXPIRES = int(getenv("JWT_REFRESH_TOKEN_EXPIRES", 86400))

    # Mail config
    MAIL_SERVER = getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(getenv("MAIL_PORT", 8025))
    MAIL_USE_TLS = getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = getenv("MAIL_DEFAULT_SENDER", "test@example.com")
    MAIL_SUPPRESS_SEND = getenv("MAIL_SUPPRESS_SEND", "true").lower() == "true"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = "test@example.com"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "jwt-test-secret-key"