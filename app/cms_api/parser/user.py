from app.cms_api.resources.config import api

def register_parser():
    parser = api.parser()
    parser.add_argument('name', required=True, type=str)
    parser.add_argument('email', required=True, type=str)
    parser.add_argument('password', required=True, type=str)
    return parser

def login_parser():
    parser = api.parser()
    parser.add_argument('email', required=True, type=str)
    parser.add_argument('password', required=True, type=str)
    return parser