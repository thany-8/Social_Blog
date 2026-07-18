#!/usr/bin/env bash
# One-time setup for a GitHub Codespace: install dependencies, create a local
# SECRET_KEY, and seed lively demo content so the app is ready to use.
set -euo pipefail

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  echo "==> Creating .env with a generated SECRET_KEY..."
  {
    echo "# Auto-generated for this Codespace (git-ignored)"
    python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
    echo "MODERATION_OFFLINE_FALLBACK=1"
  } > .env
fi

echo "==> Seeding demo content (users, posts, comments, likes)..."
PYTHONPATH=. python demo/seed_demo.py

echo "==> Done! The app starts automatically — open the forwarded port 5000."
