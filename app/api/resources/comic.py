from flask_restx import Resource, Namespace
from ...extensions import sb
from ..models import comicInputParser
from werkzeug.utils import secure_filename
from datetime import datetime

ns = Namespace("api")


@ns.route("/comics")
class ComicListAPI(Resource):
    def get(self):
        response = sb.table('comics').select("*").execute()
        return response.data


@ns.route("/comic")
class ComicAPI(Resource):
    @ns.expect(comicInputParser)
    def post(self):
        args = comicInputParser.parse_args()

        title = args['title']
        description = args['description']
        author = args['author']
        published_date = args['published_date']
        status = args['status']
        image_cover = args['imageCover']

        try:
            published_datetime = datetime.strptime(
                published_date, "%Y-%m-%d").date()
        except Exception as e:
            published_datetime = datetime.date()

        try:
            filename = secure_filename(image_cover.filename)
            timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
            _, extension = filename.rsplit('.', 1)

            imageFile = image_cover.read()
            path = f'cover/{timestamp}.{extension}'

            sb.storage.from_("upload").upload(
                file=imageFile, path=path, file_options={"content-type": image_cover.content_type, "cache-control": "3600", "upsert": "true"})

            imagePublicUrl = sb.storage.from_('upload').get_public_url(path)
            data, count = sb.table("comics") \
                .insert({
                    "image_cover_url": imagePublicUrl,
                    "title": title,
                    "description": description,
                    "status": int(status),
                    "published_date": published_datetime.isoformat(),
                    "author": author
                }) \
                .execute()

            if isinstance(data, tuple) and len(data) > 1 and isinstance(data[1], list):
                comic_id = data[1][0].get('id', None)
            else:
                comic_id = None

            return {"message": "Data received successfully", "data": f'{comic_id}'}
        except Exception as e:
            return {"result": f'{e}'}


@ns.route("/comics/<string:comicId>")
class ChapterListAPI(Resource):
    def get(self, comicId):
        try:
            response = sb.table("comics") \
                .select("*") \
                .eq("id", comicId) \
                .execute()

            return response.data[0]
        except Exception as e:
            return {"code": e.code, "message": e.message, "details": e.details, "hint": e.hint}
