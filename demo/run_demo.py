"""Orchestrate the full demo-video build.

Steps:
  1. Point the app at a throwaway sqlite DB (the real data.sqlite is untouched).
  2. Ensure avatar assets exist and seed lively demo content.
  3. Launch the Flask app on a free port and wait for it to answer.
  4. Run the Playwright walkthrough, recording a .webm.
  5. Convert to .mp4 with ffmpeg when available.
  6. Tear the server down and clean up demo-only uploaded avatars.

Usage:
    python demo/run_demo.py
"""
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
# Make both the repo root (socialblog, app) and this folder importable.
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

PORT = int(os.environ.get("DEMO_PORT", "5077"))
BASE_URL = f"http://127.0.0.1:{PORT}"
DB_PATH = pathlib.Path(os.environ.get("DEMO_DB", "/tmp/socialblog_demo.sqlite"))
OUTPUT_DIR = HERE / "output"
PROFILE_PICS = ROOT / "socialblog" / "static" / "profile_pics"

# Configure the environment BEFORE importing anything from the app package.
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ.setdefault("SECRET_KEY", "demo-secret-key")
os.environ["BASE_URL"] = BASE_URL
os.environ["OUTPUT_DIR"] = str(OUTPUT_DIR)


def wait_for_server(url, timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def convert_to_mp4(webm):
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found; keeping .webm only")
        return None
    mp4 = webm.with_suffix(".mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(webm),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(mp4),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and mp4.exists():
        return mp4
    print("ffmpeg conversion failed:\n" + result.stderr[-800:])
    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    # 1 + 2. Build assets and seed the throwaway database (in-process).
    import make_assets

    make_assets.make_default()
    make_assets.make_demo_avatar()

    import seed_demo

    seed_demo.seed()

    # Snapshot existing avatars so we can remove any uploaded during the demo.
    before = set(os.listdir(PROFILE_PICS)) if PROFILE_PICS.exists() else set()

    # 3. Start the Flask app in a subprocess.
    log = open(OUTPUT_DIR / "server.log", "w")
    server = subprocess.Popen(
        [sys.executable, "-c",
         f"import app; app.app.run(port={PORT}, debug=False, use_reloader=False)"],
        cwd=str(ROOT), env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT,
    )
    webm = None
    try:
        if not wait_for_server(BASE_URL, timeout=25):
            log.flush()
            raise RuntimeError(
                "Flask server did not start. Log tail:\n"
                + (OUTPUT_DIR / "server.log").read_text()[-1000:]
            )
        print(f"Server up at {BASE_URL}")

        # 4. Record the walkthrough.
        from record_demo import run as record

        webm = record()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
        log.close()
        # Remove avatars uploaded during the walkthrough (keep the repo clean).
        if PROFILE_PICS.exists():
            for name in set(os.listdir(PROFILE_PICS)) - before:
                try:
                    (PROFILE_PICS / name).unlink()
                except OSError:
                    pass

    # 5. Convert to mp4.
    mp4 = convert_to_mp4(webm)
    print("\n=== Demo build complete ===")
    print(f"WebM: {webm}  ({webm.stat().st_size // 1024} KB)")
    if mp4:
        print(f"MP4 : {mp4}  ({mp4.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
