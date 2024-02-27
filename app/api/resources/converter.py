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

def get_image_cover_url(request, filename, user_id, comic_id):
    if not filename:
        return Config.NO_IMAGE_URL
    return f'{request.headers.get("X-Original-URL")}/{Config.API_PREFIX}/{Config.UPLOAD_FOLDER}/{user_id}/{comic_id}/{filename}'

def get_chapter_image_url(request, filename, user_id, comic_id, chapter_id):
    if not filename:
        return Config.NO_IMAGE_URL
    return f'{request.headers.get("X-Original-URL")}/{Config.API_PREFIX}/{Config.UPLOAD_FOLDER}/{user_id}/{comic_id}/{chapter_id}/{filename}'