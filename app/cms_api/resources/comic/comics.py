from datetime import datetime
import os
from flask import jsonify, make_response, g, request, current_app
from flask_restx import Namespace, Resource
from psycopg2 import DatabaseError 
from app.cms_api.auth import auth_required
import requests
from app.cms_api.constants import STORAGE_SERVICE_FILES_URL, STORAGE_SERVICE_SAVE_URL, STORAGE_SERVICE_UPLOAD_URL
from app.cms_api.resources.helper import allowed_file, parse_published_date, get_comic_status, get_comic_type, get_image_cover_url
from app.config.db import connection
from werkzeug.utils import secure_filename
from app.cms_api.parser import comic

comicInputParser = comic.input_parser()

ns = Namespace('comics')

@ns.route("")
@ns.route("/")
class ComicListAPI(Resource):

    @auth_required
    def get(self):
        user_id = g.user_id
        page = max(1, request.args.get('page', default=1, type=int))
        limit = request.args.get('limit', default=10, type=int)

        with connection:
            with connection.cursor() as cursor:
                count_query = "SELECT COUNT(*) FROM comics WHERE user_id = %s"
                cursor.execute(count_query, (user_id,))
                total_records = cursor.fetchone()[0]
                total_pages = (total_records + limit - 1) // limit

                query = """
                SELECT 
                    c.id, c.title, c.description, c.published_date, c.status, c.type, c.image_cover, c.user_id, c.alternative_title,
                    COALESCE(author_ids, '{}') as author_ids,
                    COALESCE(author_names, '{}') as author_names,
                    COALESCE(tag_ids, '{}') as tag_ids,
                    COALESCE(tag_names, '{}') as tag_names,
                    COALESCE(genre_ids, '{}') as genre_ids,
                    COALESCE(genre_names, '{}') as genre_names, 
                    COALESCE(artist_ids, '{}') as artist_ids,
                    COALESCE(artist_names, '{}') as artist_names, 
                    COALESCE(translator_ids, '{}') as translator_ids,
                    COALESCE(translator_names, '{}') as translator_names 
                FROM 
                    comics c 
                LEFT JOIN (
                    SELECT comic_id, array_agg(author.id) as author_ids, array_agg(author.name) as author_names
                    FROM comic_authors
                    LEFT JOIN authors author ON comic_authors.author_id = author.id
                    GROUP BY comic_id
                ) author_agg ON c.id = author_agg.comic_id
                LEFT JOIN (
                    SELECT comic_id, array_agg(tag.id) as tag_ids, array_agg(tag.name) as tag_names
                    FROM comic_tags
                    LEFT JOIN tags tag ON comic_tags.tag_id = tag.id
                    GROUP BY comic_id
                ) tag_agg ON c.id = tag_agg.comic_id
                LEFT JOIN (
                    SELECT comic_id, array_agg(genre.id) as genre_ids, array_agg(genre.name) as genre_names
                    FROM comic_genres
                    LEFT JOIN genres genre ON comic_genres.genre_id = genre.id
                    GROUP BY comic_id
                ) genre_agg ON c.id = genre_agg.comic_id
                LEFT JOIN (
                    SELECT comic_id, array_agg(artist.id) as artist_ids, array_agg(artist.name) as artist_names
                    FROM comic_artists
                    LEFT JOIN artists artist ON comic_artists.artist_id = artist.id
                    GROUP BY comic_id
                ) artist_agg ON c.id = artist_agg.comic_id
                LEFT JOIN (
                    SELECT comic_id, array_agg(translator.id) as translator_ids, array_agg(translator.name) as translator_names
                    FROM comic_translators
                    LEFT JOIN translators translator ON comic_translators.translator_id = translator.id
                    GROUP BY comic_id
                ) translator_agg ON c.id = translator_agg.comic_id
                WHERE
                    c.user_id = %s
                LIMIT %s 
                OFFSET %s
                """
                offset = (page - 1) * limit
                cursor.execute(query, (user_id, limit, offset))
                comics = cursor.fetchall()
            comics_result = []
            for comic in comics:
                published_date = datetime.strftime(comic[3], "%d-%m-%Y") if comic[3] else None
                author_data = [
                    {'id': author_id, 'name': author_name} 
                    for author_id, author_name in zip(comic[9], comic[10])
                ]
                tag_data = [
                    {'id': tag_id, 'name': tag_name} 
                    for tag_id, tag_name in zip(comic[11], comic[12])
                ]
                genre_data = [
                    {'id': genre_id, 'name': genre_name} 
                    for genre_id, genre_name in zip(comic[13], comic[14])
                ]
                artist_data = [
                    {'id': artist_id, 'name': artist_name} 
                    for artist_id, artist_name in zip(comic[15], comic[16])
                ]
                translator_data = [
                    {'id': translator_id, 'name': translator_name} 
                    for translator_id, translator_name in zip(comic[17], comic[18])
                ]
                comic_data = {
                    'id': comic[0],
                    'title': comic[1],
                    'alternative_title': comic[8],
                    'description': comic[2],
                    'published_date': published_date,
                    'status': get_comic_status(comic[4]),
                    'type': get_comic_type(comic[5]),
                    'tags': tag_data,
                    'authors': author_data,
                    'genres': genre_data,
                    'artists': artist_data, 
                    'translators': translator_data, 
                    'image_cover': get_image_cover_url(current_app.config, comic[6], user_id, comic[0]),
                }
                comics_result.append(comic_data)

            result = {
                'data': comics_result,
                'total_pages': total_pages
            }

            return make_response(jsonify(result), 200)

@ns.route("/<string:comic_id>")
class ChapterListAPI(Resource):
    @auth_required
    def get(self, comic_id):
        user_id = g.user_id
        with connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        c.id, c.title, c.description, c.published_date, c.status, c.type, c.image_cover, c.user_id, c.alternative_title,
                        COALESCE(author_ids, '{}') as author_ids,
                        COALESCE(author_names, '{}') as author_names,
                        COALESCE(tag_ids, '{}') as tag_ids,
                        COALESCE(tag_names, '{}') as tag_names,
                        COALESCE(genre_ids, '{}') as genre_ids,
                        COALESCE(genre_names, '{}') as genre_names, 
                        COALESCE(artist_ids, '{}') as artist_ids,
                        COALESCE(artist_names, '{}') as artist_names, 
                        COALESCE(translator_ids, '{}') as translator_ids,
                        COALESCE(translator_names, '{}') as translator_names 
                    FROM 
                        comics c 
                    LEFT JOIN (
                        SELECT comic_id, array_agg(author.id) as author_ids, array_agg(author.name) as author_names
                        FROM comic_authors
                        LEFT JOIN authors author ON comic_authors.author_id = author.id
                        GROUP BY comic_id
                    ) author_agg ON c.id = author_agg.comic_id
                    LEFT JOIN (
                        SELECT comic_id, array_agg(tag.id) as tag_ids, array_agg(tag.name) as tag_names
                        FROM comic_tags
                        LEFT JOIN tags tag ON comic_tags.tag_id = tag.id
                        GROUP BY comic_id
                    ) tag_agg ON c.id = tag_agg.comic_id
                    LEFT JOIN (
                        SELECT comic_id, array_agg(genre.id) as genre_ids, array_agg(genre.name) as genre_names
                        FROM comic_genres
                        LEFT JOIN genres genre ON comic_genres.genre_id = genre.id
                        GROUP BY comic_id
                    ) genre_agg ON c.id = genre_agg.comic_id
                    LEFT JOIN (
                        SELECT comic_id, array_agg(artist.id) as artist_ids, array_agg(artist.name) as artist_names
                        FROM comic_artists
                        LEFT JOIN artists artist ON comic_artists.artist_id = artist.id
                        GROUP BY comic_id
                    ) artist_agg ON c.id = artist_agg.comic_id
                    LEFT JOIN (
                        SELECT comic_id, array_agg(translator.id) as translator_ids, array_agg(translator.name) as translator_names
                        FROM comic_translators
                        LEFT JOIN translators translator ON comic_translators.translator_id = translator.id
                        GROUP BY comic_id
                    ) translator_agg ON c.id = translator_agg.comic_id
                    WHERE
                        c.id = %s
                        AND c.user_id = %s
                """
                
                cursor.execute(query, (comic_id, user_id))
                comic = cursor.fetchone()
        if comic == None:
            return make_response(jsonify({'message': 'comic not found'}), 404)
        published_date = datetime.strftime(comic[3], "%d-%m-%Y") if comic[3] else None
        author_data = [
            {'id': author_id, 'name': author_name} 
            for author_id, author_name in zip(comic[9], comic[10])
        ]
        tag_data = [
            {'id': tag_id, 'name': tag_name} 
            for tag_id, tag_name in zip(comic[11], comic[12])
        ]
        genre_data = [
            {'id': genre_id, 'name': genre_name} 
            for genre_id, genre_name in zip(comic[13], comic[14])
        ]
        artist_data = [
            {'id': artist_id, 'name': artist_name} 
            for artist_id, artist_name in zip(comic[15], comic[16])
        ]
        translator_data = [
            {'id': translator_id, 'name': translator_name} 
            for translator_id, translator_name in zip(comic[17], comic[18])
        ]
        result = {
            'id': comic[0],
            'title': comic[1],
            'alternative_title': comic[8],
            'description': comic[2],
            'published_date': published_date,
            'status': get_comic_status(comic[4]),
            'type': get_comic_type(comic[5]),
            'tags': tag_data,
            'authors': author_data,
            'genres': genre_data,
            'artists': artist_data, 
            'translators': translator_data, 
            'image_cover': get_image_cover_url(config=current_app.config, filename=comic[6], user_id=comic[7], comic_id=comic[0]),
        }
        return make_response(jsonify(result), 200)
    
    @ns.expect(comicInputParser)
    @auth_required
    def put(self, comic_id):
        user_id = g.user_id
        args = comicInputParser.parse_args()

        title = args['title']
        alternative_title = args['alternative_title']
        description = args['description']
        published_date = args['published_date']
        status = args['status']
        comic_type = args['type']
        image_cover = args['image_cover']
        authors = args['authors']
        artists = args['artists']
        tags = args['tags']
        translators = args['translators']
        genres = args['genres']
        new_authors = args['new_authors']
        new_artists = args['new_artists']
        new_tags = args['new_tags']
        new_translators = args['new_translators']
        new_genres = args['new_genres']
        published_datetime = parse_published_date(published_date)

        if all(value is None for value in args.values()):
            return make_response(jsonify({'message': 'No fields provided for update'}), 400)

        try:
            with connection:
                with connection.cursor() as cursor:
                    query = "SELECT id FROM comics WHERE id = %s and user_id = %s"
                    cursor.execute(query, (comic_id, user_id))
                    comic = cursor.fetchone()
            
                    if comic == None:
                        return make_response(jsonify({'message': 'comic not found'}), 404)
                    
                    filename = ''
                    if 'image_cover' in request.files:
                        filename = secure_filename(image_cover.filename)

                        if not allowed_file(filename):
                            return make_response({"result": "File type not allowed"}, 400)

                        request_files = {"file": (filename, image_cover)}
                        request_data = {"user_id": user_id, "comic_id": comic_id}
                        response = requests.post(
                            url=STORAGE_SERVICE_UPLOAD_URL, 
                            files=request_files, 
                            data=request_data
                        )

                        if response.status_code != 200:
                            return make_response({"result": "Failed to upload image"}, 400)
                    
                    update_fields = []
                    update_values = []
                    if title:
                        update_fields.append("title = %s")
                        update_values.append(title)
                    if alternative_title:
                        update_fields.append("alternative_title = %s")
                        update_values.append(alternative_title)
                    if description:
                        update_fields.append("description = %s")
                        update_values.append(description)
                    if published_datetime:
                        update_fields.append("published_date = %s")
                        update_values.append(published_datetime)
                    if status:
                        update_fields.append("status = %s")
                        update_values.append(status)
                    if comic_type:
                        update_fields.append("type = %s")
                        update_values.append(comic_type)
                    if filename:
                        update_fields.append("image_cover = %s")
                        update_values.append(filename)
                    
                    update_values.append(comic_id)

                    set_clause = ', '.join(update_fields)  

                    if update_fields:
                        query = f"""
                            UPDATE comics
                            SET {set_clause}
                            WHERE id = %s
                        """
                        cursor.execute(query, tuple(update_values))

                    if genres:
                        cursor.execute("DELETE FROM comic_genres WHERE comic_id = %s", (comic_id,))
                        genre_values = [(comic_id, genre_id) for genre_id in genres]
                        cursor.executemany("INSERT INTO comic_genres (comic_id, genre_id) VALUES (%s, %s)", genre_values)

                    if authors:
                        cursor.execute("DELETE FROM comic_authors WHERE comic_id = %s", (comic_id,))
                        author_values = [(comic_id, author_id) for author_id in authors]
                        cursor.executemany("INSERT INTO comic_authors (comic_id, author_id) VALUES (%s, %s)", author_values)
                    
                    if artists:
                        cursor.execute("DELETE FROM comic_artists WHERE comic_id = %s", (comic_id,))
                        artist_values = [(comic_id, artist_id) for artist_id in artists]
                        cursor.executemany("INSERT INTO comic_artists (comic_id, artist_id) VALUES (%s, %s)", artist_values)

                    if tags:
                        cursor.execute("DELETE FROM comic_tags WHERE comic_id = %s", (comic_id,))
                        tag_values = [(comic_id, tag_id) for tag_id in tags]
                        cursor.executemany("INSERT INTO comic_tags (comic_id, tag_id) VALUES (%s, %s)", tag_values)

                    if translators:
                        cursor.execute("DELETE FROM comic_translators WHERE comic_id = %s", (comic_id,))
                        translator_values = [(comic_id, translator_id) for translator_id in translators]
                        cursor.executemany("INSERT INTO comic_translators (comic_id, translator_id) VALUES (%s, %s)", translator_values)

                    if new_authors:
                        author_values = [(author,) for author in new_authors]
                        new_author_ids = []
                        for author in new_authors:
                            cursor.execute("INSERT INTO authors (name) VALUES (%s) RETURNING id", (author,))
                            new_author_ids.append(cursor.fetchone()[0])

                        if new_author_ids:
                            new_author_values = [(comic_id, new_author_id) for new_author_id in new_author_ids]
                            cursor.executemany("INSERT INTO comic_authors (comic_id, author_id) VALUES (%s, %s)", new_author_values)
                            
                    if new_genres:
                        genre_values = [(genre,) for genre in new_genres]
                        new_genre_ids = []
                        for genre in new_genres:
                            cursor.execute("INSERT INTO genres (name) VALUES (%s) RETURNING id", (genre,))
                            new_genre_ids.append(cursor.fetchone()[0])

                        if new_genre_ids:
                            new_genre_values = [(comic_id, new_genre_id) for new_genre_id in new_genre_ids]
                            cursor.executemany("INSERT INTO comic_genres (comic_id, genre_id) VALUES (%s, %s)", new_genre_values)

                    if new_artists:
                        artist_values = [(artist,) for artist in new_artists]
                        new_artist_ids = []
                        for artist in new_artists:
                            cursor.execute("INSERT INTO artists (name) VALUES (%s) RETURNING id", (artist,))
                            new_artist_ids.append(cursor.fetchone()[0])

                        if new_artist_ids:
                            new_artist_values = [(comic_id, new_artist_id) for new_artist_id in new_artist_ids]
                            cursor.executemany("INSERT INTO comic_artists (comic_id, artist_id) VALUES (%s, %s)", new_artist_values)

                    if new_tags:
                        tag_values = [(tag,) for tag in new_tags]
                        new_tag_ids = []
                        for tag in new_tags:
                            cursor.execute("INSERT INTO tags (name) VALUES (%s) RETURNING id", (tag,))
                            new_tag_ids.append(cursor.fetchone()[0])
                        
                        if new_tag_ids:
                            new_tag_values = [(comic_id, new_tag_id) for new_tag_id in new_tag_ids]
                            cursor.executemany("INSERT INTO comic_tags (comic_id, tag_id) VALUES (%s, %s)", new_tag_values)

                    if new_translators:
                        translator_values = [(translator,) for translator in new_translators]
                        new_translator_ids = []
                        for translator in new_translators:
                            cursor.execute("INSERT INTO translators (name) VALUES (%s) RETURNING id", (translator,))
                            new_translator_ids.append(cursor.fetchone()[0])

                        if new_translator_ids:
                            new_translator_values = [(comic_id, new_translator_id) for new_translator_id in new_translator_ids]
                            cursor.executemany("INSERT INTO comic_translators (comic_id, translator_id) VALUES (%s, %s)", new_translator_values)
                    
                    connection.commit()
        
            return make_response(jsonify({'message': 'update success'}), 200)
        except (Exception, DatabaseError) as error:
            if connection:
                connection.rollback()
            return make_response(jsonify({'message': f'update failed {error}'}), 400)    

@ns.route("")
class ComicAPI(Resource):
    @ns.expect(comicInputParser)
    @auth_required
    def post(self):
        user_id = g.user_id
        args = comicInputParser.parse_args()

        title = args['title']
        alternative_title = args['alternative_title']
        description = args['description']
        published_date = args['published_date']
        status = args['status']
        comic_type = args['type']
        image_cover = args['image_cover']
        authors = args['authors']
        artists = args['artists']
        tags = args['tags']
        translators = args['translators']
        genres = args['genres']
        new_authors = args['new_authors']
        new_artists = args['new_artists']
        new_tags = args['new_tags']
        new_translators = args['new_translators']
        new_genres = args['new_genres']
        published_datetime = parse_published_date(published_date)

        try:
            filename = None
            if image_cover != None:
                filename = secure_filename(image_cover.filename)
                if not allowed_file(filename):
                    return make_response({"result": "File type not allowed"}, 400)

            query = """
                INSERT INTO comics (title, alternative_title, description, published_date, status, type, image_cover, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """

            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        query, (title, alternative_title, description, published_datetime, status, comic_type, filename, user_id))
                    comic_id = cursor.fetchone()[0]

                    if genres:
                        genre_values = [(comic_id, genre_id) for genre_id in genres]
                        cursor.executemany("INSERT INTO comic_genres (comic_id, genre_id) VALUES (%s, %s)", genre_values)

                    if authors:
                        author_values = [(comic_id, author_id) for author_id in authors]
                        cursor.executemany("INSERT INTO comic_authors (comic_id, author_id) VALUES (%s, %s)", author_values)
                    
                    if artists:
                        artist_values = [(comic_id, artist_id) for artist_id in artists]
                        cursor.executemany("INSERT INTO comic_artists (comic_id, artist_id) VALUES (%s, %s)", artist_values)

                    if tags:
                        tag_values = [(comic_id, tag_id) for tag_id in tags]
                        cursor.executemany("INSERT INTO comic_tags (comic_id, tag_id) VALUES (%s, %s)", tag_values)

                    if translators:
                        translator_values = [(comic_id, translator_id) for translator_id in translators]
                        cursor.executemany("INSERT INTO comic_translators (comic_id, translator_id) VALUES (%s, %s)", translator_values)
                    
                    if new_authors:
                        author_values = [(author,) for author in new_authors]
                        new_author_ids = []
                        for author in new_authors:
                            cursor.execute("INSERT INTO authors (name) VALUES (%s) RETURNING id", (author,))
                            new_author_ids.append(cursor.fetchone()[0])

                        if new_author_ids:
                            new_author_values = [(comic_id, new_author_id) for new_author_id in new_author_ids]
                            cursor.executemany("INSERT INTO comic_authors (comic_id, author_id) VALUES (%s, %s)", new_author_values)
                            

                    if new_genres:
                        genre_values = [(genre,) for genre in new_genres]
                        new_genre_ids = []
                        for genre in new_genres:
                            cursor.execute("INSERT INTO genres (name) VALUES (%s) RETURNING id", (genre,))
                            new_genre_ids.append(cursor.fetchone()[0])

                        if new_genre_ids:
                            new_genre_values = [(comic_id, new_genre_id) for new_genre_id in new_genre_ids]
                            cursor.executemany("INSERT INTO comic_genres (comic_id, genre_id) VALUES (%s, %s)", new_genre_values)

                    if new_artists:
                        artist_values = [(artist,) for artist in new_artists]
                        new_artist_ids = []
                        for artist in new_artists:
                            cursor.execute("INSERT INTO artists (name) VALUES (%s) RETURNING id", (artist,))
                            new_artist_ids.append(cursor.fetchone()[0])

                        if new_artist_ids:
                            new_artist_values = [(comic_id, new_artist_id) for new_artist_id in new_artist_ids]
                            cursor.executemany("INSERT INTO comic_artists (comic_id, artist_id) VALUES (%s, %s)", new_artist_values)

                    if new_tags:
                        tag_values = [(tag,) for tag in new_tags]
                        new_tag_ids = []
                        for tag in new_tags:
                            cursor.execute("INSERT INTO tags (name) VALUES (%s) RETURNING id", (tag,))
                            new_tag_ids.append(cursor.fetchone()[0])
                        
                        if new_tag_ids:
                            new_tag_values = [(comic_id, new_tag_id) for new_tag_id in new_tag_ids]
                            cursor.executemany("INSERT INTO comic_tags (comic_id, tag_id) VALUES (%s, %s)", new_tag_values)

                    if new_translators:
                        translator_values = [(translator,) for translator in new_translators]
                        new_translator_ids = []
                        for translator in new_translators:
                            cursor.execute("INSERT INTO translators (name) VALUES (%s) RETURNING id", (translator,))
                            new_translator_ids.append(cursor.fetchone()[0])

                        if new_translator_ids:
                            new_translator_values = [(comic_id, new_translator_id) for new_translator_id in new_translator_ids]
                            cursor.executemany("INSERT INTO comic_translators (comic_id, translator_id) VALUES (%s, %s)", new_translator_values)

                    if filename != None:
                        request_files = {"file": (filename, image_cover)}
                        request_data = {"user_id": user_id, "comic_id": comic_id}
                        response = requests.post(
                            url=STORAGE_SERVICE_UPLOAD_URL, 
                            files=request_files, 
                            data=request_data
                        )
                        if response.status_code != 200:
                            connection.rollback()
                            return make_response({"result": "Failed to upload image"}, 400)

                connection.commit()
            result = {"message": "Data received successfully"}
            return make_response(jsonify(result), 201)
        except Exception as e:
            if connection:
                connection.rollback()
            return make_response({"result": f'{e}'}, 400)

@ns.route("/bulk")
class ComicBulkAPI(Resource):
    @auth_required
    def post(self):
        try:            
            user_id = g.user_id
            file_data = request.get_array(field_name='file')

            if len(file_data) == 0 or len(file_data) == 1:
                return make_response({"result": "No data provided"}, 400)
            
            data = file_data[1:]

            for comic_data in data:
                title = comic_data[0]
                if not title:
                    continue
                
                alternative_title = comic_data[1]
                published_date = comic_data[2]
                status = comic_data[3]
                comic_type = comic_data[4]
                description = comic_data[5]
                image_url = comic_data[6]

                if published_date:
                    published_datetime = parse_published_date(published_date)

                    if published_datetime is None:
                        return make_response({"result": "Invalid published date format"}, 400)
                
                with connection:
                    with connection.cursor() as cursor:
                        query = """
                            INSERT INTO comics (title, alternative_title, published_date, status, type, description, image_cover, user_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;
                        """
                        filename = secure_filename(os.path.basename(image_url))

                        if not allowed_file(filename):
                            return make_response({"result": "File type not allowed"}, 400)

                        cursor.execute(query, (title, alternative_title, published_datetime, status, comic_type, description, filename, user_id))
                        comic_id = cursor.fetchone()[0]

                        filename = None
                        if image_url:
                            request_payload = {"url": image_url, "user_id": str(user_id), "comic_id": str(comic_id)}
                            response = requests.post(STORAGE_SERVICE_SAVE_URL, json=request_payload)
                            if response.status_code != 200:
                                connection.rollback()
                                return make_response({"result": "Failed to download image"}, 400)
                        connection.commit()

            result = {"message": "Data received successfully"}
            return make_response(jsonify(result), 201)
        except Exception as e:
            if connection:
                connection.rollback()
            return make_response({"result": f'{e}'}, 400)

@ns.route("/bulk-check")
class ComicBulkCheckAPI(Resource):
    @auth_required
    def post(self):
        file_data = request.get_array(field_name='file')
        return make_response(jsonify(file_data))


@ns.route("/<string:comic_id>")
class DeleteComicAPI(Resource):
    
    @auth_required
    def delete(self, comic_id):
        user_id = g.user_id       
        try:
            with connection:
                with connection.cursor() as cursor:
                    query = "DELETE FROM comics WHERE id = %s AND user_id = %s"
                    cursor.execute(query, (comic_id, user_id))
                    
                    if cursor.rowcount == 0:
                        return make_response(jsonify({'message': 'comic not found'}), 404)

                comic_url = f'{STORAGE_SERVICE_FILES_URL}{user_id}/{comic_id}'
                response = requests.delete(comic_url)
                if response.status_code != 200:
                    connection.rollback()
                    return make_response({"result": "Failed to delete images"}, 400)
                connection.commit()
                return make_response(jsonify({'message': 'comic deleted'}), 200)
        except Exception as e:
            if connection:
                connection.rollback()
            return make_response(jsonify({'result': f'{e}'}), 200)
