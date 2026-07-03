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

[Features](#-features) • [Demo](#-demo) • [Getting Started](#-getting-started) • [Configuration](#️-configuration) • [Project Structure](#-project-structure) • [Roadmap](#️-roadmap)

<!-- 📌 Replace this banner with your own image saved to docs/screenshots/banner.png -->
<img src="https://placehold.co/1000x300/667eea/ffffff?text=SocialBlog" alt="SocialBlog banner" width="100%" />

</div>

---

## ✨ Overview

**SocialBlog** is a full-featured, multi-user blogging web app. Users can sign up, personalize their profile with an avatar, publish posts, and engage with the community through **comments** and **likes**. It's built with a clean, blueprint-based Flask architecture and a responsive Bootstrap 5 interface.

---

## 🎬 Demo

> 📌 **These are placeholders.** Take your own screenshots, save them into [`docs/screenshots/`](docs/screenshots/), and swap the image links below (e.g. change the `src` to `docs/screenshots/home.png`).

<table>
  <tr>
    <td width="50%">
      <b>🏠 Home Feed</b><br/>
      <img src="https://placehold.co/600x360/764ba2/ffffff?text=Home+Feed" alt="Home feed" />
    </td>
    <td width="50%">
      <b>📖 Post · Likes &amp; Comments</b><br/>
      <img src="https://placehold.co/600x360/667eea/ffffff?text=Post+%2B+Comments" alt="Post detail" />
    </td>
  </tr>
  <tr>
    <td width="50%">
      <b>🔐 Register / Login</b><br/>
      <img src="https://placehold.co/600x360/667eea/ffffff?text=Register" alt="Register" />
    </td>
    <td width="50%">
      <b>🧑‍🎨 Account &amp; Profile Picture</b><br/>
      <img src="https://placehold.co/600x360/764ba2/ffffff?text=Account" alt="Account" />
    </td>
  </tr>
</table>

---

## 🚀 Features

- 🔐 **Authentication** — register, log in, and log out with securely hashed passwords (Werkzeug)
- 🧑‍🎨 **User profiles** — upload a profile picture that's automatically resized (Pillow); supports JPG, JPEG, PNG, WebP, and GIF
- ✍️ **Blog posts** — full create, read, update, and delete (CRUD), restricted to each post's author
- 💬 **Comments** — any logged-in user can comment; a comment can be removed by its **author or the post owner**
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

# 4. Create the database tables
flask --app app.py db upgrade

# 5. Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. 🎉

> 💡 **macOS note:** port `5000` is used by *AirPlay Receiver*. If the server won't start, disable it in **System Settings → General → AirDrop & Handoff → AirPlay Receiver**, or run on another port with `flask --app app.py run --port 5001`.

---

## ⚙️ Configuration

The app works out of the box, but you can override these via environment variables:

| Variable       | Description                                        | Default                          |
| -------------- | -------------------------------------------------- | -------------------------------- |
| `SECRET_KEY`   | Flask secret key used for sessions & CSRF          | a built-in dev key               |
| `DATABASE_URL` | SQLAlchemy database URI                            | `sqlite:///socialblog/data.sqlite` |

```bash
# Example
export SECRET_KEY="a-long-random-string"
export DATABASE_URL="sqlite:////absolute/path/to/data.sqlite"
```

> 🔒 Always set a strong `SECRET_KEY` in production.

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
