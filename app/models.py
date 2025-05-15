import datetime
from sqlalchemy import func, or_, and_, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db
