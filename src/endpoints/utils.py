from typing import Iterable

from sqlalchemy.exc import NoResultFound

from src.models import Post, PostLike


def check_user_data(data: dict, required_keys: Iterable):
    for key in required_keys:
        if not key in data:
            return False
    return True


def get_post_likes(post: Post, date_from, date_to):
    try:
        return (
            PostLike.query.filter_by(post=post)
            .filter(PostLike.creation_time >= date_from)
            .filter(PostLike.creation_time <= date_to)
            .all()
        )
    except NoResultFound:
        return []


def get_likes_dict(likes: list[PostLike]):
    return [
        {
            "post_name": like.post.title,
            "person_name": like.user_account.name,
            "time": str(like.creation_time),
        }
        for like in likes
    ]

def get_post_dict(posts: list[Post]):
    return [
        {
            "post_title": post.title,
            "post_text": post.text,
            "author_name": post.user_account.name,
            "likes_num": PostLike.query.filter_by(post=post).count(),
            "time": str(post.creation_time),
        }
        for post in posts
    ]

def post_exists(post_id) -> bool:
    try:
        Post.query.filter_by(id=post_id).one()
        return True
    except NoResultFound:
        return False
