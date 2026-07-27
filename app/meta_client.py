"""
WaSenderAPI client adapter for the DYP Admissions WhatsApp Bot.

Confirmed correct WaSender API payload shapes (from live 422 error debugging):
  Text:     { "to": "+91...", "text": "..." }
  Image:    { "to": "+91...", "text": "<caption>", "imageUrl": "https://..." }
  Document: { "to": "+91...", "text": "<caption>", "documentUrl": "https://...", "fileName": "file.pdf" }

Key rules:
  - Phone number MUST start with '+' (E.164 format)
  - Text content goes in the "text" key (NOT "message")
  - Media URLs use "imageUrl" / "documentUrl" (NOT "url")
  - No "type" field needed — WaSender infers from payload shape

Because WaSender does not support native WhatsApp interactive buttons or
list menus, send_buttons() and send_list() are converted to plain-text
keyword menus automatically.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

WASENDER_TOKEN = os.getenv("WASENDER_API_TOKEN", "")
API_URL = "https://wasenderapi.com/api/send-message"

HEADERS = {
    "Authorization": f"Bearer {WASENDER_TOKEN}",
    "Content-Type": "application/json",
}


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _e164(phone: str) -> str:
    """Ensure the phone number starts with '+' as WaSender requires E.164 format."""
    return phone if phone.startswith("+") else f"+{phone}"


def _post(payload: dict) -> requests.Response:
    """POST a message payload to WaSender. Logs errors but lets caller handle raises."""
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        response.raise_for_status()
        return response
    except requests.HTTPError as exc:
        logger.error(
            "WaSender API HTTP error: %s — Response body: %s",
            exc,
            exc.response.text if exc.response is not None else "N/A",
        )
        raise
    except requests.RequestException as exc:
        logger.error("WaSender API request error: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────
# Core send functions
# ─────────────────────────────────────────────────────────────────────

def send_text(to: str, body: str) -> requests.Response:
    """Send a plain text message via WaSender."""
    payload = {
        "to": _e164(to),
        "text": body,          # ← WaSender uses "text", not "message"
    }
    return _post(payload)


def send_image(to: str, image_url: str, caption: str = "") -> requests.Response:
    """Send an image with optional caption via WaSender."""
    payload = {
        "to": _e164(to),
        "text": caption,       # caption goes in "text"
        "imageUrl": image_url, # ← "imageUrl", not "url"
    }
    return _post(payload)


def send_document(
    to: str, document_url: str, filename: str, caption: str = ""
) -> requests.Response:
    """Send a document/PDF with optional caption via WaSender."""
    payload = {
        "to": _e164(to),
        "text": caption,            # caption goes in "text"
        "documentUrl": document_url, # ← "documentUrl", not "url"
        "fileName": filename,        # ← "fileName" (camelCase)
    }
    return _post(payload)


def send_media(
    to: str, media_type: str, link: str, caption: str, filename: str = None
) -> requests.Response:
    """Generic media sender — routes to image or document payload shape."""
    if media_type == "document":
        payload = {
            "to": _e164(to),
            "text": caption,
            "documentUrl": link,
        }
        if filename:
            payload["fileName"] = filename
    else:
        # image, video, etc.
        payload = {
            "to": _e164(to),
            "text": caption,
            "imageUrl": link,
        }
    return _post(payload)


# ─────────────────────────────────────────────────────────────────────
# Menu conversion helpers (buttons → plain-text keyword menus)
# ─────────────────────────────────────────────────────────────────────

def send_buttons(to: str, body_text: str, buttons: list[dict]) -> requests.Response:
    """
    Convert Meta-style reply buttons into a plain-text keyword menu.

    buttons format: [{"id": "freeze", "title": "Freeze Admission"}, ...]
    Rendered as:
        <body_text>

        👉 Type *freeze* for ✅ Freeze My Seat
        👉 Type *explore* for 👀 Explore Options
    """
    menu_text = body_text + "\n\n"
    for b in buttons:
        menu_text += f"👉 Type *{b['id']}* for {b['title']}\n"
    return send_text(to, menu_text.rstrip())


def send_list(
    to: str,
    header: str,
    body: str,
    footer: str,
    button_text: str,
    sections: list[dict],
) -> requests.Response:
    """
    Convert a Meta interactive list menu into a plain-text keyword menu.

    sections format (Meta style):
    [{"title": "Info & Admission", "rows": [{"id": "about", "title": "About DYPCET"}]}]

    Rendered as:
        *HEADER*
        body

        *Info & Admission*
        👉 Type *about* : 🏛️ About DYPCET
        👉 Type *fee* : 💰 Fee Structure
        ...
        _footer_
    """
    menu_text = f"*{header}*\n{body}\n"
    for section in sections:
        section_title = section.get("title", "")
        if section_title:
            menu_text += f"\n*{section_title}*\n"
        for row in section.get("rows", []):
            row_id = row.get("id", "")
            row_title = row.get("title", "")
            menu_text += f"👉 Type *{row_id}* : {row_title}\n"
    if footer:
        menu_text += f"\n_{footer}_"
    return send_text(to, menu_text.rstrip())


def send_template(
    to: str,
    template_name: str,
    language_code: str = "en_US",
    parameters: list[str] | None = None,
) -> requests.Response:
    """
    WaSender does not support Meta template messages.
    Falls back to a plain-text congratulations message.
    """
    logger.warning(
        "send_template() called for '%s' — WaSender does not support Meta templates. "
        "Sending a plain text fallback.",
        template_name,
    )
    fallback = (
        "🎓 Congratulations on your admission to DYPCET!\n\n"
        "We're excited to welcome you. Type *hi* or *start* to explore your new campus."
    )
    return send_text(to, fallback)