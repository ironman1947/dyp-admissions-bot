"""
WaSender Webhook handlers for the DYP Admissions WhatsApp Bot.

Two endpoints:
  GET  /webhook — Simple liveness check (WaSender doesn't do verification handshakes).
  POST /webhook — Receives all incoming messages from WaSender's webhook delivery,
                  parses the payload, and dispatches to flow_logic.route_message()
                  via a background task so we return 200 OK immediately.

Confirmed WaSender webhook payload structure (from live logs):
{
  "data": {
    "messages": {
      "messageBody": "cap1",
      "key": {
        "cleanedSenderPn": "918421382779",
        "senderPn": "918421382779@c.us"
      }
    }
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

    Tries the confirmed nested structure first (data → messages → key),
    then falls back to the flat structure (data → from / messageBody) so
    the bot stays resilient to any future WaSender API changes.

    Returns:
        A tuple (phone, text) if a valid user message was found, else None.
    """
    try:
        payload_data = data.get("data", {})

        # ── Path 1: Confirmed nested structure (data.messages.key) ──────────
        messages_obj = payload_data.get("messages", {})
        message_text: str = messages_obj.get("messageBody", "")

        key_obj = messages_obj.get("key", {})
        sender: str = (
            key_obj.get("cleanedSenderPn")
            or key_obj.get("senderPn", "")
        )

        # ── Path 2: Flat fallback (data.from / data.messageBody) ────────────
        if not sender:
            sender = (
                payload_data.get("from")
                or payload_data.get("sender")
                or data.get("from")
                or ""
            )
        if not message_text:
            message_text = (
                payload_data.get("messageBody")
                or payload_data.get("body")
                or payload_data.get("message")
                or ""
            )

        if not sender or not message_text:
            logger.debug("Could not extract sender or message_text from payload.")
            return None

        # Strip any leftover WhatsApp JID suffix (@c.us / @s.whatsapp.net)
        if "@" in sender:
            sender = sender.split("@")[0]

        # Skip group messages (group JIDs contain a hyphen before @g.us)
        if payload_data.get("isGroup") or messages_obj.get("isGroup"):
            logger.debug("Ignoring group message from %s", sender)
            return None

        return (sender, message_text)

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
      2. Extract sender phone + message text from the nested structure.
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
    logger.info("Dispatching: phone=%s, text=%s", clean_sender, message_text)

    # Dispatch to flow logic as a background task so we return 200 immediately
    background_tasks.add_task(route_message, clean_sender, "text", message_text)

    return {"status": "success"}
