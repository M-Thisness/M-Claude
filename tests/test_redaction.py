#!/usr/bin/env python3
"""
Test suite for redaction functionality in sync_raw_logs.py
Ensures sensitive data is properly redacted while preserving valid data
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from sync_raw_logs import redact_text


class TestAPIKeyRedaction:
    """Test redaction of various API keys and tokens"""

    def test_openai_api_key(self):
        text = "API_KEY=sk-1234567890abcdefghijklmnopqrst"
        result = redact_text(text)
        assert "sk-" not in result
        assert "[REDACTED_API_KEY]" in result

    def test_github_token(self):
        text = "GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        result = redact_text(text)
        assert "ghp_" not in result
        assert "[REDACTED_GITHUB_TOKEN]" in result

    def test_slack_token(self):
        # Use intentionally invalid test token (wrong length/format)
        text = "slack_token=xoxb-TEST-EXAMPLE"
        result = redact_text(text)
        assert "xoxb-" not in result

    def test_aws_access_key(self):
        text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        result = redact_text(text)
        assert "AKIA" not in result
        assert "[REDACTED_AWS_KEY]" in result


class TestEmailRedaction:
    """Test email address redaction"""

    def test_basic_email(self):
        text = "Contact me at user@example.com for details"
        result = redact_text(text)
        assert "@" not in result
        assert "[REDACTED_EMAIL]" in result

    def test_email_with_plus(self):
        text = "user+tag@gmail.com"
        result = redact_text(text)
        assert "@" not in result
        assert "[REDACTED_EMAIL]" in result

    def test_multiple_emails(self):
        text = "Email alice@example.com or bob@test.org"
        result = redact_text(text)
        assert result.count("[REDACTED_EMAIL]") == 2


class TestPhoneRedaction:
    """Test phone number redaction while preserving UUIDs and timestamps"""

    def test_phone_number_basic(self):
        text = "Call me at 555-123-4567"
        result = redact_text(text)
        assert "555-123-4567" not in result
        assert "[REDACTED_PHONE]" in result

    def test_phone_number_with_country_code(self):
        text = "Phone: +1-555-123-4567"
        result = redact_text(text)
        assert "555-123-4567" not in result
        assert "[REDACTED_PHONE]" in result

    def test_uuid_preservation(self):
        """CRITICAL: UUIDs should NOT be redacted as phone numbers"""
        uuid = "5f8a361a-cf7b-42ad-8d3e-123456789abc"
        result = redact_text(uuid)
        # UUID segments should remain intact
        assert "5f8a361a" in result
        assert "cf7b" in result
        assert "42ad" in result
        assert "[REDACTED_PHONE]" not in result

    def test_session_id_with_uuid(self):
        """Test full session ID format used in CHAT_LOGS-markdown README"""
        session_id = "session-5f8a361a-cf7b-42ad-8d3e-123456789abc"
        result = redact_text(session_id)
        assert "5f8a361a" in result
        assert "[REDACTED_PHONE]" not in result

    def test_timestamp_preservation(self):
        """ISO timestamps should not be redacted"""
        text = "2025-12-30T14:123:456:789Z"
        result = redact_text(text)
        assert "123:456" in result or "[REDACTED_PHONE]" not in result


class TestPrivateKeyRedaction:
    """Test private key redaction"""

    def test_rsa_private_key(self):
        key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890
-----END RSA PRIVATE KEY-----"""
        result = redact_text(key)
        assert "MII" not in result
        assert "[REDACTED_PRIVATE_KEY]" in result

    def test_generic_private_key(self):
        key = "-----BEGIN PRIVATE KEY-----\ndata\n-----END PRIVATE KEY-----"
        result = redact_text(key)
        assert "[REDACTED_PRIVATE_KEY]" in result


class TestCreditCardRedaction:
    """Test credit card number redaction"""

    def test_visa_card(self):
        text = "Card: 4532-1234-5678-9010"
        result = redact_text(text)
        assert "4532" not in result
        assert "[REDACTED_CARD]" in result

    def test_card_no_dashes(self):
        text = "4532 1234 5678 9010"
        result = redact_text(text)
        assert "[REDACTED_CARD]" in result


class TestIPAddressRedaction:
    """Test IP address redaction"""

    def test_ipv4_address(self):
        text = "Server at 192.168.1.100"
        result = redact_text(text)
        assert "192.168.1.100" not in result
        assert "[REDACTED_IP]" in result


class TestJWTRedaction:
    """Test JWT token redaction"""

    def test_jwt_token(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = redact_text(jwt)
        assert "eyJ" not in result
        assert "[REDACTED_JWT]" in result


class TestDatabaseConnectionRedaction:
    """Test database connection string redaction"""

    def test_postgres_connection(self):
        text = "postgres://user:pass@localhost:5432/db"
        result = redact_text(text)
        assert "postgres://" not in result
        assert "[REDACTED_DB_CONNECTION]" in result

    def test_mysql_connection(self):
        text = "mysql://root:password@localhost/mydb"
        result = redact_text(text)
        assert "[REDACTED_DB_CONNECTION]" in result

    def test_mongodb_connection(self):
        text = "mongodb://admin:secret@localhost:27017"
        result = redact_text(text)
        assert "[REDACTED_DB_CONNECTION]" in result


class TestFilePathRedaction:
    """Test file path redaction (username removal)"""

    def test_linux_home_path(self):
        text = "/home/mischa/documents/file.txt"
        result = redact_text(text)
        assert "mischa" not in result
        assert "/home/[USER]" in result

    def test_macos_users_path(self):
        text = "/Users/john/Desktop/notes.md"
        result = redact_text(text)
        assert "john" not in result
        assert "/Users/[USER]" in result

    def test_windows_path_forward_slash(self):
        text = "C:/Users/alice/Documents/file.txt"
        result = redact_text(text)
        assert "alice" not in result
        assert "C:/Users/[USER]" in result

    def test_windows_path_backslash(self):
        text = r"C:\Users\bob\Documents\file.txt"
        result = redact_text(text)
        assert "bob" not in result
        # Should be redacted to C:\Users\[USER]


class TestGenericSecretRedaction:
    """Test generic password/token/secret patterns"""

    def test_password_pattern(self):
        text = 'password="SuperSecret123"'
        result = redact_text(text)
        assert "SuperSecret123" not in result
        assert "password=[REDACTED]" in result

    def test_token_pattern(self):
        text = "token=1234567890abcdefghijklmnop"
        result = redact_text(text)
        assert "1234567890abcdefghijklmnop" not in result
        assert "token=[REDACTED]" in result

    def test_api_key_pattern(self):
        # Use TEST prefix to indicate this is not a real key
        text = "api_key: sk_test_EXAMPLE1234567890"
        result = redact_text(text)
        assert "sk_test_EXAMPLE" not in result


class TestNonStringInput:
    """Test that non-string inputs are handled gracefully"""

    def test_none_input(self):
        result = redact_text(None)
        assert result is None

    def test_number_input(self):
        result = redact_text(12345)
        assert result == 12345

    def test_list_input(self):
        result = redact_text(["test", "list"])
        assert result == ["test", "list"]


class TestEdgeCases:
    """Test edge cases and complex scenarios"""

    def test_multiple_secrets_in_text(self):
        text = """
        Email: user@example.com
        API Key: sk-1234567890abcdefghijklmnop
        Phone: 555-123-4567
        """
        result = redact_text(text)
        assert "@" not in result
        assert "sk-" not in result
        assert "555-123-4567" not in result

    def test_empty_string(self):
        result = redact_text("")
        assert result == ""

    def test_no_secrets(self):
        text = "This is a normal text with no secrets"
        result = redact_text(text)
        assert result == text


class TestRealWorldScenarios:
    """Test realistic conversation excerpts"""

    def test_conversation_with_mixed_content(self):
        """Simulate a real conversation log entry"""
        text = """
        {
            "session_id": "session-5f8a361a-cf7b-42ad-8d3e-123456789abc",
            "timestamp": "2025-12-30T14:123:456:789Z",
            "user": "mischa@example.com",
            "content": "Here's my API key: sk-1234567890abcdef"
        }
        """
        result = redact_text(text)

        # Should preserve UUID
        assert "5f8a361a" in result

        # Should redact email
        assert "mischa@example.com" not in result
        assert "[REDACTED_EMAIL]" in result

        # Should redact API key
        assert "sk-1234567890abcdef" not in result
        assert "[REDACTED_API_KEY]" in result
