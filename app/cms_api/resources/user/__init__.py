from flask import make_response, request, jsonify
from flask_restx import Namespace, Resource
from app.cms_api.parser import user
from .service import UserService
from marshmallow import ValidationError

user_ns = Namespace('user', description="user api")

register_parser = user.register_parser()
login_parser = user.login_parser()

user_service = UserService()

@user_ns.route("/register")
class RegisterAPI(Resource):

    @user_ns.expect(register_parser)
    def post(self):
        try:
            request_json = request.json
            request_data = user.register_schema.load(request_json)
        except ValidationError as err:
            return make_response(jsonify({'result': err.messages}), 400)
        
        success, data = user_service.register(request_data)

        if success:
            return make_response(data, 201)
        return make_response(data, 400)
        

@user_ns.route("/login")
class LoginAPI(Resource):
    @user_ns.expect(login_parser)
    def post(self):
        try:
            request_json = request.json
            request_data = user.auth_schema.load(request_json)
        except ValidationError as err:
            return make_response(jsonify({'result': err.messages}), 400)

        success, data = user_service.login(request_data)
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