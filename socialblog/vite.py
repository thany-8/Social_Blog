"""Bridge between Vite's build output and Jinja templates.

After `npm run build` (in ../frontend), Vite writes hashed assets and a manifest
to socialblog/static/dist/. `vite_tags()` reads that manifest and returns the
<link>/<script> tags for the entry chunk. If the bundle hasn't been built, it
returns nothing so the app still runs (just without the React enhancements).
"""
import json
import os

from flask import current_app, url_for
from markupsafe import Markup

_CACHE = {}


def _load_manifest():
    path = os.path.join(current_app.static_folder, "dist", ".vite", "manifest.json")
    if not os.path.exists(path):
        return None
    mtime = os.path.getmtime(path)
    cached = _CACHE.get(path)
    if cached and cached[0] == mtime:
        return cached[1]
    with open(path) as fh:
        data = json.load(fh)
    _CACHE[path] = (mtime, data)
    return data


def vite_tags(entry="src/main.jsx"):
    """Return the HTML tags to load a built Vite entry, or empty markup."""
    manifest = _load_manifest()
    if not manifest or entry not in manifest:
        return Markup("")

    chunk = manifest[entry]
    tags = []
    for css in chunk.get("css", []):
        href = url_for("static", filename=f"dist/{css}")
        tags.append(f'<link rel="stylesheet" href="{href}">')
    src = url_for("static", filename=f"dist/{chunk['file']}")
    tags.append(f'<script type="module" src="{src}"></script>')
    return Markup("\n".join(tags))


def init_app(app):
    """Make vite_tags() available to all templates."""
    app.jinja_env.globals["vite_tags"] = vite_tags
