"""
Master routing engine for the DYP Admissions WhatsApp Bot (WaSender edition).

Because WaSender does not support native WhatsApp interactive buttons or
list menus, every menu is rendered as a plain-text keyword prompt.
Students reply by typing a short keyword (e.g. "fee", "nss", "contact_cse").

Entry points:
  - QR Code scan → student texts "hi" / "hello" / "start" / "cap1"
  - Any unrecognized text → welcome + main menu (default fallback)
  - Known keywords → exact handler dispatch

All outbound calls go through app.meta_client which now routes to WaSenderAPI.
"""

import logging

from app.meta_client import (
    send_text,
    send_image,
    send_document,
    send_list,
    send_buttons,
)
from app.messages.content import (
    WELCOME_TEXT,
    ACK_FREEZE,
    ACK_EXPLORE,
    ABOUT_TEXT,
    FEE_CAPTION,
    PLACEMENTS_TEXT,
    ADMISSION_CAPTION,
    BUS_TEXT,
    HOSTELS_TEXT,
    CANTEEN_TEXT,
    NCC_TEXT,
    NSS_TEXT,
    RETURN_PROMPT,
    MAIN_MENU_HEADER,
    MAIN_MENU_BODY,
    MAIN_MENU_FOOTER,
    MAIN_MENU_BUTTON,
    MAIN_MENU_SECTIONS,
    FACILITIES_MENU_HEADER,
    FACILITIES_MENU_BODY,
    FACILITIES_MENU_FOOTER,
    FACILITIES_MENU_BUTTON,
    FACILITIES_MENU_SECTIONS,
    BROADCAST_FOLLOWUP_TEXT,
    BROADCAST_BUTTONS,
    MEDIA_URLS,
    TALK_TO_US_INTRO,
    BRANCH_CONTACT_MENU,
    BRANCH_CONTACTS,
)
from app.storage.db import get_or_create_session, update_session_state

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# Greeting trigger words
# ─────────────────────────────────────────────────────────────────────

GREETING_TRIGGERS = {"hi", "hello", "start", "cap1", "hey", "hlo", "hii"}


# ─────────────────────────────────────────────────────────────────────
# Menu senders (reused across multiple handlers)
# ─────────────────────────────────────────────────────────────────────

def send_main_menu(phone: str) -> None:
    """Send the main Options list menu to the user."""
    send_list(
        to=phone,
        header=MAIN_MENU_HEADER,
        body=MAIN_MENU_BODY,
        footer=MAIN_MENU_FOOTER,
        button_text=MAIN_MENU_BUTTON,
        sections=MAIN_MENU_SECTIONS,
    )
    update_session_state(phone, "main")


def send_facilities_menu(phone: str) -> None:
    """Send the Facilities sub-menu list to the user."""
    send_list(
        to=phone,
        header=FACILITIES_MENU_HEADER,
        body=FACILITIES_MENU_BODY,
        footer=FACILITIES_MENU_FOOTER,
        button_text=FACILITIES_MENU_BUTTON,
        sections=FACILITIES_MENU_SECTIONS,
    )
    update_session_state(phone, "facilities")


# ─────────────────────────────────────────────────────────────────────
# Individual handlers (one per menu option)
# ─────────────────────────────────────────────────────────────────────

def handle_welcome(phone: str) -> None:
    """Send the initial welcome message + freeze / explore choice."""
    send_buttons(
        to=phone,
        body_text=WELCOME_TEXT,
        buttons=[
            {"id": "freeze", "title": "✅ Freeze My Seat"},
            {"id": "explore", "title": "👀 Explore Options"},
        ],
    )
    update_session_state(phone, "welcome")


def handle_freeze_admission(phone: str) -> None:
    """User chose to freeze admission — merge ACK + menu into one API call."""
    send_list(
        to=phone,
        header=MAIN_MENU_HEADER,
        body=ACK_FREEZE + "\n\n" + MAIN_MENU_BODY,
        footer=MAIN_MENU_FOOTER,
        button_text=MAIN_MENU_BUTTON,
        sections=MAIN_MENU_SECTIONS,
    )
    update_session_state(phone, "main")


def handle_explore_options(phone: str) -> None:
    """User chose to explore options — merge ACK + menu into one API call."""
    send_list(
        to=phone,
        header=MAIN_MENU_HEADER,
        body=ACK_EXPLORE + "\n\n" + MAIN_MENU_BODY,
        footer=MAIN_MENU_FOOTER,
        button_text=MAIN_MENU_BUTTON,
        sections=MAIN_MENU_SECTIONS,
    )
    update_session_state(phone, "main")


def handle_about(phone: str) -> None:
    """Send the About DYPCET info text — single call with return prompt appended."""
    send_text(phone, ABOUT_TEXT + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "about")


def handle_fee(phone: str) -> None:
    """Send the fee structure image — return prompt merged into caption."""
    send_image(phone, image_url=MEDIA_URLS["fee_structure"], caption=FEE_CAPTION + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "fee")


def handle_placements(phone: str) -> None:
    """Send the placement brochure PDF — stats + return prompt merged into caption."""
    send_document(
        phone,
        document_url=MEDIA_URLS["placement_brochure"],
        filename="DYPCET_Placement_Brochure_2025.pdf",
        caption=PLACEMENTS_TEXT + "\n\n" + RETURN_PROMPT,
    )
    update_session_state(phone, "placements")


def handle_admission(phone: str) -> None:
    """Send the admission process image — return prompt merged into caption."""
    send_image(phone, image_url=MEDIA_URLS["admission_documents"], caption=ADMISSION_CAPTION + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "admission")


def handle_facilities(phone: str) -> None:
    """Send the Facilities sub-menu."""
    send_facilities_menu(phone)


def handle_bus(phone: str) -> None:
    """Send bus transport information — single call with return prompt appended."""
    send_text(phone, BUS_TEXT + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "bus")


def handle_hostels(phone: str) -> None:
    """Send hostel information — return prompt merged into caption."""
    send_image(phone, image_url=MEDIA_URLS["hostel_info"], caption=HOSTELS_TEXT + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "hostels")


def handle_canteen(phone: str) -> None:
    """Send canteen/mess facility information — single call with return prompt appended."""
    send_text(phone, CANTEEN_TEXT + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "canteen")


def handle_ncc(phone: str) -> None:
    """Send NCC information — single call with return prompt appended."""
    send_text(phone, NCC_TEXT + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "ncc")


def handle_nss(phone: str) -> None:
    """Send NSS information — return prompt merged into caption."""
    send_image(phone, image_url=MEDIA_URLS["nss_activities"], caption=NSS_TEXT + "\n\n" + RETURN_PROMPT)
    update_session_state(phone, "nss")


# ─────────────────────────────────────────────────────────────────────
# Talk to Us — Branch contact handlers
# ─────────────────────────────────────────────────────────────────────

def send_branch_contact_menu(phone: str) -> None:
    """Send the branch selector list — intro merged into body for single API call."""
    send_list(
        to=phone,
        header=BRANCH_CONTACT_MENU["header"],
        body=TALK_TO_US_INTRO + "\n\n" + BRANCH_CONTACT_MENU["body"],
        footer=BRANCH_CONTACT_MENU["footer"],
        button_text=BRANCH_CONTACT_MENU["button_text"],
        sections=BRANCH_CONTACT_MENU["sections"],
    )
    update_session_state(phone, "talk_to_us")


def handle_talk_to_us(phone: str) -> None:
    """Show the branch contact selector menu."""
    send_branch_contact_menu(phone)


def handle_branch_contact(phone: str, branch_id: str) -> None:
    """Send coordinator contacts — return prompt appended for single API call."""
    contact_text = BRANCH_CONTACTS.get(branch_id, "Contact info not available.")
    send_text(phone, f"📞 *Faculty Coordinator Contacts*\n\n{contact_text}\n\n" + RETURN_PROMPT)
    update_session_state(phone, branch_id)


# ─────────────────────────────────────────────────────────────────────
# Handler registry — maps typed keywords → handler functions
# ─────────────────────────────────────────────────────────────────────

HANDLER_MAP: dict[str, callable] = {
    # Post-welcome choice
    "freeze":           handle_freeze_admission,
    "freeze_admission": handle_freeze_admission,  # legacy alias
    "explore":          handle_explore_options,
    "explore_options":  handle_explore_options,   # legacy alias

    # Main menu
    "menu":       send_main_menu,
    "about":      handle_about,
    "fee":        handle_fee,
    "placements": handle_placements,
    "admission":  handle_admission,
    "facilities": handle_facilities,
    "talk_to_us": handle_talk_to_us,
    "contact":    handle_talk_to_us,  # user-friendly alias

    # Facilities sub-menu
    "bus":     handle_bus,
    "hostels": handle_hostels,
    "canteen": handle_canteen,
    "ncc":     handle_ncc,
    "nss":     handle_nss,
}

# Dynamically register all branch contact IDs from content.py
for _branch_id in BRANCH_CONTACTS:
    HANDLER_MAP[_branch_id] = lambda phone, bid=_branch_id: handle_branch_contact(phone, bid)


# ─────────────────────────────────────────────────────────────────────
# Master router — single entry point called by webhook.py
# ─────────────────────────────────────────────────────────────────────

def route_message(phone: str, message_type: str, content: str) -> None:
    """Route an incoming message to the correct handler.

    Called by webhook.py (as a background task) after parsing the
    incoming WaSender webhook payload.

    Args:
        phone:        Sender's WhatsApp phone number (E.164, no '+').
        message_type: Always 'text' from WaSender (no native interactive type).
        content:      The raw text body typed by the student.

    Flow:
        1. Ensure a session exists for this phone number.
        2. If the text matches a greeting trigger → send welcome screen.
        3. If the text matches a known handler keyword → dispatch.
        4. Otherwise → default fallback: welcome + main menu.
    """
    # Ensure session exists and update last_active
    get_or_create_session(phone)

    normalized = content.strip().lower()

    # 1. Greeting triggers
    if normalized in GREETING_TRIGGERS:
        logger.info("Greeting: phone=%s, text=%s", phone, content)
        handle_welcome(phone)
        return

    # 2. Known keyword → dispatch
    if normalized in HANDLER_MAP:
        logger.info("Keyword match: phone=%s, keyword=%s", phone, normalized)
        HANDLER_MAP[normalized](phone)
        return

    # 3. Default fallback — any unrecognized text shows welcome + main menu
    logger.info("Unrecognized text (default): phone=%s, text=%s", phone, content)
    send_text(phone, WELCOME_TEXT)
    send_main_menu(phone)


# ─────────────────────────────────────────────────────────────────────
# Broadcast helper (used by scripts/send_broadcast.py)
# ─────────────────────────────────────────────────────────────────────

def send_broadcast_followup(phone: str) -> None:
    """Send the post-broadcast follow-up buttons (Freeze / Explore).

    Called by scripts/send_broadcast.py after sending the congrats
    message to each admitted student. The student replies by typing
    'freeze' or 'explore', which the webhook routes back here.
    """
    send_buttons(
        to=phone,
        body_text=BROADCAST_FOLLOWUP_TEXT,
        buttons=BROADCAST_BUTTONS,
    )
    update_session_state(phone, "broadcast_followup")
