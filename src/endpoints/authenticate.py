import uuid
from datetime import datetime

import jwt
from flask import Blueprint, abort, current_app, request
from sqlalchemy.exc import IntegrityError, NoResultFound
from werkzeug.security import check_password_hash, generate_password_hash

from ..models import UserAccount
from .utils import check_user_data

authenticate_routes = Blueprint("auth", __name__, url_prefix="/auth")


@authenticate_routes.route("/registration", methods=["POST"])
def signup_user():
    data = request.json
    if not check_user_data(data, ["login", "password", "name"]):
        abort(400)

    new_user = UserAccount(
        public_id=str(uuid.uuid1()),
        login=data["login"],
        password=generate_password_hash(data["password"], method="sha256"),
        name=data["name"],
    )
    current_app.db.session.add(new_user)

    try:
        current_app.db.session.commit()
    except IntegrityError:
        return {
            "success": False,
            "message": f"Username:\"{data['login']}\" is arleady taken",
        }, 409

    current_app.logger.info(f"New user created: {data['login']}")
    return {"success": True, "message": "Registration successful"}, 201


@authenticate_routes.route("/login", methods=["POST"])
def signin_user():
    credentials = request.json
    if not check_user_data(credentials, ["login", "password"]):
        abort(400)

    try:
        user = UserAccount.query.filter_by(login=credentials["login"]).one()
    except NoResultFound:
        return {
            "success": False,
            "message": f"No user: {credentials['login']} found",
        }, 403

    if not check_password_hash(user.password, credentials["password"]):
        return {"success": False, "message": "Incorrect password"}, 403

    exp_time = int(
        datetime.timestamp(datetime.now() + current_app.config["JWT_LIFETIME"])
    )
    jwt_data = {"public_id": user.public_id, "name": user.name, "exp_time": exp_time}
    jwt_token = jwt.encode(jwt_data, current_app.config["SECRET_KEY"], "HS256")

    user.last_login_time = datetime.utcnow()
    current_app.db.session.commit()

    current_app.logger.info(f"New token created for {user.login} exp_time: {exp_time}")
    return {"success": True, "token": jwt_token}, 202
