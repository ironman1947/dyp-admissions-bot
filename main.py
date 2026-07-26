"""
FastAPI application entrypoint for the DYP Admissions WhatsApp Bot.

This file:
  - Creates the FastAPI app instance
  - Includes the webhook router (GET + POST /webhook)
  - Initializes the database tables on startup
  - Provides a GET / health check endpoint

Run locally:
    uvicorn main:app --reload --port 8000

On Render, set the Start Command to:
    uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import logging

from fastapi import FastAPI

from app.storage.db import init_db
from app.webhook import router as webhook_router

# ─────────────────────────────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DYP Admissions WhatsApp Bot",
    description="WhatsApp chatbot for D.Y. Patil College of Engineering & Technology, Kolhapur — admissions, placements, facilities & more.",
    version="1.0.0",
)

# Include the webhook router
app.include_router(webhook_router)


# ─────────────────────────────────────────────────────────────────────
# Startup Event — Initialize Database
# ─────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    """Create database tables on application startup."""
    logger.info("Starting DYP Admissions Bot...")
    init_db()
    logger.info("Bot ready. Webhook listening at /webhook")


# ─────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint for Render and monitoring."""
    return {"status": "ok", "service": "dyp-admissions-bot"}
