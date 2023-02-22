from datetime import datetime

import jwt
from flask import Blueprint, current_app, request, abort
from jwt.exceptions import DecodeError, InvalidSignatureError
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import Post, UserAccount, PostLike

user_routes = Blueprint("user", __name__)


@user_routes.before_request
def before_request():
    if not "jwt-token" in request.headers:
        current_app.logger.info(f"{request.remote_addr} requested without token")
        return {"success": False, "message": "No token"}, 403

    jwt_token = request.headers["jwt-token"]

    try:
        jwt_token = jwt.decode(jwt_token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except (InvalidSignatureError, DecodeError):
        current_app.logger.info(f"{request.remote_addr} requested with invalid token")
        return {"success": False, "message": "Token is invalid"}, 403

    if datetime.utcfromtimestamp(jwt_token["exp_time"]) < datetime.utcnow():
        current_app.logger.info(f"{request.remote_addr} requested with expired token")
        return {"success": False, "message": "Token is expired"}, 403


def add_current_user(route_func):
    def wrapper(*args, **kwargs):
        public_id = jwt.decode(
            request.headers["jwt-token"],
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )["public_id"]

        try:
            current_user = UserAccount.query.filter_by(public_id=public_id).one()
        except NoResultFound:
            current_app.logger.error(f"User wasn't fount {current_user.login}")
            return {"success": False, "message": f"No user found"}, 403
        result = route_func(current_user=current_user, *args, **kwargs)
        return result

    wrapper.__name__ = route_func.__name__
    return wrapper


def is_post_exists(post_id):
    try:
        Post.query.filter_by(id=post_id).one()
        return True
    except NoResultFound:
        current_app.logger.error(f"Post {post_id} doesn't exist")
        return False


@user_routes.route("/check_auth")
def verificate():
    return {"success": True, "message": "Token is valid"}, 202


@user_routes.route("/create_post", methods=["POST"])
@add_current_user
def create_post(current_user):
    data = request.json
    new_post = Post(title=data["title"], text=data["text"], user_account=current_user)
    current_app.db.session.add(new_post)

    try:
        current_app.db.session.commit()
    except IntegrityError:
        current_app.logger.error(f"Can't save post for {current_user.login}")
        abort(400)

    current_app.logger.info(f"User: {current_user.name} wrote a post")
    return {"success": True, "message": "Post saved"}, 201


@user_routes.route("/like_post", methods=["POST"])
@add_current_user
def like_post(current_user):
    post_id = request.json["post_id"]
    if not is_post_exists(post_id):
        return {"success": False, "message": f"Post {post_id} doesn't exist"}, 400

    new_like = PostLike(user_account=current_user, post_id=post_id)
    current_app.db.session.add(new_like)

    try:
        current_app.db.session.commit()
    except IntegrityError:
        return {"success": False, "message": "You have already liked this post"}, 400

    current_app.logger.info(f"User: {current_user.name} liked a post {post_id}")
    return {"success": True, "message": "Post liked"}, 202


@user_routes.route("/unlike_post", methods=["POST"])
@add_current_user
def unlike_post(current_user):
    post_id = request.json["post_id"]
    if not is_post_exists(post_id):
        return {"success": False, "message": f"Post {post_id} doesn't exist"}, 400

    try:
        like = PostLike.query.filter_by(user_account=current_user, post_id=post_id).one()
        current_app.db.session.delete(like)
        current_app.db.session.commit()
    except NoResultFound:
        current_app.logger.error(f"User {current_user.login} didn't like post {post_id} yet")
        return {"success": False, "message": "You didn't like this post yet"}, 400

    current_app.logger.info(f"User: {current_user.name} unliked a post {post_id}")
    return {"success": True, "message": "Post unliked"}, 202
