from flask import Blueprint


authenticate_routes = Blueprint("auth", __name__, url_prefix="/auth")
