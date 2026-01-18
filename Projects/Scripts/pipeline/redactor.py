#!/usr/bin/env python3
"""
M-Claude Redactor

Pre-compiled regex patterns for efficient secret/PII redaction.
Patterns are compiled once at module load for O(1) per-call overhead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Pattern, Tuple

# Backslash constant for Windows paths
BS = chr(92)


@dataclass(frozen=True)
class RedactionPattern:
    """A compiled redaction pattern with replacement."""
    pattern: Pattern[str]
    replacement: str
    name: str


class Redactor:
    """
    Pre-compiled regex redactor for secrets and PII.

    Compiles all patterns once at instantiation for efficient reuse.
    Patterns are applied in order - more specific patterns should come first.
    """

    # Pattern definitions: (regex, replacement, name)
    PATTERN_DEFS: List[Tuple[str, str, str]] = [
        # API Keys and Tokens
        (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]", "openai_key"),
        (r"(sk-proj-[a-zA-Z0-9_-]{20,})", "[REDACTED_API_KEY]", "openai_proj_key"),
        (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]", "github_pat"),
        (r"(gho_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]", "github_oauth"),
        (r"(ghu_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]", "github_user"),
        (r"(ghs_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]", "github_server"),
        (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]", "slack_token"),
        (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]", "aws_access_key"),
        (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]", "google_oauth"),

        # Stripe Keys
        (r"(sk_live_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]", "stripe_live_secret"),
        (r"(pk_live_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]", "stripe_live_public"),
        (r"(sk_test_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]", "stripe_test_secret"),
        (r"(pk_test_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]", "stripe_test_public"),
        (r"(rk_live_[a-zA-Z0-9]{20,})", "[REDACTED_STRIPE_KEY]", "stripe_restricted"),

        # Private Keys (multiline)
        (
            r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z]+ PRIVATE KEY-----)",
            "[REDACTED_PRIVATE_KEY]",
            "private_key"
        ),

        # JWTs
        (
            r"(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})",
            "[REDACTED_JWT]",
            "jwt"
        ),

        # Database Connections
        (r"(postgres://[^\s\"']+)", "[REDACTED_DB_URL]", "postgres_url"),
        (r"(postgresql://[^\s\"']+)", "[REDACTED_DB_URL]", "postgresql_url"),
        (r"(mysql://[^\s\"']+)", "[REDACTED_DB_URL]", "mysql_url"),
        (r"(mongodb://[^\s\"']+)", "[REDACTED_DB_URL]", "mongodb_url"),
        (r"(redis://[^\s\"']+)", "[REDACTED_DB_URL]", "redis_url"),

        # Credentials in URLs
        (r"(://[^:]+:[^@]+@)", "://[REDACTED_CREDS]@", "url_creds"),

        # Password/Token assignments
        (r"(password\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?)", "password=[REDACTED]", "password_assign"),
        (r"(token\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "token=[REDACTED]", "token_assign"),
        (r"(secret\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?)", "secret=[REDACTED]", "secret_assign"),
        (r"(api_key\s*[:=]\s*['\"]?[^\s'\"]{10,}['\"]?)", "api_key=[REDACTED]", "api_key_assign"),

        # PII: Email addresses
        (r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", "[REDACTED_EMAIL]", "email"),

        # PII: Credit card numbers
        (r"(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})", "[REDACTED_CARD]", "credit_card"),

        # PII: SSN
        (r"(\d{3}-\d{2}-\d{4})", "[REDACTED_SSN]", "ssn"),

        # PII: Phone numbers (various formats)
        (r"(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", "[REDACTED_PHONE]", "phone"),

        # IP addresses (but not version numbers like 1.2.3)
        (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", "[REDACTED_IP]", "ip_address"),

        # File paths with usernames (use raw strings to avoid escape issues)
        (r"(/home/[a-zA-Z0-9_-]+)", r"/home/[USER]", "linux_home"),
        (r"(/Users/[a-zA-Z0-9_-]+)", r"/Users/[USER]", "macos_home"),
        (r"(C:\\Users\\[a-zA-Z0-9_-]+)", r"C:\\Users\\[USER]", "windows_home"),
        (r"(/data/data/com\.termux/files/home)", r"[TERMUX_HOME]", "termux_home"),
    ]

    # Comprehensive email content redaction patterns
    GMAIL_PATTERN_DEFS: List[Tuple[str, str, str]] = [
        # Gmail API JSON fields - body content
        (r'"body"\s*:\s*\{[^}]*"data"\s*:\s*"[^"]*"', '"body": {"data": "[REDACTED_EMAIL_BODY]"}', "gmail_body"),
        (r'"body"\s*:\s*"[^"]{20,}"', '"body": "[REDACTED_EMAIL_BODY]"', "gmail_body_simple"),

        # Gmail snippets and previews
        (r'"snippet"\s*:\s*"[^"]{10,}"', '"snippet": "[REDACTED_EMAIL_SNIPPET]"', "gmail_snippet"),
        (r'"preview"\s*:\s*"[^"]{10,}"', '"preview": "[REDACTED_EMAIL_PREVIEW]"', "email_preview"),

        # Subject lines (multiple formats)
        (r'"subject"\s*:\s*"[^"]*"', '"subject": "[REDACTED_EMAIL_SUBJECT]"', "gmail_subject"),
        (r'Subject:\s*[^\n]+', 'Subject: [REDACTED_EMAIL_SUBJECT]', "email_subject_header"),

        # From/To/Cc/Bcc headers
        (r'"from"\s*:\s*"[^"]*"', '"from": "[REDACTED_SENDER]"', "gmail_from"),
        (r'"to"\s*:\s*"[^"]*"', '"to": "[REDACTED_RECIPIENT]"', "gmail_to"),
        (r'"cc"\s*:\s*"[^"]*"', '"cc": "[REDACTED_CC]"', "gmail_cc"),
        (r'"bcc"\s*:\s*"[^"]*"', '"bcc": "[REDACTED_BCC]"', "gmail_bcc"),
        (r'"sender"\s*:\s*"[^"]*"', '"sender": "[REDACTED_SENDER]"', "gmail_sender"),
        (r'"replyTo"\s*:\s*"[^"]*"', '"replyTo": "[REDACTED_REPLY_TO]"', "gmail_reply_to"),

        # Email headers in raw/text format
        (r"From:\s*[^\n]+", "From: [REDACTED_SENDER]", "email_from_header"),
        (r"To:\s*[^\n]+", "To: [REDACTED_RECIPIENT]", "email_to_header"),
        (r"Cc:\s*[^\n]+", "Cc: [REDACTED_CC]", "email_cc_header"),
        (r"Bcc:\s*[^\n]+", "Bcc: [REDACTED_BCC]", "email_bcc_header"),
        (r"Reply-To:\s*[^\n]+", "Reply-To: [REDACTED_REPLY_TO]", "email_reply_header"),
        (r"Delivered-To:\s*[^\n]+", "Delivered-To: [REDACTED]", "email_delivered_header"),
        (r"Return-Path:\s*[^\n]+", "Return-Path: [REDACTED]", "email_return_header"),

        # Message-ID and references
        (r'"messageId"\s*:\s*"[^"]*"', '"messageId": "[REDACTED_MSG_ID]"', "gmail_message_id"),
        (r'"threadId"\s*:\s*"[^"]*"', '"threadId": "[REDACTED_THREAD_ID]"', "gmail_thread_id"),
        (r'"id"\s*:\s*"[a-f0-9]{16}"', '"id": "[REDACTED_EMAIL_ID]"', "gmail_id"),
        (r"Message-ID:\s*[^\n]+", "Message-ID: [REDACTED]", "email_message_id_header"),
        (r"References:\s*[^\n]+", "References: [REDACTED]", "email_references_header"),
        (r"In-Reply-To:\s*[^\n]+", "In-Reply-To: [REDACTED]", "email_in_reply_header"),

        # Label IDs (may contain folder names)
        (r'"labelIds"\s*:\s*\[[^\]]*\]', '"labelIds": ["[REDACTED_LABELS]"]', "gmail_labels"),

        # Payload parts with email content
        (r'"mimeType"\s*:\s*"text/(plain|html)"[^}]*"body"[^}]*\}', '"mimeType": "text/\\1", "body": {"data": "[REDACTED]"}}', "gmail_payload"),

        # Raw email content (base64)
        (r'"raw"\s*:\s*"[A-Za-z0-9+/=]{100,}"', '"raw": "[REDACTED_RAW_EMAIL]"', "gmail_raw"),

        # Email quoted content patterns
        (r"On .{10,80} wrote:", "On [DATE] [SENDER] wrote:", "email_quote"),
        (r"------+ ?Original Message ?------+", "---------- Original Message ----------", "email_original"),
        (r"------+ ?Forwarded message ?------+", "---------- Forwarded Message ----------", "email_forwarded"),

        # Email threading indicators
        (r"(Re|Fwd|RE|FW|Fw):\s*[^\n]{5,}", r"\1: [REDACTED_SUBJECT]", "email_thread"),

        # Common email signatures
        (r"Sent from my (iPhone|iPad|Android|Galaxy|Pixel)[^\n]*", "Sent from my [DEVICE]", "email_signature_device"),
        (r"Get Outlook for (iOS|Android)[^\n]*", "Get Outlook for [PLATFORM]", "email_signature_outlook"),

        # Unsubscribe links (indicate email content)
        (r"[Uu]nsubscribe[^\n]{0,100}", "[UNSUBSCRIBE_LINK]", "email_unsubscribe"),
        (r"[Mm]anage\s+(your\s+)?subscriptions?[^\n]{0,50}", "[MANAGE_SUBSCRIPTIONS]", "email_manage_subs"),
    ]

    def __init__(self, include_gmail: bool = True):
        """
        Initialize the redactor with compiled patterns.

        Args:
            include_gmail: Whether to include Gmail-specific patterns
        """
        patterns = list(self.PATTERN_DEFS)
        if include_gmail:
            patterns.extend(self.GMAIL_PATTERN_DEFS)

        self.patterns: List[RedactionPattern] = []
        for regex, replacement, name in patterns:
            try:
                compiled = re.compile(regex, re.IGNORECASE | re.MULTILINE)
                self.patterns.append(RedactionPattern(compiled, replacement, name))
            except re.error as e:
                # Log but don't fail - skip bad patterns
                print(f"Warning: Invalid regex pattern '{name}': {e}")

    def redact(self, text: str) -> str:
        """
        Apply all redaction patterns to text.

        Args:
            text: Input text to redact

        Returns:
            Redacted text with sensitive content replaced
        """
        if not isinstance(text, str):
            return text

        for pattern in self.patterns:
            text = pattern.pattern.sub(pattern.replacement, text)

        return text

    def redact_with_stats(self, text: str) -> Tuple[str, dict]:
        """
        Redact text and return statistics about what was redacted.

        Args:
            text: Input text to redact

        Returns:
            Tuple of (redacted_text, stats_dict)
        """
        if not isinstance(text, str):
            return text, {}

        stats = {}
        for pattern in self.patterns:
            matches = pattern.pattern.findall(text)
            if matches:
                stats[pattern.name] = len(matches)
                text = pattern.pattern.sub(pattern.replacement, text)

        return text, stats

    def detect_sensitive(self, text: str) -> List[str]:
        """
        Detect which types of sensitive content are present.

        Args:
            text: Input text to scan

        Returns:
            List of pattern names that matched
        """
        if not isinstance(text, str):
            return []

        detected = []
        for pattern in self.patterns:
            if pattern.pattern.search(text):
                detected.append(pattern.name)

        return detected


def detect_gmail_content(text: str) -> bool:
    """
    Detect if text contains Gmail API response content or email data.

    Args:
        text: Text to analyze

    Returns:
        True if potential email content is found
    """
    if not isinstance(text, str):
        return False

    # Gmail API indicators
    gmail_indicators = [
        '"messages"',
        '"threadId"',
        '"labelIds"',
        '"mimeType"',
        "gmail_",  # MCP tool prefix
        '"snippet"',
        '"payload"',
        "multipart/",
        "Content-Type:",
        "MIME-Version:",
    ]

    text_lower = text.lower()
    return any(indicator.lower() in text_lower for indicator in gmail_indicators)


# Module-level singleton instance
_default_redactor: Redactor | None = None


def get_redactor(include_gmail: bool = True) -> Redactor:
    """Get the default redactor instance (singleton)."""
    global _default_redactor
    if _default_redactor is None:
        _default_redactor = Redactor(include_gmail=include_gmail)
    return _default_redactor


def redact(text: str) -> str:
    """Convenience function to redact text using default redactor."""
    return get_redactor().redact(text)
