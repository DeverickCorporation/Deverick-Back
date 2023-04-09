from typing import Iterable

from src.models import Post, PostLike


def fail_validation(data: dict, required_keys: Iterable, min_len=0):
    for key in required_keys:
        if not key in data:
            return f"No key {key}"
        if len(data[key]) < min_len:
            return f"Min length of {key} is {min_len}"
    return False


def get_all_dicts(rows: list[Post | PostLike]):
    return [row.get_dict() for row in rows]
