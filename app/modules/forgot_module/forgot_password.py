import os
from os import getenv
import smtplib
import ssl
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Email sender configuration
SMTP_SERVER = getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(getenv("SMTP_PORT", 587))
SERVER_EMAIL = getenv("EMAIL_USER")  # Sender's email from .env
SERVER_PASSWORD = getenv("PASSWORD_OF_EMAIL")  # App password or SMTP password


def send_email(restore_link: str, recipient_email: str) -> None:
    """
    Send a password reset email containing the provided restore link.

    :param restore_link: URL link for the user to reset their password.
    :param recipient_email: The user's email address to receive the reset link.
    """
    # Construct email headers and body
    subject = "Password Reset Request"
    body = f"Please click the following link to reset your password: {restore_link}"
    message = f"Subject: {subject}\nFrom: {SERVER_EMAIL}\nTo: {recipient_email}\n\n{body}"

    # Create secure SSL context
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SERVER_EMAIL, SERVER_PASSWORD)
            server.sendmail(SERVER_EMAIL, recipient_email, message)
            print(f"Password reset email sent to {recipient_email}")
    except Exception as e:
        # In production, consider logging instead of printing
        print(f"Failed to send password reset email: {e}")


if __name__ == "__main__":
    # Example usage
    test_link = "https://yourapp.com/reset?token=exampletoken"
    test_recipient = getenv("TEST_RECIPIENT_EMAIL", "user@example.com")
    send_email(test_link, test_recipient)
