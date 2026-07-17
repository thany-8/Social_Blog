<div align="center">

# 📝 SocialBlog

### A modern social blogging platform built with Flask

Write, share, and discover stories — complete with user profiles, profile pictures, comments, and likes.

<!-- Replace the badge versions if you upgrade dependencies -->
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-3DA639?style=for-the-badge)

[Features](#-features) • [Security](#-security) • [Demo](#-demo) • [Getting Started](#-getting-started) • [Configuration](#️-configuration) • [Project Structure](#-project-structure) • [Roadmap](#️-roadmap)

<!-- 📌 Replace this banner with your own image saved to docs/screenshots/banner.png -->
<img src="https://placehold.co/1000x300/667eea/ffffff?text=SocialBlog" alt="SocialBlog banner" width="100%" />

</div>

---

## ✨ Overview

**SocialBlog** is a full-featured, multi-user blogging web app. Users can sign up, personalize their profile with an avatar, publish posts, and engage with the community through **comments** and **likes**. It's built with a clean, blueprint-based Flask architecture and a responsive Bootstrap 5 interface.

---

## 🎬 Demo

<div align="center">

<img src="docs/demo.gif" alt="SocialBlog demo — browse the feed, register, log in, upload an avatar, publish a post, like and comment" width="800" />

*Full walkthrough: browse the feed, register, log in, personalize your profile with an avatar, publish a post, then like and comment.*

▶️ **[Watch the full-quality video](docs/socialblog_demo.mp4)**

</div>

---

## 🚀 Features

- 🔐 **Authentication** — register, log in, and log out with securely hashed passwords (Werkzeug)
- 🧑‍🎨 **User profiles** — upload a profile picture that's automatically resized (Pillow); supports JPG, JPEG, PNG, WebP, and GIF
- ✍️ **Blog posts** — full create, read, update, and delete (CRUD), restricted to each post's author
- 💬 **Comments** — any logged-in user can comment; a comment can be removed by its **author or the post owner**
- 🛡️ **Comment & post moderation** — every **post and comment** is screened for toxicity **before it's published** via Google's free [Perspective API](https://perspectiveapi.com/), with an offline fallback so it works with zero setup
- ❤️ **Likes** — one-click **toggle** like/unlike per user, with a live like count
- 📄 **Pagination** — clean, paginated feeds on the home page and user pages
- 🎨 **Modern UI** — responsive Bootstrap 5 design with a styled confirmation modal for deletes
- 🧭 **Custom error pages** — friendly `403` and `404` screens
- 🗃️ **Migrations** — schema managed with Flask-Migrate (Alembic)

---

## 🛠️ Tech Stack

| Layer         | Technology                                              |
| ------------- | ------------------------------------------------------- |
| **Backend**   | Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate     |
| **Forms**     | Flask-WTF, WTForms, email-validator                     |
| **Images**    | Pillow                                                  |
| **Database**  | SQLite (via SQLAlchemy ORM)                             |
| **Frontend**  | Jinja2 templates, Bootstrap 5                           |
| **Auth**      | Werkzeug password hashing, session-based login          |
| **Moderation**| Google Perspective API (with offline keyword fallback)  |

---

## 🔒 Security

Safety is built in at every layer — essential for a multi-user social app:

- 🛡️ **Toxicity moderation** — every post and comment is screened for toxic or abusive language **before it's saved** (see the **Content Moderation** section below).
- 🔑 **Hashed passwords** — credentials are never stored in plain text (Werkzeug password hashing).
- 🛡️ **CSRF protection** — every form is guarded with Flask-WTF CSRF tokens.
- 🔐 **Authorization checks** — only a post's author can edit or delete it, and a comment can be removed only by its author or the post owner (otherwise a `403`).
- 🗝️ **No insecure defaults** — `SECRET_KEY` is **required** (the app refuses to start without it) and secrets load from a git-ignored `.env`, never committed.
- 🧯 **Fails safe** — if the moderation API is unavailable a local screen still runs, and moderation errors never break posting or commenting.

---

## 🛡️ Content Moderation

Posts and comments are screened **before** they're saved, so toxic or abusive
content never reaches the page.

- **Primary engine — [Google Perspective API](https://perspectiveapi.com/):**
  each comment is scored for `TOXICITY`, `SEVERE_TOXICITY`, `INSULT`,
  `PROFANITY`, `THREAT`, and `IDENTITY_ATTACK`. If any score crosses its
  threshold, the comment is rejected with a friendly message.
- **Zero-config fallback:** with no `PERSPECTIVE_API_KEY` set (or if the API is
  unreachable), a lightweight offline keyword screen keeps the app safe by
  default — the feature works the moment you clone the repo.
- **Fails open:** an unexpected moderation error never blocks commenting.

Enable the full API with a free key:

```bash
export PERSPECTIVE_API_KEY="your-key"   # https://developers.perspectiveapi.com
```

Logic lives in [`socialblog/moderation.py`](socialblog/moderation.py); the tests
mock the API so they run offline:

```bash
python -m unittest tests.test_moderation
```

---

## 🏁 Getting Started

### Prerequisites

- Python 3.10 or newer
- `pip` and `venv`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/Social_Blog_Flask.git
cd Social_Blog_Flask

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment (SECRET_KEY is required; auto-loaded from .env)
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste as SECRET_KEY in .env

# 5. Create the database tables
flask --app app.py db upgrade

# 6. Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. 🎉

> 💡 **macOS note:** port `5000` is used by *AirPlay Receiver*. If the server won't start, disable it in **System Settings → General → AirDrop & Handoff → AirPlay Receiver**, or run on another port with `flask --app app.py run --port 5001`.

---

## ⚙️ Configuration

Configuration is read from environment variables. A `.env` file at the project
root is **auto-loaded** on startup (via `python-dotenv`), so the easiest setup is
to copy the template and fill it in:

```bash
cp .env.example .env      # then edit .env
```

| Variable       | Description                                        | Default                          |
| -------------- | -------------------------------------------------- | -------------------------------- |
| `SECRET_KEY`   | Flask secret key used for sessions & CSRF          | **required** (no default)        |
| `DATABASE_URL` | SQLAlchemy database URI                            | `sqlite:///socialblog/data.sqlite` |
| `PERSPECTIVE_API_KEY` | Google Perspective API key that enables toxicity moderation | _offline fallback if unset_ |
| `MODERATION_OFFLINE_FALLBACK` | Set to `0` to disable the offline keyword screen | `1` (enabled) |

Generate a strong secret with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> 🔒 `SECRET_KEY` is required — the app refuses to start without it. Never commit your real `.env`.

---

## 🧭 Pages & Routes

| Method     | Route                        | Description                          |
| ---------- | ---------------------------- | ------------------------------------ |
| `GET`      | `/`                          | Home feed (paginated posts)          |
| `GET`      | `/info`                      | About page                           |
| `GET/POST` | `/register`                  | Create an account                    |
| `GET/POST` | `/login`                     | Log in                               |
| `GET`      | `/logout`                    | Log out                              |
| `GET/POST` | `/account`                   | Edit profile & upload picture        |
| `GET`      | `/<username>`                | A user's posts                       |
| `GET/POST` | `/create`                    | Create a new post                    |
| `GET`      | `/<int:id>`                  | View a post (likes & comments)       |
| `GET/POST` | `/<int:id>/update`           | Edit a post *(author only)*          |
| `POST`     | `/<int:id>/delete`           | Delete a post *(author only)*        |
| `POST`     | `/<int:id>/like`             | Like / unlike a post                 |
| `POST`     | `/<int:id>/comment`          | Add a comment                        |
| `POST`     | `/comment/<int:id>/delete`   | Delete a comment *(author/owner)*    |

---

## 📂 Project Structure

```text
Social_Blog_Flask/
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── migrations/                  # Alembic database migrations
├── docs/screenshots/            # 📸 Put your README images here
└── socialblog/
    ├── __init__.py              # App setup, config & blueprint registration
    ├── models.py                # User, BlogPost, Comment, Like models
    ├── core/                    # Home & info pages
    │   └── views.py
    ├── users/                   # Auth, profiles & picture upload
    │   ├── forms.py
    │   ├── views.py
    │   └── picture_handler.py
    ├── blog_posts/              # Posts, comments & likes
    │   ├── forms.py
    │   └── views.py
    ├── error_pages/             # 403 / 404 handlers
    │   └── handlers.py
    ├── templates/               # Jinja2 templates (Bootstrap 5)
    └── static/profile_pics/     # Uploaded profile images
```

---

## 🗺️ Roadmap

Ideas for future improvements:

- [ ] Edit comments
- [ ] Show who liked a post
- [ ] Tags & categories for posts
- [ ] Search and filtering
- [ ] Rich-text / Markdown post editor
- [ ] Email verification & password reset

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. <!-- Add a LICENSE file to make this official. -->

---

## 👩‍💻 Author

**Tania Tatis**
<!-- Add your links -->
[GitHub](https://github.com/<your-username>) · [LinkedIn](https://www.linkedin.com/in/<your-profile>)

<div align="center">

⭐️ If you like this project, consider giving it a star!

</div>
