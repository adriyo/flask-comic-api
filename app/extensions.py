from flask_restx import Api


api = Api(
    title="Comic API",
    version='1.0',
    description="Testing Comic API",
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
