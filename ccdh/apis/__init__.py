from flask_restx import Api
from ccdh.apis.resources import ns as ccdh_ns

api = Api(
    title='CCDH Terminology Harmonization API',
    version='0.1',
    description='An api to facilitate the CCDH terminology value harmonization process',
)

api.add_namespace(ccdh_ns, path='/ccdh')
