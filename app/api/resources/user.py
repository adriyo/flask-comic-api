from flask import jsonify, make_response
from flask_restx import Resource, Namespace
from app.config import DBManager
from ..models import userRegisterParser, userLoginParser
import bcrypt
import base64
ns = Namespace("api")

connection = DBManager().get_connection()

@ns.route("/register")
class RegisterAPI(Resource):
    @ns.expect(userRegisterParser)
    def post(self):
        args = userRegisterParser.parse_args()
        name = args['name']
        email = args['email']
        password = args['password']

        password_bytes = password.encode('utf-8')
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                existing_user = cursor.fetchone()
        if existing_user:
            return make_response(jsonify({'message': 'user already exists'}), 401)

        hashed_pwd = (bcrypt.hashpw(password_bytes,
                      bcrypt.gensalt())).decode('utf-8')

        with connection:
            with connection.cursor() as cursor:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(
                    query, (name, email, hashed_pwd))
        string_token = base64.b64encode(
            f"{email}:{hashed_pwd}".encode('ascii')).decode('utf-8')
        result = {
            'message': 'User registered successfully',
            'data': {'name': name, 'email': email, 'token': string_token}
        }

        return make_response(jsonify(result), 201)


@ns.route("/login")
class LoginAPI(Resource):
    @ns.expect(userLoginParser)
    def post(self):
        args = userLoginParser.parse_args()
        email = args['email']
        password = args['password']

        password_bytes = password.encode('utf-8')
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT name, password FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                existing_user = cursor.fetchone()

        if not existing_user:
            return make_response(jsonify({'message': 'user not exists'}), 400)

        existing_password = existing_user[1].encode('utf-8')
        if not bcrypt.checkpw(password_bytes, existing_password):
            return make_response(jsonify({'message': 'invalid password'}), 400)

        string_token = base64.b64encode(
            f"{email}:{existing_user[1]}".encode('ascii')).decode('utf-8')
        result = {
            'message': 'Success',
            'data': {'name': existing_user[0], 'email': email, 'token': string_token}
        }

        return make_response(jsonify(result), 201)
