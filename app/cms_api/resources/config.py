from flask_restx import Api
from app.cms_api import cms_api_bp

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    cms_api_bp,
    title="Comic CMS API",
    version='1.0',
    description="API for comic cms",
    doc='/docs',
    authorizations=authorizations,
    security='apikey'
 )
