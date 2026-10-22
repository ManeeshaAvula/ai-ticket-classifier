"""SQLAlchemy models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base


class Ticket(Base):
    """A support ticket and the label the classifier predicted for it."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    label = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
