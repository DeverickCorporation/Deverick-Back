from datetime import datetime
from functools import wraps

import jwt
from flask import Blueprint, Response, abort, current_app, request
from jwt.exceptions import DecodeError, InvalidSignatureError
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.models import Post, PostLike, UserAccount

from .utils import fail_validation, get_all_dicts

user_routes = Blueprint("user", __name__)


@user_routes.before_request
def before_request():
    if request.method == "OPTIONS":
        return {}, 200

    if not "jwt-token" in request.headers:
        current_app.logger.info(f"{request.remote_addr} requested without token")
        return {"success": False, "verefication": "Failed", "message": "No token"}, 403

    jwt_token = request.headers["jwt-token"]

    try:
        jwt_token = jwt.decode(jwt_token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except (InvalidSignatureError, DecodeError):
        current_app.logger.info(f"{request.remote_addr} requested with invalid token")
        return {
            "success": False,
            "verefication": "Failed",
            "message": "Token is invalid",
        }, 403

    if datetime.utcfromtimestamp(jwt_token["exp_time"]) < datetime.utcnow():
        current_app.logger.info(f"{request.remote_addr} requested with expired token")
        return {
            "success": False,
            "verefication": "Failed",
            "message": "Token is expired",
        }, 403


def add_current_user(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        public_id = jwt.decode(
            request.headers["jwt-token"],
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )["public_id"]

        try:
            current_user = UserAccount.query.filter_by(public_id=public_id).one()
        except NoResultFound:
            current_app.logger.error("User wasn't found")
            return False

        request.current_user = current_user
        return route_func(current_user=current_user, *args, **kwargs)

    return wrapper


@user_routes.route("/check_auth")
def verify():
    return {"success": True, "message": "Token is valid"}, 202


@user_routes.route("/create_post", methods=["POST"])
@add_current_user
def create_post(current_user):
    data = request.json
    if resp := fail_validation(data, ["title", "text"], 5):
        return {"success": False, "message": resp}, 400

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
    if not Post.exists_post(post_id):
        current_app.logger.error(f"Post {post_id} doesn't exist")
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
    if not Post.exists_post(post_id):
        current_app.logger.error(f"Post {post_id} doesn't exist")
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


@user_routes.route("/analitics")
@add_current_user
def like_analitics(current_user):
    try:
        date_from = datetime.strptime(request.args["date_from"], "%Y-%m-%d")
        date_to = datetime.strptime(request.args["date_to"], "%Y-%m-%d")
    except ValueError:
        return {
            "success": False,
            "message": "args example: ?date_from=2020-02-02&date_to=2020-02-15",
        }, 400
    if not current_user.has_posts():
        current_app.logger.error(f"User {current_user.login} hasn't posts")
        return {"success": False, "message": "You haven'n posts"}, 409

    likes = current_user.get_likes(date_from, date_to)
    return {
        "success": True,
        "message": "your likes",
        "likes_num": len(likes),
        "likes_dict": get_all_dicts(likes),
    }, 200


@user_routes.route("/my_activity")
@add_current_user
def my_activity(current_user):
    request.ignore_update_time = True
    return {
        "success": True,
        "last_login": current_user.last_login_time.strftime("%d/%m/%Y, %H:%M:%S"),
        "last_request": current_user.last_request_time.strftime("%d/%m/%Y, %H:%M:%S"),
    }, 200


@user_routes.route("/posts")
@add_current_user
def get_posts(current_user):
    data = request.args

    if fail_validation(data, ["limit"]) or not data["limit"].isdigit():
        abort(400)

    if "start_from" in data:
        if not data["start_from"].isdigit():
            return {"success": False, "message": "Incorrect start_from "}
        posts = (
            Post.query.filter(Post.id <= int(data["start_from"]))
            .order_by(desc(Post.creation_time))
            .limit(data["limit"])
            .all()
        )
    else:
        posts = Post.query.order_by(desc(Post.creation_time)).limit(data["limit"]).all()

    posts_dicts = get_all_dicts(posts)

    # add current user like info
    [post.update(current_user.liked_post(post["post_id"])) for post in posts_dicts]

    return {
        "success": True,
        "message": "posts",
        "posts_num": len(posts),
        "posts_dict": posts_dicts,
    }, 200


@user_routes.after_request
def after_request(response: Response):
    current_app.db.session.rollback()

    if user := getattr(request, "current_user", False):
        if getattr(request, "ignore_update_time", False):
            return response

        user.last_request_time = datetime.utcnow()
        current_app.db.session.commit()
        current_app.logger.debug(f"User {user.login} Last request time updated")

    return response
