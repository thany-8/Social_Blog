"""Comment moderation.

Primary engine: Google's free `Perspective API`, which scores text for
TOXICITY, INSULT, THREAT, PROFANITY, etc. Set an API key to enable it:

    export PERSPECTIVE_API_KEY="your-key-from-google-cloud"

When no key is configured (or the API is unreachable) we fall back to a small
offline keyword screen so the app stays "safe by default" and the feature is
demonstrable without any setup. Both paths fail open on unexpected errors so a
moderation outage never blocks the whole comment system.
"""
import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

PERSPECTIVE_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

# Perspective attributes we request, and the probability (0-1) at or above which
# a comment is flagged for that attribute.
DEFAULT_THRESHOLDS = {
    "TOXICITY": 0.80,
    "SEVERE_TOXICITY": 0.60,
    "INSULT": 0.80,
    "PROFANITY": 0.85,
    "THREAT": 0.70,
    "IDENTITY_ATTACK": 0.70,
}

# Human-readable labels for messages shown to the user.
_LABELS = {
    "TOXICITY": "toxic",
    "SEVERE_TOXICITY": "severely toxic",
    "INSULT": "insulting",
    "PROFANITY": "profane",
    "THREAT": "threatening",
    "IDENTITY_ATTACK": "an identity attack",
    "PROFANITY_OFFLINE": "profane",
}

# Minimal offline safety net used only when the Perspective API is unavailable.
# Perspective is far more accurate; this just catches the obvious cases so the
# feature works with zero configuration.
_OFFLINE_BLOCKLIST = frozenset({
    "fuck", "fucking", "shit", "bitch", "bastard", "asshole",
    "dick", "cunt", "slut", "whore", "retard", "faggot", "nigger",
})
_WORD_RE = re.compile(r"[a-z]+")


class ModerationResult:
    """Outcome of a moderation check."""

    def __init__(self, flagged, scores=None, tripped=None, source="none", error=None):
        self.flagged = flagged
        self.scores = scores or {}
        self.tripped = tripped or []
        self.source = source  # "perspective", "offline", or "none"
        self.error = error

    @property
    def reason(self):
        names = [_LABELS.get(a, a.lower().replace("_", " ")) for a in self.tripped]
        if not names:
            return "inappropriate"
        if len(names) == 1:
            return names[0]
        return ", ".join(names[:-1]) + " and " + names[-1]

    def __repr__(self):
        return (
            f"ModerationResult(flagged={self.flagged}, source={self.source!r}, "
            f"tripped={self.tripped}, error={self.error!r})"
        )


def _config(key, default=None):
    """Read config from the Flask app when available, else the environment."""
    try:
        from flask import current_app

        return current_app.config.get(key, os.environ.get(key, default))
    except (RuntimeError, ImportError):
        return os.environ.get(key, default)


def _offline_check(text):
    tokens = set(_WORD_RE.findall(text.lower()))
    hit = tokens & _OFFLINE_BLOCKLIST
    if hit:
        return ModerationResult(
            flagged=True, tripped=["PROFANITY_OFFLINE"], source="offline"
        )
    return ModerationResult(flagged=False, source="offline")


def _perspective_check(text, api_key):
    thresholds = _config("MODERATION_THRESHOLDS", DEFAULT_THRESHOLDS)
    payload = {
        "comment": {"text": text},
        "languages": ["en"],
        "doNotStore": True,
        "requestedAttributes": {attr: {} for attr in thresholds},
    }
    resp = requests.post(
        PERSPECTIVE_URL, params={"key": api_key}, json=payload, timeout=5
    )
    resp.raise_for_status()
    data = resp.json()

    scores, tripped = {}, []
    attr_scores = data.get("attributeScores", {})
    for attr, threshold in thresholds.items():
        value = attr_scores.get(attr, {}).get("summaryScore", {}).get("value")
        if value is None:
            continue
        scores[attr] = value
        if value >= threshold:
            tripped.append(attr)
    return ModerationResult(
        flagged=bool(tripped), scores=scores, tripped=tripped, source="perspective"
    )


def moderate_comment(text):
    """Return a :class:`ModerationResult` for ``text``.

    Uses the Perspective API when ``PERSPECTIVE_API_KEY`` is set, otherwise a
    small offline keyword screen. Always fails open (``flagged=False``) on
    unexpected errors so moderation never breaks commenting.
    """
    if not text or not text.strip():
        return ModerationResult(flagged=False, source="none")

    api_key = _config("PERSPECTIVE_API_KEY")
    offline_enabled = str(_config("MODERATION_OFFLINE_FALLBACK", "1")).lower() not in (
        "0", "false", "no", "",
    )

    if api_key:
        try:
            return _perspective_check(text, api_key)
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Perspective API request failed (%s); using fallback.", exc)
            if offline_enabled:
                result = _offline_check(text)
                result.error = str(exc)
                return result
            return ModerationResult(flagged=False, source="none", error=str(exc))

    if offline_enabled:
        return _offline_check(text)

    logger.info("No PERSPECTIVE_API_KEY and offline fallback disabled; skipping moderation.")
    return ModerationResult(flagged=False, source="none", error="no_api_key")
