from werkzeug.datastructures import FileStorage

def input_parser():
    from app.cms_api.resources.config import api
    parser = api.parser()
    parser.add_argument('title', required=True, help='chapter title', location='form')
    parser.add_argument('images', required=True, type=FileStorage, location='files', action="append")
    return parser

def update_input_parser():
    from app.cms_api.resources.config import api
    parser = api.parser()
    parser.add_argument('title', required=True, help='chapter title', location='form')
    parser.add_argument('images', required=True, type=FileStorage, location='files', action="append")
    parser.add_argument('image_ids', required=True, type=int, location='form', action="append")
    return parser