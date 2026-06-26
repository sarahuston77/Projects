import os

from personalization import build_greeting, load_profile, personalize_message


def test_load_profile_prefers_environment_values(monkeypatch, tmp_path):
    monkeypatch.setenv("HEALTH_APP_USER_NAME", "Mina")
    monkeypatch.setenv("HEALTH_APP_CAREGIVER_NAME", "Ava")
    monkeypatch.setenv("HEALTH_APP_CAREGIVER_RELATION", "daughter")

    profile = load_profile(path=str(tmp_path / "profile.json"))

    assert profile["user_name"] == "Mina"
    assert profile["caregiver_name"] == "Ava"
    assert profile["caregiver_relation"] == "daughter"


def test_personalize_message_uses_the_profile_names():
    profile = {
        "user_name": "Mom",
        "caregiver_name": "Sara",
        "caregiver_relation": "daughter",
    }

    message = personalize_message(
        "{user_name}, {caregiver_name} is thinking of you.",
        profile,
    )

    assert message == "Mom, Sara is thinking of you."


def test_build_greeting_is_kind_and_personal():
    profile = {"user_name": "Mom", "caregiver_name": "Sara", "caregiver_relation": "daughter"}

    greeting = build_greeting(profile)

    assert "Mom" in greeting
    assert "Sara" in greeting
