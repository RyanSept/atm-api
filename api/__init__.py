from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

rest_api = Api()


def create_app():
    """
    Create app with the specified config

    :return: Flask app object
    """
    app = Flask(__name__)
    app.config["DEBUG"] = True
    # db.init_app(app)
    register_api_resources(rest_api)
    rest_api.init_app(app)

    return app


def register_api_resources(rest_api):
    """
    Register resource endpoints on app

    :param rest_api: flask_restful api object
    :return: None
    """
    from api.views.balance import Balance
    rest_api.add_resource(Balance, "/accounts/balance")
