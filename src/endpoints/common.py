from flask import Blueprint

common_routes = Blueprint("common", __name__)


@common_routes.route("/favicon.ico")
def favicon():
    return {"favicon": False}


@common_routes.app_errorhandler(401)
def handle_401(error):
    print(error)
    return {"success": False, "msg": "Sign in firstly, unauthorized"}, 401


@common_routes.app_errorhandler(403)
def handle_403(error):
    print(error)
    return {"success": False, "msg": "Forbidden"}, 403


@common_routes.app_errorhandler(404)
def handle_404(error):
    print(error)
    return {"success": False, "msg": "Page doesn't exist"}, 404
