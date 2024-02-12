from werkzeug.datastructures import FileStorage
from app import api

comicInputParser = api.parser()
comicInputParser.add_argument(
    'title', required=True, help='comic title', location='form')
comicInputParser.add_argument(
    'author', required=True, help='comic author', location='form')
comicInputParser.add_argument(
    'published_date', required=False, location='form', type=str)
comicInputParser.add_argument(
    'status', required=False, location='form', type=int)
comicInputParser.add_argument(
    'description', required=True, help='fill the description', location='form')
comicInputParser.add_argument(
    'image_cover', required=True, type=FileStorage, location='files')

chapterInputParser = api.parser()
chapterInputParser.add_argument(
    'title', required=True, help='chapter title', location='form')
chapterInputParser.add_argument(
    'images', required=True, type=FileStorage, location='files', action="append")

chapterUpdateInputParser = api.parser()
chapterUpdateInputParser.add_argument(
    'title', required=True, help='chapter title', location='form')
chapterUpdateInputParser.add_argument(
    'images', required=True, type=FileStorage, location='files', action="append")
chapterUpdateInputParser.add_argument(
    'image_ids', required=True, type=int, location='form', action="append")

userRegisterParser = api.parser()
userRegisterParser.add_argument(
    'name', required=True, type=str)
userRegisterParser.add_argument(
    'email', required=True, type=str)
userRegisterParser.add_argument(
    'password', required=True, type=str)

userLoginParser = api.parser()
userLoginParser.add_argument(
    'email', required=True, type=str)
userLoginParser.add_argument(
    'password', required=True, type=str)
