import httpx
from typing import Optional
from app.config import settings

BASE_URL = f"https://graph.facebook.com/v21.0/{settings.META_PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def _post(payload: dict) -> dict:
    """Internal helper: sends the payload to Meta and returns the JSON response."""
    with httpx.Client(timeout=15.0) as client:
        response = client.post(BASE_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()


def send_text(to: str, body: str) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    return _post(payload)


def send_template(to: str, template_name: str, language_code: str = "en_US", parameters: list[str] | None = None) -> dict:
    components = []
    if parameters:
        components.append({
            "type": "body",
            "parameters": [{"type": "text", "text": p} for p in parameters],
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components,
        },
    }
    return _post(payload)


def send_image(to: str, image_url: str, caption: str = "") -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url, "caption": caption},
    }
    return _post(payload)


def send_document(to: str, document_url: str, filename: str, caption: str = "") -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {"link": document_url, "filename": filename, "caption": caption},
    }
    return _post(payload)


def send_video(to: str, video_url: str, caption: str = "") -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "video",
        "video": {"link": video_url, "caption": caption},
    }
    return _post(payload)


def send_buttons(to: str, body_text: str, buttons: list[dict]) -> dict:
    """
    buttons format: [{"id": "freeze_admission", "title": "Freeze Admission"}, ...]
    Max 3 buttons allowed by WhatsApp.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons
                ]
            },
        },
    }
    return _post(payload)


def send_list(to: str, header: str, body: str, footer: str, button_text: str, sections: list[dict]) -> dict:
    """
    sections format:
    [{"title": "Info & Admission", "rows": [{"id": "about", "title": "About DYPCET", "description": "..."}]}]
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {"button": button_text, "sections": sections},
        },
    }
    return _post(payload)