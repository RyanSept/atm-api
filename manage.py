from flask_script import Manager
from api import create_app, db
from config import load_config

app = create_app(load_config())
manager = Manager(app)


@manager.command
def init_app():
    """
    Initialise the app
    """
    db.create_all()


if __name__ == '__main__':
    manager.run()
