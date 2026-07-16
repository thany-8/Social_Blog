# SocialBlog — automated demo video

This folder builds a narrated screen-recording of SocialBlog automatically with
[Playwright](https://playwright.dev/python/). It seeds a throwaway database,
drives a real browser through the main features (register, log in, avatar
upload, create post, like, comment, browse a profile, log out) with an animated
cursor and on-screen captions, and records the session to video.

## Output

- `output/socialblog_demo.webm` — raw Playwright recording
- `output/socialblog_demo.mp4` — H.264 version (if `ffmpeg` is installed)

Both are ~80 seconds at 1280×720. The `output/` folder is git-ignored.

## Requirements

```bash
source .venv/bin/activate
pip install playwright
python -m playwright install chromium
# ffmpeg is optional, used only for the .mp4 conversion
```

## Build the video

```bash
python demo/run_demo.py
```

That single command:

1. points the app at a disposable sqlite DB (`/tmp/socialblog_demo.sqlite`) so
   the real `socialblog/data.sqlite` is never touched;
2. regenerates avatar assets and seeds demo users/posts/comments/likes;
3. starts the Flask app on port `5077` (override with `DEMO_PORT`);
4. records the walkthrough and writes the video to `output/`;
5. converts to `.mp4` and cleans up the avatar uploaded during the demo.

## Files

| File             | Purpose                                                        |
| ---------------- | ------------------------------------------------------------- |
| `run_demo.py`    | Orchestrates seeding, server startup, recording, conversion.  |
| `record_demo.py` | The Playwright walkthrough (cursor, captions, title cards).   |
| `seed_demo.py`   | Populates the throwaway DB with lively demo content.          |
| `make_assets.py` | Generates `default_profile.png` and the demo upload avatar.   |
| `assets/`        | Generated images used by the walkthrough.                     |

## Customising

- Edit the caption text and step order in `record_demo.py` (`run()`).
- Edit the seeded users/posts in `seed_demo.py`.
- Change resolution via `VIEWPORT` in `record_demo.py`.
