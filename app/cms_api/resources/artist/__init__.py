from flask import jsonify, make_response
from flask_restx import Namespace, Resource
from app.config.db import connection


ns = Namespace("artists")

@ns.route("")
class GenresApi(Resource):
    def get(self):

        with connection:
            with connection.cursor() as cursor:
                query = "SELECT * FROM artists"
                cursor.execute(query)
                genres = cursor.fetchall()
                
        result = [{'id': genre[0], 'name': genre[1]} for genre in genres]
        return make_response(jsonify(result), 200)
