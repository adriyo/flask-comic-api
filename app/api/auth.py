from functools import wraps
from flask import jsonify, make_response, request, g
import base64
from app.config import DBManager

db_manager = DBManager()
connection = db_manager.get_connection()


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return make_response(jsonify({'message': 'no authorization'}), 401)
        auth_header = request.headers.get('Authorization')

        if not auth_header.startswith('Basic '):
            return make_response(jsonify({'message': 'invalid authorization'}), 401)

        token = auth_header.replace('Basic ', '')
        decoded_token = base64.b64decode(token).decode('ascii')
        email, hashed_pwd = decoded_token.split(':')

        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, email, password FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user = cursor.fetchone()
        if not user:
            return make_response(jsonify({'message': 'invalid account'}), 401)
        if hashed_pwd == user[2]:
            g.user_id = user[0]
            return f(*args, **kwargs)
        return make_response(jsonify({'message': 'invalid authorization'}), 401)
    return wrapper
