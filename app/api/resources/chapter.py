from flask_restx import Resource, Namespace
from ...extensions import sb
from ..models import chapterInputParser
from werkzeug.utils import secure_filename
from datetime import datetime

ns = Namespace("api")


@ns.route("/comics/chapter/<string:comicId>")
class ChapterImagesAPI(Resource):
    @ns.expect(chapterInputParser)
    def post(self, comicId):
        args = chapterInputParser.parse_args()

        title = args['title']
        images = args['images']

        try:
            data, count = sb.table("comic_chapters") \
                .insert({
                    "label": title,
                    "comic_id": comicId
                }) \
                .execute()
            if isinstance(data, tuple) and len(data) > 1 and isinstance(data[1], list):
                chapter_id = data[1][0].get('id', None)
            else:
                chapter_id = None

            index = 0
            for image in images:
                filename = secure_filename(image.filename)
                timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
                _, extension = filename.rsplit('.', 1)

                imageFile = image.read()
                path = f'chapter/{timestamp}-{index + 1}.{extension}'

                sb.storage.from_("upload").upload(
                    file=imageFile, path=path, file_options={"content-type": image.content_type})

                imagePublicUrl = sb.storage.from_(
                    'upload').get_public_url(path)
                data, count = sb.table("chapter_images") \
                    .insert({"url": imagePublicUrl, "chapter_id": chapter_id}) \
                    .execute()
                index += 1
            return {"message": "Data received successfully "}
        except Exception as e:
            return {"result": f'{e}'}
