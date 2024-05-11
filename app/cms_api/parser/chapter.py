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
    parser.add_argument('title', help='chapter title', location='form')
    parser.add_argument('images', type=FileStorage, location='files', action="append")
    parser.add_argument('deleted_image_ids', type=int, location='form', action="append")
    return parser