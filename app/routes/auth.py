from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
import hmac, hashlib, datetime
from os import getenv

from ..models import User, ForgotPassword, WrongPassword
from ..extensions import db

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
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not all([username, email, password, name]):
        return jsonify({"msg": "Missing fields"}), 400

    if User.is_duplicated(username, email):
        return jsonify({"msg": "Username or email already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password, name=name)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 201

# Log in
@auth_bp.route("/login", methods = ["POST"])
def login():
    """
    Log in function.
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
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "name": user.name,
        "create_at": user.created_at
    })

@auth_bp.route("/register/verify-email", methods = ["GET"])

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
    from ..extensions import db
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