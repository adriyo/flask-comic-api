from flask import Flask
from app.config import Config
from .api import create_api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    create_api(app)
    return app


app = create_app()
