from flask import Blueprint, request, session, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import hmac, hashlib, datetime
from os import getenv
import datetime

from ..models import User, ForgotPassword
from ..modules.agent_tool.gmail_tool import send_email
from ..extensions import db, jwt

auth_bp = Blueprint('auth', __name__)


def generate_email_hash(email: str) -> str:
    """
    Generate a hash for email using HMAC with SHA256.
    This is reversible so it's good as an alternative to B-Crypt to store email.
    """
    secret = getenv("SECRET_KEY")
    if not secret:
        raise ValueError("SECRET_KEY environment variable not set")
    hashed_email = hmac.new(secret.encode(), str(email).encode(), hashlib.sha256)
    return hashed_email.hexdigest()

# Register account
@auth_bp.route("/register", methods=["POST"])
def register(): 
    """
    Register function. All fields are required. 
    check if username or email is duplicated.
    If not, create a new user and return a success message.
    """
    data = request.json
    username = data.get("username")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    retype_password = data.get("retype_password")

    if not all([username, name, email, password, retype_password]):
        return jsonify({"msg": "Missing fields"}), 400
    if password != retype_password:
        return jsonify({"msg": "Passwords do not match"}), 400
    if User.is_duplicated(username, email):
        return jsonify({"msg": "Username or email already exists"}), 400

    hashed_password = generate_password_hash(password)
    verify_token = generate_email_hash(email + str(datetime.datetime.now()))
    
    new_user = User(username=username, 
                    name=name, 
                    email=email, 
                    password=hashed_password,
                    email_verify_token=verify_token,
                    is_verified=False)
    
    db.session.add(new_user)
    db.session.commit()
    
    verify_link = f"http://localhost:5000/auth/register/verify-email?token={verify_token}"
    body=f"Please click the link to verify your email: {verify_link}"
    send_email(subject = "Verify your email", content = body,
               receiver_email = email, is_server = True)
    
    access_token = create_access_token(identity=new_user.user_id)

    return jsonify({
        "msg": "User registered successfully. Please verify your email.",
        "access_token": access_token
    }), 201

@auth_bp.route("/register/verify-email", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"msg": "Missing token"}), 400

    user = User.query.filter_by(email_verify_token=token).first()
    if not user:
        return jsonify({"msg": "Invalid or expired token"}), 400

    user.is_verified = True
    user.email_verify_token = None
    db.session.commit()

    return jsonify({"msg": "Email verified successfully!"})

# Log in
@auth_bp.route("/login", methods = ["POST"])
def login():
    """
    Log in function.
    Create a JWT token for the user.
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

# lấy dữ liệu người dùng 
@auth_bp.route("/profile", methods = ["GET"])
@jwt_required()
def profile():
    """
    Get user profile.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "name": user.name,
        "create_at": user.created_at
    })

# tái tạo token
@auth_bp.route("/refresh", methods = ["POST"])
@jwt_required(refresh = True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"msg": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "No user with this email"}), 404

    timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    hash_token = generate_email_hash(email + str(timestamp))

    # Lưu token
    forgot = ForgotPassword(email=email, hashed_timestamp=hash_token, created_at=timestamp)
    db.session.add(forgot)
    db.session.commit()

    # In thực ra là sẽ gửi email. Ở đây chỉ mock.
    reset_url = f"http://yourdomain.com/recover-password?a={hash_token}"
    print(f"[MOCK] Password reset link: {reset_url}")

    return jsonify({"msg": "Reset link sent to your email (mock)"}), 200

@auth_bp.route("/recover-password?a=<token>", methods = ["POST"])
def recover_password(token):
    """
    Recover password function.
    This function is used to recover the user's password.
    The function takes a token as an argument, which is used to verify the user's identity.
    """
    data = request.json
    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all(token, new_password, confirm_password):
        return jsonify({"msg": "Missing fields"}), 400
    if new_password != confirm_password:
        return jsonify({"msg": "Passwords do not match"}), 400
    
    email = ForgotPassword.take_email_from_hash(token)
    if not email:
        return jsonify({"msg": "Invalid or expired token"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    user.password = generate_password_hash(new_password)    
    db.session.commit()

    return jsonify({"msg": "Password updated successfully"}), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # Vì JWT không có session, logout chỉ là xóa token ở client
    return jsonify({"msg": "Logout successful — just remove token on client"}), 200