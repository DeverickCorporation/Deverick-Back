from .authenticate import authenticate_routes
from .common import common_routes


all_routes = [authenticate_routes, common_routes]
