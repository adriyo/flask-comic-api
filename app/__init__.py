from app.config import app
from app.cms_api import cms_api_bp
from app.cms_api.resources.user import user_ns
from app.cms_api.resources.comic import ns as comic_ns
from app.cms_api.resources.chapter import comics_ns 
from app.cms_api.resources.storage import ns as storage_ns
from app.cms_api.resources.config import api

api.add_namespace(user_ns)
api.add_namespace(comic_ns)
api.add_namespace(comics_ns)
api.add_namespace(storage_ns)

app.register_blueprint(cms_api_bp)