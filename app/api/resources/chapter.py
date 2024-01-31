from flask import jsonify, make_response
from flask_restx import Resource, Namespace
from ..models import chapterInputParser

ns = Namespace("api")


@ns.route("/comics/chapter/<string:comicId>")
class ChapterImagesAPI(Resource):
    def get(self, comicId):
        return make_response(jsonify({'message': 'success'}), 200)

    @ns.expect(chapterInputParser)
    def post(self, comicId):
        return make_response(jsonify({'message': 'success'}), 200)
