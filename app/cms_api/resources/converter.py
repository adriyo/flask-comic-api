import os

from flask import request
from app.config import Config
from datetime import datetime

def parse_published_date(published_date):
    try:
        if '-' in published_date:
            return datetime.strptime(published_date, "%Y-%m-%d").date()
        return datetime.strptime(published_date, "%d/%m/%Y").date()
    except ValueError as e:
        return None

def get_comic_type(type):
    comic_types = {
        0: 'manga',
        1: 'manhwa',
        2: 'manhua',
    }
    return comic_types.get(type, 'Unknown')

def get_comic_status(type):
    comic_status = {
        0: 'ongoing',
        1: 'completed',
        2: 'hiatus',
    }
    return comic_status.get(type, 'Unknown')
def get_host_url() -> str:
    if os.environ['FLASK_ENV'] == 'development':
        return f'{request.url_root}'
    return f'{request.headers.get('X-Original-URL')}/'

def get_image_cover_url(filename, user_id, comic_id):
    if not filename:
        return Config.NO_IMAGE_URL
    return f'{get_host_url()}{Config.CMS_API_PREFIX}/{Config.UPLOAD_FOLDER}/{user_id}/{comic_id}/{filename}'

def get_chapter_image_url(filename, user_id, comic_id, chapter_id):
    if not filename:
        return Config.NO_IMAGE_URL
    return f'{get_host_url()}{Config.CMS_API_PREFIX}/{Config.UPLOAD_FOLDER}/{user_id}/{comic_id}/{chapter_id}/{filename}'