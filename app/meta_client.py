"""
WaSenderAPI client adapter for the DYP Admissions WhatsApp Bot.

Previously this module talked to Meta's Graph API. It now routes all
outbound messages through WaSenderAPI (https://wasenderapi.com).

Because WaSender does not support native WhatsApp interactive buttons or
list menus, every send_buttons() / send_list() call is converted into a
plain-text numbered menu so students can reply by typing a short keyword.
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
# Internal helper
# ─────────────────────────────────────────────────────────────────────

def _post(payload: dict) -> dict:
    """POST a message payload to WaSender and return the JSON response."""
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.error("WaSender API error: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────
# Core send functions
# ─────────────────────────────────────────────────────────────────────

def send_text(to: str, body: str) -> dict:
    """Send a plain text message via WaSender."""
    payload = {
        "to": to,
        "type": "text",
        "message": body,
    }
    return _post(payload)


def send_image(to: str, image_url: str, caption: str = "") -> dict:
    """Send an image message via WaSender."""
    payload = {
        "to": to,
        "type": "image",
        "url": image_url,
        "caption": caption,
    }
    return _post(payload)


def send_document(to: str, document_url: str, filename: str, caption: str = "") -> dict:
    """Send a document/PDF message via WaSender."""
    payload = {
        "to": to,
        "type": "document",
        "url": document_url,
        "caption": caption,
        "filename": filename,
    }
    return _post(payload)


def send_media(to: str, media_type: str, link: str, caption: str, filename: str = None) -> dict:
    """Generic media sender — routes to image or document based on media_type."""
    payload = {
        "to": to,
        "type": media_type,
        "url": link,
        "caption": caption,
    }
    if filename:
        payload["filename"] = filename
    return _post(payload)


# ─────────────────────────────────────────────────────────────────────
# Menu conversion helpers
# ─────────────────────────────────────────────────────────────────────

def send_buttons(to: str, body_text: str, buttons: list[dict]) -> dict:
    """
    Convert Meta-style reply buttons into a plain-text numbered menu.

    buttons format: [{"id": "freeze", "title": "Freeze Admission"}, ...]
    Rendered as:
        <body_text>

        👉 Type *freeze* for Freeze Admission
        👉 Type *explore* for Explore Options
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
) -> dict:
    """
    Convert a Meta interactive list menu into a plain-text keyword menu.

    sections format (Meta style):
    [{"title": "Info & Admission", "rows": [{"id": "about", "title": "About DYPCET", "description": "..."}]}]

    Rendered as:
        *HEADER*
        body

        📚 Info & Admission
        👉 Type *about* : About DYPCET
        👉 Type *fee*   : Fee Structure
        ...
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


def send_template(to: str, template_name: str, language_code: str = "en_US", parameters: list[str] | None = None) -> dict:
    """
    Template messages are not natively supported by WaSender in the same
    way as Meta. We fall back to a plain-text message that mirrors the
    template body for now.
    """
    logger.warning(
        "send_template() called for template '%s' — WaSender does not support Meta templates. "
        "Sending a plain text fallback.",
        template_name,
    )
    fallback = (
        "🎓 Congratulations on your admission to DYPCET!\n\n"
        "We're excited to welcome you. Type *hi* or *start* to explore your new campus."
    )
    return send_text(to, fallback)