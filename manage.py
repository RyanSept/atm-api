from flask_script import Manager
from api import create_app, db
from api.models.account import Account
from api.models.transaction import Transaction
from api.config import load_config
from binascii import hexlify

import os

app = create_app(load_config())
manager = Manager(app)


@manager.command
def init_app():
    """
    Initialise the app
    """
    db.create_all()


@manager.command
def generate_secret_key():
    """
    Generate random 1024 bit long hex for use as app secret
    """
    return "SECRET_KEY: " + hexlify(os.urandom(64)).decode("utf-8")


if __name__ == '__main__':
    manager.run()
