import datetime
from sqlalchemy import func, or_, and_, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    is_verified: Mapped[bool] = mapped_column(default=False)
    email_verify_token: Mapped[str] = mapped_column(nullable=True)

    def get_id(self):
        return self.user_id

    @classmethod
    def is_duplicated(self, username, email) -> bool:
        return db.session.query(User).filter(or_(User.username == username, User.email == email)).first() is not None

class ForgotPassword(db.Model):
    __tablename__ = "forgot_password"
    fp_id: Mapped[int] = mapped_column("fp_id", primary_key = True)
    email: Mapped[str] = mapped_column(nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(nullable = False)
    hashed_timestamp: Mapped[str] = mapped_column(nullable = False)

    @classmethod
    @staticmethod
    def take_email_from_hash(self, hashed_timestamp):
        """
        Take email from a hashed timestamp, while checking if the created_at timestamp is less than 1 hour away.

        :hashed_timestamp: A hashed timestamp, used to get unique string.
        """

        current_timestamp = datetime.datetime.now(tz = datetime.timezone(datetime.timedelta(seconds=25200)))

        # Check if username or email is duplicated with only one query
        result = db.session.query(self.email, self.created_at).filter(
            self.hashed_timestamp == hashed_timestamp,
            current_timestamp - self.created_at <= datetime.timedelta(hours = 1)
        ).first()
        return result[0] if result else None
    
class WrongPassword(db.Model):
    __tablename__ = "user_login_check"
    login_id: Mapped[int] = mapped_column("login_id", primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    first_time: Mapped[datetime.datetime] = mapped_column(nullable=False)
    login_attempts: Mapped[int] = mapped_column(nullable=False)

    @classmethod
    def record_attempt(cls, username: str, is_successful: bool) -> bool:
        """
        Record a login attempt for username.
        If the login is successful, reset the counter.
        Returns True if login is allowed (<=5 failed attempts in window), False if denied.
        """
        tz = datetime.timezone(datetime.timedelta(seconds=25200))
        now = datetime.datetime.now(tz=tz)
        window = datetime.timedelta(minutes=30)

        # Look up existing record
        record = cls.query.filter_by(username=username).first()

        if record is None:
            # First-ever login for this user
            record = cls(
                username=username,
                first_time=now,
                login_attempts=0 if is_successful else 1
            )
            db.session.add(record)
            db.session.commit()
            return True

        if is_successful:
            # Reset on successful login
            record.first_time = now
            record.login_attempts = 0
            db.session.commit()
            return True

        # If window has expired, reset
        if now - record.first_time > window:
            record.first_time = now
            record.login_attempts = 1
            db.session.commit()
            return True

        # Within window: allow up to 5 failed attempts
        if record.login_attempts < 5:
            record.login_attempts += 1
            db.session.commit()
            return True

        # 5 or more failed attempts already used up
        return False
