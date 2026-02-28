import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


database = SQLAlchemy()


def create_app(config_overrides=None):
    application = Flask(__name__)

    database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "glenigan.db")
    application.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config_overrides:
        application.config.update(config_overrides)

    database.init_app(application)

    from application.routes import api

    application.register_blueprint(api)

    return application
