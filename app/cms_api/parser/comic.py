from werkzeug.datastructures import FileStorage
from app.cms_api.resources.config import api

def input_parser():
    parser = api.parser()
    parser.add_argument('title', required=True, help='comic title', location='form')
    parser.add_argument('alternative_title', help='alternative title', location='form')
    parser.add_argument('authors', action='append', type=int, help='comic authors id', location='form')
    parser.add_argument('artists', action='append', type=int, help='comic artists id', location='form')
    parser.add_argument('tags', action='append', type=int, help='comic tags id', location='form')
    parser.add_argument('translators', action='append', type=int, help='comic translators id', location='form')
    parser.add_argument('genres', action='append', type=int, help='comic genres id', location='form')
    parser.add_argument('published_date', location='form', type=str)
    parser.add_argument('status', location='form', type=int)
    parser.add_argument('type', location='form', type=int)
    parser.add_argument('description', required=True, help='fill the description', location='form')
    parser.add_argument('image_cover', type=FileStorage, location='files')
    parser.add_argument('new_authors', action='append', type=str, help='new comic authors name', location='form')
    parser.add_argument('new_artists', action='append', type=str, help='new comic artists name', location='form')
    parser.add_argument('new_tags', action='append', type=str, help='new comic tags', location='form')
    parser.add_argument('new_translators', action='append', type=str, help='new comic translators', location='form')
    parser.add_argument('new_genres', action='append', type=str, help='new comic genres', location='form')
    return parser