import os
from flask import Flask
from flask_mail import Mail
import flask_excel as excel
from flask_cors import CORS
from flask_marshmallow import Marshmallow

class Config:
    CMS_API_PREFIX = 'cms-api'
    API_DOC_PREFIX = 'docs'
    UPLOAD_FOLDER = 'storages'
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = os.environ['MAIL_PORT']
    MAIL_USE_SSL = os.environ['MAIL_USE_SSL']
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    NO_IMAGE_URL = 'https://via.placeholder.com/200x200?text=NOT%20FOUND'
    FLASK_ENV = 'development'
    DEBUG = True

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

def create_app():
    app = Flask(__name__)
    CORS(app)
    app_env = f"{os.environ['FLASK_ENV']}"
    app.config.from_object(config_dict[app_env])
    excel.init_excel(app)

    from app.cms_api import cms_api_bp
    app.register_blueprint(cms_api_bp)
    return app

app = create_app()
mail = Mail(app)
ma = Marshmallow(app)