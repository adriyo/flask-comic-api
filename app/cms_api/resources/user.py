import os
from flask import jsonify, make_response, render_template
from flask_restx import Namespace, Resource
from app.cms_api.resources.converter import get_host_url, get_config_env
from app.config import Config, DBManager, mail, app
from app.cms_api.parser import user
import bcrypt
import base64
from flask_mail import Message

user_ns = Namespace('user', description="user api")

connection = DBManager().get_connection()

register_parser = user.register_parser()
login_parser = user.login_parser()

@user_ns.route("/register")
class RegisterAPI(Resource):

    @user_ns.expect(register_parser)
    def post(self):
        args = register_parser.parse_args()
        name = args['name']
        email = args['email']
        password = args['password']

        password_bytes = password.encode('utf-8')
 
        try:            
            with connection:
                with connection.cursor() as cursor:
                    query = "SELECT id FROM users WHERE email = %s"
                    cursor.execute(query, (email,))
                    existing_user = cursor.fetchone()
                    if existing_user:
                        return make_response(jsonify({'message': 'user already exists'}), 401)

                    hashed_pwd = (bcrypt.hashpw(password_bytes, bcrypt.gensalt())).decode('utf-8')

                    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                    cursor.execute(query, (name, email, hashed_pwd))
                    string_token = base64.b64encode(
                        f"{email}:{hashed_pwd}".encode('ascii')).decode('utf-8')
                    
                    result = None
                    confirm_url = f'{get_host_url(app.config)}{Config.CMS_API_PREFIX}/user/confirm/{string_token}'

                    if get_config_env(app.config) == 'production':  
                        msg = Message(
                            subject='Confirmation',
                            sender=Config.MAIL_USERNAME,
                            recipients=[email]
                        )
                        body = render_template('mail_confirmation.html', url_confirmation=confirm_url)
                        msg.html = body
                        mail.send(msg)
                        
                        result = {
                            'message': 'User registered successfully, please check your email for confirmation',
                            'data': {'name': name, 'email': email}
                        }
                    else:
                        result = {
                            'message': 'User registered successfully, please check your email for confirmation',
                            'data': {'name': name, 'email': email, 'confirm_url': confirm_url}
                        }
                    connection.commit()
                    return make_response(jsonify(result), 201)
        except Exception as e:
            if connection:
                connection.rollback()
            return make_response(jsonify({"result": f'{e}'}), 400)
        

@user_ns.route("/login")
class LoginAPI(Resource):
    @user_ns.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()
        email = args['email']
        password = args['password']

        password_bytes = password.encode('utf-8')
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT name, password, status FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                existing_user = cursor.fetchone()

        if not existing_user:
            return make_response(jsonify({'message': 'user not exists'}), 400)

        if existing_user[2] == 0:
            return make_response(jsonify({'message': 'Check your email for confirmation'}), 400)

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


@user_ns.route("/confirm/<token>")
class UserConfirmAPI(Resource):

    @user_ns.header('Content-Type', 'text/html')
    def get(self, token):
        decoded_token = base64.b64decode(token).decode('ascii')
        email, hashed_pwd = decoded_token.split(':')
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, status FROM users WHERE email = %s AND password = %s"
                cursor.execute(query, (email, hashed_pwd))
                existing_user = cursor.fetchone()
    
                if not existing_user:
                    return make_response(render_template('message.html', message='user not found'))
    
                if existing_user[1]:
                    return make_response(render_template('message.html', message='user already confirmed'))

                query = "UPDATE users SET status=1 WHERE email = %s AND password = %s"
                cursor.execute(query, (email, hashed_pwd))

        if cursor.rowcount == 0:
            return make_response(render_template('message.html', message='confirmation failed'))
    
        return make_response(render_template('message.html', message='user confirmed'))