"""
WhatsApp Webhook handlers for the DYP Admissions Bot.

Two endpoints:
  GET  /webhook — Meta's verification handshake (one-time setup).
  POST /webhook — Receives all incoming messages from WhatsApp users,
                  verifies the HMAC signature, parses the payload,
                  and dispatches to flow_logic.route_message().

Meta expects the POST handler to return 200 OK quickly (< 5 seconds).
All outbound API calls to Meta are made synchronously within the
handler since they're fast HTTP posts. If latency becomes an issue,
these can be moved to a background task queue later.
"""

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.config import settings
from app.flow_logic import route_message

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────
# GET /webhook — Verification Handshake
# ─────────────────────────────────────────────────────────────────────

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
) -> Response:
    """Handle Meta's webhook verification request.

    Meta sends a GET request with three query parameters:
      - hub.mode = 'subscribe'
      - hub.verify_token = the token you configured in Meta dashboard
      - hub.challenge = a random string Meta expects back as the response body

    We validate the mode and token, then echo back the challenge value.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(
        "Webhook verification failed: mode=%s, token_match=%s",
        hub_mode,
        hub_verify_token == settings.META_VERIFY_TOKEN,
    )
    raise HTTPException(status_code=403, detail="Verification failed")


# ─────────────────────────────────────────────────────────────────────
# POST /webhook — Incoming Message Handler
# ─────────────────────────────────────────────────────────────────────

def _verify_signature(payload: bytes, signature_header: str | None) -> bool:
    """Verify the X-Hub-Signature-256 HMAC SHA256 signature.

    Meta signs every webhook POST body with your App Secret so you
    can confirm it really came from Meta and wasn't tampered with.

    Args:
        payload: The raw request body bytes.
        signature_header: The 'X-Hub-Signature-256' header value
                          (format: 'sha256=<hex_digest>').

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature_header:
        return False

    if not signature_header.startswith("sha256="):
        return False

    expected_sig = signature_header[7:]  # Strip the 'sha256=' prefix
    computed_sig = hmac.new(
        key=settings.META_APP_SECRET.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed_sig, expected_sig)


def _extract_message_data(body: dict[str, Any]) -> tuple[str, str, str] | None:
    """Extract sender phone, message type, and content from the webhook payload.

    Meta's webhook payload structure:
    ```
    {
      "entry": [{
        "changes": [{
          "value": {
            "messages": [{
              "from": "919876543210",
              "type": "text" | "interactive",
              "text": {"body": "Hello DYP"},
              "interactive": {
                "type": "button_reply" | "list_reply",
                "button_reply": {"id": "freeze_admission"},
                "list_reply": {"id": "about"}
              }
            }]
          }
        }]
      }]
    }
    ```

    Returns:
        A tuple of (phone, message_type, content) or None if not a user message.
        - phone: sender's phone number
        - message_type: 'text' or 'interactive'
        - content: the text body or the button/list reply ID
    """
    try:
        entry = body.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return None

        message = messages[0]
        phone = message.get("from", "")
        msg_type = message.get("type", "")

        if msg_type == "text":
            content = message.get("text", {}).get("body", "")
            return (phone, "text", content)

        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            interactive_type = interactive.get("type", "")

            if interactive_type == "button_reply":
                content = interactive.get("button_reply", {}).get("id", "")
            elif interactive_type == "list_reply":
                content = interactive.get("list_reply", {}).get("id", "")
            else:
                return None

            return (phone, "interactive", content)

        else:
            # Ignore other message types (image, location, etc.)
            logger.debug("Ignoring message type: %s", msg_type)
            return None

    except (IndexError, KeyError, TypeError) as exc:
        logger.error("Failed to parse webhook payload: %s", exc)
        return None


@router.post("/webhook")
async def receive_webhook(request: Request) -> dict[str, str]:
    """Handle incoming WhatsApp messages from Meta's webhook.

    Steps:
      1. Read the raw body and verify the HMAC signature.
      2. Parse the JSON payload and extract sender phone + message content.
      3. Dispatch to flow_logic.route_message().
      4. Return 200 OK immediately (Meta requires fast acknowledgment).
    """
    # Step 1: Verify signature
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _verify_signature(raw_body, signature):
        logger.warning("Invalid webhook signature — rejecting request.")
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Step 2: Parse payload
    body: dict[str, Any] = await request.json()

    # Meta sends periodic "status" updates (delivered/read receipts)
    # which don't contain messages — we should ignore those gracefully.
    extracted = _extract_message_data(body)
    if extracted is None:
        logger.debug("No actionable message in webhook payload.")
        return {"status": "ok"}

    phone, message_type, content = extracted
    logger.info("Incoming: phone=%s, type=%s, content=%s", phone, message_type, content)

    # Step 3: Route to the correct handler
    try:
        route_message(phone, message_type, content)
    except Exception as exc:
        # Log but don't crash — Meta must always get 200 OK
        logger.exception("Error routing message from %s: %s", phone, exc)

    # Step 4: Acknowledge receipt
    return {"status": "ok"}
