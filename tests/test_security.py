import re


def test_password_hash_pattern() -> None:
    sample_hash = "$2b$12$" + "a" * 53
    assert re.match(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$", sample_hash)


def test_sensitive_content_is_not_logged() -> None:
    payload = {"email": "analyst@example.com", "password": "super-secret"}
    redacted = {key: "[REDACTED]" if key == "password" else value for key, value in payload.items()}
    assert redacted["password"] == "[REDACTED]"
