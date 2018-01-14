from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
import logging


db = SQLAlchemy()

rest_api = Api()


def create_app(config):
    """
    Create app with the specified config

    :param config: config file object
    :return: Flask app object
    """
    app = Flask(__name__)
    app.config.from_object(config)
    # app.config["DEBUG"] = True
    db.init_app(app)
    register_api_resources(rest_api)
    rest_api.init_app(app)
    setup_logging(app)
    CORS(app)

    return app


def register_api_resources(rest_api):
    """
    Register resource endpoints on app

    :param rest_api: flask_restful api object
    :return: None
    """
    from api.views.balance import Balance
    rest_api.add_resource(Balance, "/accounts/balance")

    from api.views.register import Register
    rest_api.add_resource(Register, "/accounts/create")

    from api.views.deposit import Deposit
    rest_api.add_resource(Deposit, "/accounts/deposit")

    from api.views.login import Login
    rest_api.add_resource(Login, "/accounts/login")

    from api.views.withdraw import Withdraw
    rest_api.add_resource(Withdraw, "/accounts/withdraw")


def setup_logging(app):
    """
    Set up app logger
    """
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler(
        'atm_api.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(app.config["LOG_LEVEL"])
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
