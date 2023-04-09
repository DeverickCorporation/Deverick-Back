import secrets
from datetime import timedelta

from environs import Env
from flask import Config

env = Env()
env.read_env(override=True)


class CustomConfig(Config):
    def load_config(self):
        with env.prefixed("FLASK_"):
            self["SECRET_KEY"] = "1111" #secrets.token_hex(env.int("SECRET_KEY_BYTES"))
            self["SQLALCHEMY_TRACK_MODIFICATIONS"] = env.bool("SQLALCHEMY_TRACK_MODIFICATIONS")

        self["SQLALCHEMY_DATABASE_URI"] = self.load_db_conf()
        self["JWT_LIFETIME"] = timedelta(minutes=env.int("JWT_LIFETIME"))
        self["DOCS_LINK"] = env.str("DOCS_LINK")
        self["USER_MIN_DATA_LEN"] = env.int("USER_MIN_DATA_LEN")

    @staticmethod
    def load_db_conf():
        if uri := env.str("SQLALCHEMY_DATABASE_URI", default=None):
            return uri

        with env.prefixed("DB_"):
            credentials = [
                env.str("USER"),
                env.str("PASSWORD"),
                env.str("HOST"),
                env.int("PORT"),
                env.str("NAME"),
            ]
            return "postgresql+psycopg2://{}:{}@{}:{}/{}".format(*credentials)
