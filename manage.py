from flask_script import Manager
from api import create_app, db

app = create_app()
manager = Manager(app)


@manager.command
def init_app():
    """
    Initialise the app
    """
    db.create_all()


if __name__ == '__main__':
    manager.run()
