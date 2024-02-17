import io
from flask import redirect, send_file
from flask_restx import Resource, Namespace
import requests
import mimetypes

ns = Namespace("storages")
STORAGE_SERVICE_URL = 'http://storage-service:8080/files/'  # Change this to your storage service URL

@ns.route('/<filename>')
class StoragesAPI(Resource):
    def get(self, filename):
        no_image_url = 'https://via.placeholder.com/200x200?text=NOT%20FOUND'
        image_url = f"{STORAGE_SERVICE_URL}{filename}"
        response = requests.get(image_url)
        if response.status_code == 200:
            mimetype, _ = mimetypes.guess_type(filename)
            if not mimetype:
                mimetype = 'application/octet-stream'
            return send_file(io.BytesIO(response.content), mimetype=mimetype)
        return redirect(no_image_url)
