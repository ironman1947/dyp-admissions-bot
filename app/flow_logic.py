"""
Master routing engine for the DYP Admissions WhatsApp Bot.

This module is the brain of the chatbot. It receives parsed webhook
events (phone number + message content) from webhook.py and routes
them to the correct handler based on the message type:

1. **Button/List Reply IDs**: If the incoming payload has a recognized
   ID (e.g. 'about', 'fee', 'facilities'), the matching handler sends
   the appropriate media/text response.

2. **Plain Text Messages**: Any unrecognized text (e.g. "Hello DYP",
   "hi", "menu") triggers the welcome message + main Options menu.

Both entry points (QR code scan → text, and broadcast template →
button reply) converge on the same main Options menu.
"""

import logging

from app.meta_client import send_text, send_image, send_document, send_list, send_buttons
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
# Menu Senders (reused across multiple handlers)
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
# Individual Handlers (one per menu option)
# ─────────────────────────────────────────────────────────────────────

def handle_freeze_admission(phone: str) -> None:
    """User chose to freeze admission from the broadcast follow-up buttons."""
    send_text(phone, ACK_FREEZE)
    send_main_menu(phone)


def handle_explore_options(phone: str) -> None:
    """User chose to explore options from the broadcast follow-up buttons."""
    send_text(phone, ACK_EXPLORE)
    send_main_menu(phone)


def handle_about(phone: str) -> None:
    """Send the About DYPCET info text."""
    send_text(phone, ABOUT_TEXT)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "about")


def handle_fee(phone: str) -> None:
    """Send the fee structure image with caption."""
    send_image(phone, image_url=MEDIA_URLS["fee_structure"], caption=FEE_CAPTION)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "fee")


def handle_placements(phone: str) -> None:
    """Send placement stats text and the placement brochure PDF."""
    send_text(phone, PLACEMENTS_TEXT)
    send_document(
        phone,
        document_url=MEDIA_URLS["placement_brochure"],
        filename="DYPCET_Placement_Brochure_2025.pdf",
        caption="📄 DYPCET Placement Brochure 2025",
    )
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "placements")


def handle_admission(phone: str) -> None:
    """Send the admission process image with document requirements."""
    send_image(phone, image_url=MEDIA_URLS["admission_documents"], caption=ADMISSION_CAPTION)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "admission")


def handle_facilities(phone: str) -> None:
    """Send the Facilities sub-menu."""
    send_facilities_menu(phone)


def handle_bus(phone: str) -> None:
    """Send bus transport information."""
    send_text(phone, BUS_TEXT)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "bus")


def handle_hostels(phone: str) -> None:
    """Send hostel information with image."""
    send_image(phone, image_url=MEDIA_URLS["hostel_info"], caption=HOSTELS_TEXT)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "hostels")


def handle_canteen(phone: str) -> None:
    """Send canteen/mess facility information."""
    send_text(phone, CANTEEN_TEXT)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "canteen")


def handle_ncc(phone: str) -> None:
    """Send NCC information."""
    send_text(phone, NCC_TEXT)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "ncc")


def handle_nss(phone: str) -> None:
    """Send NSS and rural internship information with image."""
    send_image(phone, image_url=MEDIA_URLS["nss_activities"], caption=NSS_TEXT)
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, "nss")


# ─────────────────────────────────────────────────────────────────────
# Talk to Us — Branch Contact Handlers
# ─────────────────────────────────────────────────────────────────────

def send_branch_contact_menu(phone: str) -> None:
    """Send the branch selector list for Talk to Us."""
    send_text(phone, TALK_TO_US_INTRO)
    send_list(
        to=phone,
        header=BRANCH_CONTACT_MENU["header"],
        body=BRANCH_CONTACT_MENU["body"],
        footer=BRANCH_CONTACT_MENU["footer"],
        button_text=BRANCH_CONTACT_MENU["button_text"],
        sections=BRANCH_CONTACT_MENU["sections"],
    )
    update_session_state(phone, "talk_to_us")


def handle_talk_to_us(phone: str) -> None:
    """Show the branch contact selector menu."""
    send_branch_contact_menu(phone)


def handle_branch_contact(phone: str, branch_id: str) -> None:
    """Send the coordinator contacts for a specific branch."""
    contact_text = BRANCH_CONTACTS.get(branch_id, "Contact info not available.")
    send_text(phone, f"📞 *Faculty Coordinator Contacts*\n\n{contact_text}")
    send_text(phone, RETURN_PROMPT)
    update_session_state(phone, branch_id)


# ─────────────────────────────────────────────────────────────────────
# Handler Registry — maps button/list IDs to handler functions
# ─────────────────────────────────────────────────────────────────────

HANDLER_MAP: dict[str, callable] = {
    "freeze_admission": handle_freeze_admission,
    "explore_options": handle_explore_options,
    "about": handle_about,
    "fee": handle_fee,
    "placements": handle_placements,
    "admission": handle_admission,
    "facilities": handle_facilities,
    "bus": handle_bus,
    "hostels": handle_hostels,
    "canteen": handle_canteen,
    "ncc": handle_ncc,
    "nss": handle_nss,
    "talk_to_us": handle_talk_to_us,
}

# Dynamically register all branch contact IDs
for _branch_id in BRANCH_CONTACTS:
    HANDLER_MAP[_branch_id] = lambda phone, bid=_branch_id: handle_branch_contact(phone, bid)


# ─────────────────────────────────────────────────────────────────────
# Master Router — single entry point called by webhook.py
# ─────────────────────────────────────────────────────────────────────

def route_message(phone: str, message_type: str, content: str) -> None:
    """Route an incoming message to the correct handler.

    This is the single entry point called by webhook.py after parsing
    the incoming Meta webhook payload.

    Args:
        phone: Sender's WhatsApp phone number (E.164, no '+').
        message_type: Either 'interactive' (button/list reply) or 'text'.
        content: The button/list reply ID (if interactive) or the text body.

    Flow:
        1. Ensure a session exists for this phone number.
        2. If the content matches a known handler ID → dispatch to that handler.
        3. Otherwise (plain text) → send welcome + main menu.
    """
    # Ensure session exists and update last_active
    get_or_create_session(phone)

    if message_type == "interactive" and content in HANDLER_MAP:
        logger.info("Interactive reply: phone=%s, id=%s", phone, content)
        HANDLER_MAP[content](phone)
    elif message_type == "text" and content.lower().strip() in HANDLER_MAP:
        # Allow users to type handler names directly (e.g. "about", "fee")
        logger.info("Text shortcut: phone=%s, text=%s", phone, content)
        HANDLER_MAP[content.lower().strip()](phone)
    else:
        # Default: any unrecognized text → welcome + main menu
        logger.info("Plain text (default): phone=%s, text=%s", phone, content)
        send_text(phone, WELCOME_TEXT)
        send_main_menu(phone)


def send_broadcast_followup(phone: str) -> None:
    """Send the post-broadcast follow-up buttons (Freeze / Explore).

    Called by scripts/send_broadcast.py after sending the congrats
    template to each admitted student. The student then taps one of
    the two buttons, which comes back through the webhook and routes
    to handle_freeze_admission or handle_explore_options — both of
    which eventually show the main Options menu.
    """
    send_buttons(
        to=phone,
        body_text=BROADCAST_FOLLOWUP_TEXT,
        buttons=BROADCAST_BUTTONS,
    )
    update_session_state(phone, "broadcast_followup")
