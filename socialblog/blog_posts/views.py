from flask import render_template,url_for,flash, redirect,request,Blueprint,abort
from flask_login import current_user,login_required
from socialblog import db
from socialblog.models import BlogPost, Comment, Like
from socialblog.blog_posts.forms import BlogPostForm, CommentForm
from socialblog.moderation import moderate_text

blog_posts = Blueprint('blog_posts',__name__)

@blog_posts.route('/create',methods=['GET','POST'])
@login_required
def create_post():
    form = BlogPostForm()

    if form.validate_on_submit():

        result = moderate_text(f"{form.title.data}\n{form.text.data}")
        if result.flagged:
            flash(
                f"Your post was flagged as {result.reason} and was not published. "
                "Please keep things respectful and try again.",
                "danger",
            )
            return render_template('create_post.html', form=form)

        blog_post = BlogPost(title=form.title.data,
                             text=form.text.data,
                             user_id=current_user.id
                             )
        db.session.add(blog_post)
        db.session.commit()
        flash("Blog Post Created", "success")
        return redirect(url_for('core.index'))

    return render_template('create_post.html',form=form)


# int: makes sure that the blog_post_id gets passed as in integer
# instead of a string so we can look it up later.
@blog_posts.route('/<int:blog_post_id>')
def blog_post(blog_post_id):
    # grab the requested blog post by id number or return 404
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    form = CommentForm()
    return render_template('blog_post.html',title=blog_post.title,
                            date=blog_post.date,post=blog_post,form=form
    )

@blog_posts.route("/<int:blog_post_id>/update", methods=['GET', 'POST'])
@login_required
def update(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        # Forbidden, No Access
        abort(403)

    form = BlogPostForm()
    if form.validate_on_submit():
        result = moderate_text(f"{form.title.data}\n{form.text.data}")
        if result.flagged:
            flash(
                f"Your changes were flagged as {result.reason} and were not saved. "
                "Please keep things respectful and try again.",
                "danger",
            )
            return render_template('create_post.html', title='Update', form=form)
        blog_post.title = form.title.data
        blog_post.text = form.text.data
        db.session.commit()
        flash('Post Updated', "success")
        return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
    # Pass back the old blog post information so they can start again with
    # the old text and title.
    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.text.data = blog_post.text
    return render_template('create_post.html', title='Update',
                           form=form)


@blog_posts.route("/<int:blog_post_id>/delete", methods=['POST'])
@login_required
def delete_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    db.session.delete(blog_post)
    db.session.commit()
    flash('Post has been deleted')
    return redirect(url_for('core.index'))


@blog_posts.route('/<int:blog_post_id>/comment', methods=['POST'])
@login_required
def add_comment(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    form = CommentForm()
    if form.validate_on_submit():
        result = moderate_text(form.text.data)
        if result.flagged:
            flash(
                f"Your comment was flagged as {result.reason} and was not posted. "
                "Please keep things respectful and try again.",
                "danger",
            )
            return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
        comment = Comment(text=form.text.data,
                          user_id=current_user.id,
                          blog_post_id=blog_post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added', 'success')
    return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))


@blog_posts.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # Only the comment author or the post owner may delete a comment.
    if current_user != comment.author and current_user != comment.post.author:
        abort(403)
    post_id = comment.blog_post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted')
    return redirect(url_for('blog_posts.blog_post', blog_post_id=post_id))


@blog_posts.route('/<int:blog_post_id>/like', methods=['POST'])
@login_required
def like_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    like = Like.query.filter_by(user_id=current_user.id,
                                blog_post_id=blog_post.id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=current_user.id, blog_post_id=blog_post.id))
    db.session.commit()
    return redirect(request.referrer or url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
