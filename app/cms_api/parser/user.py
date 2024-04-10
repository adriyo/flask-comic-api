from app.cms_api.resources.config import api
from app.config import ma

def register_parser():
    parser = api.parser()
    parser.add_argument('name', required=True, type=str, location='json')
    parser.add_argument('email', required=True, type=str, location='json')
    parser.add_argument('password', required=True, type=str, location='json')
    return parser

def login_parser():
    parser = api.parser()
    parser.add_argument('email', required=True, type=str, location='json')
    parser.add_argument('password', required=True, type=str, location='json')
    return parser

class AuthSchema(ma.Schema):
    email = ma.Email(required=True)
    password = ma.String(required=True)

class RegisterSchema(ma.Schema):
    name = ma.String(required=True)
    email = ma.Email(required=True)
    password = ma.String(required=True)
    
auth_schema = AuthSchema()
register_schema = RegisterSchema()