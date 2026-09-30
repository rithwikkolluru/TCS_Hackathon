import re
from typing import Any, Dict, List, Union

# Regex patterns for Indian banking PII detection and redaction
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(?:\+91[-\s]?)?[6789]\d{9}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
ACCOUNT_NUM_PATTERN = re.compile(r"\b\d{9,18}\b")  # Standard Indian Bank Account Number Lengths

# Prohibited sensitive keys that must never appear in frontend outputs
PROHIBITED_KEYS = {
    "password", "password_hash", "aadhaar", "pan", "phone", "phone_number",
    "customer_name", "account_number", "ssn", "credit_card_full", "cvv",
    "jwt_secret", "secret_key"
}


def sanitize_text(text: str) -> str:
    """Redacts any PII patterns (Aadhaar, PAN, phone, email, account number) from text."""
    if not isinstance(text, str):
        return text

    sanitized = AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", text)
    sanitized = PAN_PATTERN.sub("[REDACTED_PAN]", sanitized)
    sanitized = PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)
    return sanitized


def sanitize_data(data: Any) -> Any:
    """Recursively walks through dictionaries, lists, or primitives to strip prohibited keys and sanitize strings."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if str(k).lower() in PROHIBITED_KEYS:
                continue  # Drop prohibited field entirely
            cleaned[k] = sanitize_data(v)
        return cleaned

    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]

    elif isinstance(data, str):
        return sanitize_text(data)

    else:
        return data
