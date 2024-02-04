from flask_restx import Api

api = Api(
        title="Comic API",
        version='1.0',
        description="Testing Comic API",
        prefix="/api",
        doc='/docs',
 )