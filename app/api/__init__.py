from .resources.comic import ns as comic_ns
from .resources.chapter import ns as chapter_ns
from ..extensions import api


def create_api(app):
    api.add_namespace(comic_ns)
    api.add_namespace(chapter_ns)
    api.init_app(app)
