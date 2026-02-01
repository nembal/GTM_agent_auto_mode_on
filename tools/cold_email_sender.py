"""
cold_email_sender

Send personalized cold outreach emails to prospects and track engagement metrics.
Primary outbound channel for reaching CTOs and operations leaders.

Built by Builder from PRD: cold_email_sender
"""

import os
import time
from typing import Any, Optional
from datetime import datetime

try:
    import resend
except ImportError:
    resend = None


def cold_email_sender(
    recipients: list[dict[str, Any]],
    template: dict[str, str],
    campaign_name: str,
    send_options: Optional[dict[str, Any]] = None
) -> dict:
    """
    Send personalized cold outreach emails with tracking.

    Args:
        recipients: List of dicts with keys: email, first_name, last_name, company, title, custom_fields (optional)
        template: Dict with 'subject' and 'body' keys containing {{variable}} placeholders
        campaign_name: String identifier for grouping and tracking
        send_options: Optional dict with:
            - schedule_time: ISO 8601 timestamp or natural language ("in 1 hour")
            - daily_limit: Max emails per day (default: 50)
            - sender_name: Name to send from
            - sender_email: Email to send from (required if RESEND_SENDER_EMAIL not set)
            - delay_seconds: Delay between sends for rate limiting (default: 1)

    Returns:
        dict with:
            - result: Dict containing:
                - send_results: List of {recipient_email, status, message_id, timestamp}
                - campaign_stats: {total_sent, total_failed, open_count, click_count, reply_count, bounce_count}
                - detailed_events: Placeholder for webhook events (requires separate listener)
            - success: Boolean indicating overall success
            - error: Error message if any
    """
    result = {
        "send_results": [],
        "campaign_stats": {
            "total_sent": 0,
            "total_failed": 0,
            "open_count": 0,
            "click_count": 0,
            "reply_count": 0,
            "bounce_count": 0
        },
        "detailed_events": []
    }

    try:
        # Validate resend library is available
        if resend is None:
            raise ImportError("resend library not installed. Run: pip install resend")

        # Get API key
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            raise ValueError("RESEND_API_KEY environment variable not set")

        resend.api_key = api_key

        # Parse send options
        send_options = send_options or {}
        sender_email = send_options.get("sender_email") or os.getenv("RESEND_SENDER_EMAIL")
        if not sender_email:
            raise ValueError("sender_email must be provided in send_options or RESEND_SENDER_EMAIL env var")

        sender_name = send_options.get("sender_name", "Fullsend")
        from_address = f"{sender_name} <{sender_email}>"
        daily_limit = send_options.get("daily_limit", 50)
        delay_seconds = send_options.get("delay_seconds", 1)
        schedule_time = send_options.get("schedule_time")

        # Validate template
        if "subject" not in template or "body" not in template:
            raise ValueError("template must contain 'subject' and 'body' keys")

        # Validate recipients
        if not recipients or not isinstance(recipients, list):
            raise ValueError("recipients must be a non-empty list")

        # Enforce daily limit
        if len(recipients) > daily_limit:
            recipients = recipients[:daily_limit]
            print(f"Warning: Limited to {daily_limit} recipients per send_options.daily_limit")

        # Send emails
        for i, recipient in enumerate(recipients):
            recipient_email = recipient.get("email")
            if not recipient_email:
                result["send_results"].append({
                    "recipient_email": "unknown",
                    "status": "failed",
                    "message_id": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": "Missing email field"
                })
                result["campaign_stats"]["total_failed"] += 1
                continue

            try:
                # Personalize subject and body
                personalized_subject = _personalize_template(template["subject"], recipient)
                personalized_body = _personalize_template(template["body"], recipient)

                # Prepare send parameters
                params = {
                    "from": from_address,
                    "to": [recipient_email],
                    "subject": personalized_subject,
                    "html": personalized_body,
                    "tags": [
                        {"name": "campaign", "value": campaign_name},
                        {"name": "recipient_company", "value": recipient.get("company", "unknown")},
                        {"name": "recipient_title", "value": recipient.get("title", "unknown")}
                    ]
                }

                # Add scheduling if specified
                if schedule_time:
                    params["scheduled_at"] = schedule_time

                # Send email
                response = resend.Emails.send(params)

                # Extract message ID from response
                message_id = None
                if hasattr(response, "id"):
                    message_id = response.id
                elif isinstance(response, dict) and "id" in response:
                    message_id = response["id"]

                result["send_results"].append({
                    "recipient_email": recipient_email,
                    "status": "sent",
                    "message_id": message_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": None
                })
                result["campaign_stats"]["total_sent"] += 1

                # Rate limiting: delay between sends
                if i < len(recipients) - 1:  # Don't delay after last email
                    time.sleep(delay_seconds)

            except Exception as send_error:
                result["send_results"].append({
                    "recipient_email": recipient_email,
                    "status": "failed",
                    "message_id": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(send_error)
                })
                result["campaign_stats"]["total_failed"] += 1

        # Add note about tracking
        result["tracking_note"] = (
            "Open/click tracking is enabled by default in Resend. "
            "Set up webhooks at https://resend.com/webhooks to receive "
            "real-time events for opens, clicks, bounces, and replies."
        )

        return {
            "result": result,
            "success": True,
            "error": None
        }

    except Exception as e:
        return {
            "result": result,  # Return partial results
            "success": False,
            "error": str(e)
        }


def _personalize_template(template_str: str, recipient: dict[str, Any]) -> str:
    """
    Replace {{variable}} placeholders with recipient data.

    Args:
        template_str: Template string with {{variable}} placeholders
        recipient: Dict with recipient data

    Returns:
        Personalized string with variables replaced
    """
    personalized = template_str

    # Standard fields
    replacements = {
        "first_name": recipient.get("first_name", ""),
        "last_name": recipient.get("last_name", ""),
        "email": recipient.get("email", ""),
        "company": recipient.get("company", ""),
        "title": recipient.get("title", "")
    }

    # Add custom fields if present
    custom_fields = recipient.get("custom_fields", {})
    if isinstance(custom_fields, dict):
        replacements.update(custom_fields)

    # Replace all {{variable}} occurrences
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"
        personalized = personalized.replace(placeholder, str(value))

    return personalized


# For Executor compatibility
run = cold_email_sender
