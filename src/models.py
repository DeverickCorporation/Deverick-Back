from datetime import datetime

from sqlalchemy.exc import NoResultFound

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

    def has_posts(self) -> bool:
        first_post = Post.query.filter_by(user_account=self).first()
        return bool(first_post)

    def liked_post(self, post_id: int) -> bool:
        try:
            PostLike.query.filter_by(post_id=post_id, user_account=self).one()
            return {"user_like": True}
        except NoResultFound:
            return {"user_like": False}

    def get_likes(self, date_from, date_to):
        posts = Post.query.filter_by(user_account=self).all()
        if not posts:
            return False

        return db.session.query(PostLike).join(Post).filter(Post.user_account == self,Post.creation_time.between(date_from, date_to)).all()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_account_id = db.Column(db.Integer, db.ForeignKey("user_account.id"))
    liked_by = db.relationship("PostLike", backref="post")

    @staticmethod
    def exists_post(post_id: int) -> bool:
        try:
            Post.query.filter_by(id=post_id).one()
            return True
        except NoResultFound:
            return False

    def get_dict(self):
        return {
            "post_id": self.id,
            "post_title": self.title,
            "post_text": self.text,
            "author_name": self.user_account.name,
            "likes_num": PostLike.query.filter_by(post=self).count(),
            "time": int(self.creation_time.timestamp()),
        }


class PostLike(db.Model):
    __tablename__ = "post_like"
    __table_args__ = (db.UniqueConstraint("user_account_id", "post_id"),)

    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_account_id = db.Column(db.Integer, db.ForeignKey("user_account.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    def get_dict(self):
        return {
            "like_id": self.id,
            "post_id": self.post.id,
            "post_name": self.post.title,
            "person_name": self.user_account.name,
            "time": int(self.creation_time.timestamp()),
        }
