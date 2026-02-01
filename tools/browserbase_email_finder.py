"""
browserbase_email_finder

Research companies and find contact emails using Browserbase headless browser.
Built by Builder from PRD: browserbase_email_finder
"""

import os
import re
from typing import Optional
from urllib.parse import urljoin, urlparse


def browserbase_email_finder(
    company_name: str,
    company_url: Optional[str] = None,
    target_role: Optional[str] = None,
) -> dict:
    """
    Find email addresses and contacts for a company using Browserbase.

    Args:
        company_name: Name of the company to research
        company_url: Optional direct URL to company website
        target_role: Optional specific role/title to prioritize (e.g., 'VP Operations', 'CTO')

    Returns:
        dict with:
            - result: Dict containing:
                - emails: List of discovered email addresses (strings)
                - contacts: Array of contact objects with name, role, email, source_url
            - success: Boolean indicating whether any emails were found
            - error: Error message if the search failed
    """
    result = {
        "emails": [],
        "contacts": [],
    }

    try:
        # Validate inputs
        if not company_name:
            return {
                "result": result,
                "success": False,
                "error": "company_name is required"
            }

        # Check for required environment variables
        api_key = os.getenv("BROWSERBASE_API_KEY")
        project_id = os.getenv("BROWSERBASE_PROJECT_ID")

        if not api_key or not project_id:
            return {
                "result": result,
                "success": False,
                "error": "Missing environment variables: BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID are required"
            }

        # Import dependencies
        try:
            from browserbase import Browserbase
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            missing_pkg = str(e).split("'")[-2] if "'" in str(e) else "browserbase/playwright"
            return {
                "result": result,
                "success": False,
                "error": f"Missing dependency: {missing_pkg}. Install with: pip install browserbase playwright"
            }

        # If no company_url provided, construct one from company_name
        if not company_url:
            # Simple heuristic: convert "Company Name" -> "companyname.com"
            domain_guess = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")
            company_url = f"https://{domain_guess}.com"
        elif not company_url.startswith(("http://", "https://")):
            company_url = f"https://{company_url}"

        # Initialize Browserbase
        bb = Browserbase(api_key=api_key)
        session = bb.sessions.create(project_id=project_id)

        # Common pages to check for emails
        pages_to_check = [
            "",  # Homepage
            "/about",
            "/team",
            "/contact",
            "/leadership",
            "/about-us",
            "/meet-the-team",
            "/contact-us",
        ]

        emails_found = set()
        contacts_found = []

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.set_default_timeout(30000)

            # Try each page
            for page_path in pages_to_check:
                try:
                    target_url = company_url.rstrip("/") + page_path
                    page.goto(target_url, wait_until="domcontentloaded", timeout=15000)

                    # Get page content
                    content = page.evaluate("""
                        () => {
                            const clone = document.body.cloneNode(true);
                            clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());
                            return clone.innerText || clone.textContent || '';
                        }
                    """)

                    # Also get HTML for more structured extraction
                    html = page.content()

                    # Extract emails from content
                    page_emails = _extract_emails(content + " " + html)
                    emails_found.update(page_emails)

                    # Try to extract structured contacts
                    page_contacts = _extract_contacts(html, page.url, target_role)
                    contacts_found.extend(page_contacts)

                except Exception as page_error:
                    # Page failed, continue to next
                    continue

            # Close browser
            browser.close()

        # Convert set to list and filter out generic/placeholder emails
        result["emails"] = _filter_emails(list(emails_found))

        # Deduplicate contacts by email
        seen_emails = set()
        unique_contacts = []
        for contact in contacts_found:
            if contact["email"] and contact["email"] not in seen_emails:
                seen_emails.add(contact["email"])
                unique_contacts.append(contact)

        result["contacts"] = unique_contacts

        # Success if we found at least one email
        if result["emails"] or result["contacts"]:
            return {
                "result": result,
                "success": True,
                "error": None
            }
        else:
            return {
                "result": result,
                "success": False,
                "error": f"No emails found for {company_name}"
            }

    except Exception as e:
        return {
            "result": result,
            "success": False,
            "error": str(e)
        }


def _extract_emails(text: str) -> set:
    """Extract email addresses from text using regex."""
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return set(email.lower() for email in emails)


def _filter_emails(emails: list) -> list:
    """Filter out generic/placeholder emails."""
    filtered = []
    # Skip common placeholders
    skip_patterns = [
        r'^info@',
        r'^contact@',
        r'^support@',
        r'^hello@',
        r'^admin@',
        r'^noreply@',
        r'^no-reply@',
        r'^example@',
        r'^test@',
        r'^webmaster@',
    ]

    for email in emails:
        # Check if email matches any skip pattern
        skip = False
        for pattern in skip_patterns:
            if re.match(pattern, email, re.IGNORECASE):
                skip = True
                break

        if not skip:
            filtered.append(email)

    # If we filtered everything out, return original list (at least we have something)
    return filtered if filtered else emails


def _extract_contacts(html: str, source_url: str, target_role: Optional[str] = None) -> list:
    """
    Extract structured contact information from HTML.

    Looks for patterns like:
    - <div class="team-member">Name<span>Title</span>email@example.com</div>
    - Lists with name, role, email together
    """
    contacts = []

    # Simple heuristic: find email addresses and try to extract nearby text for name/role
    # This is a basic implementation - could be enhanced with more sophisticated parsing

    email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'

    # Split HTML into sections (by common delimiters)
    # Look for emails and extract surrounding context
    matches = re.finditer(email_pattern, html)

    for match in matches:
        email = match.group(1).lower()
        start_pos = max(0, match.start() - 500)  # 500 chars before email
        end_pos = min(len(html), match.end() + 100)  # 100 chars after email
        context = html[start_pos:end_pos]

        # Remove HTML tags to get text
        context_text = re.sub(r'<[^>]+>', ' ', context)
        context_text = re.sub(r'\s+', ' ', context_text).strip()

        # Try to extract name (capitalized words near email)
        name_pattern = r'\b([A-Z][a-z]+(?: [A-Z][a-z]+){1,3})\b'
        name_matches = re.findall(name_pattern, context_text)
        name = name_matches[0] if name_matches else None

        # Try to extract role/title (words like CEO, VP, Director, etc.)
        role_pattern = r'\b(CEO|CTO|CFO|COO|VP|Vice President|Director|Manager|Head of|Chief|Founder|Co-Founder|President|Partner)\b[^<>]{0,50}'
        role_matches = re.findall(role_pattern, context_text, re.IGNORECASE)
        role = role_matches[0] if role_matches else None

        # If target_role specified, check if this contact matches
        if target_role and role:
            if target_role.lower() not in role.lower():
                continue  # Skip contacts that don't match target role

        contact = {
            "name": name,
            "role": role,
            "email": email,
            "source_url": source_url
        }

        contacts.append(contact)

    return contacts


# For Executor compatibility
run = browserbase_email_finder
