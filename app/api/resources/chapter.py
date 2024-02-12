import os
from flask import jsonify, make_response, g, request
from flask_restx import Resource, Namespace
from werkzeug.utils import secure_filename
from app.api.auth import auth_required
from app.config import Config, DBManager
from ..models import chapterInputParser, chapterUpdateInputParser

comics_ns = Namespace('comics')
connection = DBManager().get_connection()

@comics_ns.route("")
class ComicListAPI(Resource):
    @auth_required
    def get(self):
        user_id = g.user_id
        with connection:
            with connection.cursor() as cursor:
                query = "SELECT id, title, description, author, published_date, status, image_cover FROM comics WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                comics = cursor.fetchall()
        results = [
            {
                'id': comic[0],
                'title': comic[1],
                'description': comic[2],
                'author': comic[3],
                'published_date': comic[4],
                'status': comic[5],
                'image_cover': f'{request.headers.get('X-Original-URL')}/{Config.API_PREFIX}/{Config.UPLOAD_FOLDER}/{comic[6]}',
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
                        chapter_images.image as image
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
                'images': [image[1] for image in comic]
            }
        return make_response(jsonify({'message': 'success', 'data': chapter_data}), 200)

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

        storage_dir = Config.UPLOAD_FOLDER
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

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

                if cursor.rowcount == 0:
                    return make_response(jsonify({'message': 'chapter not found'}), 404)

                try:
                    for image in images:
                        filename = secure_filename(image.filename)
                        query = "INSERT INTO chapter_images (chapter_id, image) VALUES (%s, %s)"
                        cursor.execute(query, (last_chapter_id, filename))
                        
                        if cursor.rowcount == 0:
                            return make_response(jsonify({'message': 'failed to upload'}), 404)

                        image.save(os.path.join(storage_dir, filename)) 
                except Exception as e:
                    return make_response({"message": f'{e}'}, 400)
                
        return make_response(jsonify({'message': 'success'}), 200)
    
    
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

        storage_dir = Config.UPLOAD_FOLDER
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        with connection:
            with connection.cursor() as cursor:
                query = "SELECT c.id FROM comics c INNER JOIN comic_chapters ch ON c.id = ch.comic_id WHERE c.id = %s AND c.user_id = %s AND ch.id = %s"
                cursor.execute(query, (comicId, user_id, chapterId))
                existing_chapter = cursor.fetchone()

                if existing_chapter is None:
                    return make_response(jsonify({'message': 'comic chapter not found'}), 404)

                try:
                    query = "UPDATE comic_chapters SET title = %s WHERE id = %s"
                    cursor.execute(query, (title, chapterId))

                    for image, image_id in zip(images, image_ids):
                        filename = secure_filename(image.filename)
                        query = "UPDATE chapter_images SET image = %s WHERE id = %s AND chapter_id = %s"
                        cursor.execute(query, (filename, image_id, chapterId))
                        
                        if cursor.rowcount == 0:
                            return make_response(jsonify({'message': 'failed to update image'}), 404)

                        image.save(os.path.join(storage_dir, filename)) 
                except Exception as e:
                    return make_response({"message": f'{e}'}, 400)

        return make_response(jsonify({'message': 'success'}), 200)
