import os
from flask import jsonify, make_response, g, request
from flask_restx import Namespace, Resource
from app.api.auth import auth_required

from app.config import Config, DBManager

from ..models import comicInputParser
from werkzeug.utils import secure_filename
from datetime import datetime

ns = Namespace('comic')

connection = DBManager().get_connection()



@ns.route("/<string:comicId>")
class ChapterListAPI(Resource):
    @auth_required
    def get(self, comicId):
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, title, description, author, published_date, status, image_cover FROM comics WHERE id = %s"
                cursor.execute(query, comicId)
                comic = cursor.fetchone()
        if comic == None:
            return make_response(jsonify({'message': 'comic not found'}), 404)
        result = {
            'id': comic[0],
            'title': comic[1],
            'description': comic[2],
            'author': comic[3],
            'published_date': comic[4],
            'status': comic[5],
            'image_cover': f'{request.url_root}{Config.API_PREFIX}/{Config.UPLOAD_FOLDER}/{comic[6]}',
        }
        return make_response(jsonify(result), 200)


@ns.route("/")
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

        storage_dir = Config.UPLOAD_FOLDER
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
                INSERT INTO comics (title, author, published_date, status, description, image_cover, user_id)
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
