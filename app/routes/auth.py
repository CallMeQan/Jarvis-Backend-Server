from flask import Blueprint


##################
from dotenv import load_dotenv
from os import getenv
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from app import db, bcrypt  # Import db và bcrypt từ app/__init__.py
from models import User  # Import model User từ models.py
from config import Config # import secret_key, thay cho load_env,...
import re

###################


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

@auth_bp.route("/forgot-password", methods = ["GET", "POST"])
def forgot_password():
    """
    Forgot password function.
    This function is used to send a reset password link to the user's email.
    The link contains a token that is used to verify the user's identity.
    The token is generated using HMAC with SHA256 based on the current timestamp and a secret key.
    """
    
    #TODO




#######################
def generate_reset_token(user): # bên quý, token cho gửi mail
    now = datetime.now(timezone.utc)
    payload = {
        'sub': user.id,
        'iat': now,
        'exp': now + timedelta(minutes=15),
        'type': 'reset' # phân biệt, quản li type - thêm vô nếu sau này làm refesh token 
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_reset_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded['sub']  # Trả về user ID nếu token hợp lệ
    except ExpiredSignatureError:
        return None  # Token hết hạn
    except InvalidTokenError:
        return None  # Token không hợp lệ

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'\d', password)
    )

@auth_bp.route('/recover-password', methods=['POST'])
def recover_password():
    """
    Recover password function.
    This function is used to recover the user's password.
    The function takes a token as an argument, which is used to verify the user's identity.
    """
    data = request.json
    token = data.get('token')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not token or not password or not confirm_password:
        return jsonify({'message': 'Missing required fields'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    if not is_strong_password(password):
        return jsonify({'message': 'Password must be at least 8 characters, include an uppercase letter and a number'}), 400

    try:
        # Giải mã token và kiểm tra tính hợp lệ
        payload = jwt.decode(token, getenv('SECRET_KEY'), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 400

    # Lấy user từ database theo ID trong payload
    user = User.query.get(payload['sub'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Kiểm tra token đã dùng chưa
    if user.password_changed_at and payload['iat'] < user.password_changed_at.timestamp():
        return jsonify({'message': 'Token already used'}), 400

    # Hash mật khẩu mới sử dụng bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Cập nhật mật khẩu mới và thời gian thay đổi mật khẩu
    user.password = hashed_password
    user.password_changed_at = datetime.utcnow()
    db.session.commit()

    # Tạo access token sau khi reset mật khẩu (tự động đăng nhập)
    access_payload = {
    'sub': user.id,
    'iat': datetime.now(timezone.utc),
    'exp': datetime.now(timezone.utc) + timedelta(days=1)
}
    access_token = jwt.encode(access_payload, getenv('SECRET_KEY'), algorithm='HS256')

    return jsonify({'message': 'Password reset successful', 'access_token': access_token}), 200

#####


@auth_bp.route("/logout")
def logout():
    """
    TODO
    """