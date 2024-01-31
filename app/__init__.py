from flask import Flask
from .api import create_api


def create_app():
    app = Flask(__name__)
    create_api(app)
    return app


app = create_app()
