from flask import jsonify, make_response
from app.config.db import connection
from flask_restx import Resource, Namespace

ns = Namespace('comics')

@ns.route("/options")
class ComicOptionsAPI(Resource):
    def get(self):
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT * FROM genres"
                cursor.execute(query)
                genres = cursor.fetchall()
                genres_result = [{'id': genre[0], 'name': genre[1]} for genre in genres]

                query = "SELECT * FROM tags"
                cursor.execute(query)
                tags = cursor.fetchall()
                tags_result = [{'id': tag[0], 'name': tag[1]} for tag in tags]

                
                query = "SELECT * FROM translators"
                cursor.execute(query)
                translators = cursor.fetchall()
                translators_result = [{'id': translator[0], 'name': translator[1]} for translator in translators]

                
                query = "SELECT * FROM artists"
                cursor.execute(query)
                artists = cursor.fetchall()
                artists_result = [{'id': artist[0], 'name': artist[1]} for artist in artists]

                
                query = "SELECT * FROM authors"
                cursor.execute(query)
                authors = cursor.fetchall()
                authors_result = [{'id': author[0], 'name': author[1]} for author in authors]


        result = {
            'genres': genres_result,
            'tags': tags_result,
            'translators': translators_result,
            'artists': artists_result,
            'authors': authors_result
        }

        return make_response(jsonify(result), 200)