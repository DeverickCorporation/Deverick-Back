import secrets
from datetime import timedelta

from environs import Env
from flask import Config

env = Env()
env.read_env(override=True)


class CustomConfig(Config):
    def load_config(self):
        with env.prefixed("FLASK_"):
            self["PERMANENT_SESSION_LIFETIME"] = timedelta(
                minutes=env.int("PERMANENT_SESSION_LIFETIME")
            )
            self[
                "SECRET_KEY"
            ] = "1234"  # secrets.token_hex(env.int("SECRET_KEY_BYTES"))
            self["SQLALCHEMY_TRACK_MODIFICATIONS"] = env.bool(
                "SQLALCHEMY_TRACK_MODIFICATIONS"
            )

        self["SQLALCHEMY_DATABASE_URI"] = env.str(
            "SQLALCHEMY_DATABASE_URI", default=self.load_db_conf()
        )
        self["JWT_LIFETIME"] = timedelta(minutes=env.int("JWT_LIFETIME"))

    @staticmethod
    def load_db_conf():
        with env.prefixed("DB_"):
            credentials = [
                env.str("USER"),
                env.str("PASSWORD"),
                env.str("HOST"),
                env.int("PORT"),
                env.str("NAME"),
            ]
            return "postgresql+psycopg2://{}:{}@{}:{}/{}".format(*credentials)
