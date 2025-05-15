from flask import Blueprint, request, jsonify
import os
import datetime
import jwt
from dotenv import load_dotenv

from ..models import User, ForgotPasswordRequest, db
from ..modules.forgot_module.forgot_password import send_email

auth_bp = Blueprint('auth', __name__)

# Register account
@auth_bp.route("/register", methods = ["GET", "POST"])
def register():
    """
    Register a new user account.
    """
    # TODO: 

# Log in
@auth_bp.route("/login", methods = ["GET", "POST"])
def login():
    """
    Log in function.
    """
    # TODO

#-------------------------------------------------------------------------------------#
# Configuration for JSON Web Tokens (JWT)
# SECRET_KEY: Loaded from environment variable to sign and verify tokens.
# ALGORITHM: Algorithm used for signing the tokens (e.g., HS256).
# EXPIRATION_DELTA: Token validity duration set to 30 minutes.
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
EXPIRATION_DELTA = datetime.timedelta(minutes=30)

def generate_jwt(payload):
    """
    Generate a JWT token with the provided payload.
    The token is signed using SECRET_KEY and ALGORITHM.
    """
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@auth_bp.route("/forgot-password", methods = ["POST"])
def forgot_password():
    """
    Mobile API: request reset password.
    Input JSON: { "email": "user@example.com" }

    Response JSON:
      - 200: success message + expires_in
      - 400: error if missing email
    """
    
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({
            'status': 'error',
            'code': 'EMAIL_REQUIRED',
            'message': 'Email is required.'
        }), 400

    user = User.query.filter_by(email=email).first()
    if user:
        # Create JWT reset token (expires in 30 minutes)
        payload = {
            'email': user.email,
            'exp': datetime.datetime.utcnow() + EXPIRATION_DELTA
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Store token request for auditing
        req = ForgotPasswordRequest(
            user_id=user.id,
            token=token,
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(req)
        db.session.commit()

        # Send reset link via email
        reset_link = f"https://yourapp.com/reset-password?token={token}"
        send_email(
            restore_link=reset_link,
    recipient_email=user.email
        )

    return jsonify({
        'status': 'success',
        'message': 'If that email is registered, a reset link has been sent.',
        'expires_in': EXPIRATION_DELTA.seconds
    }), 200
#-------------------------------------------------------------------------------------#

@auth_bp.route("/recover-password?a=<token>", methods = ["GET", "POST"])
def recover_password(token):
    """
    Recover password function.
    This function is used to recover the user's password.
    The function takes a token as an argument, which is used to verify the user's identity.
    """
    
    # TODO

@auth_bp.route("/logout")
def logout():
    """
    TODO
    """