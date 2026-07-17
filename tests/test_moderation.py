"""Tests for comment moderation.

All network access is mocked, so these run without a Perspective API key:

    python -m unittest tests.test_moderation
"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requests

# The app requires SECRET_KEY and reads DATABASE_URL at import time.
os.environ.setdefault("SECRET_KEY", "test-secret")
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".sqlite")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"

from socialblog import app, db  # noqa: E402
from socialblog.models import BlogPost, Comment, User  # noqa: E402
from socialblog.moderation import ModerationResult, moderate_comment  # noqa: E402


def _perspective_response(scores):
    """Build a fake Perspective API response with the given attribute scores."""
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {
        "attributeScores": {
            attr: {"summaryScore": {"value": value, "type": "PROBABILITY"}}
            for attr, value in scores.items()
        }
    }
    return resp


class ModerationEngineTests(unittest.TestCase):
    """Unit tests for moderate_comment() across its code paths."""

    def setUp(self):
        os.environ.pop("PERSPECTIVE_API_KEY", None)

    def test_offline_fallback_blocks_profanity(self):
        result = moderate_comment("you are a piece of shit")
        self.assertTrue(result.flagged)
        self.assertEqual(result.source, "offline")

    def test_offline_fallback_allows_clean_text(self):
        result = moderate_comment("what a lovely and thoughtful post")
        self.assertFalse(result.flagged)
        self.assertEqual(result.source, "offline")

    def test_empty_text_is_not_flagged(self):
        self.assertFalse(moderate_comment("   ").flagged)

    @patch("socialblog.moderation.requests.post")
    def test_perspective_flags_toxic(self, mock_post):
        mock_post.return_value = _perspective_response({"TOXICITY": 0.97, "INSULT": 0.9})
        with patch.dict(os.environ, {"PERSPECTIVE_API_KEY": "test-key"}):
            result = moderate_comment("horrible toxic garbage")
        self.assertTrue(result.flagged)
        self.assertEqual(result.source, "perspective")
        self.assertIn("TOXICITY", result.tripped)

    @patch("socialblog.moderation.requests.post")
    def test_perspective_allows_clean(self, mock_post):
        mock_post.return_value = _perspective_response({"TOXICITY": 0.03, "INSULT": 0.01})
        with patch.dict(os.environ, {"PERSPECTIVE_API_KEY": "test-key"}):
            result = moderate_comment("great write-up, thanks for sharing!")
        self.assertFalse(result.flagged)
        self.assertEqual(result.source, "perspective")

    @patch("socialblog.moderation.requests.post",
           side_effect=requests.exceptions.ConnectionError("boom"))
    def test_perspective_error_falls_back_to_offline(self, mock_post):
        with patch.dict(os.environ, {"PERSPECTIVE_API_KEY": "test-key"}):
            result = moderate_comment("totally clean comment")
        self.assertFalse(result.flagged)  # offline screen says clean
        self.assertEqual(result.source, "offline")
        self.assertIsNotNone(result.error)

    def test_reason_is_human_readable(self):
        result = ModerationResult(flagged=True, tripped=["TOXICITY", "INSULT"])
        self.assertEqual(result.reason, "toxic and insulting")


class AddCommentModerationTests(unittest.TestCase):
    """Integration tests for the /<id>/comment route."""

    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

        self.user = User(email="commenter@example.com", username="commenter", password="pw")
        db.session.add(self.user)
        db.session.commit()
        self.post = BlogPost(title="Hello", text="A body", user_id=self.user.id)
        db.session.add(self.post)
        db.session.commit()

        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.user.id)
            sess["_fresh"] = True

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    @patch("socialblog.blog_posts.views.moderate_comment")
    def test_flagged_comment_is_blocked(self, mock_mod):
        mock_mod.return_value = ModerationResult(
            flagged=True, tripped=["TOXICITY"], source="perspective"
        )
        resp = self.client.post(
            f"/{self.post.id}/comment", data={"text": "something nasty"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.query.count(), 0)
        self.assertIn(b"was not posted", resp.data)

    @patch("socialblog.blog_posts.views.moderate_comment")
    def test_clean_comment_is_saved(self, mock_mod):
        mock_mod.return_value = ModerationResult(flagged=False, source="perspective")
        resp = self.client.post(
            f"/{self.post.id}/comment", data={"text": "great post!"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.query.count(), 1)
        self.assertEqual(Comment.query.first().text, "great post!")

    def test_offline_fallback_blocks_end_to_end(self):
        """With no API key, the real offline screen should block profanity."""
        os.environ.pop("PERSPECTIVE_API_KEY", None)
        resp = self.client.post(
            f"/{self.post.id}/comment", data={"text": "this is shit"},
            follow_redirects=True,
        )
        self.assertEqual(Comment.query.count(), 0)
        self.assertIn(b"was not posted", resp.data)


if __name__ == "__main__":
    unittest.main()
