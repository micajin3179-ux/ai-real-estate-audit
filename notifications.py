"""Instant lead notifications via Telegram.

The landing page fires a Telegram message to the configured chat as soon as
someone submits the lead form. No cron jobs, no polling — just an immediate
POST to the Telegram Bot API.
"""

import os
from typing import Optional

import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _escape(text: str) -> str:
    """Minimal Telegram HTML escape."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_lead_alert(lead: dict) -> str:
    """Format a lead record into a concise Telegram HTML message."""
    name = _escape(lead.get("name") or "Unknown")
    phone = _escape(lead.get("phone") or "—")
    email = _escape(lead.get("email") or "—")
    agency = _escape(lead.get("agency") or "—")
    role = _escape(lead.get("role") or "—")
    interest = _escape(lead.get("interest") or "—")
    lead_id = lead.get("id")
    dashboard_url = "https://ai-real-estate-audit.onrender.com/dashboard"

    return (
        f"🔔 <b>New AI Real Estate Audit Lead</b>\n\n"
        f"<b>Name:</b> {name}\n"
        f"<b>Phone:</b> {phone}\n"
        f"<b>Email:</b> {email}\n"
        f"<b>Agency:</b> {agency}\n"
        f"<b>Role:</b> {role}\n"
        f"<b>Challenge:</b> {interest}\n\n"
        f"<a href='{dashboard_url}'>Open Dashboard</a>"
        + (f" · Lead #{lead_id}" if lead_id else "")
    )


async def send_telegram_lead_alert(lead: dict) -> Optional[dict]:
    """Send an immediate Telegram notification for a new lead.

    Returns the parsed Telegram API response, or None if no bot token/chat id
    is configured. Errors are swallowed so they don't break the form flow.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return None

    text = format_lead_alert(lead)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        # Don't fail the lead submission if Telegram is down or misconfigured.
        return None
