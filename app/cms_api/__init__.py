from flask import Blueprint

cms_api_bp = Blueprint(
    'cms_api_bp',
    __name__,
    url_prefix='/cms-api',
    template_folder="templates"
)

from .resources import user, storage, comic, chapter