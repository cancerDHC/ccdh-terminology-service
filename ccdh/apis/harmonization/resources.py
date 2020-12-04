from flask_restx import Resource, Namespace

from ccdh.apis.harmonization.schemas import DataElementSchema, MappingSetSchema
from ccdh.config import neo4j_graph
from ccdh.mdr.mdr_graph import MdrGraph

from ccdh.apis.harmonization.parsers import file_upload

ns = Namespace('harmonization', description='CCDH Value Harmonization')
mdr_graph = MdrGraph(neo4j_graph())

data_element_schema = DataElementSchema()
data_elements_schema = DataElementSchema(many=True)
mapping_set_schema = MappingSetSchema()


param_descriptions = {
    'context': 'The context of the data element',
    'entity': 'The entity that the data element is defined in',
    'attribute': 'The attribute name of the data element',
}


@ns.route('/data-elements/<context>/<entity>/<attribute>', endpoint='harmonization_data-element', doc={
    "description": "Data element of a context-entity-attribute",
    "params": {key: param_descriptions[key] for key in ['context', 'entity', 'attribute']}
})
@ns.route('/data-elements/<context>/<entity>', endpoint='harmonization_entity-data-elements', doc={
    "description": "Data elements in a context-entity",
    "params":  {key: param_descriptions[key] for key in ['context', 'entity']}
}, defaults={'attribute': None})
@ns.route('/data-elements/<context>', endpoint='harmonization_context-data-elements', doc={
    "description": "Data elements in a context",
    "params": {'context': param_descriptions['context']}
}, defaults={'attribute': None, 'entity': None})
@ns.response(404, 'Data Element not found')
class DataElement(Resource):
    def get(self, context, entity, attribute):
        return data_elements_schema.dump(mdr_graph.find_data_elements(context, entity, attribute))


@ns.route('/mapping/data-elements/<context>/<entity>/<attribute>', endpoint='harmonization_mapping-data-element', doc={
    "description": "Mapping of permissible values of a data element",
    "params": {key: param_descriptions[key] for key in ['context', 'entity', 'attribute']}
})
@ns.route('/mapping/data-elements/<context>/<entity>', endpoint='harmonization_mapping-entity-data-elements', doc={
    "description": "Mapping of permissible values of data elements in a context-entity",
    "params":  {key: param_descriptions[key] for key in ['context', 'entity']}
}, defaults={'attribute': None})
@ns.route('/mapping/data-elements/<context>', endpoint='harmonization_mapping-context-data-elements', doc={
    "description": "Mapping of permissible values of data elements in a context",
    "params": {'context': param_descriptions['context']}
}, defaults={'attribute': None, 'entity': None})
@ns.response(404, 'Mapping not found for data element')
class DataElementMapping(Resource):
    @ns.produces(['application/json', 'text/tab-separated-values+sssom'])
    def get(self, context, entity, attribute):
        return mapping_set_schema.dump(mdr_graph.find_mappings_of_data_element(context, entity, attribute, pagination=False))


@ns.route('/mapping', endpoint='Upload mapping SSSOM file', doc={
    'tsv_file': 'TSV format of mapping',
})
@ns.expect(file_upload)
class Mapping(Resource):
    def post(self):
        args = file_upload.parse_args()
        file = args.get('tsv_file')
        print(file.filename)
        return "Uploaded file is " + file.filename