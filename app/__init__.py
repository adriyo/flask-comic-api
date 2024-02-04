from app.config import app
from app.api import api
from app.api.resources.user import user_ns
from app.api.resources.comic import ns as comic_ns
from app.api.resources.storage import ns as storage_ns
from app.api.resources.chapter import comics_ns


api.init_app(app)
api.add_namespace(user_ns)
api.add_namespace(comic_ns)
api.add_namespace(comics_ns)
api.add_namespace(storage_ns)