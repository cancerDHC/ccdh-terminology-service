from flask import Flask, jsonify, stream_with_context, request, Response, current_app
from flask_marshmallow import Marshmallow
from flask_restx import Api
from py2neo import Graph
from ccdh.apis.db import get_neo4j_graph
from ccdh.mdr.mdr_graph import MdrGraph
from sssom.sssom_document import MappingSetDocument
from datetime import datetime
from biolinkml.utils.yamlutils import as_json_object
from jsonasobj.jsonobj import as_dict
from ccdh.apis import api
from ccdh.apis.schemas import ma

app = Flask(__name__)
api.init_app(app)
ma.init_app(app)


def generate_sssom_tsv(mapping_set_doc: MappingSetDocument):
    meta_attributes = ['creator_id', 'license', 'mapping_provider', 'comment']

    mapping_set = mapping_set_doc.mapping_set
    for meta_attribute in meta_attributes:
        if mapping_set[meta_attribute]:
            yield f'#{meta_attribute}: {mapping_set[meta_attribute]}\n'
    yield '#curie_map:\n'
    for curie, uri in mapping_set_doc.curie_map.items():
        yield f'#  {curie}: "{uri}"\n'
    mappings = mapping_set.mappings
    row_num = 0
    keys = []
    for mapping in mappings:
        if row_num == 0:
            for key in mapping:
                if mapping[key] is not None:
                    keys.append(key)
            yield '\t'.join(keys) + '\n'
        row_num += 1
        row = []
        for key in keys:
            row.append(mapping[key] if mapping[key] else '')
        yield '\t'.join(row) + '\n'


def jsonify_mapping_set_document(mapping_set_doc: MappingSetDocument):
    mapping_set = mapping_set_doc.mapping_set
    mapping_set_dict = {'curie_map': mapping_set_doc.curie_map, 'mapping_set': []}
    meta_attributes = ['creator_id', 'license', 'mapping_provider', 'comment']
    for meta_attribute in meta_attributes:
        if mapping_set[meta_attribute]:
            mapping_set_dict[meta_attribute] = mapping_set[meta_attribute]
    for mapping in mapping_set.mappings:
        mapping_dict = as_dict(as_json_object(mapping))
        mapping_set_dict['mapping_set'].append(mapping_dict)
    return jsonify(mapping_set_dict)


@app.route('/mapping/data_element/<context>/<entity>', methods=['GET'])
@app.route('/mapping/data_element/<context>/<entity>/<attribute>', methods=['GET'])
def data_element(context: str, entity: str, attribute: str = None):
    graph: Graph = get_neo4j_graph()
    mdr_graph = MdrGraph(graph)

    content_type = request.mimetype
    if content_type == 'text/tab-separated-values+sssom':
        mapping_set_doc = mdr_graph.find_permissible_value_mappings(context, entity, attribute, pagination=False)
        return Response(stream_with_context(generate_sssom_tsv(mapping_set_doc)))
    else:  # default mimetype is JSON
        mapping_set_doc = mdr_graph.find_permissible_value_mappings(context, entity, attribute)
        return jsonify_mapping_set_document(mapping_set_doc)


@app.route('/hello')
def hello():
    return 'hello world!'


if __name__ == '__main__':
    app.run()
