from datetime import datetime

from src import db


class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, unique=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(88))
    name = db.Column(db.String(50))
    last_login_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_request_time = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("Post", backref="user_account")
    like = db.relationship("PostLike", backref="user_account")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_account_id = db.Column(db.Integer, db.ForeignKey("user_account.id"))
    liked_by = db.relationship("PostLike", backref="post")


class PostLike(db.Model):
    __tablename__ = 'post_like'
    __table_args__ = (db.UniqueConstraint('user_account_id', 'post_id'), )

    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_account_id = db.Column(db.Integer, db.ForeignKey("user_account.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
