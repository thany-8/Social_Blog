"""Generate avatar assets used by the demo.

Creates two images:
  * socialblog/static/profile_pics/default_profile.png  -- the app-wide default
    avatar (the models reference this filename but it was missing from the repo).
  * demo/assets/demo_avatar.png -- a distinct avatar uploaded during the recorded
    walkthrough so the profile-picture change is visible on camera.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROFILE_PICS = os.path.join(ROOT, "socialblog", "static", "profile_pics")
ASSETS = os.path.join(HERE, "assets")

SIZE = 400  # rendered big then downscaled for smooth edges


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient(size, top, bottom):
    img = Image.new("RGB", (size, size), top)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        draw.line([(0, y), (size, y)], fill=_lerp(top, bottom, y / size))
    return img


def _silhouette(img):
    """Draw a generic white person silhouette centred on the image."""
    draw = ImageDraw.Draw(img)
    s = img.size[0]
    # head
    head_r = int(s * 0.16)
    cx, cy = s // 2, int(s * 0.40)
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill="white")
    # shoulders / body
    bw, bh = int(s * 0.52), int(s * 0.42)
    bx, by = (s - bw) // 2, int(s * 0.60)
    draw.ellipse([bx, by, bx + bw, by + bh + int(s * 0.3)], fill="white")


def _initials(img, text, color):
    draw = ImageDraw.Draw(img)
    s = img.size[0]
    font = None
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ):
        if os.path.exists(candidate):
            try:
                font = ImageFont.truetype(candidate, int(s * 0.42))
                break
            except OSError:
                continue
    if font is None:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((s - tw) / 2 - bbox[0], (s - th) / 2 - bbox[1]), text, font=font, fill=color)


def _circular(img):
    """Return the square image masked to a circle on a transparent background."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, img.size[0], img.size[1]], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def make_default():
    img = _gradient(SIZE, (102, 126, 234), (118, 75, 162))  # brand blue -> purple
    _silhouette(img)
    img = _circular(img).resize((200, 200), Image.LANCZOS)
    os.makedirs(PROFILE_PICS, exist_ok=True)
    path = os.path.join(PROFILE_PICS, "default_profile.png")
    img.save(path)
    return path


def make_demo_avatar():
    img = _gradient(SIZE, (17, 153, 158), (56, 239, 125))  # teal -> green
    _initials(img, "AV", "white")
    img = _circular(img).resize((200, 200), Image.LANCZOS)
    os.makedirs(ASSETS, exist_ok=True)
    path = os.path.join(ASSETS, "demo_avatar.png")
    img.save(path)
    return path


if __name__ == "__main__":
    print("wrote", make_default())
    print("wrote", make_demo_avatar())
