import os
from flask import jsonify, make_response, g, request
from flask_restx import Namespace, Resource
from app.api.auth import auth_required
import requests
from app.config import Config, DBManager

from ..models import comicInputParser, comicUpdateInputParser
from werkzeug.utils import secure_filename
from datetime import datetime

ns = Namespace('comic')

connection = DBManager().get_connection()

STORAGE_SERVICE_URL = "http://storage-service:8080/upload"  # Update with the actual URL of your storage service


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
            'image_cover': f'{request.headers.get('X-Original-URL')}/{Config.API_PREFIX}/{Config.UPLOAD_FOLDER}/{comic[6]}',
        }
        return make_response(jsonify(result), 200)
    
    @ns.expect(comicUpdateInputParser)
    @auth_required
    def put(self, comicId):
        user_id = g.user_id
        args = comicUpdateInputParser.parse_args()

        title = args['title']
        description = args['description']
        author = args['author']
        published_date = args['published_date']
        status = args['status']
        image_cover = args['image_cover']

        if all(value is None for value in args.values()):
            return make_response(jsonify({'message': 'No fields provided for update'}), 400)


        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id FROM comics WHERE id = %s and user_id = %s"
                cursor.execute(query, (comicId, user_id))
                comic = cursor.fetchone()
        
                if comic == None:
                    return make_response(jsonify({'message': 'comic not found'}), 404)
                
                storage_dir = Config.UPLOAD_FOLDER
                if not os.path.exists(storage_dir):
                    os.makedirs(storage_dir)

                filename = None
                if 'image_cover' in request.files:
                    try:
                        filename = secure_filename(image_cover.filename)
                        image_cover.save(os.path.join(storage_dir, filename))
                    except Exception as e:
                        return make_response({"result": f'{e}'}, 400)
                
                update_fields = []
                update_values = []
                if 'title' in args and title:
                    update_fields.append("title = %s")
                    update_values.append(title)
                if 'description' in args and description:
                    update_fields.append("description = %s")
                    update_values.append(description)
                if 'author' in args and author:
                    update_fields.append("author = %s")
                    update_values.append(author)
                if 'published_date' in args and published_date:
                    update_fields.append("published_date = %s")
                    update_values.append(published_date)
                if 'status' in args and status:
                    update_fields.append("status = %s")
                    update_values.append(status)
                if filename:
                    update_fields.append("image_cover = %s")
                    update_values.append(filename)
                
                update_values.append(comicId)

                set_clause = ', '.join(update_fields)                

                query = f"""
                    UPDATE comics
                    SET {set_clause}
                    WHERE id = %s
                """
                cursor.execute(query, tuple(update_values))

                if cursor.rowcount == 0:
                    return make_response(jsonify({'message': 'update failed'}), 400)

        return make_response(jsonify({'message': 'success'}), 200)


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

        try:
            filename = ''
            if image_cover != None:
                try:
                    filename = secure_filename(image_cover.filename)
                except Exception as e:
                    return make_response({"result": f'{e}'}, 400)

                response = requests.post(STORAGE_SERVICE_URL, files={"file": (filename, image_cover)})
                if response.status_code != 200:
                    return make_response({"result": "Failed to upload image"}, 400)

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


@ns.route("/<string:comic_id>")
class DeleteComicAPI(Resource):
    
    @auth_required
    def delete(self, comic_id):
        user_id = g.user_id       
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT image_cover FROM comics WHERE id = %s AND user_id = %s", (comic_id, user_id))
                cover_filename = cursor.fetchone()[0]
                cursor.execute("SELECT image FROM chapter_images WHERE chapter_id IN (SELECT id FROM comic_chapters WHERE comic_id = %s)", (comic_id,))
                chapter_filenames = cursor.fetchall()

                storage_dir = Config.UPLOAD_FOLDER

                if cover_filename:
                    cover_path = os.path.join(storage_dir, cover_filename)
                    if os.path.exists(cover_path):
                        os.remove(cover_path)
                for chapter_filename in chapter_filenames:
                    if chapter_filename:
                        chapter_path = os.path.join(storage_dir, chapter_filename[0])
                        if os.path.exists(chapter_path):
                            os.remove(chapter_path)

                query = "DELETE FROM comics WHERE id = %s AND user_id = %s"
                cursor.execute(query, (comic_id, user_id))
                if cursor.rowcount == 0:
                    return make_response(jsonify({'message': 'comic not found'}), 404)
                else:
                    return make_response(jsonify({'message': 'comic deleted'}), 200)