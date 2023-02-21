import jwt
from flask import Blueprint, current_app, request
from jwt.exceptions import DecodeError, InvalidSignatureError

user_routes = Blueprint("user", __name__)


@user_routes.before_request
def before_request():
    if not "jwt-token" in request.headers:
        current_app.logger.info(f"{request.remote_addr} requested without token")
        return {"success": False, "message": "No token"}, 403

    jwt_token = request.headers["jwt-token"]

    try:
        jwt_token = jwt.decode(
            jwt_token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        print(jwt_token)
    except (InvalidSignatureError, DecodeError):
        current_app.logger.info(f"{request.remote_addr} requested with invalid token")
        return {"success": False, "message": "Token is invalid"}, 403


@user_routes.route("/check_auth")
def verificate():
    return {"success": True, "message": "Token is valid"}, 202
