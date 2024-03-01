import io
from flask import redirect, send_file
from flask_restx import Resource, Namespace
import requests
import mimetypes
from app.cms_api.constants import STORAGE_SERVICE_FILES_URL
from app.config import Config

ns = Namespace("storages") 

@ns.route('/<user_id>/<comic_id>/<chapter_id>/<filename>')
class StoragesChapterAPI(Resource):
    def get(self, user_id, comic_id, chapter_id, filename):
        image_url = f"{STORAGE_SERVICE_FILES_URL}{user_id}/{comic_id}/{chapter_id}/{filename}"
        response = requests.get(image_url)
        if response.status_code == 200:
            mimetype, _ = mimetypes.guess_type(filename)
            if not mimetype:
                mimetype = 'application/octet-stream'
            return send_file(io.BytesIO(response.content), mimetype=mimetype)
        return redirect(Config.NO_IMAGE_URL)
    

@ns.route('/<user_id>/<comic_id>/<filename>')
class StoragesCoverAPI(Resource):
    def get(self, user_id, comic_id, filename):
        image_url = f"{STORAGE_SERVICE_FILES_URL}{user_id}/{comic_id}/{filename}"
        response = requests.get(image_url)
        if response.status_code == 200:
            mimetype, _ = mimetypes.guess_type(filename)
            if not mimetype:
                mimetype = 'application/octet-stream'
            return send_file(io.BytesIO(response.content), mimetype=mimetype)
        return redirect(Config.NO_IMAGE_URL)
    
    
