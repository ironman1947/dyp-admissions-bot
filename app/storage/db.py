"""
Database engine setup and session state management.

Provides the SQLAlchemy engine/session factory connected to the
PostgreSQL database on Render, plus two helper functions used by
flow_logic.py to read and update each student's conversation state.

The `init_db()` function must be called at application startup
(in main.py) to create the tables if they don't exist.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.student_session import Base, StudentSession

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# Engine & Session Factory
# ─────────────────────────────────────────────────────────────────────

# Convert standard postgresql:// URL to use the psycopg (v3) driver.
# Render provides URLs starting with "postgresql://" but SQLAlchemy
# defaults to the psycopg2 dialect. We need "postgresql+psycopg://".
_db_url = settings.DATABASE_URL
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    _db_url,
    pool_pre_ping=True,        # auto-reconnect on stale connections
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create all tables defined in models (idempotent — safe to call on every startup)."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")


# ─────────────────────────────────────────────────────────────────────
# Session State Helpers
# ─────────────────────────────────────────────────────────────────────

def get_or_create_session(phone: str) -> StudentSession:
    """Return the existing session for `phone`, or create a new one.

    This is called on every incoming message so the bot always has
    a session object to read and update the user's current menu.

    Args:
        phone: WhatsApp phone number in E.164 format (without '+').

    Returns:
        The StudentSession for this phone number.
    """
    db: Session = SessionLocal()
    try:
        session = db.query(StudentSession).filter(StudentSession.phone == phone).first()
        if session is None:
            session = StudentSession(
                phone=phone,
                current_menu="main",
                last_active=datetime.now(timezone.utc),
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            logger.info("New session created for phone=%s", phone)
        else:
            # Update last_active on every interaction
            session.last_active = datetime.now(timezone.utc)
            db.commit()
            db.refresh(session)
        return session
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_session_state(phone: str, new_state: str) -> None:
    """Update the current_menu for the given phone number.

    Called after every leaf response so the bot knows where the
    user is in the conversation tree.

    Args:
        phone: WhatsApp phone number in E.164 format.
        new_state: The menu state to set (e.g. 'main', 'facilities', 'about').
    """
    db: Session = SessionLocal()
    try:
        session = db.query(StudentSession).filter(StudentSession.phone == phone).first()
        if session:
            session.current_menu = new_state
            session.last_active = datetime.now(timezone.utc)
            db.commit()
            logger.info("Session updated: phone=%s → state=%s", phone, new_state)
        else:
            # Edge case: session doesn't exist yet, create it with the new state
            new_session = StudentSession(
                phone=phone,
                current_menu=new_state,
                last_active=datetime.now(timezone.utc),
            )
            db.add(new_session)
            db.commit()
            logger.info("Session created with state: phone=%s → state=%s", phone, new_state)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
