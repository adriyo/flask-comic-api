from flask_restx import Api
from app.config import Config

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
        title="Comic API",
        version='1.0',
        description="Testing Comic API",
        prefix=f'/{Config.API_PREFIX}',
        doc=f'/{Config.API_DOC_PREFIX}',
        authorizations=authorizations,
        security='apikey'
 )