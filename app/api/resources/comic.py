import os
from flask import jsonify, make_response, g
from flask_restx import Resource, Namespace
from app.api.auth import auth_required

from app.config import DBManager

from ..models import comicInputParser
from werkzeug.utils import secure_filename
from datetime import datetime

ns = Namespace("api")

db_manager = DBManager()
connection = db_manager.get_connection()


@ns.route("/comics")
class ComicListAPI(Resource):
    @auth_required
    def get(self):
        user_id = g.user_id
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, title, description, author, published_date, image_cover_url FROM comics WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                comics = cursor.fetchall()
        results = [
            {
                'id': comic[0],
                'title': comic[1],
                'description': comic[2],
                'author': comic[3],
                'published_date': comic[4],
                'image_cover_url': comic[5],
            }
            for comic in comics
        ]

        return make_response(jsonify(results), 200)


@ns.route("/comics/<string:comicId>")
class ChapterListAPI(Resource):
    @auth_required
    def get(self, comicId):
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, title FROM comics WHERE id = %s"
                cursor.execute(query, comicId)
                comic = cursor.fetchone()
        if comic == None:
            return make_response(jsonify({'message': 'comic not found'}), 404)
        result = {
            'id': comic[0],
            'title': comic[1],
        }
        return make_response(jsonify(result), 200)


@ns.route("/comic")
class ComicAPI(Resource):
    @ns.expect(comicInputParser)
    @auth_required
    def post(self):
        user_id = g.user_id
        args = comicInputParser.parse_args()

        title = args['title']
        description = args['description']
        author = args['author']
        published_date = args['published_date']
        status = args['status']
        image_cover = args['image_cover']

        try:
            published_datetime = datetime.strptime(
                published_date, "%Y-%m-%d").date()
        except Exception as e:
            published_datetime = datetime.date()

        storage_dir = 'storages'
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        try:
            filename = secure_filename(image_cover.filename)
            image_cover.save(os.path.join(storage_dir, filename))
        except Exception as e:
            return make_response({"result": f'{e}'}, 400)

        try:
            filename = secure_filename(image_cover.filename)
            query = """
                INSERT INTO comics (title, author, published_date, status, description, image_cover_url, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        query, (title, author, published_datetime, status, description, filename, user_id))
            result = {"message": "Data received successfully"}
            return make_response(jsonify(result), 201)
        except Exception as e:
            return make_response({"result": f'{e}'}, 400)
