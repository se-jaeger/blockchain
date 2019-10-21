from flask import Flask
from src.routes import blueprint


def create_ui():
    """
    Construct the core application.
    """

    app = Flask(__name__)

    # register blueprint
    app.register_blueprint(blueprint)

    # config goes here, like:
    # app.config['SOME_CONFIG'] = 0815

    return app
