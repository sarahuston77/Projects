import json
import os


DEFAULT_PROFILE = {
    "user_name": "Mom",
    "caregiver_name": "Sara",
    "caregiver_relation": "daughter",
}


def _env_key(key):
    return {
        "user_name": "HEALTH_APP_USER_NAME",
        "caregiver_name": "HEALTH_APP_CAREGIVER_NAME",
        "caregiver_relation": "HEALTH_APP_CAREGIVER_RELATION",
    }.get(key)


def load_profile(path=None):
    profile = dict(DEFAULT_PROFILE)

    if path:
        try:
            with open(path, encoding="utf-8") as handle:
                loaded = json.load(handle)
                if isinstance(loaded, dict):
                    profile.update({k: v for k, v in loaded.items() if v})
        except (OSError, ValueError, TypeError):
            pass

    for key, value in list(profile.items()):
        env_name = _env_key(key)
        if env_name and os.environ.get(env_name):
            profile[key] = os.environ[env_name]

    return profile


def personalize_message(template, profile=None):
    profile = profile or load_profile()
    return template.format_map(profile)


def build_greeting(profile=None):
    profile = profile or load_profile()
    caregiver_name = profile.get("caregiver_name") or "your loved one"
    caregiver_relation = profile.get("caregiver_relation") or "caregiver"
    user_name = profile.get("user_name") or "friend"

    if caregiver_name and caregiver_relation:
        return f"Hi {user_name} — {caregiver_name}, your {caregiver_relation}, is thinking of you today."
    return f"Hi {user_name} — you are cared for today."
