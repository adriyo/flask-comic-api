import os
from flask import redirect, send_from_directory
from flask_restx import Resource, Namespace
from app.config import Config

ns = Namespace("storages")

@ns.route('/<filename>')
class StoragesAPI(Resource):
    def get(self, filename):
        no_image_url = 'https://via.placeholder.com/200x200?text=NOT%20FOUND'
        file_path = os.path.join(os.getcwd(), Config.UPLOAD_FOLDER) 
        if not os.path.exists(file_path):
            return redirect(no_image_url)
        return send_from_directory(file_path, filename)
