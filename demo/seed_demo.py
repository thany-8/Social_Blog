"""Seed a throwaway database with lively demo content for the recorded walkthrough.

Run with DATABASE_URL pointing at a disposable sqlite file so the real
socialblog/data.sqlite is never touched, e.g.:

    DATABASE_URL="sqlite:////tmp/socialblog_demo.sqlite" python demo/seed_demo.py
"""
from datetime import datetime, timedelta

from socialblog import app, db
from socialblog.models import BlogPost, Comment, Like, User

# Users created up-front so the feed looks active before we register live.
SEED_USERS = [
    ("maya@demo.test", "maya_rivers", "DemoPass123"),
    ("leo@demo.test", "leo_bennett", "DemoPass123"),
    ("sofia@demo.test", "sofia_chen", "DemoPass123"),
]

# (author_username, title, text)
SEED_POSTS = [
    (
        "maya_rivers",
        "Sunrise over the Dolomites",
        "I hiked three hours in the dark to catch first light on the peaks. "
        "It was freezing, my coffee spilled, and I would do it all again. "
        "The mountains turned from grey to pink to gold in about ten minutes.",
    ),
    (
        "leo_bennett",
        "Why I switched to Flask blueprints",
        "For years I crammed every route into a single file. Blueprints changed "
        "how I think about structure: each feature owns its views, forms, and "
        "templates. The app got easier to reason about almost overnight.",
    ),
    (
        "sofia_chen",
        "A 20-minute weeknight ramen",
        "No 12-hour broth here. Good stock, a jammy egg, charred scallions, and a "
        "spoonful of chili crisp will carry you a long way after a long day.",
    ),
    (
        "maya_rivers",
        "Packing light for two weeks",
        "One carry-on, seven days of clothes, and a laundry sink. The trick isn't "
        "packing less stuff, it's packing stuff that works together.",
    ),
    (
        "leo_bennett",
        "Reading tracebacks without fear",
        "The scariest wall of red text is usually telling you exactly what's wrong "
        "on the very last line. Start at the bottom and work up.",
    ),
]

# (post_title, commenter_username, text)
SEED_COMMENTS = [
    ("Sunrise over the Dolomites", "leo_bennett", "These colours are unreal. Which trail was this?"),
    ("Sunrise over the Dolomites", "sofia_chen", "Adding this to my someday list. Stunning."),
    ("Why I switched to Flask blueprints", "maya_rivers", "This finally made blueprints click for me, thank you!"),
    ("Why I switched to Flask blueprints", "sofia_chen", "Do you split templates per blueprint too?"),
    ("A 20-minute weeknight ramen", "leo_bennett", "Made this tonight. The chili crisp is doing heavy lifting."),
]

# (post_title, liker_username)
SEED_LIKES = [
    ("Sunrise over the Dolomites", "leo_bennett"),
    ("Sunrise over the Dolomites", "sofia_chen"),
    ("Why I switched to Flask blueprints", "maya_rivers"),
    ("Why I switched to Flask blueprints", "sofia_chen"),
    ("A 20-minute weeknight ramen", "maya_rivers"),
    ("A 20-minute weeknight ramen", "leo_bennett"),
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = {}
        for email, username, password in SEED_USERS:
            u = User(email=email, username=username, password=password)
            db.session.add(u)
            users[username] = u
        db.session.commit()

        posts = {}
        base = datetime.utcnow() - timedelta(days=len(SEED_POSTS))
        for i, (author, title, text) in enumerate(SEED_POSTS):
            p = BlogPost(title=title, text=text, user_id=users[author].id)
            p.date = base + timedelta(days=i, hours=i)  # natural chronological order
            db.session.add(p)
            posts[title] = p
        db.session.commit()

        for title, commenter, text in SEED_COMMENTS:
            db.session.add(
                Comment(text=text, user_id=users[commenter].id, blog_post_id=posts[title].id)
            )

        for title, liker in SEED_LIKES:
            db.session.add(Like(user_id=users[liker].id, blog_post_id=posts[title].id))

        db.session.commit()

        print(
            f"Seeded {len(users)} users, {len(posts)} posts, "
            f"{len(SEED_COMMENTS)} comments, {len(SEED_LIKES)} likes "
            f"into {app.config['SQLALCHEMY_DATABASE_URI']}"
        )


if __name__ == "__main__":
    seed()
