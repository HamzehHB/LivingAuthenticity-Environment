from src.living_authenticity.security import (
    SECRET_PATTERNS,
    contains_machine_specific_path,
    contains_secret,
    find_secrets,
)


def test_clean_text_has_no_secrets():
    assert contains_secret("plain research note") is False
    assert find_secrets("plain research note") == ()


def test_github_token_prefix_is_detected_by_label():
    fake = "ghp_" + "a" * 36

    assert contains_secret(fake) is True
    assert find_secrets(fake) == ("ghp_",)


def test_private_key_header_is_detected():
    text = "-----BEGIN RSA PRIVATE KEY-----"

    assert find_secrets(text) == ("BEGIN RSA PRIVATE KEY",)


def test_detection_reports_only_known_labels():
    fake = "AKIA" + "B" * 16

    matches = find_secrets(fake)

    assert matches == ("AKIA",)
    assert set(matches) <= set(SECRET_PATTERNS)


def test_machine_specific_path_detection():
    assert contains_machine_specific_path(
        "root = F:/LivingAuthenticity_Data"
    ) is True
    assert contains_machine_specific_path(
        "root = C:/LivingAuthenticity_Data"
    ) is False
