from src import db


class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, unique=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(88))
    name = db.Column(db.String(50))
