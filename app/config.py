import os
from flask import Flask
import psycopg2
from flask_mail import Mail


class Config:
    API_PREFIX = 'api'
    API_DOC_PREFIX = 'docs'
    UPLOAD_FOLDER = 'storages'
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = os.environ['MAIL_PORT']
    MAIL_USE_SSL = os.environ['MAIL_USE_SSL']
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    NO_IMAGE_URL = 'https://via.placeholder.com/200x200?text=NOT%20FOUND'


class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ['POSTGRES_HOST_DB'],
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])

    def get_connection(self):
        return self.conn

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)