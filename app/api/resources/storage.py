import io
from flask import redirect, send_file
from flask_restx import Resource, Namespace
import requests
import mimetypes
from app.config import Config

ns = Namespace("storages")
STORAGE_SERVICE_URL = 'http://storage-service:8080/files/' 

@ns.route('/<filename>')
class StoragesAPI(Resource):
    def get(self, filename):
        image_url = f"{STORAGE_SERVICE_URL}{filename}"
        response = requests.get(image_url)
        if response.status_code == 200:
            mimetype, _ = mimetypes.guess_type(filename)
            if not mimetype:
                mimetype = 'application/octet-stream'
            return send_file(io.BytesIO(response.content), mimetype=mimetype)
        return redirect(Config.NO_IMAGE_URL)
