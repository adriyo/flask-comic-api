import os

from flask import request
from app.config import Config
from datetime import datetime

def parse_published_date(published_date):
    if not published_date:
        return None
    try:
        if '-' in published_date:
            return datetime.strptime(published_date, "%Y-%m-%d").date()
        return datetime.strptime(published_date, "%d/%m/%Y").date()
    except ValueError as e:
        return None
    
def get_config_env(config):
    return config['FLASK_ENV']

def get_comic_type(type):
    comic_types = {
        0: {'id': 0, 'name': 'manga',},
        1: {'id': 1, 'name': 'manhwa',},
        2: {'id': 2, 'name': 'manhua',},
        3: {'id': 3, 'name': 'webtoon',},
    }
    return comic_types.get(type, {'id': type, 'name': 'Unknown'})

def get_comic_status(type):
    comic_status = {
        0: {'id': 0, 'name': 'ongoing',},
        1: {'id': 1, 'name': 'completed',},
        2: {'id': 2, 'name': 'hiatus',},
    }
    return comic_status.get(type, {'id': type, 'name': 'Unknown'})

def get_host_url(config) -> str:
    if get_config_env(config) == 'development':
        return f'{request.url_root}'
    return f"{request.headers.get('X-Original-URL')}/"

def get_image_cover_url(config, filename, user_id, comic_id):
    if not filename:
        return Config.NO_IMAGE_URL
    return f'{get_host_url(config)}{Config.CMS_API_PREFIX}/{Config.UPLOAD_FOLDER}/{user_id}/{comic_id}/{filename}'

def get_chapter_image_url(config, filename, user_id, comic_id, chapter_id):
    if not filename:
        return Config.NO_IMAGE_URL
    return f'{get_host_url(config)}{Config.CMS_API_PREFIX}/{Config.UPLOAD_FOLDER}/{user_id}/{comic_id}/{chapter_id}/{filename}'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename) -> bool:
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
