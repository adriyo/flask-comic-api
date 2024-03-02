from flask import make_response
from flask_restx import Namespace, Resource
from app.cms_api.parser import user
from .service import UserService

user_ns = Namespace('user', description="user api")

register_parser = user.register_parser()
login_parser = user.login_parser()

user_service = UserService()

@user_ns.route("/register")
class RegisterAPI(Resource):

    @user_ns.expect(register_parser)
    def post(self):
        args = register_parser.parse_args()
        success, data = user_service.register(args)
        if success:
            return make_response(data, 201)
        return make_response(data, 400)
        

@user_ns.route("/login")
class LoginAPI(Resource):
    @user_ns.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()
        success, data = user_service.login(args)
        if success:
            return make_response(data, 200)
        return make_response(data, 400)


@user_ns.route("/confirm/<token>")
class UserConfirmAPI(Resource):

    @user_ns.header('Content-Type', 'text/html')
    def get(self, token):
        success, data = user_service.confirm(token)
        if success:
            return make_response(data, 200)
        return make_response(data, 400)