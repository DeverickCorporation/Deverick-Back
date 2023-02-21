import uuid
from datetime import datetime

import jwt
from flask import Blueprint, abort, current_app, request
from sqlalchemy.exc import IntegrityError, NoResultFound
from werkzeug.security import check_password_hash, generate_password_hash

from ..models import UserAccount

authenticate_routes = Blueprint("auth", __name__, url_prefix="/auth")


@authenticate_routes.route("/register", methods=["POST"])
def signup_user():
    data = request.json

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
    if not "login" in credentials or not "password" in credentials:
        abort(400)

    try:
        user = UserAccount.query.filter_by(login=credentials["login"]).one()
    except NoResultFound:
        return {
            "success": False,
            "message": f"No user: {credentials['login']} found",
        }, 403

    if check_password_hash(user.password, credentials["password"]):
        exp_date = int(datetime.timestamp(datetime.now()))
        jwt_data = {"public_id": user.public_id, "exp_date": exp_date}
        jwt_token = jwt.encode(jwt_data, current_app.config["SECRET_KEY"], "HS256")

        return {"success": True, "token": jwt_token}, 202

    return {"success": False, "message": f"Incorrect password"}, 403
