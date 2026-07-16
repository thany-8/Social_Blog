"""Record an automated walkthrough of SocialBlog as a video.

Assumes the app is already running (see run_demo.py, which orchestrates the DB
seeding, server startup, this recording, and mp4 conversion).

Environment variables:
    BASE_URL    default http://127.0.0.1:5055
    OUTPUT_DIR  where the raw .webm is written (default demo/output)
"""
import os
import pathlib

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5055").rstrip("/")
OUTPUT_DIR = pathlib.Path(os.environ.get("OUTPUT_DIR", pathlib.Path(__file__).parent / "output"))
ASSETS = pathlib.Path(__file__).parent / "assets"
VIEWPORT = {"width": 1280, "height": 720}

# Live demo account created during the walkthrough.
EMAIL = "alex@example.com"
USERNAME = "alex_dev"
PASSWORD = "DemoPass123"

# Injected once per document: an animated cursor, click ripples, a caption bar
# and full-screen title/outro cards. Re-usable across navigations because it is
# registered with add_init_script.
INIT_SCRIPT = r"""
window.__demo = (function () {
  function ensure() {
    if (document.getElementById('__demo_style')) return;
    const style = document.createElement('style');
    style.id = '__demo_style';
    style.textContent = `
      #__demo_cursor{position:fixed;width:22px;height:22px;border-radius:50%;
        background:rgba(56,239,125,.35);border:2px solid #38ef7d;z-index:2147483647;
        left:0;top:0;transform:translate(-50%,-50%);pointer-events:none;
        transition:left .55s cubic-bezier(.22,1,.36,1),top .55s cubic-bezier(.22,1,.36,1);
        box-shadow:0 2px 8px rgba(0,0,0,.35);}
      #__demo_ripple{position:fixed;width:14px;height:14px;border-radius:50%;
        border:2px solid #38ef7d;z-index:2147483646;pointer-events:none;opacity:0;
        transform:translate(-50%,-50%) scale(1);}
      #__demo_ripple.go{animation:__demo_r .6s ease-out;}
      @keyframes __demo_r{from{opacity:.9;transform:translate(-50%,-50%) scale(1);}
        to{opacity:0;transform:translate(-50%,-50%) scale(4);}}
      #__demo_caption{position:fixed;left:28px;bottom:28px;max-width:520px;
        background:rgba(17,20,28,.86);color:#fff;padding:16px 20px;border-radius:14px;
        font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
        z-index:2147483645;box-shadow:0 10px 30px rgba(0,0,0,.35);pointer-events:none;
        border-left:4px solid #38ef7d;opacity:0;transition:opacity .3s;}
      #__demo_caption .t{font-size:20px;font-weight:700;line-height:1.25;}
      #__demo_caption .s{font-size:15px;opacity:.85;margin-top:4px;}
      #__demo_card{position:fixed;inset:0;z-index:2147483644;display:flex;
        flex-direction:column;align-items:center;justify-content:center;color:#fff;
        text-align:center;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
        background:linear-gradient(135deg,#667eea,#764ba2);opacity:0;transition:opacity .5s;
        pointer-events:none;}
      #__demo_card .b{font-size:64px;font-weight:800;letter-spacing:-1px;}
      #__demo_card .sub{font-size:24px;opacity:.9;margin-top:10px;}
    `;
    document.documentElement.appendChild(style);

    const cursor = document.createElement('div');
    cursor.id = '__demo_cursor';
    document.documentElement.appendChild(cursor);
    const ripple = document.createElement('div');
    ripple.id = '__demo_ripple';
    document.documentElement.appendChild(ripple);
  }
  function point(x, y) {
    ensure();
    const c = document.getElementById('__demo_cursor');
    c.style.left = x + 'px'; c.style.top = y + 'px';
  }
  function ripple() {
    ensure();
    const c = document.getElementById('__demo_cursor');
    const r = document.getElementById('__demo_ripple');
    r.style.left = c.style.left; r.style.top = c.style.top;
    r.classList.remove('go'); void r.offsetWidth; r.classList.add('go');
  }
  function caption(t, s) {
    ensure();
    let el = document.getElementById('__demo_caption');
    if (!el) { el = document.createElement('div'); el.id = '__demo_caption';
      document.documentElement.appendChild(el); }
    el.innerHTML = '<div class="t"></div>' + (s ? '<div class="s"></div>' : '');
    el.querySelector('.t').textContent = t;
    if (s) el.querySelector('.s').textContent = s;
    requestAnimationFrame(() => { el.style.opacity = 1; });
  }
  function clearCaption() {
    const el = document.getElementById('__demo_caption');
    if (el) el.style.opacity = 0;
  }
  function card(b, sub) {
    let el = document.getElementById('__demo_card');
    if (!el) { el = document.createElement('div'); el.id = '__demo_card';
      document.documentElement.appendChild(el); }
    el.innerHTML = '<div class="b"></div><div class="sub"></div>';
    el.querySelector('.b').textContent = b;
    el.querySelector('.sub').textContent = sub || '';
    requestAnimationFrame(() => { el.style.opacity = 1; });
  }
  function clearCard() {
    const el = document.getElementById('__demo_card');
    if (el) el.style.opacity = 0;
  }
  return { ensure, point, ripple, caption, clearCaption, card, clearCard };
})();
"""


class Demo:
    def __init__(self, page):
        self.page = page

    def caption(self, title, sub="", hold=1500):
        self.page.evaluate("([t,s]) => window.__demo.caption(t,s)", [title, sub])
        self.page.wait_for_timeout(hold)

    def card(self, big, sub="", hold=2600):
        self.page.evaluate("([b,s]) => window.__demo.card(b,s)", [big, sub])
        self.page.wait_for_timeout(hold)

    def clear_card(self):
        self.page.evaluate("() => window.__demo.clearCard()")
        self.page.wait_for_timeout(500)

    def _center(self, locator):
        locator.scroll_into_view_if_needed()
        self.page.wait_for_timeout(250)
        box = locator.bounding_box()
        return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

    def move_to(self, locator):
        x, y = self._center(locator)
        self.page.evaluate("([x,y]) => window.__demo.point(x,y)", [x, y])
        self.page.wait_for_timeout(650)

    def click(self, locator):
        self.move_to(locator)
        self.page.evaluate("() => window.__demo.ripple()")
        self.page.wait_for_timeout(180)
        locator.click()

    def type(self, locator, text, delay=45):
        self.move_to(locator)
        locator.click()
        locator.type(text, delay=delay)
        self.page.wait_for_timeout(300)

    def goto(self, path):
        self.page.goto(BASE_URL + path)
        self.page.wait_for_load_state("networkidle")


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=60)
        context = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(OUTPUT_DIR),
            record_video_size=VIEWPORT,
            device_scale_factor=1,
        )
        context.add_init_script(INIT_SCRIPT)
        page = context.new_page()
        page.set_default_timeout(15000)
        d = Demo(page)

        # --- Intro ---------------------------------------------------------
        d.goto("/")
        d.card("SocialBlog", "A social blogging platform built with Flask", hold=2800)
        d.clear_card()

        # --- Home feed -----------------------------------------------------
        d.caption("The home feed", "Latest posts from the whole community", hold=1800)
        page.mouse.wheel(0, 350)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, 350)
        page.wait_for_timeout(1200)
        page.evaluate("() => window.scrollTo({top:0,behavior:'smooth'})")
        page.wait_for_timeout(900)

        # --- Read a post ---------------------------------------------------
        d.caption("Open any post to read the full story", hold=1500)
        d.click(page.locator(".card-title a").first)
        page.wait_for_load_state("networkidle")
        d.caption("Every post has likes and comments", hold=1600)
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(1400)

        # --- Register ------------------------------------------------------
        d.goto("/")
        d.caption("Let's join — create an account", hold=1400)
        d.click(page.locator("ul.nav").get_by_role("link", name="Register"))
        page.wait_for_load_state("networkidle")
        d.caption("Register", "Sign up with an email, username and password", hold=1200)
        d.type(page.locator("#email"), EMAIL)
        d.type(page.locator("#username"), USERNAME)
        d.type(page.locator("#password"), PASSWORD, delay=30)
        d.type(page.locator("#pass_confirm"), PASSWORD, delay=30)
        d.click(page.get_by_role("button", name="Register!"))
        page.wait_for_url("**/login")
        page.wait_for_load_state("networkidle")

        # --- Login ---------------------------------------------------------
        d.caption("Log in with your new account", hold=1300)
        d.type(page.locator("#email"), EMAIL)
        d.type(page.locator("#password"), PASSWORD, delay=30)
        d.click(page.get_by_role("button", name="Log In"))
        page.wait_for_load_state("networkidle")
        page.locator("ul.nav").get_by_role("link", name="Log Out").wait_for()

        # --- Account & avatar ---------------------------------------------
        d.caption("Personalize your profile", hold=1300)
        d.click(page.locator("ul.nav").get_by_role("link", name="Account"))
        page.wait_for_load_state("networkidle")
        d.caption("Upload a profile picture", "It's automatically resized with Pillow", hold=1600)
        page.set_input_files("#picture", str(ASSETS / "demo_avatar.png"))
        page.wait_for_timeout(600)
        d.click(page.get_by_role("button", name="Update", exact=True))
        page.wait_for_load_state("networkidle")
        d.caption("Your new avatar is live", hold=1600)
        page.wait_for_timeout(600)

        # --- Create a post -------------------------------------------------
        d.caption("Write and publish a post", hold=1300)
        d.click(page.locator("ul.nav").get_by_role("link", name="Create Post"))
        page.wait_for_load_state("networkidle")
        d.type(page.locator("#title"), "My first post on SocialBlog")
        d.type(
            page.locator("#text"),
            "Just joined and I'm already hooked. Clean, fast, and it has "
            "everything a small community needs: profiles, likes and comments.",
            delay=12,
        )
        d.click(page.get_by_role("button", name="BlogPost"))
        page.wait_for_load_state("networkidle")

        # --- Like & comment ------------------------------------------------
        d.caption("Your post is live at the top of the feed", hold=1500)
        d.click(page.locator(".card-title a").first)
        page.wait_for_load_state("networkidle")
        d.caption("Like a post with one click", hold=1300)
        d.click(page.locator("form[action*='/like'] button[type=submit]"))
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(900)
        d.caption("Join the conversation with comments", hold=1300)
        d.type(page.locator("#text"), "Excited to be here! 👋", delay=35)
        d.click(page.get_by_role("button", name="Post Comment"))
        page.wait_for_load_state("networkidle")
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(1600)

        # --- User page -----------------------------------------------------
        d.caption("Every user gets their own page", hold=1400)
        d.click(page.get_by_role("link", name=USERNAME).first)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1400)

        # --- Log out & outro ----------------------------------------------
        d.click(page.locator("ul.nav").get_by_role("link", name="Log Out"))
        page.wait_for_load_state("networkidle")
        d.card("Thanks for watching", "SocialBlog · Flask · Bootstrap 5", hold=3000)

        # Finalize the recording.
        page.wait_for_timeout(400)
        video = page.video
        context.close()
        browser.close()
        raw_path = pathlib.Path(video.path())
        final = OUTPUT_DIR / "socialblog_demo.webm"
        if final.exists():
            final.unlink()
        raw_path.rename(final)
        print(f"Recorded {final}")
        return final


if __name__ == "__main__":
    run()
