import os
from flask import send_from_directory
from flask_restx import Resource, Namespace
from ...extensions import api
ns = Namespace("storages")


@ns.route('/<filename>')
class StoragesAPI(Resource):
    def get(self, filename):
        return send_from_directory(
            os.path.join(os.getcwd(), 'storages'),
            filename)
