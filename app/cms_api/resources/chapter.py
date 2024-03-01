from flask import jsonify, make_response, g, request
from flask_restx import Resource, Namespace
from werkzeug.utils import secure_filename
from app.cms_api.auth import auth_required
from app.cms_api.constants import STORAGE_SERVICE_UPLOAD_URL
from app.cms_api.resources.converter import get_chapter_image_url, get_comic_status, get_comic_type, get_image_cover_url
from app.config import DBManager
import requests
from app.cms_api.parser import chapter

comics_ns = Namespace('comics')
connection = DBManager().get_connection()


chapterInputParser = chapter.input_parser()
chapterUpdateInputParser = chapter.update_input_parser()

@comics_ns.route("")
class ComicListAPI(Resource):

    @auth_required
    def get(self):
        user_id = g.user_id
        page = max(1, request.args.get('page', default=1, type=int))
        limit = request.args.get('limit', default=10, type=int)

        with connection:
            with connection.cursor() as cursor:
                query = """
                SELECT id, title, description, published_date, status, type, image_cover
                FROM comics WHERE user_id = %s
                LIMIT %s OFFSET %s
                """
                offset = (page - 1) * limit
                cursor.execute(query, (user_id, limit, offset))
                comics = cursor.fetchall()
        results = [
            {
                'id': comic[0],
                'title': comic[1],
                'description': comic[2],
                'published_date': comic[3],
                'status': get_comic_status(comic[4]),
                'type': get_comic_type(comic[5]),
                'image_cover': get_image_cover_url(comic[6], user_id, comic[0]),
            }
            for comic in comics
        ]

        return make_response(jsonify(results), 200)
    
@comics_ns.route("/<string:comicId>/chapters")
class ChapterListAPI(Resource):
    @auth_required
    def get(self, comicId):
        user_id = g.user_id
        with connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        comic_chapters.id,
                        comic_chapters.title
                    FROM comics
                    INNER JOIN comic_chapters ON comics.id = comic_chapters.comic_id
                    WHERE comics.user_id = %s AND comics.id = %s
                """
                cursor.execute(query, (user_id, comicId))
                chapters = cursor.fetchall()
            
            if chapters == None:
                return make_response(jsonify({'message': 'comic not found'}), 404)
        result = [
            {
                'id': chapter[0],
                'title': chapter[1],
            }
            for chapter in chapters
        ]
        return make_response(jsonify({'message': 'success', 'data': result}), 200)
    
@comics_ns.route("/<string:comicId>/chapter/<string:chapterId>")
class ComicChapterDetailAPI(Resource):

    @auth_required
    def get(self, comicId, chapterId):
        user_id = g.user_id
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id FROM comics WHERE user_id = %s AND id = %s"
                cursor.execute(query, (user_id, comicId))
                existing_comic = cursor.fetchone()

                if existing_comic == None:
                    return make_response(jsonify({'message': 'comic not found'}), 404)

                query = """
                    SELECT 
                        comic_chapters.title as chapter_title, 
                        chapter_images.image as image,
                        chapter_images.id as id
                    FROM 
                        comic_chapters 
                    JOIN 
                        chapter_images ON comic_chapters.id = chapter_images.chapter_id
                    WHERE 
                        comic_chapters.comic_id = %s 
                        AND comic_chapters.id = %s
                """
                cursor.execute(query, (comicId, chapterId))
                comic = cursor.fetchall()
            
            if not comic:
                return make_response(jsonify({'message': 'chapter not found'}), 404)
            
            chapter_data = {
                'title': comic[0][0],
                'images': [
                    {
                        'id':image[2],
                        'url':get_chapter_image_url(image[1], user_id, comicId, chapterId)
                    }
                    for image in comic
                ]
            }
        return make_response(jsonify(chapter_data), 200)

@comics_ns.route("/<string:comicId>/chapter")
class ChapterImagesAPI(Resource):
    @auth_required
    def get(self, comicId):
        user_id = g.user_id
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, title, description, author, published_date, image_cover FROM comics WHERE user_id = %s AND id = %s"
                cursor.execute(query, (user_id, comicId))
                comic = cursor.fetchone()
            
            if comic == None:
                return make_response(jsonify({'message': 'comic not found'}), 404)
            
        return make_response(jsonify({'message': 'success', 'data': comic}), 200)

    @comics_ns.expect(chapterInputParser)
    @auth_required
    def post(self, comicId):    
        user_id = g.user_id
        args = chapterInputParser.parse_args()

        title = args['title']
        images = args['images']

        try:
            with connection:
                with connection.cursor() as cursor:
                    query = "SELECT id FROM comics WHERE id = %s AND user_id = %s"
                    cursor.execute(query, (comicId, user_id))
                    existing_comic = cursor.fetchone()

                    if existing_comic == None:
                        return make_response(jsonify({'message': 'comic not found'}), 404)
                    
                    query = "INSERT INTO comic_chapters (title, comic_id) VALUES (%s, %s) RETURNING id"
                    cursor.execute(query, (title, comicId))
                    last_chapter_id = cursor.fetchone()[0]

                    for image in images:
                        filename = secure_filename(image.filename)
                        query = "INSERT INTO chapter_images (chapter_id, image) VALUES (%s, %s)"
                        cursor.execute(query, (last_chapter_id, filename))
                        
                        if cursor.rowcount == 0:
                            connection.rollback()
                            return make_response(jsonify({'message': 'failed to upload'}), 404)

                        request_files = {"file": (filename, image)}
                        request_data = {"user_id": user_id, "comic_id": comicId, "chapter_id": last_chapter_id}
                        response = requests.post(
                            url=STORAGE_SERVICE_UPLOAD_URL, 
                            files=request_files,
                            data=request_data)
                        if response.status_code != 200:
                            connection.rollback()
                            return make_response({"result": "Failed to upload image"}, 400)
                connection.commit()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            if connection:
                connection.rollback()
            return make_response({"message": f'{e}'}, 400)
    
@comics_ns.route("/<string:comicId>/chapter/<string:chapterId>")
class ChapterUpdateAPI(Resource):
    @comics_ns.expect(chapterUpdateInputParser)
    @auth_required
    def put(self, comicId, chapterId):    
        user_id = g.user_id
        args = chapterUpdateInputParser.parse_args()

        title = args['title']
        images = args['images']
        image_ids = args['image_ids']

        try:
            with connection:
                with connection.cursor() as cursor:
                    query = "SELECT c.id FROM comics c INNER JOIN comic_chapters ch ON c.id = ch.comic_id WHERE c.id = %s AND c.user_id = %s AND ch.id = %s"
                    cursor.execute(query, (comicId, user_id, chapterId))
                    existing_chapter = cursor.fetchone()

                    if existing_chapter is None:
                        return make_response(jsonify({'message': 'comic chapter not found'}), 404)

                    query = "UPDATE comic_chapters SET title = %s WHERE id = %s"
                    cursor.execute(query, (title, chapterId))

                    for image, image_id in zip(images, image_ids):
                        filename = secure_filename(image.filename)
                        query = "UPDATE chapter_images SET image = %s WHERE id = %s AND chapter_id = %s"
                        cursor.execute(query, (filename, image_id, chapterId))

                        request_files = {"file": (filename, image)}
                        request_data = {"user_id": user_id, "comic_id": comicId, "chapter_id": chapterId}
                        response = requests.post(
                            url=STORAGE_SERVICE_UPLOAD_URL,
                            files=request_files, 
                            data=request_data)
                        if response.status_code != 200:
                            connection.rollback()
                            return make_response({"result": "Failed to upload image"}, 400)
                        
                connection.commit()
            return make_response(jsonify({'message': 'success'}), 200)
        except Exception as e:
            if connection:
                connection.rollback()
            return make_response({"message": f'{e}'}, 400)

