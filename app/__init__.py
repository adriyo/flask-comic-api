from app.config import app
from app.cms_api import cms_api_bp
from app.cms_api.resources.user import user_ns
from app.cms_api.resources.comic.comics import ns as comic_ns
from app.cms_api.resources.comic.chapter import comics_ns as chapter_ns 
from app.cms_api.resources.storage import ns as storage_ns
from app.cms_api.resources.config import api
from app.cms_api.resources.genre import ns as genre_ns 
from app.cms_api.resources.author import ns as author_ns 
from app.cms_api.resources.artist import ns as artist_ns 
from app.cms_api.resources.tag import ns as tag_ns 
from app.cms_api.resources.translators import ns as translator_ns 

api.add_namespace(user_ns)
api.add_namespace(comic_ns)
api.add_namespace(chapter_ns)
api.add_namespace(storage_ns)
api.add_namespace(genre_ns)
api.add_namespace(author_ns)
api.add_namespace(artist_ns)
api.add_namespace(tag_ns)
api.add_namespace(translator_ns)

app.register_blueprint(cms_api_bp)