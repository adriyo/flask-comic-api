from .resources.comic import ns as comic_ns
from .resources.chapter import ns as chapter_ns
from .resources.user import ns as user_ns
from .resources.storage import ns as storages_ns
from ..extensions import api


def create_api(app):
    api.add_namespace(comic_ns)
    api.add_namespace(chapter_ns)
    api.add_namespace(user_ns)
    api.add_namespace(storages_ns)
    api.init_app(app)
