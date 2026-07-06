from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from socialblog import db
from socialblog.models import BlogPost

api_posts = Blueprint("api_posts", __name__)

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