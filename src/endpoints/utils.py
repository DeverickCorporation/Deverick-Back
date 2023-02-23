from typing import Iterable

from src.models import Post, PostLike


def check_user_data(data: dict, required_keys: Iterable):
    for key in required_keys:
        if not key in data:
            return False
    return True


def get_all_dicts(rows: list[Post | PostLike]):
    return [row.get_dict() for row in rows]
