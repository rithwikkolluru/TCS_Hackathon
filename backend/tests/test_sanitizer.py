from backend.app.core.sanitizer import sanitize_text, sanitize_data


def test_sanitize_text_redacts_aadhaar():
    text = "Customer Aadhaar is 1234 5678 9012 for account verification."
    sanitized = sanitize_text(text)
    assert "1234 5678 9012" not in sanitized
    assert "[REDACTED_AADHAAR]" in sanitized


def test_sanitize_text_redacts_pan():
    text = "Form 60 submitted, customer PAN is ABCDE1234F."
    sanitized = sanitize_text(text)
    assert "ABCDE1234F" not in sanitized
    assert "[REDACTED_PAN]" in sanitized


def test_sanitize_text_redacts_phone_and_email():
    text = "Reach user at 9876543210 or user@example.com."
    sanitized = sanitize_text(text)
    assert "9876543210" not in sanitized
    assert "user@example.com" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_EMAIL]" in sanitized


def test_sanitize_data_drops_prohibited_keys():
    payload = {
        "branch_id": "BR001",
        "predicted_customers": 180,
        "password": "secret_password",
        "aadhaar": "999988887777",
        "customer_name": "Ravi Kumar",
        "details": {
            "phone_number": "9123456789",
            "comment": "Good teller service at counter."
        }
    }
    cleaned = sanitize_data(payload)
    assert "password" not in cleaned
    assert "aadhaar" not in cleaned
    assert "customer_name" not in cleaned
    assert "phone_number" not in cleaned["details"]
    assert cleaned["predicted_customers"] == 180
    assert cleaned["details"]["comment"] == "Good teller service at counter."
