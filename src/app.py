import logging
import logging.config

import yaml
from flask import Flask
from flask_cors import CORS

from src.config import CustomConfig


def init_logger(app):
    with open("./logger.yaml", "r") as stream:
        loggers_config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(loggers_config)
    app.logger = logging.getLogger(name="verificator")


def init_app():
    Flask.config_class = CustomConfig
    app = Flask(__name__)
    CORS(app)

    app.config.load_config()
    init_logger(app)

    app.logger.info("app inited")
    print(8)
    return app
