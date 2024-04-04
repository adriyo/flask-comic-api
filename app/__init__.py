from app.config import app
from app.cms_api import cms_api_bp
from app.cms_api.resources.user import user_ns
from app.cms_api.resources.comic.comics import ns as comic_ns
from app.cms_api.resources.comic.chapter import comics_ns as chapter_ns 
from app.cms_api.resources.storage import ns as storage_ns
from app.cms_api.resources.config import api
from app.cms_api.resources.comic.form_options import ns as comic_options

api.add_namespace(user_ns)
api.add_namespace(comic_ns)
api.add_namespace(chapter_ns)
api.add_namespace(storage_ns)
api.add_namespace(comic_options)

app.register_blueprint(cms_api_bp)