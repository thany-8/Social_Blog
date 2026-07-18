from socialblog import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    profile_image = db.Column(db.String(20),nullable=False,default='default_profile.png')
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.Text)

    posts = db.relationship('BlogPost', backref='author', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Username {self.username}"


class BlogPost(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)

    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    title = db.Column(db.String(140),nullable=False)
    text = db.Column(db.Text,nullable=False)

    def __init__(self,title,text,user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return f"Post ID: {self.id} -- Date: {self.date} -- {self.title}"

    def is_liked_by(self, user):
        if not getattr(user, 'is_authenticated', False):
            return False
        return any(like.user_id == user.id for like in self.likes)


class Comment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)

    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('BlogPost', backref=db.backref('comments', lazy=True,
                           order_by='Comment.date', cascade='all, delete-orphan'))

    def __init__(self, text, user_id, blog_post_id):
        self.text = text
        self.user_id = user_id
        self.blog_post_id = blog_post_id

    def __repr__(self):
        return f"Comment {self.id} on Post {self.blog_post_id} by user {self.user_id}"


class Like(db.Model):

    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'blog_post_id', name='uq_user_post_like'),)

    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    post = db.relationship('BlogPost', backref=db.backref('likes', lazy=True,
                           cascade='all, delete-orphan'))

    def __init__(self, user_id, blog_post_id):
        self.user_id = user_id
        self.blog_post_id = blog_post_id
