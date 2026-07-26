"""
SQLAlchemy model for tracking each student's conversation state.

Each WhatsApp user is identified by their phone number (primary key).
The `current_menu` field tracks where they are in the menu tree so
the bot can provide context-aware responses. `last_active` is updated
on every interaction to support future analytics and session timeouts.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in this project."""
    pass


class StudentSession(Base):
    """Tracks the current conversation state for a WhatsApp user.

    Attributes:
        phone: The user's WhatsApp phone number (E.164 format, e.g. '919876543210').
                Used as the primary key — one session per phone number.
        current_menu: The menu/state the user is currently viewing.
                      Defaults to 'main'. Possible values:
                      'main', 'facilities', 'about', 'fee', 'placements',
                      'admission', 'bus', 'hostels', 'canteen', 'ncc', 'nss'.
        last_active: Timestamp of the user's most recent interaction.
                     Auto-updated on every incoming message.
    """

    __tablename__ = "student_sessions"

    phone: str = Column(String, primary_key=True, index=True)
    current_menu: str = Column(String, default="main", nullable=False)
    last_active: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<StudentSession(phone={self.phone!r}, menu={self.current_menu!r})>"
