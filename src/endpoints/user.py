from datetime import datetime

import jwt
from flask import Blueprint, current_app, request, abort, g, Response
from jwt.exceptions import DecodeError, InvalidSignatureError
from sqlalchemy.exc import IntegrityError, NoResultFound

from ..models import Post, UserAccount, PostLike

user_routes = Blueprint("user", __name__)


@user_routes.before_request
def before_request():
    if not "jwt-token" in request.headers:
        current_app.logger.info(f"{request.remote_addr} requested without token")
        return {"success": False, "verefication": "Failed", "message": "No token"}, 403

    jwt_token = request.headers["jwt-token"]

    try:
        jwt_token = jwt.decode(jwt_token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except (InvalidSignatureError, DecodeError):
        current_app.logger.info(f"{request.remote_addr} requested with invalid token")
        return {"success": False, "verefication": "Failed", "message": "Token is invalid"}, 403

    if datetime.utcfromtimestamp(jwt_token["exp_time"]) < datetime.utcnow():
        current_app.logger.info(f"{request.remote_addr} requested with expired token")
        return {"success": False, "verefication": "Failed", "message": "Token is expired"}, 403


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
            current_app.logger.error(f"User wasn't fount")
            return False

        g.current_user = current_user
        return route_func(current_user=current_user, *args, **kwargs)

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


@user_routes.route("/analitics")
@add_current_user
def like_analitics(current_user):
    print(request.args)

    try:
        date_from = datetime.strptime(request.args["date_from"], "%Y-%m-%d")
        date_to = datetime.strptime(request.args["date_to"], "%Y-%m-%d")
    except ValueError:
        return {"success": False, "message": "args example: ?date_from=2020-02-02&date_to=2020-02-15"}, 400

    posts = Post.query.filter_by(user_account=current_user).all()
    if not posts:
        current_app.logger.error(f"User {current_user.login} hasn't posts")
        return {"success": False, "message": "You haven'n posts"}, 409
    print(posts)
    
    likes_2d = [get_post_likes(post,date_from,date_to) for post in posts]
    likes = [lk for lks in likes_2d for lk in lks]

    print(likes)

    return {"success": True, "message": len(likes)}, 200

def get_post_likes(post:Post,date_from,date_to):
    try:
        return PostLike.query.filter_by(post=post).filter(PostLike.creation_time >= date_from).filter(PostLike.creation_time <= date_to).all()
    except NoResultFound:
        return []


@user_routes.route("/my_activity")
@add_current_user
def my_activity(current_user):
    g.update_request_time = False
    return {
        "success": True,
        "last_login": current_user.last_login_time.strftime("%d/%m/%Y, %H:%M:%S"),
        "last_request": current_user.last_request_time.strftime("%d/%m/%Y, %H:%M:%S"),
    }, 202


@user_routes.after_request
def after_request(response: Response):
    current_app.db.session.rollback()

    if (user := g.get("current_user")):

        if g.get("update_request_time") == False:
            return response

        user.last_request_time = datetime.utcnow()
        current_app.db.session.commit()
        current_app.logger.debug(f"User {user.login} Last request time updated")

    return response
