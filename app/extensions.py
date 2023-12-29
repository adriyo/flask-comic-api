from supabase import create_client
from app.config import Config
from flask_restx import Api


api = Api(
    title="Comic API",
    version='1.0',
    description="Testing Comic API",
)

sb = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
