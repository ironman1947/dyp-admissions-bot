"""
Broadcast script: send congratulations templates to admitted CAP-I students.

Reads data/students.csv, sends the WhatsApp congrats template to each
student who hasn't been contacted yet, then sends the follow-up buttons
(Freeze Admission / Explore Options). Updates the CSV with send status.

Usage:
    python -m scripts.send_broadcast

CSV Format (data/students.csv):
    Name,Phone,Branch,Status
    Rahul Patil,919876543210,Computer Engineering,
    Sneha Deshmukh,919123456789,AI & Data Science,
    Aditya Kulkarni,919112233445,Mechanical,Sent

- 'Phone' must be in E.164 format without the '+' (e.g. 919876543210)
- 'Status' is empty initially; the script sets it to 'Sent' or 'Failed: <reason>'
- Rows where Status is already 'Sent' are skipped.
"""

import csv
import logging
import sys
import time
from pathlib import Path

# Add project root to sys.path so we can import app modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.meta_client import send_template  # noqa: E402
from app.flow_logic import send_broadcast_followup  # noqa: E402
from app.messages.content import BROADCAST_TEMPLATE_NAME, BROADCAST_TEMPLATE_LANG  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────

CSV_PATH = PROJECT_ROOT / "data" / "students.csv"
DELAY_BETWEEN_SENDS = 1.5  # seconds — avoids Meta's rate limiting


def run_broadcast() -> None:
    """Main broadcast logic: read CSV, send templates, update status.

    For each student not yet marked 'Sent':
      1. Send the congrats template with Name and Branch as parameters.
      2. Wait a beat, then send the follow-up buttons (Freeze / Explore).
      3. Mark the row as 'Sent' (or 'Failed: <reason>' on error).
      4. Rewrite the CSV with updated statuses.
    """
    if not CSV_PATH.exists():
        logger.error("CSV file not found at %s", CSV_PATH)
        logger.info("Create data/students.csv with columns: Name,Phone,Branch,Status")
        return

    # Read all rows
    rows: list[dict[str, str]] = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            logger.error("CSV has no headers. Expected: Name,Phone,Branch,Status")
            return
        for row in reader:
            rows.append(row)

    if not rows:
        logger.info("No students found in CSV.")
        return

    # Ensure the Status column exists
    if "Status" not in fieldnames:
        fieldnames = list(fieldnames) + ["Status"]

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for i, row in enumerate(rows):
        name = row.get("Name", "").strip()
        phone = row.get("Phone", "").strip()
        branch = row.get("Branch", "").strip()
        status = row.get("Status", "").strip()

        # Skip already-sent rows
        if status == "Sent":
            skipped_count += 1
            logger.info("Skipped (already sent): %s (%s)", name, phone)
            continue

        # Validate required fields
        if not phone or not name:
            rows[i]["Status"] = "Failed: missing name or phone"
            failed_count += 1
            logger.warning("Skipped (invalid data): row %d — Name=%s, Phone=%s", i + 1, name, phone)
            continue

        try:
            # Step 1: Send the congrats template
            logger.info("Sending template to %s (%s, %s)...", name, phone, branch)
            send_template(
                to=phone,
                template_name=BROADCAST_TEMPLATE_NAME,
                language_code=BROADCAST_TEMPLATE_LANG,
                parameters=[name, branch] if branch else [name],
            )

            # Small delay before follow-up to ensure template arrives first
            time.sleep(0.5)

            # Step 2: Send follow-up buttons (Freeze / Explore)
            send_broadcast_followup(phone)

            rows[i]["Status"] = "Sent"
            sent_count += 1
            logger.info("✅ Sent successfully to %s (%s)", name, phone)

        except Exception as exc:
            rows[i]["Status"] = f"Failed: {exc}"
            failed_count += 1
            logger.error("❌ Failed for %s (%s): %s", name, phone, exc)

        # Rate limiting delay
        time.sleep(DELAY_BETWEEN_SENDS)

    # Rewrite CSV with updated statuses
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(
        "Broadcast complete: %d sent, %d skipped, %d failed (out of %d total)",
        sent_count,
        skipped_count,
        failed_count,
        len(rows),
    )


if __name__ == "__main__":
    run_broadcast()
