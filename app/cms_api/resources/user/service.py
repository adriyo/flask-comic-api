from flask import jsonify, render_template
from app.config.db import connection
from app.cms_api.resources.helper import get_host_url, get_config_env
from app.config import Config, mail, app
from flask_mail import Message
import bcrypt
import base64

class UserService():

    def register(self, args):
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
                        return False, jsonify({'message': 'user already exists'})

                    hashed_pwd = (bcrypt.hashpw(password_bytes, bcrypt.gensalt())).decode('utf-8')

                    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                    cursor.execute(query, (name, email, hashed_pwd))
                    string_token = base64 \
                        .b64encode(f"{email}:{hashed_pwd}".encode('ascii')) \
                        .decode('utf-8')
                    
                    result = None
                    confirm_url = f'{get_host_url(app.config)}{Config.CMS_API_PREFIX}/user/confirm/{string_token}'
                    message = 'User registered successfully, please check your email for confirmation'
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
                            'message': message,
                            'data': {'name': name, 'email': email}
                        }
                    else:
                        result = {
                            'message': message,
                            'data': {'name': name, 'email': email, 'confirm_url': confirm_url}
                        }
                    connection.commit()
                    return True, jsonify(result)
        except Exception as e:
            if connection:
                connection.rollback()
            return False, jsonify({"message": f'{e}'})

    def login(self, args):
        email = args['email']
        password = args['password']

        password_bytes = password.encode('utf-8')
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT name, password, status FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                existing_user = cursor.fetchone()

                if not existing_user:
                    return False, jsonify({'message': 'user not exists'})

                if existing_user[2] == 0:
                    return False, jsonify({'message': 'Check your email for confirmation'})

                existing_password = existing_user[1].encode('utf-8')
                if not bcrypt.checkpw(password_bytes, existing_password):
                    return False, jsonify({'message': 'invalid password'})

                string_token = base64 \
                    .b64encode(f"{email}:{existing_user[1]}".encode('ascii')) \
                    .decode('utf-8')
                result = {
                    'message': 'Success',
                    'data': {'name': existing_user[0], 'email': email, 'token': string_token}
                }
        return True, jsonify(result)
    
    def confirm(self, token):
        decoded_token = base64.b64decode(token).decode('ascii')
        email, hashed_pwd = decoded_token.split(':')
        try:            
            with connection:
                with connection.cursor() as cursor:
                    query = "SELECT id, status FROM users WHERE email = %s AND password = %s"
                    cursor.execute(query, (email, hashed_pwd))
                    existing_user = cursor.fetchone()
        
                    if not existing_user:
                        return False, render_template('message.html', message='user not found')
        
                    if existing_user[1]:
                        return False, render_template('message.html', message='user already confirmed')

                    query = "UPDATE users SET status=1 WHERE email = %s AND password = %s"
                    cursor.execute(query, (email, hashed_pwd))
                connection.commit()
            return True, render_template('message.html', message='user confirmed')
        except Exception as e:
            if connection:
                connection.rollback()
            return False, render_template('message.html', message=f'Error {e}')
