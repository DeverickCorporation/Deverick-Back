from typing import Iterable


def check_user_data(data: dict, required_keys: Iterable):
    for key in required_keys:
        if not key in data:
            return False
    return True
