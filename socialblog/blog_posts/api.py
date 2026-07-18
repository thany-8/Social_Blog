from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required, current_user
from socialblog import db
from socialblog.models import BlogPost, Comment, Like
from socialblog.moderation import moderate_text

api_posts = Blueprint("api_posts", __name__)


@api_posts.route("/api/moderate", methods=["POST"])
@login_required
def moderate():
    """Score arbitrary text for toxicity (used by the live preview widget)."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"flagged": False, "reason": None, "source": "none"})

    result = moderate_text(text)
    return jsonify({
        "flagged": result.flagged,
        "reason": result.reason if result.flagged else None,
        "tripped": result.tripped,
        "source": result.source,
    })


@api_posts.route("/api/posts/<int:post_id>/like", methods=["POST"])
@login_required
def like_toggle(post_id):
    """Toggle the current user's like and return the new state and count."""
    post = BlogPost.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, blog_post_id=post.id).first()
    if like:
        db.session.delete(like)
        liked = False
    else:
        db.session.add(Like(user_id=current_user.id, blog_post_id=post.id))
        liked = True
    db.session.commit()
    return jsonify({"liked": liked, "count": len(post.likes)})


@api_posts.route("/api/posts/<int:post_id>/comments", methods=["POST"])
@login_required
def add_comment_api(post_id):
    """Add a comment after moderation; return the rendered comment as JSON."""
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Comment cannot be empty."}), 400

    result = moderate_text(text)
    if result.flagged:
        return jsonify({
            "ok": False,
            "flagged": True,
            "error": f"Your comment was flagged as {result.reason} and was not posted.",
        }), 422

    comment = Comment(text=text, user_id=current_user.id, blog_post_id=post.id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "ok": True,
        "comment": {
            "id": comment.id,
            "text": comment.text,
            "author": current_user.username,
            "author_url": url_for("users.user_posts", username=current_user.username),
            "date": comment.date.strftime("%Y-%m-%d %H:%M"),
            "can_delete": True,
            "delete_url": url_for("blog_posts.delete_comment", comment_id=comment.id),
        },
        "count": len(post.comments),
    }), 201

@api_posts.route("/api/posts", methods=["GET"])
def get_posts():
    posts = BlogPost.query.all()

    return jsonify([
        {
            "id": post.id,
            "title": post.title,
            "text": post.text,
            "user_id": post.user_id
        }
        for post in posts
    ])


@api_posts.route("/api/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    return jsonify({
        "id": post.id,
        "title": post.title,
        "text": post.text,
        "user_id": post.user_id
    })


@api_posts.route("/api/posts", methods=["POST"])
@login_required
def create_post():
    data = request.get_json()

    post = BlogPost(
        title=data["title"],
        text=data["text"],
        user_id=current_user.id
    )

    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created", "id": post.id}), 201


@api_posts.route("/api/posts/<int:post_id>", methods=["PUT"])
@login_required
def update_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        return jsonify({"error": "You cannot edit this post"}), 403

    data = request.get_json()

    post.title = data.get("title", post.title)
    post.text = data.get("text", post.text)

    db.session.commit()

    return jsonify({"message": "Post updated"})


@api_posts.route("/api/posts/<int:post_id>", methods=["DELETE"])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        return jsonify({"error": "You cannot delete this post"}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted"})