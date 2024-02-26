from app.config import Config

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

def get_image_url(request, filename):
    if filename:
        return f'{request.headers.get("X-Original-URL")}/{Config.API_PREFIX}/{Config.UPLOAD_FOLDER}/{filename}'
    return Config.NO_IMAGE_URL