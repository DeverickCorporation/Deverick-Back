from .authenticate import authenticate_routes
from .common import common_routes
from .user import user_routes

all_routes = [authenticate_routes, user_routes, common_routes]
