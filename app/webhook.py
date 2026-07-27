"""
WaSender Webhook handlers for the DYP Admissions WhatsApp Bot.

Two endpoints:
  GET  /webhook — Simple liveness check (WaSender doesn't do verification handshakes).
  POST /webhook — Receives all incoming messages from WaSender's webhook delivery,
                  parses the payload, and dispatches to flow_logic.route_message()
                  via a background task so we return 200 OK immediately.

WaSender webhook payload structure (may vary slightly by plan/version):
{
  "data": {
    "from": "919876543210@c.us",   # or @s.whatsapp.net
    "messageBody": "hello",         # or "body" / "message"
    "type": "chat"
  }
}
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request

from app.flow_logic import route_message

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────
# Payload Parser
# ─────────────────────────────────────────────────────────────────────

def _extract_wasender_message(data: dict[str, Any]) -> tuple[str, str] | None:
    """Extract (clean_phone, message_text) from a WaSender webhook payload.

    WaSender wraps the actual message inside a "data" key in some plans.
    We try multiple known field names defensively so minor API changes
    don't break the bot.

    Returns:
        A tuple (phone, text) if a valid user message was found, else None.
    """
    try:
        # Some WaSender payloads nest data under a "data" key
        body = data.get("data", data)

        # Sender field variants
        sender: str = (
            body.get("from")
            or body.get("sender")
            or ""
        )

        # Message body field variants
        message_text: str = (
            body.get("messageBody")
            or body.get("body")
            or body.get("message")
            or ""
        )

        if not sender or not message_text:
            return None

        # Strip WhatsApp JID suffixes to get a clean E.164-style phone number
        clean_sender = (
            sender
            .replace("@c.us", "")
            .replace("@s.whatsapp.net", "")
            .replace("@g.us", "")   # ignore group messages
        )

        # Skip group messages (they contain a hyphen in the group JID prefix)
        if "@g.us" in sender:
            logger.debug("Ignoring group message from %s", sender)
            return None

        return (clean_sender, message_text)

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to parse WaSender payload: %s", exc)
        return None


# ─────────────────────────────────────────────────────────────────────
# GET /webhook — Liveness Check
# ─────────────────────────────────────────────────────────────────────

@router.get("/webhook")
async def verify_webhook() -> dict[str, str]:
    """Simple liveness endpoint — WaSender does not do a verification handshake."""
    return {"status": "Webhook is live", "service": "dyp-admissions-bot"}


# ─────────────────────────────────────────────────────────────────────
# POST /webhook — Incoming Message Handler
# ─────────────────────────────────────────────────────────────────────

@router.post("/webhook")
async def wasender_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Handle incoming WaSender webhook events.

    Steps:
      1. Parse the raw JSON payload.
      2. Extract sender phone + message text.
      3. Dispatch route_message() as a background task (non-blocking).
      4. Return {"status": "success"} immediately so WaSender knows we
         received the event.
    """
    try:
        data: dict[str, Any] = await request.json()
        logger.info("Incoming WaSender webhook: %s", data)
    except Exception as exc:  # noqa: BLE001
        logger.error("Could not parse webhook JSON: %s", exc)
        return {"status": "error", "detail": "invalid json"}

    extracted = _extract_wasender_message(data)

    if extracted is None:
        logger.debug("No actionable message in webhook payload — skipping.")
        return {"status": "ok", "detail": "no message"}

    clean_sender, message_text = extracted
    logger.info("Message from %s: %s", clean_sender, message_text)

    # Dispatch to flow logic as a background task so we return 200 immediately
    background_tasks.add_task(route_message, clean_sender, "text", message_text)

    return {"status": "success"}
