from flask import Blueprint

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